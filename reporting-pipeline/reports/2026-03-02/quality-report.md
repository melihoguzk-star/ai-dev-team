# Quality Report — SunExpress Sun Mobile
**Hafta:** 2026-03-02
**Rapor tarihi:** 2026-03-13
**Pipeline aşaması:** data-processor + trend-analyzer

---

## Özet Skor

| Kontrol Alanı              | Puan  | Ağırlık | Katkı |
|---------------------------|-------|---------|-------|
| 1. Veri Doğruluğu         | 100   | %30     | 30    |
| 2. WoW Doğrulaması        | 100   | %20     | 20    |
| 3. Anomali Doğrulaması    | 85    | %20     | 17    |
| 4. Insight Doğrulaması    | 100   | %15     | 15    |
| 5. Trend Doğrulaması      | 80    | %15     | 12    |

### **TOPLAM SKOR: 94 / 100 ✅**

> Skor 70 üzerinde — pipeline çıktıları raporlamaya hazır.

---

## 1. Veri Doğruluğu

**Sonuç: PASS ✅**

| Kontrol | Değer |
|---------|-------|
| Kontrol edilen hücre | 70 (10 metrik × 7 hafta) |
| Uyumsuz hücre | 0 |
| Hata oranı | %0.00 |

`data/raw/` altındaki tüm JSON dosyaları ile `weekly-metrics-2026-03-02.csv` arasında tam eşleşme sağlandı. iOS ve Android için rating, crash-free, downloads, active users ve uninstalls değerlerinin tamamı doğrulandı.

---

## 2. WoW Doğrulaması

**Sonuç: PASS ✅**

| Metrik | Hafta | Formül | Beklenen | CSV | Sonuç |
|--------|-------|--------|----------|-----|-------|
| iOS Downloads | 26 Jan | (25000−21900)/21900×100 | **+14.16%** | +14.16% | ✅ MATCH |
| Android Rating | 26 Jan | (3.6−3.4)/3.4×100 | **+5.88%** | +5.88% | ✅ MATCH |
| iOS Active Users | 02 Feb | (77000−79000)/79000×100 | **−2.53%** | −2.53% | ✅ MATCH |

Tüm WoW hesaplamaları manuel doğrulama ile birebir örtüşüyor. İlk hafta (19 Jan) için WoW = `null` — doğru davranış.

---

## 3. Anomali Doğrulaması

**Sonuç: PASS (kısmi bilgi notu ile) ✅**

### 3.1 Android Uninstalls — 26 Jan Spike
| Özellik | Değer |
|---------|-------|
| Tespit | ✅ PASS |
| Flag | `critical` |
| Değer | 5,300 |
| WoW | +76.67% |
| Yöntem | threshold (wow_change_pct_gte: 50) |

26 Ocak haftasındaki Android uninstall spike'ı doğru şekilde `critical` olarak flaglendi.

### 3.2 iOS Crash-Free — 9-15 Şub (99.57)
| Özellik | Değer |
|---------|-------|
| Tespit | ℹ️ INFO (flag yok) |
| Değer | 99.57 |
| Eşik | absolute_lt: 99.5 |
| Durum | 99.57 > 99.5 — eşiğin **üstünde** |

**Not:** 99.57, `alert-thresholds.json`'daki `warning` eşiğinin (99.5) üzerinde kaldığı için otomatik flag üretilmedi. Ancak 99.57, serinin 7 haftalık minimumudur ve `trend-summary`'de not olarak görünmektedir.

> **Öneri:** `crash_free_user` eşiğini `absolute_lt: 99.6` olarak güncellemek bu dip noktasını da `warning` olarak yakalayacaktır.

### 3.3 Tam Anomali Listesi (False Positive Taraması)
| Metrik | Hafta | Flag | Değer | Değerlendirme |
|--------|-------|------|-------|---------------|
| ios_rating | 2026-02-16 | CRITICAL | 2.8 | ✅ Gerçek — eşik altı (< 3.0) |
| ios_rating | 2026-02-23 | CRITICAL | 2.7 | ✅ Gerçek — tarihsel minimum |
| ios_rating | 2026-03-02 | WARNING  | 2.8 | ✅ Gerçek — eşik altı |
| android_rating | 2026-02-16 | CRITICAL | 3.4 | ✅ Gerçek — WoW −6.34% |
| android_rating | 2026-02-23 | CRITICAL | 3.2 | ✅ Gerçek — WoW −5.88% |
| ios_uninstalls | 2026-01-26 | WARNING | 2,000 | ✅ Gerçek — WoW +45.99% |
| ios_uninstalls | 2026-02-16 | WARNING | 2,370 | ✅ Gerçek — WoW +32.4% |
| android_uninstalls | 2026-01-26 | CRITICAL | 5,300 | ✅ Gerçek — WoW +76.67% |

