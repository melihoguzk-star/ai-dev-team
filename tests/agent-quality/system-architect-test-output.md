# Basit Blog Uygulaması — Mimari Kararlar

## 1. Backend Teknoloji Seçimi

### Framework: **FastAPI (Python)**

- **Seçim:** FastAPI
- **Gerekçe:** Basit bir blog uygulaması için FastAPI yeterli ve hızlı geliştirme sağlar. Otomatik OpenAPI/Swagger dokümantasyonu üretir — iOS tarafı API'yi keşfederken bu çok işe yarar. Async desteği built-in gelir, performans açısından Flask'ın önündedir. Type hint tabanlı validation (Pydantic) sayesinde runtime hataları azalır.
- **Neden Django değil:** Django "batteries-included" bir framework. Admin paneli, template engine, form handling gibi bir blog API'si için gereksiz bileşenler taşır. Sadece REST API sunacaksak Django overkill.
- **Neden Express.js değil:** Express minimal ama tip güvenliği yok. TypeScript eklenince boilerplate artar. Python ekosistemi veri işleme ve basit CRUD için daha pragmatik.
- **Neden Spring Boot değil:** Java/Kotlin ekosistemi basit bir blog için fazla ağır. Build süreleri, konfigürasyon karmaşıklığı ve öğrenme eğrisi gereksiz yük getirir.
- **Alternatifler:** Django REST Framework, Express.js, Go (Gin), Spring Boot

### ORM: **SQLAlchemy 2.0**

- **Seçim:** SQLAlchemy 2.0
- **Gerekçe:** Python ekosisteminin en olgun ORM'i. FastAPI ile doğal entegre olur. 2.0 sürümü modern async desteği ve daha temiz query API'si sunar. Migration'lar için Alembic ile birlikte çalışır. Blog gibi basit CRUD operasyonları için yeterli ve anlaşılır.
- **Neden Tortoise ORM değil:** Daha az olgun, topluluk desteği zayıf, production'da karşılaşılan edge case'ler için kaynak bulmak zor.
- **Neden Django ORM değil:** Django framework'üne bağımlı. Sadece ORM olarak kullanmak mümkün ama pratik değil.
- **Alternatifler:** Tortoise ORM, SQLModel, Peewee

---

## 2. Veritabanı Seçimi

### Veritabanı: **PostgreSQL**

- **Seçim:** PostgreSQL
- **Gerekçe:** Blog uygulamasının verisi ilişkiseldir (kullanıcı → yazı → yorum). PostgreSQL bu ilişkileri doğal olarak modeller. Full-text search desteği var — blog yazılarında arama için ayrı bir search engine'e (Elasticsearch vb.) gerek kalmaz. JSON sütun desteği sayesinde ileride esnek veri saklamak gerekirse (örn. post metadata) ek araç gerekmez. Ücretsiz, açık kaynak, production-ready.
- **Neden MySQL değil:** PostgreSQL'in full-text search'ü daha güçlü. JSON desteği daha olgun. Genel olarak standartlara daha uyumlu.
- **Neden MongoDB değil:** Blog verisi ilişkisel yapıda (user → post → comment). Document DB'de bu ilişkileri yönetmek gereksiz karmaşıklık getirir. JOIN yerine application-level lookup yapmak zorunda kalırsınız.
- **Neden SQLite değil:** Geliştirme ortamı için uygun ama concurrent write'larda sorun çıkarır. Production'a taşınacak bir uygulama için baştan PostgreSQL kullanmak geçiş maliyetini sıfırlar.
- **Alternatifler:** MySQL, SQLite (sadece dev), MongoDB

### Temel Tablolar

```sql
-- Kullanıcılar
CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(50) UNIQUE NOT NULL,
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    display_name  VARCHAR(100),
    created_at    TIMESTAMP DEFAULT NOW(),
    updated_at    TIMESTAMP DEFAULT NOW()
);

-- Blog Yazıları
CREATE TABLE posts (
    id          SERIAL PRIMARY KEY,
    author_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title       VARCHAR(255) NOT NULL,
    slug        VARCHAR(255) UNIQUE NOT NULL,
    content     TEXT NOT NULL,
    status      VARCHAR(20) DEFAULT 'draft',  -- draft, published
    published_at TIMESTAMP,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

-- Yorumlar
CREATE TABLE comments (
    id         SERIAL PRIMARY KEY,
    post_id    INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content    TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Notlar:**
- `slug` alanı SEO-friendly URL'ler için (`/posts/basit-blog-mimarisi`).
- `status` alanı taslak/yayın ayrımı için yeterli. Ayrı bir tablo veya enum tipi overkill.
- `ON DELETE CASCADE` ile kullanıcı silinince yazıları ve yorumları da temizlenir.
- Index'ler: `posts.slug`, `posts.author_id`, `comments.post_id` sütunlarına index eklenmeli.

---

## 3. iOS Mimari Kararları

### Mimari Pattern: **MVVM (Model-View-ViewModel)**

- **Seçim:** MVVM
- **Gerekçe:** SwiftUI ile doğal uyum sağlar (`@Published`, `@StateObject`, `ObservableObject`). Blog gibi basit bir uygulamada View ↔ ViewModel ↔ Model katmanlaması yeterli ve anlaşılır. Unit test yazarken ViewModel'i View'dan bağımsız test edebilirsiniz.
- **Neden MVC değil:** Apple'ın varsayılan pattern'i ama ViewController'lar şişer (Massive View Controller). Test edilebilirlik düşük.
- **Neden VIPER/Clean Architecture değil:** Basit bir blog uygulaması için çok fazla katman ve protokol. 3 ekranlı bir uygulama için Router, Interactor, Presenter ayrımı gereksiz karmaşıklık.
- **Neden TCA değil:** Composable Architecture güçlü ama öğrenme eğrisi yüksek. Küçük bir ekip veya tek geliştirici için overfit.
- **Alternatifler:** MVC, VIPER, TCA (The Composable Architecture)

### Networking Layer: **URLSession + basit API client**

- **Seçim:** Native URLSession üzerine ince bir abstraction katmanı
- **Gerekçe:** Blog uygulamasının network ihtiyacı basit: GET (yazıları listele, detay getir), POST (yazı/yorum oluştur), PUT (yazı güncelle), DELETE. Bu CRUD operasyonları için 3. parti kütüphane gereksiz bağımlılık. `async/await` ile URLSession zaten temiz ve okunabilir kod üretir. Basit bir `APIClient` struct'ı ile generic request/response handling yeterli.
- **Neden Alamofire değil:** URLSession modern Swift ile (async/await) zaten yeterince ergonomik. Alamofire'ın sunduğu ek özellikler (retry, intercept, certificate pinning) basit blog için gerekli değil. Gereksiz dependency.
- **Neden Moya değil:** Moya, Alamofire üzerine bir katman daha ekler. Basit CRUD için iki kütüphane dependency'si gereksiz.
- **Alternatifler:** Alamofire, Moya

---

## Özet Tablo

| Karar | Seçim | Ana Gerekçe |
|-------|-------|-------------|
| Backend Framework | FastAPI | Hızlı geliştirme, otomatik API docs, async |
| ORM | SQLAlchemy 2.0 | Olgun, async destekli, Alembic migration |
| Veritabanı | PostgreSQL | İlişkisel veri, full-text search, production-ready |
| iOS Pattern | MVVM | SwiftUI uyumu, test edilebilirlik |
| Networking | URLSession | Yeterli, bağımlılık yok, async/await |
