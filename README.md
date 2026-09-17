# Mini Görev Takip Sistemi

Staj bitirme projesi kapsamında hazırlanan basit bir görev takip uygulaması. Görev ekleme, listeleme, düzenleme, silme ve tamamlanma durumunu değiştirme işlemleri yapılabilir.

**Canlı demo:** https://mini-gorev-takip.onrender.com/

> Demo, Render’ın ücretsiz servisinde çalışır. İlk açılış yaklaşık bir dakika sürebilir. Demodaki kayıtlar sunucu yeniden başlatıldığında silinebilir. Kullanıcı girişi olmadığı için görevler tüm ziyaretçiler tarafından görülebilir ve değiştirilebilir.

## Kullanılan teknolojiler

- Python ve Flask
- SQLite
- HTML, CSS ve Jinja
- Docker

## Özellikler

- Yeni görev ekleme
- Görevleri listeleme ve detaylarını görüntüleme
- Başlık ve açıklamayı düzenleme
- Görev durumunu “Bekliyor” veya “Tamamlandı” olarak değiştirme
- Görev silme
- SQLite ile verileri saklama
- JSON API üzerinden görev işlemleri

Her görevde `id`, `title`, `description`, `status` ve `created_at` alanları bulunur.

## Docker ile çalıştırma

Bilgisayarda Docker kurulu ve çalışır durumda olmalıdır. Proje klasöründe terminal açıp aşağıdaki komutları çalıştırın:

```bash
docker build -t intern-task-app .
docker run -d --name gorev-takip -p 5000:5000 -v gorev-verileri:/app/data intern-task-app
```

Tarayıcıdan http://localhost:5000 adresini açın.

`gorev-verileri` volume’u, konteyner silinip yeniden oluşturulduğunda da verilerin korunmasını sağlar. Volume silinirse kayıtlar da silinir.

Uygulamayı durdurmak için:

```bash
docker stop gorev-takip
```

Yeniden başlatmak için:

```bash
docker start gorev-takip
```

## Docker olmadan çalıştırma

Python 3.12 ile proje klasöründe:

```bash
python -m pip install -r requirements.txt
python app.py
```

Ardından http://localhost:5000 adresini açın.

## API adresleri

| Metot | Adres | Açıklama |
|---|---|---|
| GET | `/tasks` | Tüm görevleri listeler |
| GET | `/tasks/<id>` | Bir görevi getirir |
| POST | `/tasks` | Yeni görev oluşturur |
| PUT | `/tasks/<id>` | Görevi günceller |
| DELETE | `/tasks/<id>` | Görevi siler |

POST ve PUT istekleri `Content-Type: application/json` başlığıyla gönderilir.

Örnek görev:

```json
{
  "title": "Staj raporunu hazırla",
  "description": "Bu hafta yapılan çalışmaları yaz.",
  "status": "pending"
}
```

Durumu değiştirmek için PUT isteğinde şu gövde gönderilebilir:

```json
{
  "status": "completed"
}
```

## Proje yapısı

```text
mini-gorev-takip/
├── app.py
├── templates/
├── static/
│   └── style.css
├── test_app.py
├── requirements.txt
├── Dockerfile
└── README.md
```

`app.py` uygulama adreslerini ve veritabanı işlemlerini, `templates` HTML sayfalarını, `static` ise CSS dosyasını içerir. SQLite veritabanı ilk çalıştırmada otomatik oluşturulur.

## Testler

```bash
python -m unittest -v
```

Testler; API işlemlerini, form kullanımını, geçersiz girişleri ve uygulama yeniden oluşturulduğunda kayıtların korunmasını kontrol eder.
