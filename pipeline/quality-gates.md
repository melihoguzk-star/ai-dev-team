# Kalite Kapıları — Faz Sonrası Kalite Kontrol Prompt'ları

Her faz tamamlandığında aşağıdaki kalite kontrol prompt'unu Claude Code'a verin. `code-reviewer` subagent'ı çıktıyı değerlendirir ve skor verir.

---

## Genel Kalite Kontrol Komutu

```
code-reviewer subagent'ını kullan.

[FAZ_ÇIKTISI_DOSYA_YOLU] dosyasını/dizinini oku ve değerlendir.

Değerlendirme kriterleri:
1. Eksiksizlik: Önceki fazın tüm beklenen bölümleri var mı?
2. Tutarlılık: Önceki fazların çıktılarıyla uyumlu mu?
3. Kalite: İçerik yeterli detayda mı? Belirsiz ifadeler var mı?
4. Format: Beklenen formata uygun mu?

100 üzerinden skor ver.

- Skor ≥ 70: ✅ GEÇER — sonraki faza devam edilebilir
- Skor 50-69: ⚠️ KOŞULLU — sorunları listele, düzeltme sonrası tekrar değerlendir
- Skor < 50: ❌ KALIR — fazı tekrar çalıştır

Skor 70 altındaysa:
1. Tespit edilen sorunları öncelik sırasıyla listele
2. Her sorun için düzeltme önerisi ver
3. Geri bildirim raporunu ~/ai-dev-team/docs/quality-feedback-faz-[N].md olarak kaydet
```

---

## Faz Bazlı Kalite Kapıları

### Faz 1 Kalite Kapısı: Web Analiz

```
code-reviewer subagent'ını kullan.

~/ai-dev-team/analysis/web-analysis-report.html dosyasını oku ve şu kontrolleri yap:

KONTROL LİSTESİ:
□ Sayfa Yapısı Analizi: Tüm sayfalar ve route'lar listelenmiş mi?
□ UI Bileşen Analizi: Her sayfadaki bileşenler tespit edilmiş mi?
□ API Analizi: Endpoint'ler URL, method, request/response ile listelenmiş mi?
□ Veri Modeli: Entity'ler ve ilişkiler çıkarılmış mı?
□ İş Mantığı: Kullanıcı akışları ve iş kuralları belirlenmiş mi?
□ Teknoloji Stack: Frontend/backend/3rd party tespiti yapılmış mı?
□ Format: HTML rapor düzgün render ediliyor mu?

Her kontrol için TAMAM / EKSİK / YETERSİZ belirt.
100 üzerinden skor ver.

Skor 70 altındaysa geri bildirim raporunu ~/ai-dev-team/docs/quality-feedback-faz-1.md olarak kaydet.
```

---

### Faz 2 Kalite Kapısı: Mimari Tasarım

```
code-reviewer subagent'ını kullan.

~/ai-dev-team/docs/architecture-decisions.md dosyasını oku.
Referans: ~/ai-dev-team/analysis/web-analysis-report.html

KONTROL LİSTESİ:
□ Backend Teknoloji: Framework, DB, ORM, auth, hosting seçilmiş mi?
□ API Tasarımı: REST/GraphQL kararı gerekçelendirilmiş mi? Endpoint yapısı tanımlı mı?
□ Veritabanı Şeması: Tablolar, ilişkiler, index stratejisi var mı?
□ iOS Mimari: Pattern, networking, state management seçilmiş mi?
□ Proje Yapısı: Backend + iOS dizin yapıları tanımlı mı?
□ Gerekçeler: Her karar neden seçildi, alternatifleri ne?
□ Web analize uyum: Kararlar web analizdeki karmaşıklığa uygun mu? (overengineering yok mu?)

100 üzerinden skor ver.

Skor 70 altındaysa geri bildirim raporunu ~/ai-dev-team/docs/quality-feedback-faz-2.md olarak kaydet.
```

---

### Faz 3 Kalite Kapısı: BA Dokümanı

