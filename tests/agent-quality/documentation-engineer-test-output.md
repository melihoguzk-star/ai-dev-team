# Basit REST API

CRUD operasyonlarini destekleyen, Python tabanli hafif bir REST API servisi. FastAPI uzerine insa edilmistir ve JWT tabanli kimlik dogrulama ile guvenli erisim saglar.

---

## Ozellikler

- **CRUD Islemleri** -- Kaynaklari olusturma, okuma, guncelleme ve silme
- **JWT Kimlik Dogrulama** -- Token tabanli guvenli erisim kontrolu
- **Otomatik API Dokumantasyonu** -- Swagger UI ve ReDoc destegi (`/docs`, `/redoc`)
- **Veri Dogrulama** -- Pydantic modelleri ile istek/yanit sema kontrolu
- **CORS Destegi** -- Farkli originlerden gelen isteklere yapilandirmali erisim izni

---

## Hizli Baslangic

### Gereksinimler

| Bagimlilk   | Minimum Surum |
|-------------|---------------|
| Python      | 3.11+         |
| pip         | 23.0+         |

### Kurulum

1. **Repoyu klonlayin:**

```bash
git clone https://github.com/kullanici/basit-rest-api.git
cd basit-rest-api
```

2. **Sanal ortam olusturun ve aktif edin:**

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Bagimliliklari yukleyin:**

```bash
pip install -r requirements.txt
```

4. **Ortam degiskenlerini yapilandirin:**

```bash
cp .env.example .env
# .env dosyasini duzenleyin
```

### Calistirma

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Sunucu baslatildiktan sonra API dokumantasyonuna erisim:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## API Endpoint'leri

| Method   | Path              | Aciklama                        | Auth    |
|----------|-------------------|---------------------------------|---------|
| `POST`   | `/auth/login`     | Kullanici girisi, JWT token al  | Hayir   |
| `POST`   | `/auth/register`  | Yeni kullanici kaydı            | Hayir   |
| `GET`    | `/items`          | Tum kayitlari listele           | Evet    |
| `GET`    | `/items/{id}`     | Belirli bir kaydi getir         | Evet    |
| `POST`   | `/items`          | Yeni kayit olustur              | Evet    |
| `PUT`    | `/items/{id}`     | Mevcut kaydi guncelle           | Evet    |
| `DELETE` | `/items/{id}`     | Kaydi sil                       | Evet    |
| `GET`    | `/health`         | Servis saglik kontrolu          | Hayir   |

### Ornek Istek

```bash
# Giris yap ve token al
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "kullanici@ornek.com", "password": "sifre123"}'

# Token ile kayitlari listele
curl -X GET http://localhost:8000/items \
  -H "Authorization: Bearer <TOKEN>"
```

---

## Ortam Degiskenleri

| Degisken          | Aciklama                     | Varsayilan            | Zorunlu |
|-------------------|------------------------------|-----------------------|---------|
| `DATABASE_URL`    | Veritabani baglanti adresi   | `sqlite:///./app.db`  | Evet    |
| `SECRET_KEY`      | JWT imzalama anahtari        | --                    | Evet    |
| `ACCESS_TOKEN_TTL`| Token gecerlilik suresi (dk) | `30`                  | Hayir   |
| `DEBUG`           | Hata ayiklama modu           | `false`               | Hayir   |
| `CORS_ORIGINS`    | Izin verilen originler       | `*`                   | Hayir   |

---

## Proje Yapisi

```
basit-rest-api/
├── app/
│   ├── __init__.py
│   ├── main.py            # Uygulama giris noktasi
│   ├── config.py          # Yapilandirma ayarlari
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py        # Kullanici modeli
│   │   └── item.py        # Kayit modeli
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py        # Kimlik dogrulama endpoint'leri
│   │   └── items.py       # CRUD endpoint'leri
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py        # Kullanici semalari
│   │   └── item.py        # Kayit semalari
│   └── services/
│       ├── __init__.py
│       ├── auth.py        # JWT islemleri
│       └── database.py    # Veritabani baglantisi
├── tests/
│   ├── test_auth.py
│   └── test_items.py
├── .env.example
├── requirements.txt
└── README.md
```

---

## Katkida Bulunma

1. Repoyu forklayın
2. Yeni bir branch olusturun (`git checkout -b ozellik/yeni-ozellik`)
3. Degisikliklerinizi commit edin (`git commit -m "feat: yeni ozellik eklendi"`)
4. Branch'i push edin (`git push origin ozellik/yeni-ozellik`)
5. Pull Request acin

Commit mesajlari icin [Conventional Commits](https://www.conventionalcommits.org/) standardini takip edin.

---

## Lisans

Bu proje [MIT Lisansi](LICENSE) altinda lisanslanmistir.
