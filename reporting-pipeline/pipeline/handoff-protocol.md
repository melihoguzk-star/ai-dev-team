# Reporting Pipeline — Handoff Protokolü

---

## 1. Standart Dosya Yapısı

Her faz çıktısı aşağıdaki dizin yapısına uygun olmalıdır:

```
~/ai-dev-team/reporting-pipeline/
├── data/
│   ├── raw/                                    # Faz 1 çıktıları
│   │   ├── ios_rating_{tarih}.json
│   │   ├── ios_downloads_{tarih}.json
│   │   ├── ios_active_users_{tarih}.json
│   │   ├── ios_uninstalls_{tarih}.json
│   │   ├── android_rating_{tarih}.json
│   │   ├── android_downloads_{tarih}.json
│   │   ├── android_active_users_{tarih}.json
│   │   ├── android_uninstalls_{tarih}.json
│   │   ├── ios_crashlytics_{tarih}.json
│   │   └── android_crashlytics_{tarih}.json
│   │
│   └── processed/                              # Faz 2 + 3 çıktıları
│       ├── weekly-metrics-{tarih}.csv          # Faz 2
│       ├── platform-comparison-{tarih}.csv     # Faz 2
│       ├── wow-changes-{tarih}.csv             # Faz 2
│       ├── insights-{tarih}.json               # Faz 3
│       ├── anomalies-{tarih}.json              # Faz 3
│       └── trend-summary-{tarih}.json          # Faz 3
│
└── reports/
    └── {tarih}/                                # Faz 4 çıktısı
        └── quality-report.md
```

**Tarih formatı:** `YYYY-MM-DD` (haftanın Pazartesi günü)

---

## 2. Context Aktarım Kuralları

### Faz Bazlı Context Haritası

| Hedef Faz | Okuması Gereken Dosyalar | Neden |
|-----------|--------------------------|-------|
| **Faz 2** | `data/raw/*.json` + `config/metrics-config.json` | Ham veriyi normalize etmek için |
| **Faz 3** | `data/processed/weekly-metrics-*.csv` + `data/processed/wow-changes-*.csv` + `config/alert-thresholds.json` | Trend ve anomali analizi için |
| **Faz 4** | `data/raw/` + `data/processed/` (tümü) | Cross-check ve doğrulama için |

### Veri Boyut Limiti

Bu pipeline'daki veriler genellikle küçüktür (7 hafta × 5 metrik × 2 platform = ~70 satır). Context window sorunu beklenmez. Ancak geçmiş verilerin biriktiği durumlarda:

1. **Raw JSON:** Her dosya tek haftalık veri içerir → küçük
2. **Processed CSV:** Sliding window ile son 7 hafta → küçük
3. **Insight JSON:** Maksimum 7 insight → küçük

---

## 3. Faz Geçiş Protokolü

### Standart Geçiş Adımları

```
1. FAZ TAMAMLAMA
   → Agent çıktıyı belirtilen dosyaya/dizine kaydeder
   → Agent tamamlanma özeti sunar

2. ÇIKTI DOĞRULAMA
   → Beklenen dosyalar mevcut mu?
   → Dosya boyutları > 0 mu?
   → JSON geçerli mi? CSV parseable mi?

3. KALİTE KAPISI
   → quality-gates.md'deki ilgili faz prompt'unu çalıştır
   → Skor değerlendir

4. SKOR DEĞERLENDİRME
   → Skor ≥ 70: Sonraki faza geç
   → Skor 50-69: Düzeltme döngüsüne gir
   → Skor < 50: Fazı tekrar çalıştır

5. SONRAKI FAZA GEÇİŞ
   → Çıktının doğru dizinde olduğunu kontrol et
   → Sonraki fazı başlat
```

### Geçiş Kontrol Listesi

```
□ Çıktı dosyaları mevcut ve boş değil
□ JSON dosyaları geçerli (json.loads başarılı)
□ CSV dosyaları parseable (pandas.read_csv başarılı)
□ Tarih formatları tutarlı
□ Kalite kapısı skoru ≥ 70
□ Önceki fazın çıktısı bozulmamış
```

---

## 4. Hata Durumları ve Retry Mekanizması

### Hata Tipleri