```
code-reviewer subagent'ını kullan.

~/ai-dev-team/docs/ba-document.md dosyasını oku.
Referans: ~/ai-dev-team/analysis/web-analysis-report.html + ~/ai-dev-team/docs/architecture-decisions.md

KONTROL LİSTESİ:
□ Numaralandırma: FR, BR, AC, VAL numaraları sürekli mi? (bölüm başında sıfırlanmamış mı?)
□ Modül Yapısı: Her modül için açıklama, iş akışı, FR, BR, AC, VAL var mı?
□ İş Akışı Diyagramları: Mermaid formatında doğru çizilmiş mi?
□ Test Edilebilirlik: Her gereksinim somut ve test edilebilir mi? (belirsiz ifadeler: "uygun sürede", "gerektiğinde" yok mu?)
□ Kapsam: Web analizdeki tüm sayfalar/akışlar BA'da karşılanmış mı?
□ Format: GIVEN-WHEN-THEN kullanılmamış mı?

100 üzerinden skor ver.

Skor 70 altındaysa geri bildirim raporunu ~/ai-dev-team/docs/quality-feedback-faz-3.md olarak kaydet.
```

---

### Faz 4 Kalite Kapısı: UI/UX Tasarım

```
code-reviewer subagent'ını kullan.

~/ai-dev-team/design/components/ dizinindeki tüm component spec'leri oku.
~/ai-dev-team/design/tokens.json dosyasını kontrol et.
Referans: ~/ai-dev-team/docs/ba-document.md

KONTROL LİSTESİ:
□ Kapsam: BA dokümanındaki tüm ekranlar için component spec var mı?
□ Varyantlar: Her bileşen için varyantlar tanımlı mı?
□ Design Tokens: tokens.json dosyası var mı ve tutarlı mı?
□ States: Default, hover, active, disabled, focus tanımlı mı?
□ Erişilebilirlik: ARIA rolleri, klavye navigasyon, kontrast oranları belirtilmiş mi?
□ Dark Mode: Dark mode varyantları düşünülmüş mü?
□ Implementation Note: React ve SwiftUI karşılıkları verilmiş mi?

100 üzerinden skor ver.

Skor 70 altındaysa geri bildirim raporunu ~/ai-dev-team/docs/quality-feedback-faz-4.md olarak kaydet.
```

---

### Faz 5 Kalite Kapısı: iOS Dönüşüm

```
code-reviewer subagent'ını kullan.

~/ai-dev-team/docs/ios-design-spec.md dosyasını oku.
Referans: ~/ai-dev-team/design/components/ + ~/ai-dev-team/docs/ba-document.md

KONTROL LİSTESİ:
□ Component Hierarchy: Tüm web bileşenleri iOS karşılığıyla eşleştirilmiş mi?
□ Ekran Listesi: Her ekran için SwiftUI view adı verilmiş mi?
□ Navigasyon Haritası: Mermaid diagram var mı? TabBar/NavigationStack yapısı doğru mu?
□ HIG Uyumu: iOS Human Interface Guidelines'a uygun mu?
□ iOS-Specific: Pull-to-refresh, swipe actions, haptic feedback düşünülmüş mü?
□ Tasarım Token'ları: Web → iOS renk/font dönüşümleri yapılmış mı?
□ SwiftUI Kod Taslakları: Her component için kod taslağı var mı?

100 üzerinden skor ver.

Skor 70 altındaysa geri bildirim raporunu ~/ai-dev-team/docs/quality-feedback-faz-5.md olarak kaydet.
```

---

### Faz 6 Kalite Kapısı: Geliştirme

