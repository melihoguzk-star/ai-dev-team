# Reporting Pipeline Konfigürasyonu

SunExpress Sun Mobile uygulamasının haftalık performans raporlarını otomatize eden 5 fazlı pipeline.

---

## Faz Tanımları

### Faz 1: Veri Toplama (Data Collection)

| Parametre | Değer |
|-----------|-------|
| **Ad** | Çoklu Kaynak Veri Toplama |
| **Agent** | `data-collector` (claude-sonnet-4-6) |
| **Alt Görevler** | 1a: iOS (App Store Connect), 1b: Android (Google Play), 1c: Crashlytics (Firebase) |
| **Girdi** | `config/credentials.json` + `config/metrics-config.json` |
| **Çıktı** | `data/raw/{platform}_{metric}_{tarih}.json` |
| **Kalite Kapısı** | Tüm 5 metrik × 2 platform için veri mevcut; tarih aralığı doğru; JSON schema uyumlu |
| **Tahmini Süre** | 5-10 dakika |
| **Paralellik** | 1a, 1b, 1c **tamamen paralel** çalışabilir |

**Toplanan Metrikler:**

| # | Metrik | iOS API Endpoint | Android API Endpoint |
|---|--------|-----------------|---------------------|
| 1 | App Rating | `GET /v1/apps/{id}/customerReviews` → aggregate | `reviews.list` → aggregate |
| 2 | Crash Free User (%) | Firebase Crashlytics REST API | Firebase Crashlytics REST API |
| 3 | Weekly Downloads | `GET /v1/apps/{id}/analyticsReportRequests` | `stats.getInstalls` |
| 4 | Weekly Active Users | `GET /v1/apps/{id}/analyticsReportRequests` | `stats.getActiveUsers` |
| 5 | Weekly Uninstalls | `GET /v1/apps/{id}/analyticsReportRequests` | `stats.getUninstalls` |

---

### Faz 2: Veri İşleme & Normalizasyon (Data Processing)

| Parametre | Değer |
|-----------|-------|
| **Ad** | Veri Normalizasyon ve Birleştirme |
| **Agent** | `data-processor` (claude-sonnet-4-6) |
| **Girdi** | `data/raw/` dizinindeki tüm JSON dosyaları |
| **Çıktı** | `data/processed/weekly-metrics-{tarih}.csv` + `data/processed/platform-comparison-{tarih}.csv` |
| **Kalite Kapısı** | Eksik veri %5'ten az; outlier'lar flag'lenmiş; tarih sıralaması doğru; birimler tutarlı |
| **Tahmini Süre** | 2-5 dakika |

**İşleme Adımları:**
1. JSON → DataFrame dönüşümü
2. Tarih normalizasyonu (hafta başlangıcı: Pazartesi)
3. Birim standardizasyonu (K → binlik, % → ondalık)
4. Eksik veri interpolasyonu (en fazla 1 hafta)
5. Platform bazlı birleştirme (iOS + Android yan yana)
6. Haftalık değişim oranı hesaplama (WoW %)
7. Kümülatif metrik hesaplama

---

### Faz 3: Trend Analizi & Insight Üretimi

| Parametre | Değer |
|-----------|-------|
| **Ad** | Trend Analizi, Anomali Tespiti ve Insight Üretimi |
| **Agent** | `trend-analyzer` (claude-opus-4-6) |
| **Girdi** | `data/processed/weekly-metrics-{tarih}.csv` + `config/alert-thresholds.json` |
| **Çıktı** | `data/processed/insights-{tarih}.json` + `data/processed/anomalies-{tarih}.json` |
| **Kalite Kapısı** | Her metrik için trend yönü belirlenmiş; anomaliler gerekçelendirilmiş; insight'lar actionable |
| **Tahmini Süre** | 5-15 dakika |

**Analiz Katmanları:**

| # | Analiz Tipi | Yöntem | Çıktı |
|---|------------|--------|-------|
| 1 | Haftalık Değişim (WoW) | Basit yüzde değişim | `+5.2%`, `-3.1%` |
| 2 | 4 Haftalık Trend | Lineer regresyon eğimi | `↑ Yükseliş`, `↓ Düşüş`, `→ Stabil` |
| 3 | Anomali Tespiti | Z-Score (σ > 2) + IQR | `⚠️ Anormal düşüş`, `🔥 Spike` |
| 4 | Platform Karşılaştırma | iOS vs Android delta | `iOS %12 geride` |
| 5 | Korelasyon Analizi | Metrikler arası Pearson | `Rating ↓ ↔ Uninstall ↑` |
| 6 | Insight Üretimi | LLM-based (Claude API) | Doğal dilde 3-5 insight |

