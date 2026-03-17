# SunExpress Haftalık Rapor — Görsel QA Sonucu

**Rapor Haftası:** 2026-03-02
**QA Tarihi:** 2026-03-13 14:15:24
**PPTX Dosyası:** `reports/2026-03-02/sunexpress-weekly-report-2026-03-02.pptx`

## 1. Üretim Durumu

| Kontrol | Sonuç |
|---------|-------|
| PPTX oluşturuldu | ✅ PASS |
| PPTX boyutu | 224.3 KB |
| Slide sayısı | 9 |

## 2. PDF Dönüşüm Durumu

| Kontrol | Sonuç |
|---------|-------|
| PDF oluşturuldu | ⚠️ HAYIR |
| Sebep | LibreOffice yok; pptx2pdf ve aspose-slides Python 3.14 ile uyumsuz |
| Etki | PDF çıktısı mevcut değil — PPTX manuel dönüşüm gerektirebilir |

## 3. JPG Thumbnail Durumu

| Kontrol | Sonuç |
|---------|-------|
| Thumbnail üretildi | ✅ PASS |
| Dosya sayısı | 9/9 |
| slide-01.jpg | 33.3 KB |
| slide-02.jpg | 57.8 KB |
| slide-03.jpg | 58.3 KB |
| slide-04.jpg | 86.7 KB |
| slide-05.jpg | 96.9 KB |
| slide-06.jpg | 93.1 KB |
| slide-07.jpg | 95.0 KB |
| slide-08.jpg | 97.6 KB |
| slide-09.jpg | 63.4 KB |

## 4. Slide Bazlı QA Sonuçları

### Slide 1 — Kapak