```
code-reviewer subagent'ını kullan.

Şu dizinleri incele:
- ~/ai-dev-team/backend/ (backend kodu)
- ~/ai-dev-team/ios/ (iOS kodu)

Referanslar:
- ~/ai-dev-team/docs/architecture-decisions.md
- ~/ai-dev-team/docs/ba-document.md

KONTROL LİSTESİ:
□ Mimari Uyum: Kod, architecture-decisions.md'deki kararlara uygun mu?
□ FR Karşılama: BA dokümanındaki tüm FR'ler implement edilmiş mi?
□ API Uyumu: Backend endpoint'leri ile iOS API client eşleşiyor mu?
□ Error Handling: Hata yönetimi tutarlı mı? (backend + iOS)
□ Security: Auth, input validation, data sanitization uygun mu?
□ Kod Kalitesi: Okunabilirlik, naming convention, SOLID prensipleri
□ Build: Backend çalışıyor mu? iOS projesi build alıyor mu?

100 üzerinden skor ver.

Skor 70 altındaysa geri bildirim raporunu ~/ai-dev-team/docs/quality-feedback-faz-6.md olarak kaydet.
```

---

### Faz 7 Kalite Kapısı: Test

```
code-reviewer subagent'ını kullan.

~/ai-dev-team/tests/ dizinini oku.
Referans: ~/ai-dev-team/docs/ba-document.md (AC listesi)

KONTROL LİSTESİ:
□ AC Coverage: BA dokümanındaki her AC için en az 1 test var mı?
□ Test Kalitesi: Testler anlamlı assertion'lar içeriyor mu? (sadece "test exists" değil)
□ Backend Testler: API endpoint testleri (happy path + error case) var mı?
□ iOS Testler: ViewModel unit testleri var mı?
□ Edge Cases: Sınır durumları test edilmiş mi?
□ Coverage: ≥ %80 test coverage hedefine ulaşılmış mı?
□ Çalışıyor mu: Testler hatasız çalışıyor mu?

100 üzerinden skor ver.

Skor 70 altındaysa geri bildirim raporunu ~/ai-dev-team/docs/quality-feedback-faz-7.md olarak kaydet.
```

---

### Faz 8 Kalite Kapısı: Deployment ve Dokümantasyon

```
code-reviewer subagent'ını kullan.

Şu dizinleri/dosyaları incele:
- ~/ai-dev-team/infra/ (CI/CD, Docker, Terraform)
- ~/ai-dev-team/README.md
- ~/ai-dev-team/docs/api-docs/
- ~/ai-dev-team/docs/CONTRIBUTING.md
- ~/ai-dev-team/docs/ARCHITECTURE.md

KONTROL LİSTESİ:
□ CI/CD: GitHub Actions workflow dosyası var mı ve doğru tanımlı mı?
□ Docker: Dockerfile çalışır mı? docker-compose.yml var mı?
□ Environment: .env.example var mı? Staging/production ayrımı yapılmış mı?
□ README: Proje açıklaması, kurulum, çalıştırma adımları eksiksiz mi?
□ API Docs: Tüm endpoint'ler belgelenmiş mi? Request/response örnekleri var mı?
□ Architecture Doc: Mermaid diyagramları ile mimari açıklanmış mı?
□ Deployment Checklist: Canlıya çıkış kontrol listesi var mı?

100 üzerinden skor ver.

Skor 70 altındaysa geri bildirim raporunu ~/ai-dev-team/docs/quality-feedback-faz-8.md olarak kaydet.
```

---

## Skor Karşılaştırma Tablosu

Pipeline tamamlandığında tüm fazların skorlarını şu tablo ile karşılaştırın:

| Faz | Ad | Skor | Durum |
|-----|-----|------|-------|
| 1 | Web Analiz | — | — |
| 2 | Mimari Tasarım | — | — |
| 3 | BA Doküman | — | — |
| 4 | UI/UX Tasarım | — | — |
| 5 | iOS Dönüşüm | — | — |
| 6 | Geliştirme | — | — |
| 7 | Test & QA | — | — |
| 8 | Deploy & Docs | — | — |
| **Ortalama** | — | **—** | — |

> **Pipeline başarı kriteri:** Ortalama skor ≥ 75 ve hiçbir faz 50 altında olmamalı.
