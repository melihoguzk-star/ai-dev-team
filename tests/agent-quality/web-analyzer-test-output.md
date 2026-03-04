# JSONPlaceholder API Analiz Raporu

**Tarih:** 2026-03-04  
**Analiz Eden:** Dvina Code - Web Analyzer Agent  
**Hedef:** https://jsonplaceholder.typicode.com

---

## 1. GENEL BAKIS

**JSONPlaceholder**, gelisiticiler icin olusturulmus ucretsiz bir **fake REST API** servisidir.

- **Amac:** Frontend gelistiricilerin prototipleme, test yazma ve ogrenme sureclerinde gercek bir backend olmadan REST API cagrilari yapabilmesini saglamak.
- **Hedef Kitle:** Frontend gelisiticiler, mobil uygulama gelistiriciler, API ogrenmeye baslayan yeni gelisiticiler, bootcamp ogrencileri.
- **Kullanim Alanlari:** Prototipleme, kod ornekleri, tutorial'lar, teknik mulakat hazirlik, test ortamlari.
- **Veri Yapisi:** Statik, onceden tanimlanmis sahte (fake) veri seti. Yazma islemleri (POST/PUT/DELETE) simule edilir ancak sunucuda kalici degisiklik yapmaz.

---

## 2. SAYFA YAPISI

| Sayfa/Bolum | Aciklama |
|---|---|
| `/` | Ana sayfa - API dokumantasyonu ve kullanim kilavuzu |
| `/posts` | Blog yazilari (100 adet) |
| `/comments` | Yorum verileri (500 adet) |
| `/albums` | Foto albumu verileri (100 adet) |
| `/photos` | Fotograf verileri (5000 adet) |
| `/todos` | Yapilacaklar listesi (200 adet) |
| `/users` | Kullanici verileri (10 adet) |

---

## 3. API ENDPOINTLERI

### 3.1 Posts (Yazilar)

| Method | Endpoint | Aciklama |
|---|---|---|
| `GET` | `/posts` | Tum yazilari listele |
| `GET` | `/posts/{id}` | Belirli bir yaziyi getir |
| `GET` | `/posts?userId={id}` | Kullaniciya gore yazilari filtrele |
| `POST` | `/posts` | Yeni yazi olustur (simule) |
| `PUT` | `/posts/{id}` | Yaziyi guncelle (simule) |
| `PATCH` | `/posts/{id}` | Yaziyi kismi guncelle (simule) |
| `DELETE` | `/posts/{id}` | Yaziyi sil (simule) |

### 3.2 Comments (Yorumlar)

| Method | Endpoint | Aciklama |
|---|---|---|
| `GET` | `/comments` | Tum yorumlari listele |
| `GET` | `/comments/{id}` | Belirli bir yorumu getir |
| `GET` | `/comments?postId={id}` | Yaziya gore yorumlari filtrele |
| `GET` | `/posts/{id}/comments` | Nested: Yazinin yorumlarini getir |

### 3.3 Users (Kullanicilar)

| Method | Endpoint | Aciklama |
|---|---|---|
| `GET` | `/users` | Tum kullanicilari listele |
| `GET` | `/users/{id}` | Belirli bir kullaniciyi getir |

### 3.4 Albums (Albumler)

| Method | Endpoint | Aciklama |
|---|---|---|
| `GET` | `/albums` | Tum albumleri listele |
| `GET` | `/albums/{id}` | Belirli bir albumu getir |
| `GET` | `/albums?userId={id}` | Kullaniciya gore albumleri filtrele |
| `GET` | `/albums/{id}/photos` | Nested: Album fotograflarini getir |

### 3.5 Photos (Fotograflar)

| Method | Endpoint | Aciklama |
|---|---|---|
| `GET` | `/photos` | Tum fotograflari listele |
| `GET` | `/photos/{id}` | Belirli bir fotografi getir |
| `GET` | `/photos?albumId={id}` | Albume gore fotograflari filtrele |

### 3.6 Todos (Yapilacaklar)

| Method | Endpoint | Aciklama |
|---|---|---|
| `GET` | `/todos` | Tum todo'lari listele |
| `GET` | `/todos/{id}` | Belirli bir todo'yu getir |
| `GET` | `/todos?userId={id}` | Kullaniciya gore todo'lari filtrele |