| Kontrol | Sonuç |
|---------|-------|
| 'SunExpress' metni var | ✅ PASS |
| 'Performance Overview' metni var | ✅ PASS |
| Tarih aralığı metni var | ✅ PASS |
| 'loodos' footer var | ✅ PASS |
| Dekoratif şekil var (teal) | ✅ PASS |
| Arka plan LGRAY (#F0F0F0) | ✅ PASS |
| Başlık rengi NAVY (#1B3A5C) | ✅ PASS |

### Slide 2 — iOS Performance Overview

| Kontrol | Sonuç |
|---------|-------|
| 'iOS' başlıkta var | ✅ PASS |
| 'Performance Overview' var | ✅ PASS |
| 'loodos' footer var | ✅ PASS |
| 'SunExpress Airlines' footer var | ✅ PASS |
| Tablo 8 satır (1 header + 7 veri) | ✅ PASS |
| Tablo 6 sütun | ✅ PASS |
| Tabloda 7 hafta var | ✅ PASS |
| Header rengi NAVY | ✅ PASS |

### Slide 3 — Android Performance Overview

| Kontrol | Sonuç |
|---------|-------|
| 'Android' başlıkta var | ✅ PASS |
| 'Performance Overview' var | ✅ PASS |
| 'loodos' footer var | ✅ PASS |
| 'SunExpress Airlines' footer var | ✅ PASS |
| Tablo 8 satır (1 header + 7 veri) | ✅ PASS |
| Tablo 6 sütun | ✅ PASS |
| Tabloda 7 hafta var | ✅ PASS |
| Header rengi NAVY | ✅ PASS |

### Slide 4 — App Rating

| Kontrol | Sonuç |
|---------|-------|
| 'App Rating' başlıkta var | ✅ PASS |
| Grafik PNG embed var | ✅ PASS |
| 'loodos' footer var | ✅ PASS |
| 'SunExpress Airlines' footer var | ✅ PASS |
| Tablo 8 satır | ✅ PASS |
| Tablo 3 sütun (Date | iOS | Android) | ✅ PASS |

### Slide 5 — Crash Free User

| Kontrol | Sonuç |
|---------|-------|
| 'Crash Free User' başlıkta var | ✅ PASS |
| Grafik PNG embed var | ✅ PASS |
| 'loodos' footer var | ✅ PASS |
| 'SunExpress Airlines' footer var | ✅ PASS |
| Tablo 8 satır | ✅ PASS |
| Tablo 3 sütun (Date | iOS | Android) | ✅ PASS |

### Slide 6 — Download

| Kontrol | Sonuç |
|---------|-------|
| 'Download' başlıkta var | ✅ PASS |
| Grafik PNG embed var | ✅ PASS |
| 'loodos' footer var | ✅ PASS |
| 'SunExpress Airlines' footer var | ✅ PASS |
| Tablo 8 satır | ✅ PASS |
| Tablo 3 sütun (Date | iOS | Android) | ✅ PASS |

### Slide 7 — Active User

| Kontrol | Sonuç |
|---------|-------|
| 'Active User' başlıkta var | ✅ PASS |
| Grafik PNG embed var | ✅ PASS |
| 'loodos' footer var | ✅ PASS |
| 'SunExpress Airlines' footer var | ✅ PASS |
| Tablo 8 satır | ✅ PASS |
| Tablo 3 sütun (Date | iOS | Android) | ✅ PASS |

### Slide 8 — Uninstall

| Kontrol | Sonuç |
|---------|-------|
| 'Uninstall' başlıkta var | ✅ PASS |
| Grafik PNG embed var | ✅ PASS |
| 'loodos' footer var | ✅ PASS |
| 'SunExpress Airlines' footer var | ✅ PASS |
| Tablo 8 satır | ✅ PASS |
| Tablo 3 sütun (Date | iOS | Android) | ✅ PASS |

### Slide 9 — Trend Summary & Key Insights

| Kontrol | Sonuç |
|---------|-------|
| 'loodos' footer var | ✅ PASS |
| 'SunExpress Airlines' footer var | ✅ PASS |
| Trend tablosu (6+ satır × 3+ sütun) | ✅ PASS |
| En az 3 insight metin kutusu | ✅ PASS |
| Insight metin sayısı | 5 |
| Trend tablo satır × sütun | 6 × 3 |

## 5. Veri Doğruluğu (CSV ↔ PPTX)

| Platform | Eşleşen / Toplam | Oran |
|----------|-----------------|------|
| iOS (Slide 2) | 35/35 | 100.0% |
| Android (Slide 3) | 35/35 | 100.0% |
| **Toplam** | **70/70** | **100.0%** |

Tüm değerler eşleşiyor. ✅

## 6. Branding Uyum Kontrolü

**Branding Skoru: 100/100 (100.0%)**

| Kontrol | Ağırlık | Sonuç |
|---------|---------|-------|
| Kapak arka planı LGRAY (#F0F0F0) | 10 | ✅ PASS |
| Tablo header rengi NAVY (#1B3A5C) | 10 | ✅ PASS |
| Platform adı turuncu (#E85D26) | 10 | ✅ PASS |
| Loodos footer teal (#2ABFBF) | 10 | ✅ PASS |
| Kritik hücre rengi (#F8D7DA) | 10 | ✅ PASS |
| Uyarı hücre rengi (#FFF3CD) | 10 | ✅ PASS |
| Tüm slide'larda loodos footer var | 10 | ✅ PASS |
| Tüm slide'larda SunExpress Airlines footer var | 10 | ✅ PASS |
| Slide boyutu 16:9 (13.33" x 7.5") | 10 | ✅ PASS |
| Toplam 9 slide | 10 | ✅ PASS |

## 7. Tespit Edilen Sorunlar

1. PDF dönüşümü yapılamadı — LibreOffice, pptx2pdf ve aspose-slides Python 3.14 ile uyumsuz.

## 8. Genel Skor

| Bileşen | Skor |
|---------|------|
| Slide QA (pass/fail) | 67/67 |
| Veri Doğruluğu | 100.0% |
| Branding Uyumu | 100.0% |
| PPTX Üretimi | ✅ |
| JPG Thumbnail | ✅ 9/9 |
| PDF Dönüşümü | ⚠️ Yapılamadı |
| **Genel Kontrol Oranı** | **70/70 (100.0%)** |
| **Sonuç** | **MÜKEMMEL** |

---
*Bu rapor `qa-report.py` tarafından otomatik oluşturulmuştur — 2026-03-13 14:15:25*
*Loodos Reporting Pipeline v1.0*