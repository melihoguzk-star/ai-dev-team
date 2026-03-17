# Faz Prompt'ları — Claude Code'a Verilecek Komutlar

Her faz için Claude Code'a yapıştırılacak hazır prompt'lar. `[BÜYÜK_HARF]` ile belirtilen kısımları projenize göre değiştirin.

---

## Faz 1: Web Analizi

```
web-analyzer subagent'ını kullan.

[URL] adresini analiz et. Tüm 6 analiz katmanını (sayfa yapısı, UI bileşenleri, API endpointleri, veri modeli, iş mantığı, teknoloji stack) eksiksiz tamamla.

Çıktıyı ~/ai-dev-team/analysis/web-analysis-report.html olarak kaydet.

Analiz tamamlandığında şu istatistikleri raporla:
- Toplam sayfa sayısı
- Tespit edilen API endpoint sayısı
- Veri modeli sayısı
- Kullanıcı akışı sayısı
- Tespit edilen risk sayısı
```

---

## Faz 1.5: Marka Kimliği Analizi

```
brand-analyzer subagent'ını kullan.

Şu dosyayı oku:
1. ~/ai-dev-team/analysis/web-analysis-report.html (web analiz raporu)

Ayrıca [URL] adresine WebFetch ile eriş ve CSS dosyalarını analiz et.

Web sitesinin marka kimliğini derinlemesine analiz et:
- Renk paleti (primary, secondary, accent, background, text, status)
- Tipografi (font ailesi, ağırlıklar, boyut skalası)
- Spacing ve grid sistemi
- Border radius ve shadow değerleri
- İkon seti ve stili
- Buton ve form stilleri
- Genel marka tonu

Çıktıları şu dosyalara kaydet:
- ~/ai-dev-team/docs/brand-tokens.json (makine okunur token seti)
- ~/ai-dev-team/docs/brand-style-guide.html (görsel stil rehberi)

Analiz tamamlandığında şu özeti sun:
- Tespit edilen ana renk ve marka tonu
- Seçilen tipografi ailesi ve iOS karşılığı
- Tespit edilen ikon kütüphanesi
- Güven skoru (CSS'den mi çıkarıldı, tahmini mi?)
```

---

## Faz 2: Mimari Tasarım

```
system-architect subagent'ını kullan.

~/ai-dev-team/analysis/web-analysis-report.html dosyasını oku. Bu web analizine dayanarak backend ve iOS uygulama için mimari kararları ver.

Şu 5 karar alanını tamamla:
1. Backend teknoloji seçimi (framework, DB, ORM, auth, hosting)
2. API tasarımı (REST vs GraphQL, endpoint yapısı, error standardı)
3. Veritabanı şeması (tablolar, ilişkiler, index stratejisi)
4. iOS mimari kararları (pattern, networking, state, persistence, navigation)
5. Proje yapısı (backend + iOS dizin yapıları)

Her karar için seçim, gerekçe, riskler ve alternatifleri belirt.

Çıktıyı ~/ai-dev-team/docs/architecture-decisions.md olarak kaydet.
```

---

## Faz 3: BA Doküman Üretimi

```
ba-doc-generator subagent'ını kullan.

Şu iki dosyayı oku:
1. ~/ai-dev-team/analysis/web-analysis-report.html (web analiz raporu)
2. ~/ai-dev-team/docs/architecture-decisions.md (mimari kararlar)

Bu iki kaynağı sentezleyerek kapsamlı bir İş Analizi dokümanı üret.

Kurallar:
- FR, BR, AC, VAL numaralandırması tüm dokümanda sürekli olmalı (bölüm başında sıfırlama YOK)
- Her modül için: Açıklama, İş Akışı Diyagramı (mermaid), Fonksiyonel Gereksinimler, İş Kuralları, Kabul Kriterleri, Validasyonlar
- GIVEN-WHEN-THEN formatı KULLANMA
- Her gereksinim test edilebilir ve somut olmalı

Çıktıyı ~/ai-dev-team/docs/ba-document.md olarak kaydet.
```

---

## Faz 4: UI/UX Tasarım