**Toplam tespit edilen endpoint sayisi: 21**

---

## 4. VERI MODELLERI

### 4.1 Entity Yapilari

```
User (Kullanici)
├── id: number
├── name: string
├── username: string
├── email: string
├── address: object
│   ├── street, suite, city, zipcode: string
│   └── geo: { lat: string, lng: string }
├── phone: string
├── website: string
└── company: object
    ├── name: string
    ├── catchPhrase: string
    └── bs: string

Post (Yazi)
├── id: number
├── userId: number (FK -> User)
├── title: string
└── body: string

Comment (Yorum)
├── id: number
├── postId: number (FK -> Post)
├── name: string
├── email: string
└── body: string

Album (Album)
├── id: number
├── userId: number (FK -> User)
└── title: string

Photo (Fotograf)
├── id: number
├── albumId: number (FK -> Album)
├── title: string
├── url: string
└── thumbnailUrl: string

Todo (Yapilacak)
├── id: number
├── userId: number (FK -> User)
├── title: string
└── completed: boolean
```

### 4.2 Entity Iliskileri

```
User (1) ──→ (N) Post
User (1) ──→ (N) Album
User (1) ──→ (N) Todo
Post (1) ──→ (N) Comment
Album (1) ──→ (N) Photo
```

- Tum entity'ler `userId` veya ilgili FK uzerinden bir ust entity'ye baglidir.
- `User` entity'si merkezde yer alir ve diger tum entity'lerin kok kaynagi konumundadir.

---

## 5. TEKNOLOJI STACK (Tahmin)

| Katman | Teknoloji |
|---|---|
| **Runtime** | Node.js |
| **Framework** | Muhtemelen Express.js veya benzeri minimalist framework |
| **Veri Katmani** | Statik JSON dosyalari (veritabani yok) |
| **Hosting** | Vercel / Netlify uzerinde serverless veya klasik VPS |
| **Protokol** | HTTPS, REST (JSON response) |
| **CORS** | Tum originlere acik (Access-Control-Allow-Origin: *) |
| **CDN** | Cloudflare veya benzeri CDN arkasinda |
| **Diger** | Rate limiting yok, authentication yok, stateless yapi |

---

## 6. iOS DONUSUM ONERILERI

Bu API'yi bir iOS uygulamasinda kullanmak icin asagidaki oneriler sunulmaktadir:

### 6.1 Networking Katmani

- **URLSession** veya **Alamofire** ile REST istemcisi olusturun.
- `Codable` protokolunu kullanarak JSON parse islemi yapin.
- Her entity icin ayri `struct` tanimlayarak type-safe veri modelleri olusturun.

### 6.2 Ornek Swift Model

```swift
struct Post: Codable, Identifiable {
    let id: Int
    let userId: Int
    let title: String
    let body: String
}

struct User: Codable, Identifiable {
    let id: Int
    let name: String
    let username: String
    let email: String
    let address: Address
    let phone: String
    let website: String
    let company: Company
}
```

### 6.3 Mimari Oneriler

| Konu | Oneri |
|---|---|
| **Mimari** | MVVM + Repository Pattern |
| **State Yonetimi** | Combine veya async/await ile reactive veri akisi |
| **Cache** | NSCache veya URLCache ile response caching |
| **Offline** | Core Data veya SwiftData ile yerel veri saklama |
| **Sayfalama** | API pagination desteklemiyor; client-side sayfalama uygulayin |
| **Hata Yonetimi** | Custom Error enum ile HTTP durum kodlarini yonetin |
| **Test** | URLProtocol ile mock network layer olusturun |

### 6.4 Onemli Notlar

- Bu API **fake** bir API'dir; yazma islemleri (POST/PUT/DELETE) sunucuda kalici olmaz.
- **Authentication** yoktur; gercek uygulamada token-based auth eklenmelidir.
- **Rate limiting** yoktur; ancak gercek API'ler icin retry ve backoff mekanizmasi planlanmalidir.
- Fotograflar `via.placeholder.com` uzerinden sunulur; `AsyncImage` veya **Kingfisher/SDWebImage** ile yuklenebilir.

---

> **Not:** Bu rapor, Dvina Code Web Analyzer Agent tarafindan otomatik olarak olusturulmustur.