| Hata Tipi | Açıklama | Eylem |
|-----------|----------|-------|
| **API_TIMEOUT** | App Store / Play Store API yanıt vermedi | Exponential backoff ile 3 retry |
| **API_AUTH_FAIL** | Credential'lar geçersiz veya expired | Credential yenileme iste, pipeline durdur |
| **API_RATE_LIMIT** | Rate limit aşıldı (429) | 60 saniye bekle, retry |
| **PARTIAL_DATA** | Bazı metrikler eksik ama diğerleri tamam | Eksik metrikleri "N/A" olarak işaretle, devam et |
| **DATA_FORMAT_ERROR** | API response formatı beklenenden farklı | Schema mapping'i güncelle, retry |
| **EMPTY_RESPONSE** | API boş yanıt döndü | Tarih aralığını kontrol et, alternatif endpoint dene |
| **PROCESSING_ERROR** | Veri işleme sırasında hata | Hata detayını logla, faz 2'yi tekrar çalıştır |
| **QUALITY_FAIL** | Kalite kapısı skoru düşük | Düzeltme döngüsüne gir |

### API-Spesifik Retry Kuralları

```
APP_STORE_CONNECT:
  max_retry: 3
  backoff: exponential (1s, 2s, 4s)
  rate_limit: 200 requests/hour
  auth_refresh: JWT token her 20 dakikada yenile

GOOGLE_PLAY_CONSOLE:
  max_retry: 3
  backoff: exponential (2s, 4s, 8s)
  rate_limit: 200 queries/day
  data_delay: 48 saat (en güncel veri 2 gün öncesine ait)

FIREBASE_CRASHLYTICS:
  max_retry: 3
  backoff: exponential (1s, 2s, 4s)
  rate_limit: 100 requests/minute
  data_delay: ~3 saat
```

### Kısmi Veri Stratejisi

Tüm veriler toplanamasa bile pipeline devam edebilir:

```
EKSİK VERİ POLİTİKASI:
  - 1-2 metrik eksik: Pipeline devam eder, eksikler "N/A" olarak raporlanır
  - 3+ metrik eksik: Pipeline durur, insan müdahalesi iste
  - 1 platform tamamen eksik: Pipeline devam eder, tek platform raporu üretilir
  - Her iki platform eksik: Pipeline durur
```

---

## 5. Paralel Çalışma Kuralları

### Faz 1: Paralel Veri Toplama

| Alt Faz | Agent | Çıktı Dizini | Bağımsız? |
|---------|-------|-------------|-----------|
| 1a (iOS) | `data-collector` | `data/raw/ios_*` | ✅ |
| 1b (Android) | `data-collector` | `data/raw/android_*` (Play) | ✅ |
| 1c (Crashlytics) | `data-collector` | `data/raw/*_crashlytics_*` | ✅ |

- Üç alt faz tamamen paralel çalışabilir
- Farklı API'lere gittikleri için rate limit çakışması yok
- Farklı dosyalara yazdıkları için write conflict yok
- Faz 2, **tüm alt fazlar tamamlanınca** başlar

### Paralel Çalıştırma Komutu

```bash
# tmux ile paralel
./scripts/parallel-run.sh \
  "data-collector subagent. iOS verilerini topla." \
  "data-collector subagent. Android verilerini topla."

# Crashlytics ayrı bir terminal'de
claude --print "data-collector subagent. Crashlytics verilerini topla."
```

---

## 6. Pipeline Durum Takibi

**Dosya:** `~/ai-dev-team/reporting-pipeline/pipeline/pipeline-status.md`

```markdown
# Reporting Pipeline — Durum Takibi

| Faz | Durum | Skor | Deneme | Başlangıç | Bitiş | Notlar |
|-----|-------|------|--------|-----------|-------|--------|
| 1a (iOS) | ⏳ Bekliyor | — | — | — | — | — |
| 1b (Android) | ⏳ Bekliyor | — | — | — | — | — |
| 1c (Crashlytics) | ⏳ Bekliyor | — | — | — | — | — |
| 2 | ⏳ Bekliyor | — | — | — | — | — |
| 3 | ⏳ Bekliyor | — | — | — | — | — |
| 4 | ⏳ Bekliyor | — | — | — | — | — |
```