```
ui-designer subagent'ını kullan.

Şu dosyaları oku:
1. ~/ai-dev-team/analysis/web-analysis-report.html (web analiz — mevcut UI bileşenleri)
2. ~/ai-dev-team/docs/ba-document.md (BA dokümanı — tüm ekranlar ve gereksinimler)
3. ~/ai-dev-team/docs/architecture-decisions.md (mimari kararlar — tech stack bilgisi)

Her ekran ve bileşen için component spec üret:
- Varyantlar, design tokens, states (default/hover/active/disabled/focus)
- Erişilebilirlik (ARIA, klavye, kontrast)
- Dark mode desteği
- Responsive davranış

Çıktıları şu dizine kaydet:
- Component spec'ler: ~/ai-dev-team/design/components/ (her bileşen için ayrı .md dosyası)
- Design tokens: ~/ai-dev-team/design/tokens.json
- Değişiklik logu: ~/ai-dev-team/design/CHANGELOG.md
```

---

## Faz 5: iOS Tasarım Dönüşümü

```
uiux-translator subagent'ını kullan.

Şu dosyaları oku:
1. ~/ai-dev-team/design/components/ dizinindeki tüm component spec'ler
2. ~/ai-dev-team/docs/ba-document.md (BA dokümanı — ekran listesi ve akışlar)
3. ~/ai-dev-team/docs/architecture-decisions.md (iOS mimari kararları)
4. ~/ai-dev-team/docs/brand-tokens.json (marka token'ları — renkler, tipografi, spacing, border, shadow)

Web tasarımını iOS Human Interface Guidelines'a uyumlu native tasarıma dönüştür:
1. Component Hierarchy — ağaç yapısı (her web bileşeni → SwiftUI karşılığı)
2. Ekran Listesi — her ekran için SwiftUI view adı
3. Navigasyon Haritası — mermaid diagram
4. Tasarım Token'ları — Web renklerinden iOS semantic color'lara dönüşüm, SF Pro font mapping
5. Component Detayları — her component için SwiftUI kod taslağı

Çıktıyı ~/ai-dev-team/docs/ios-design-spec.md olarak kaydet.
```

---

## Faz 6: Geliştirme (Backend + iOS)

### Faz 6a: Backend Geliştirme

```
backend-developer subagent'ını kullan.

Şu dosyaları oku:
1. ~/ai-dev-team/docs/architecture-decisions.md (tech stack, API tasarımı, DB şeması)
2. ~/ai-dev-team/docs/ba-document.md (fonksiyonel gereksinimler ve iş kuralları)

Mimari kararlara uygun backend uygulamasını geliştir:
- API endpoint'leri (architecture-decisions.md'deki tasarıma uygun)
- Veritabanı modelleri ve migration'lar
- Authentication ve authorization
- Error handling ve validation
- Bütün FR'leri karşılayan business logic

Kodu ~/ai-dev-team/backend/ dizinine kaydet.
README.md ile kurulum talimatlarını ekle.
```

### Faz 6b: iOS Core Modüller

```
swift-expert subagent'ını kullan.

Şu dosyaları oku:
1. ~/ai-dev-team/docs/architecture-decisions.md (iOS mimari kararları)
2. ~/ai-dev-team/docs/ios-design-spec.md (component hierarchy ve SwiftUI taslakları)
3. ~/ai-dev-team/docs/ba-document.md (iş kuralları ve validasyonlar)

iOS uygulamasının core modüllerini geliştir:
- Networking layer (URLSession + async/await, API client)
- Data models (Codable struct'lar, backend API'ye uyumlu)
- Business logic layer (iş kuralları implementasyonu)
- Persistence layer (SwiftData/CoreData modelleri)
- Utility ve extension'lar

Kodu ~/ai-dev-team/ios/ dizinine kaydet.
```

### Faz 6c: iOS UI Katmanı

> **Platform notu:** `~/ai-dev-team/docs/tech-decisions.json` dosyasını oku.
> - `"platform": "ios-native"` → **swift-expert** subagent'ını kullan
> - `"platform": "flutter"` veya `"platform": "react-native"` → **mobile-developer** subagent'ını kullan

```
[PLATFORMA GÖRE: swift-expert VEYA mobile-developer] subagent'ını kullan.

Şu dosyaları oku:
1. ~/ai-dev-team/docs/ios-design-spec.md (ekran listesi, navigasyon, component detayları)
2. ~/ai-dev-team/docs/brand-tokens.json (marka token'ları — renk, tipografi, spacing)
3. ~/ai-dev-team/design/tokens.json (design tokens)
4. ~/ai-dev-team/ios/ dizinindeki mevcut core modüller (swift-expert çıktısı)

iOS uygulamasının UI katmanını geliştir:
- SwiftUI view'ları (ios-design-spec'teki ekran listesine uygun)
- NavigationStack yapısı
- Reusable component'ler
- Dark mode desteği
- Dynamic Type desteği
- Erişilebilirlik (VoiceOver, aksesibilite label'ları)

Kodu ~/ai-dev-team/ios/ dizinindeki mevcut yapıya entegre et.
```