**Anomali Eşik Değerleri (Varsayılan):**

| Metrik | Uyarı (Sarı) | Kritik (Kırmızı) |
|--------|-------------|-------------------|
| App Rating | WoW ≤ -0.2 | WoW ≤ -0.5 veya mutlak < 3.0 |
| Crash Free User | < 99.5% | < 99.0% |
| Downloads | WoW ≤ -20% | WoW ≤ -40% |
| Active Users | WoW ≤ -10% | WoW ≤ -25% |
| Uninstalls | WoW ≥ +30% | WoW ≥ +50% |

---

### Faz 4: Kalite Kontrol & Doğrulama

| Parametre | Değer |
|-----------|-------|
| **Ad** | Rapor Kalite Kontrolü |
| **Agent** | `report-reviewer` (claude-sonnet-4-6) |
| **Girdi** | `data/processed/` dizinindeki tüm çıktılar + `data/raw/` (cross-check) |
| **Çıktı** | `reports/{tarih}/quality-report.md` |
| **Kalite Kapısı** | Veri doğruluğu %100 (raw vs processed cross-check); trend açıklamaları tutarlı; insight'lar veriyle destekli |
| **Tahmini Süre** | 3-5 dakika |

---

### Faz 5: Rapor Üretimi (Report Generation)

| Parametre | Değer |
|-----------|-------|
| **Ad** | SunExpress Branded Rapor Üretimi |
| **Agent** | `report-generator` (claude-sonnet-4-6) |
| **Girdi** | `data/processed/weekly-metrics-{tarih}.csv` + `data/processed/insights-{tarih}.json` + `data/processed/anomalies-{tarih}.json` + `data/processed/trend-summary-{tarih}.json` + `templates/branding-spec.md` |
| **Çıktı** | `reports/{tarih}/sunexpress-weekly-report-{tarih}.pptx` + PDF versiyonu |
| **Kalite Kapısı** | Slide sayısı ≥ 9; branding uyumu (`templates/branding-spec.md`); veri doğruluğu; grafik render başarılı |
| **Tahmini Süre** | 5–10 dakika |

---

## Faz Bağımlılık Haritası

```
Faz 1a (iOS Collect) ──┐
Faz 1b (Android Collect)├──→ Faz 2 (Process) ──→ Faz 3 (Analyze) ──→ Faz 4 (QA) ──→ Faz 5 (Report)
Faz 1c (Crashlytics) ──┘
```

### Bağımlılık Tablosu

| Faz | Bağımlı Olduğu Fazlar | Paralel Çalışabilir Mi? |
|-----|------------------------|-------------------------|
| Faz 1a | — | **Evet** — 1b ve 1c ile paralel |
| Faz 1b | — | **Evet** — 1a ve 1c ile paralel |
| Faz 1c | — | **Evet** — 1a ve 1b ile paralel |
| Faz 2 | Faz 1a + 1b + 1c (tümü) | Hayır |
| Faz 3 | Faz 2 | Hayır |
| Faz 4 | Faz 3 | Hayır |
| Faz 5 | Faz 2 + Faz 3 + Faz 4 | Hayır |

---

## Zamanlama

| Senaryo | Süre |
|---------|------|
| **Normal çalışma** (tüm API'ler erişilebilir) | ~15-35 dakika |
| **API timeout ile** (1 retry) | ~25-45 dakika |
| **Manuel tetikleme** (cache'li veri) | ~10-20 dakika |

### Önerilen Çalışma Zamanı

| Parametre | Değer |
|-----------|-------|
| Periyot | Her Pazartesi 09:00 (UTC+3) |
| Kapsam | Önceki Pazartesi-Pazar (7 gün) |
| Tetikleme | cron / GitHub Actions schedule |
| Bildirim | Slack webhook (tamamlanma + anomali alert) |

---

## Mevcut Pipeline (ai-dev-team) ile İlişki

Bu modül, ana `ai-dev-team` pipeline'ından **bağımsız** çalışır. Ancak:

- Aynı proje kök dizinini (`~/ai-dev-team/`) paylaşır
- Aynı naming convention'ları takip eder
- Kalite kapısı mekanizması aynı pattern'ı kullanır (skor ≥ 70)
- `code-reviewer` agent'ı paylaşımlı kullanılabilir (`report-reviewer` olarak)

```
~/ai-dev-team/
├── pipeline/              # Ana pipeline (web → iOS dönüşüm)
├── reporting-pipeline/    # Bu modül (performans raporlama)
├── analysis/              # Ana pipeline çıktıları
├── docs/                  # Ana pipeline çıktıları
└── ...
```
