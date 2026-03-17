# AI Dev Team Pipeline Konfigürasyonu

Bu doküman, bir web sitesini iOS native uygulamaya dönüştürmek için kullanılan 8 fazlı pipeline'ın tam konfigürasyonunu içerir.

---

## Faz Tanımları

### Faz 1: Web Analiz
| Parametre | Değer |
|-----------|-------|
| **Ad** | Web Sitesi Analizi |
| **Agent** | `web-analyzer` (claude-opus-4-6) |
| **Girdi** | Hedef web sitesi URL'si |
| **Çıktı** | `~/ai-dev-team/analysis/web-analysis-report.html` |
| **Kalite Kapısı** | Tüm 6 analiz katmanı (sayfa yapısı, UI bileşen, API, veri modeli, iş mantığı, teknoloji stack) doldurulmuş olmalı |
| **Tahmini Süre** | 15-30 dakika |

---

### Faz 1.5: Marka Kimliği Analizi
| Parametre | Değer |
|-----------|-------|
| **Ad** | Marka Kimliği Analizi ve Token Üretimi |
| **Agent** | `brand-analyzer` (claude-sonnet-4-6) |
| **Girdi** | `~/ai-dev-team/analysis/web-analysis-report.html` + hedef web sitesi URL'si |
| **Çıktı** | `~/ai-dev-team/docs/brand-tokens.json` + `~/ai-dev-team/docs/brand-style-guide.html` |
| **Kalite Kapısı** | Renk paleti (tüm semantik roller), tipografi, spacing, border, shadow, ikon mapping ve buton stilleri eksiksiz tanımlanmış; iOS eşdeğerleri belirtilmiş olmalı |
| **Tahmini Süre** | 10-20 dakika |

---

### Faz 2: Mimari Tasarım
| Parametre | Değer |
|-----------|-------|
| **Ad** | Sistem Mimarisi Kararları |
| **Agent** | `system-architect` (claude-opus-4-6) |
| **Girdi** | `~/ai-dev-team/analysis/web-analysis-report.html` |
| **Çıktı** | `~/ai-dev-team/docs/architecture-decisions.md` |
| **Kalite Kapısı** | 5 karar alanı (backend tech, API tasarımı, DB şeması, iOS mimari, proje yapısı) tamamlanmış, her karar gerekçelendirilmiş olmalı |
| **Tahmini Süre** | 10-20 dakika |

---

### Faz 3: BA Doküman Üretimi
| Parametre | Değer |
|-----------|-------|
| **Ad** | İş Analizi Dokümanı |
| **Agent** | `ba-doc-generator` (claude-sonnet-4-6) |
| **Girdi** | `~/ai-dev-team/analysis/web-analysis-report.html` + `~/ai-dev-team/docs/architecture-decisions.md` |
| **Çıktı** | `~/ai-dev-team/docs/ba-document.md` |
| **Kalite Kapısı** | FR, BR, AC, VAL numaralandırması sürekli ve tutarlı; her gereksinim test edilebilir olmalı |
| **Tahmini Süre** | 15-25 dakika |

---

### Faz 4: UI/UX Tasarım
| Parametre | Değer |
|-----------|-------|
| **Ad** | Arayüz Tasarımı ve Design System |
| **Agent** | `ui-designer` (claude-sonnet-4-6) |
| **Girdi** | `~/ai-dev-team/analysis/web-analysis-report.html` + `~/ai-dev-team/docs/ba-document.md` |
| **Çıktı** | `~/ai-dev-team/design/components/` dizini + `~/ai-dev-team/design/tokens.json` |
| **Kalite Kapısı** | Tüm BA dokümanındaki ekranlar için component spec mevcut; erişilebilirlik WCAG 2.1 AA uyumlu |
| **Tahmini Süre** | 20-30 dakika |

---

### Faz 5: iOS Tasarım Dönüşümü
| Parametre | Değer |
|-----------|-------|
| **Ad** | Web → iOS Native Tasarım Dönüşümü |
| **Agent** | `uiux-translator` (claude-sonnet-4-6) |
| **Girdi** | `~/ai-dev-team/design/components/` + `~/ai-dev-team/docs/ba-document.md` |
| **Çıktı** | `~/ai-dev-team/docs/ios-design-spec.md` |
| **Kalite Kapısı** | HIG uyumu kontrol edilmiş; her web bileşeni için iOS karşılığı eşleştirilmiş; navigasyon haritası mermaid ile çizilmiş |
| **Tahmini Süre** | 10-20 dakika |

---