---

## Faz 7: Test ve Kalite Kontrol

### Faz 7a: Otomatik Test Yazımı

```
test-automator subagent'ını kullan.

Şu dosyaları oku:
1. ~/ai-dev-team/docs/ba-document.md (kabul kriterleri — AC-XX'ler)
2. ~/ai-dev-team/backend/ dizinindeki backend kodu
3. ~/ai-dev-team/ios/ dizinindeki iOS kodu

BA dokümanındaki her AC (kabul kriteri) için test yaz:
- Backend: API endpoint testleri (unit + integration)
- iOS: ViewModel unit testleri + UI testleri
- Her test, hangi AC'yi karşıladığını comment ile belirtsin

Test coverage hedefi: ≥ %80

Testleri ~/ai-dev-team/tests/ dizinine kaydet:
- ~/ai-dev-team/tests/backend/
- ~/ai-dev-team/tests/ios/
```

### Faz 7b: Kod İnceleme

```
code-reviewer subagent'ını kullan.

Şu dizinleri incele:
1. ~/ai-dev-team/backend/ (backend kodu)
2. ~/ai-dev-team/ios/ (iOS kodu)
3. ~/ai-dev-team/tests/ (test kodu)

Referans dokümanlar:
- ~/ai-dev-team/docs/architecture-decisions.md (mimari uyum kontrolü)
- ~/ai-dev-team/docs/ba-document.md (fonksiyonel uyum kontrolü)

Şu kriterleri değerlendir:
- Kod kalitesi ve okunabilirlik
- Mimari kararlara uyum
- Error handling
- Security best practices
- Performance
- BA dokümanındaki tüm FR'lerin implement edilip edilmediği

100 üzerinden skor ver. Skor 70 altıysa kritik sorunları listele.

Çıktıyı ~/ai-dev-team/docs/code-review-report.html olarak kaydet.
```

---

## Faz 8: Deployment ve Dokümantasyon

### Faz 8a: DevOps ve Deployment

```
devops-engineer subagent'ını kullan.

Şu dosyaları oku:
1. ~/ai-dev-team/docs/architecture-decisions.md (hosting ve tech stack kararları)
2. ~/ai-dev-team/backend/ dizinindeki backend kodu

Deployment altyapısını oluştur:
- Dockerfile ve docker-compose.yml
- CI/CD pipeline (GitHub Actions)
- Environment konfigürasyonu (.env.example, staging/production)
- Monitoring ve logging setup
- Terraform/IaC dosyaları (gerekirse)
- Deployment checklist

Çıktıları ~/ai-dev-team/infra/ dizinine kaydet.
```

### Faz 8b: Dokümantasyon

```
documentation-engineer subagent'ını kullan.

Şu dizinleri ve dosyaları oku:
1. ~/ai-dev-team/docs/ (tüm dokümanlar)
2. ~/ai-dev-team/backend/ (backend kodu)
3. ~/ai-dev-team/ios/ (iOS kodu)
4. ~/ai-dev-team/infra/ (deployment konfigürasyonu)

Şunları üret:
1. ~/ai-dev-team/README.md — Proje genel bakış, kurulum, çalıştırma talimatları
2. ~/ai-dev-team/docs/api-docs/ — API dokümantasyonu (endpoint'ler, request/response örnekleri)
3. ~/ai-dev-team/docs/CONTRIBUTING.md — Katkı kılavuzu
4. ~/ai-dev-team/docs/ARCHITECTURE.md — Mimari genel bakış (mermaid diyagramları ile)

Tüm dokümantasyon Türkçe olmalı. Teknik terimler İngilizce kalabilir.
```

---

## Kullanım Notu

Her prompt'taki `[URL]` kısmını hedef web sitesi adresi ile değiştirin. Prompt'ları sırasıyla Claude Code'a verin. Her faz tamamlandığında çıktıyı kontrol edin, sonraki faza geçin.

> **İpucu:** Faz 6a, 6b ve 6c paralel çalıştırılabilir. Faz 7a ve 7b de paralel çalıştırılabilir.