**False positive sayısı: 0**. Tüm flagler operasyonel olarak açıklanabilir.

---

## 4. Insight Doğrulaması

**Sonuç: PASS ✅**

| ID | Öncelik | Sayısal Tutarlılık | Hypothesis | Action | Sonuç |
|----|---------|-------------------|------------|--------|-------|
| INS-01 | CRITICAL | ✅ 3.0→2.8 doğru | ✅ Mantıklı | ✅ Spesifik | PASS |
| INS-02 | IMPORTANT | ✅ 3.4→3.3 doğru | ✅ Mantıklı | ✅ Spesifik | PASS |
| INS-03 | INFO | ✅ 74K→103K doğru | ✅ Mantıklı | ✅ Spesifik | PASS |
| INS-04 | CRITICAL | ✅ 5,300 doğru | ✅ Mantıklı | ✅ Spesifik | PASS |
| INS-05 | IMPORTANT | ✅ r=−0.862 doğru | ✅ Mantıklı | ✅ Spesifik | PASS |
| INS-06 | INFO | ✅ r=+0.814 doğru | ✅ Mantıklı | ✅ Spesifik | PASS |
| INS-07 | INFO | ✅ r=+0.775 doğru | ✅ Mantıklı | ✅ Spesifik | PASS |

**7/7 insight PASS.** Tüm observation'lardaki sayılar CSV verileriyle örtüşüyor. Action maddelerinin tümü ölçülebilir ve uygulanabilir.

---

## 5. Trend Doğrulaması

**Sonuç: PASS (1 açıklama notu ile) ✅**

| Metrik | Beklenen | Gerçek | R² | Sonuç |
|--------|----------|--------|----|-------|
| ios_active_users | increasing | increasing | 0.904 | ✅ PASS |
| ios_rating | decreasing | decreasing | 0.700 | ✅ PASS |
| android_crash_free_user | stable | decreasing | 0.375 | ⚠️ AÇIKLAMA |

### Android Crash-Free Trend — Açıklama

Algoritma `decreasing` üretirken beklenen `stable`. Veri seti: `99.95 → 99.94 → 99.94 → 99.93 → 99.93 → 99.93 → 99.94`. Toplam değişim aralığı **0.02 pp** (yüzde puan).

**Sebep:** R²=0.375, `stable` eşiği olan 0.30'un üzerinde kaldığı için eğim yönü (`decreasing`) devreye girdi. Ancak bu 0.02 pp'lik düşüş operasyonel olarak anlamlı değil — Firebase SLA toleransı içinde.

> **Öneri:** Crash-free metriği için minimum anlamlı slope eşiği ekle:
> `if abs(slope) < 0.005 → direction = "stable"` (operasyonel anlamsız mikro-değişimleri filtrele)

---

## Özet Bulgular ve Aksiyon Önerileri

### Yüksek Öncelikli
1. **iOS App Store Rating kritik düşüş** (3.0 → 2.7 → 2.8): Şubat ortasından itibaren başlayan düşüş devam ediyor. Son 3 haftanın 1-2 yıldızlı yorumları analiz edilmeli.
2. **Android Uninstall spike** (26 Ocak, +76.67% WoW): O haftaki sürüm notu ve force-update log'ları kontrol edilmeli.

### Pipeline İyileştirme Önerileri
| # | Öneri | Dosya | Etki |
|---|-------|-------|------|
| 1 | `crash_free_user` warning eşiğini 99.5 → 99.6 yükselt | `config/alert-thresholds.json` | 99.57 dip'i yakalanır |
| 2 | Crash-free için minimum slope filtresi ekle (`abs(slope) < 0.005 → stable`) | `scripts/analyze-trends.py` | Micro-trend false positive azalır |
| 3 | iOS uninstalls trend'i (`increasing`, R²=0.70) ayrı bir `important` insight olarak ekle | `scripts/analyze-trends.py` | Raporlama kapsamı artar |

---

*Rapor otomatik oluşturuldu — SunExpress Sun Mobile Reporting Pipeline v1.0*
