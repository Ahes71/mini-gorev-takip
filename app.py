import os
import sqlite3
from pathlib import Path

from flask import Flask, abort, g, jsonify, redirect, render_template, request, url_for


def create_app(database=None):
    app = Flask(__name__)
    app.config['DATABASE'] = database or os.environ.get(
        'DATABASE_PATH', str(Path(__file__).parent / 'data' / 'tasks.db')
    )

    def get_db():
        if 'db' not in g:
            g.db = sqlite3.connect(app.config['DATABASE'])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(error):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    Path(app.config['DATABASE']).parent.mkdir(parents=True, exist_ok=True)
    with app.app_context():
        get_db().execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'completed')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        get_db().commit()

    def find_task(task_id):
        task = get_db().execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
        if task is None:
            abort(404, description='Görev bulunamadı.')
        return task

    def validate(data):
        if not isinstance(data, dict):
            return 'Geçerli bir JSON nesnesi gönderin.'
        if not isinstance(data.get('title'), str) or not data['title'].strip():
            return 'Başlık boş bırakılamaz.'
        if len(data['title'].strip()) > 120:
            return 'Başlık en fazla 120 karakter olabilir.'
        if not isinstance(data.get('description', ''), str) or len(data.get('description', '')) > 2000:
            return 'Açıklama en fazla 2000 karakter olabilir.'
        if data.get('status', 'pending') not in ('pending', 'completed'):
            return 'Durum pending veya completed olmalıdır.'

    def save_task(data, task_id=None):
        values = (data['title'].strip(), data.get('description', '').strip(), data.get('status', 'pending'))
        if task_id is None:
            cursor = get_db().execute(
                'INSERT INTO tasks (title, description, status) VALUES (?, ?, ?)', values)
            task_id = cursor.lastrowid
        else:
            get_db().execute('UPDATE tasks SET title = ?, description = ?, status = ? WHERE id = ?',
                             values + (task_id,))
        get_db().commit()
        return task_id

    @app.get('/')
    def index():
        tasks = get_db().execute('SELECT * FROM tasks ORDER BY id DESC').fetchall()
        return render_template('index.html', tasks=tasks)

    @app.route('/new', methods=['GET', 'POST'])
    def new_task():
        data = {'title': '', 'description': '', 'status': 'pending'}
        error = None
        if request.method == 'POST':
            data = request.form.to_dict()
            error = validate(data)
            if error is None:
                save_task(data)
                return redirect(url_for('index'))
        return render_template('form.html', task=data, error=error, editing=False), 400 if error else 200

    @app.get('/view/<int:task_id>')
    def detail(task_id):
        return render_template('detail.html', task=find_task(task_id))

    @app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
    def edit_task(task_id):
        data = dict(find_task(task_id))
        error = None
        if request.method == 'POST':
            data.update(request.form.to_dict())
            error = validate(data)
            if error is None:
                save_task(data, task_id)
                return redirect(url_for('detail', task_id=task_id))
        return render_template('form.html', task=data, error=error, editing=True), 400 if error else 200

    @app.post('/delete/<int:task_id>')
    def delete_task(task_id):
        find_task(task_id)
        get_db().execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        get_db().commit()
        return redirect(url_for('index'))

    @app.get('/tasks')
    def api_list():
        rows = get_db().execute('SELECT * FROM tasks ORDER BY id DESC').fetchall()
        return jsonify([dict(row) for row in rows])

    @app.get('/tasks/<int:task_id>')
    def api_detail(task_id):
        return jsonify(dict(find_task(task_id)))

    @app.post('/tasks')
    def api_create():
        data = request.get_json(silent=True)
        error = validate(data)
        if error:
            return jsonify(error=error), 400
        task_id = save_task(data)
        return jsonify(dict(find_task(task_id))), 201

    @app.put('/tasks/<int:task_id>')
    def api_update(task_id):
        data = dict(find_task(task_id))
        incoming = request.get_json(silent=True)
        if not isinstance(incoming, dict) or not incoming:
            return jsonify(error='Güncellenecek alanları JSON olarak gönderin.'), 400
        data.update(incoming)
        error = validate(data)
        if error:
            return jsonify(error=error), 400
        save_task(data, task_id)
        return jsonify(dict(find_task(task_id)))

    @app.delete('/tasks/<int:task_id>')
    def api_delete(task_id):
        find_task(task_id)
        get_db().execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        get_db().commit()
        return '', 204

    @app.errorhandler(404)
    def not_found(error):
        if request.path == '/tasks' or request.path.startswith('/tasks/'):
            return jsonify(error='Görev bulunamadı.'), 404
        return render_template('404.html'), 404

    return app


if __name__ == '__main__':
    create_app().run(host='0.0.0.0', port=5000, debug=False)
