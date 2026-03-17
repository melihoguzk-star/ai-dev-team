# ProteinOcean Pipeline Durum Takibi

**Proje URL:** https://proteinocean.com
**Platform:** iOS Native (SwiftUI + ikas GraphQL API)
**Son Güncelleme:** 2026-03-05

---

## Faz Durumları

| Faz | Ad | Durum | Skor | Notlar |
|-----|-----|-------|------|--------|
| 1 | Web Analizi | ✅ Tamamlandı | — | `analysis/web-analysis.md` (MD formatı, HTML bekleniyor) |
| 1.5 | Marka Kimliği Analizi | ✅ Tamamlandı | — | `docs/brand-tokens.json` + `docs/brand-analysis-report.html` + `docs/brand-style-guide.html` yeniden oluşturuldu |
| 2 | Mimari Tasarım | ✅ Retrospektif | — | `docs/tech-decisions.json` + `docs/architecture-decisions.md` oluşturuldu |
| 3 | BA Dokümanı | ✅ Retrospektif | — | `docs/ba-document.md` oluşturuldu |
| 4 | UI/UX Tasarım | 🔄 Kısmen | — | `design/tokens.json` oluşturuldu (geçici). `design/components/` boş. |
| 5 | iOS Tasarım Dönüşümü | ✅ Retrospektif | — | `docs/ios-design-spec.md` oluşturuldu |
| 6 | iOS Geliştirme | 🔄 Kısmen | — | Temel ekranlar çalışıyor. Eksikler: pull-to-refresh, accessibility labels |
| 7 | Test & QA | 🔄 Başlangıç | — | Test dosyaları oluşturuldu. Test target Package.swift'e eklenmeli. |
| 8 | Deploy & Docs | ⏳ Bekliyor | — | `infra/` yok, CI/CD yok, App Store hazırlığı yok |

---

## Tamamlanan Dosyalar

### Retrospektif Oluşturulanlar (2026-03-05)
- `docs/tech-decisions.json` — Mimari kararlar (JSON)
- `docs/architecture-decisions.md` — Mimari kararlar (Markdown)
- `docs/ba-document.md` — İş analizi dokümanı
- `docs/ios-design-spec.md` — iOS tasarım spesifikasyonu
- `design/tokens.json` — Tasarım token'ları (geçici, brand-tokens.json bekliyor)
- `tests/ios/ProductListViewModelTests.swift` — ViewModel unit testleri
- `tests/ios/CategoriesViewModelTests.swift` — Categories unit testleri

### Kod Düzeltmeleri (2026-03-05)
- `CategoriesView.swift:73` — Typo: `"urun"` → `"ürün"`

---

## Kritik Açık Görevler

### Öncelik: Yüksek

1. **Faz 1.5 — brand-analyzer çalıştırılmalı**
   - `brand-tokens.json` oluşturulmalı
   - `brand-style-guide.html` oluşturulmalı
   - `ContentView.swift`, `ProductListView.swift`, `CategoriesView.swift` içindeki hardcoded `.blue` renkler brand token'larla değiştirilmeli

2. **Test target — Package.swift güncellenmeli**
   - Test dosyaları hazır (`tests/ios/`) ama `Package.swift`'de test target yok
   - XcodeGen ile `project.yml`'a test target eklenmeli veya Xcode projesi oluşturulmalı

### Öncelik: Orta

3. **Accessibility (VoiceOver) label'ları eklenmeli**
   - `ProductCard`, `StoreCategoryCard` için `.accessibilityLabel` ve `.accessibilityValue`

4. **Pull-to-refresh**
   - `CategoriesView` ve `ProductListView`'a `.refreshable` modifier eklenmeli

5. **design/components/ dizini doldurulmalı**
   - `ui-designer` agent'ı çalıştırılmalı veya bileşen spec dosyaları manuel yazılmalı

### Öncelik: Düşük

6. **Faz 8 — Deployment & Docs**
   - GitHub Actions CI/CD
   - TestFlight yapılandırması
   - `docs/ARCHITECTURE.md` Mermaid diyagramları ile

---

## iOS Kodu Kalite Notları

| Sorun | Dosya | Satır | Durum |
|-------|-------|-------|-------|
| Hardcoded `.blue` tint | ContentView.swift | 17 | ✅ `.tint(Color.brandPrimary)` |
| Hardcoded `.blue` fiyat | ProductListView.swift | 207 | ✅ `.foregroundStyle(Color.brandSecondary)` |
| Hardcoded `Color.blue.opacity` | CategoriesView.swift | 107 | ✅ `Color.brandPrimary.opacity(0.08)` |
| Hardcoded `.red` indirim badge | ProductListView.swift | 229 | ✅ `Color.brandError` |
| Hardcoded `.orange` stok badge | ProductListView.swift | 240–243 | ✅ `Color.brandWarning` |
| Hardcoded `.orange` hata ikonu | CategoriesView.swift | 122 | ✅ `Color.brandWarning` |
| ASCII Türkçe tab label | ContentView.swift | 11–13 | ✅ "Tüm Ürünler" / "Ürünler" |
| Typo: "urun" → "ürün" | CategoriesView.swift | 73 | ✅ Düzeltildi |
| `brandWarning` token eksik | ProteinOceanApp.swift | — | ✅ `#FF6600` eklendi |
| Test target yok | Package.swift | — | ⏳ Yapılacak |
| Code signing boş | project.yml | 15–17 | ⏳ Dağıtım öncesi |
| `useMockData = true` | IkasAPIConfig.swift | 6 | ⏳ Token alındığında false yap |
