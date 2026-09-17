import tempfile
import unittest
from pathlib import Path
from app import create_app


class TaskTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.database = str(Path(self.folder.name) / 'tasks.db')
        self.app = create_app(self.database)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def tearDown(self):
        self.folder.cleanup()

    def test_api_crud_and_restart(self):
        response = self.client.post('/tasks', json={'title': 'Rapor', 'description': 'Haftalık rapor'})
        self.assertEqual(response.status_code, 201)
        task = response.get_json()
        task_id = task['id']
        self.assertEqual(task['status'], 'pending')
        self.assertTrue(task['created_at'])
        self.assertEqual(len(self.client.get('/tasks').get_json()), 1)
        self.assertEqual(self.client.get(f'/tasks/{task_id}').get_json()['title'], 'Rapor')
        response = self.client.put(f'/tasks/{task_id}', json={'status': 'completed', 'title': 'Bitti'})
        self.assertEqual(response.get_json()['status'], 'completed')
        restarted = create_app(self.database).test_client()
        self.assertEqual(restarted.get(f'/tasks/{task_id}').get_json()['title'], 'Bitti')
        self.assertEqual(self.client.delete(f'/tasks/{task_id}').status_code, 204)
        self.assertEqual(self.client.get(f'/tasks/{task_id}').status_code, 404)

    def test_invalid_data(self):
        for data in ({'title': ' '}, {'title': 12}, {'title': 'a', 'status': 'unknown'}, [], {'title': 'a', 'description': None}):
            self.assertEqual(self.client.post('/tasks', json=data).status_code, 400)
        self.assertEqual(self.client.post('/tasks', data='not json').status_code, 400)
        self.assertEqual(self.client.put('/tasks/999', json={'title': 'x'}).status_code, 404)

    def test_browser_forms(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(self.client.get('/new').status_code, 200)
        self.assertEqual(self.client.post('/new', data={'title': ' '}).status_code, 400)
        self.client.post('/new', data={'title': 'Form görevi', 'description': '<script>alert(1)</script>'})
        self.assertIn(b'&lt;script&gt;', self.client.get('/view/1').data)
        self.assertEqual(self.client.get('/edit/1').status_code, 200)
        self.client.post('/edit/1', data={'title': 'Yeni başlık', 'status': 'completed'})
        self.assertEqual(self.client.get('/tasks/1').get_json()['status'], 'completed')
        self.client.post('/delete/1')
        self.assertEqual(self.client.get('/tasks').get_json(), [])


if __name__ == '__main__':
    unittest.main()
