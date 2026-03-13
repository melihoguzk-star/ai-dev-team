# Reporting Pipeline — Project Context

Bu modül, **SunExpress Sun Mobile** uygulamasının haftalık performans raporlarını otomatize eden 5 fazlı bir pipeline'dır.

## Amaç

App Store Connect, Google Play Console ve Firebase/Crashlytics'ten veri toplayarak:
1. iOS ve Android metriklerini otomatik çeker
2. Haftalık trend analizi ve anomali tespiti yapar
3. Insight'lar ve aksiyonlar üretir

## Tech Stack

| Katman | Teknoloji |
|--------|-----------|
| Veri Toplama | Python 3.11+ |
| App Store Connect | app-store-connect-api (JWT auth) |
| Google Play Console | google-api-python-client (Service Account) |
| Firebase/Crashlytics | firebase-admin SDK |
| Veri İşleme | pandas + numpy |
| Anomali Tespiti | scipy.stats (z-score, IQR) |
| Rapor Çıktısı | PPTX (python-pptx) + PDF |
| Otomasyon | cron / GitHub Actions |

## Pipeline Fazları

1. Veri Toplama → `data-collector`
2. Veri İşleme & Normalizasyon → `data-processor`
3. Trend Analizi & Insight → `trend-analyzer`
4. Kalite Kontrol → `report-reviewer`
5. Rapor Üretimi → `report-generator`

## Metrikler

| Metrik | iOS Kaynağı | Android Kaynağı |
|--------|-------------|-----------------|
| App Rating | App Store Connect API | Google Play Developer API |
| Crash Free User (%) | Firebase Crashlytics | Firebase Crashlytics |
| Download (Weekly) | App Store Connect API | Google Play Developer API |
| Active User (Weekly) | App Store Connect API | Google Play Developer API |
| Uninstall Count (Weekly) | App Store Connect API | Google Play Developer API |

### report-generator Agent

| Parametre | Değer |
|-----------|-------|
| **Rol** | Pipeline çıktılarından SunExpress branded PPTX/PDF performans raporu üretir |
| **Model** | claude-sonnet-4-6 |
| **Tetikleme** | `report-generator` subagent'ını kullan |
| **Branding referansı** | `templates/branding-spec.md` |

## Dizin Yapısı

```
~/ai-dev-team/reporting-pipeline/
├── CLAUDE.md                    # Bu dosya
├── pipeline/                    # Pipeline config & prompt'lar
│   ├── pipeline-config.md       # Faz tanımları
│   ├── phase-prompts.md         # Agent prompt'ları
│   ├── quality-gates.md         # Kalite kapıları
│   └── handoff-protocol.md      # Faz geçiş kuralları
├── config/                      # API key'ler ve ayarlar
│   ├── credentials.example.json # Credential şablonu
│   ├── metrics-config.json      # Metrik tanımları & eşik değerler
│   └── alert-thresholds.json    # Anomali eşik değerleri
├── scripts/                     # Otomasyon scriptleri
│   ├── collect-ios.py           # App Store Connect veri çekme
│   ├── collect-android.py       # Google Play Console veri çekme
│   ├── collect-crashlytics.py   # Firebase Crashlytics veri çekme
│   ├── process-data.py          # Veri normalizasyon & birleştirme
│   ├── analyze-trends.py        # Trend analizi & anomali tespiti
│   ├── generate-report.py       # PPTX/PDF rapor üretimi
│   └── run-pipeline.sh          # Tüm pipeline'ı çalıştır
├── templates/                   # Rapor şablonları
│   └── sunexpress-report.pptx   # SunExpress branded PPTX template
├── data/                        # Veri dizini
│   ├── raw/                     # Ham API yanıtları (JSON)
│   └── processed/               # İşlenmiş veriler (CSV/Parquet)
├── reports/                     # Üretilen raporlar
│   └── YYYY-MM-DD/              # Tarih bazlı rapor dizini
└── tests/                       # Test dosyaları
    ├── test_collectors.py
    ├── test_processor.py
    └── test_analyzer.py
```

## Naming Convention'lar

- Python dosya: `kebab-case` → `collect-ios.py`
- Python sınıf: `PascalCase` → `AppStoreCollector`
- Python fonksiyon: `snake_case` → `fetch_weekly_downloads`
- Config dosya: `kebab-case.json`
- Veri dosya: `{platform}_{metric}_{YYYY-MM-DD}.json`
- Rapor dosya: `sunexpress-weekly-report-{YYYY-MM-DD}.pptx`

## Önemli Kurallar

- API credential'ları ASLA repo'ya commit'lenmez
- Raw data JSON olarak saklanır (audit trail)
- Her pipeline çalışması idempotent olmalı
- Anomali tespitinde false positive'leri minimize et
- Rapor formatı mevcut SunExpress PDF'iyle uyumlu olmalı