### Faz 6: Geliştirme (Backend + iOS)
| Parametre | Değer |
|-----------|-------|
| **Ad** | Kod Geliştirme |
| **Agent'lar** | `backend-developer` (claude-sonnet-4-6) + `swift-expert` (claude-sonnet-4-6) + `mobile-developer` (claude-sonnet-4-6) |
| **Girdi** | `~/ai-dev-team/docs/architecture-decisions.md` + `~/ai-dev-team/docs/ba-document.md` + `~/ai-dev-team/docs/ios-design-spec.md` |
| **Çıktı** | `~/ai-dev-team/backend/` + `~/ai-dev-team/ios/` dizinleri |
| **Kalite Kapısı** | Backend API'ler çalışır durumda; iOS projesi build alır; BA dokümanındaki tüm FR'ler implement edilmiş |
| **Tahmini Süre** | 60-120 dakika |
| **Not** | Bu faz paralel çalışabilir: backend-developer API'yi kurar, swift-expert core modülleri yazar, mobile-developer UI katmanını oluşturur |

---

### Faz 7: Test ve Kalite Kontrol
| Parametre | Değer |
|-----------|-------|
| **Ad** | Otomatik Test Yazımı ve Kalite Kontrolü |
| **Agent'lar** | `test-automator` (claude-sonnet-4-6) + `code-reviewer` (claude-sonnet-4-6) |
| **Girdi** | `~/ai-dev-team/backend/` + `~/ai-dev-team/ios/` + `~/ai-dev-team/docs/ba-document.md` |
| **Çıktı** | `~/ai-dev-team/tests/` + `~/ai-dev-team/docs/code-review-report.html` |
| **Kalite Kapısı** | Test coverage ≥ %80; tüm AC (kabul kriterleri) test edilmiş; code review skoru ≥ 70/100 |
| **Tahmini Süre** | 30-60 dakika |

---

### Faz 8: Deployment ve Dokümantasyon
| Parametre | Değer |
|-----------|-------|
| **Ad** | Deployment Hazırlığı ve Final Dokümantasyonu |
| **Agent'lar** | `devops-engineer` (claude-sonnet-4-6) + `documentation-engineer` (claude-sonnet-4-6) |
| **Girdi** | Tüm önceki faz çıktıları |
| **Çıktı** | `~/ai-dev-team/infra/` (CI/CD, Docker, Terraform) + `~/ai-dev-team/docs/README.md` + `~/ai-dev-team/docs/api-docs/` |
| **Kalite Kapısı** | CI/CD pipeline çalışır; README ve API dokümantasyonu eksiksiz; deployment checklist tamamlanmış |
| **Tahmini Süre** | 20-40 dakika |

---

## Faz Bağımlılık Haritası

```
Faz 1 (Web Analiz)
  ├──→ Faz 1.5 (Marka Kimliği Analizi)
  │      └──────────────────────────────────────────┐
  ├──→ Faz 2 (Mimari Tasarım)                       │
  │      └──→ Faz 3 (BA Doküman) ─────────────────┐ │
  │             └──→ Faz 4 (UI/UX Tasarım) ◄───────┘ │
  │                    └──→ Faz 5 (iOS Dönüşüm) ◄────┘
  │                           │
  │                           ▼
  │                    Faz 6 (Geliştirme)
  │                           │
  │                           ▼
  │                    Faz 7 (Test & QA)
  │                           │
  │                           ▼
  └──────────────────→ Faz 8 (Deploy & Docs) ◄── tüm çıktıları toplar
```

### Bağımlılık Tablosu

| Faz | Bağımlı Olduğu Fazlar | Paralel Çalışabilir Mi? |
|-----|------------------------|-------------------------|
| Faz 1 | — | — |
| Faz 1.5 | Faz 1 | **Evet** — Faz 2 ile paralel çalışabilir |
| Faz 2 | Faz 1 | **Evet** — Faz 1.5 ile paralel çalışabilir |
| Faz 3 | Faz 1, Faz 2 | Hayır |
| Faz 4 | Faz 1, Faz 1.5, Faz 3 | Hayır |
| Faz 5 | Faz 1.5, Faz 3, Faz 4 | Hayır |
| Faz 6 | Faz 2, Faz 3, Faz 5 | **Evet** — backend-developer, swift-expert paralel çalışabilir |
| Faz 7 | Faz 6 | **Kısmen** — test-automator ve code-reviewer paralel çalışabilir |
| Faz 8 | Faz 1-7 (tümü) | **Kısmen** — devops ve documentation paralel çalışabilir |

---

## Toplam Tahmini Süre

| Senaryo | Süre |
|---------|------|
| **Basit site** (5-10 sayfa, basit API) | ~3-5 saat |
| **Orta karmaşık site** (20-50 sayfa, CRUD + auth) | ~6-10 saat |
| **Karmaşık platform** (e-ticaret, çoklu entegrasyon) | ~12-20 saat |

> **Not:** Süreler Claude Code'un paralel agent çalıştırma kapasitesine ve sitenin karmaşıklığına göre değişir. Faz 6'daki paralellik toplam süreyi önemli ölçüde kısaltabilir.
