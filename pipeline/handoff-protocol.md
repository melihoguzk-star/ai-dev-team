# Handoff Protokolü — Faz Geçiş Kuralları

Bu doküman, pipeline'daki bir fazdan diğerine geçerken uyulması gereken standart dosya yapısı, context aktarımı ve hata durumunda retry mekanizmasını tanımlar.

---

## 1. Standart Dosya Yapısı

Her faz çıktısı aşağıdaki dizin yapısına uygun olmalıdır:

```
~/ai-dev-team/
├── analysis/                          # Faz 1 çıktıları
│   ├── web-analysis-report.html       # Ana analiz raporu
│   └── web-analysis-report.md         # (opsiyonel) Markdown versiyonu
│
├── docs/                              # Faz 1.5, 2, 3, 5, 7b, 8b çıktıları
│   ├── brand-tokens.json              # Faz 1.5: Marka token'ları (makine okunur)
│   ├── brand-style-guide.html         # Faz 1.5: Görsel marka rehberi
│   ├── architecture-decisions.md      # Faz 2: Mimari kararlar
│   ├── ba-document.md                 # Faz 3: İş analizi dokümanı
│   ├── ios-design-spec.md             # Faz 5: iOS tasarım spesifikasyonu
│   ├── code-review-report.html        # Faz 7b: Kod inceleme raporu
│   ├── README.md                      # Faz 8b: Proje README
│   ├── CONTRIBUTING.md                # Faz 8b: Katkı kılavuzu
│   ├── ARCHITECTURE.md                # Faz 8b: Mimari genel bakış
│   ├── api-docs/                      # Faz 8b: API dokümantasyonu
│   │   └── *.md
│   └── quality-feedback-faz-*.md      # Kalite kapısı geri bildirimleri
│
├── design/                            # Faz 4 çıktıları
│   ├── components/                    # Component spec dosyaları
│   │   └── *.md
│   ├── tokens.json                    # Design token'ları
│   └── CHANGELOG.md                   # Tasarım değişiklik logu
│
├── backend/                           # Faz 6a çıktıları
│   ├── README.md                      # Backend kurulum talimatları
│   └── [proje dosyaları]
│
├── ios/                               # Faz 6b + 6c çıktıları
│   └── [proje dosyaları]
│
├── tests/                             # Faz 7a çıktıları
│   ├── backend/                       # Backend testleri
│   └── ios/                           # iOS testleri
│
├── infra/                             # Faz 8a çıktıları
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── .github/workflows/             # CI/CD
│   ├── .env.example
│   └── [IaC dosyaları]
│
└── pipeline/                          # Pipeline konfigürasyonu (bu dizin)
    ├── pipeline-config.md
    ├── phase-prompts.md
    ├── quality-gates.md
    └── handoff-protocol.md
```

---

## 2. Context Aktarım Kuralları

### Genel İlke

Her faz, sadece kendi bağımlı olduğu fazların çıktılarını okur. Gereksiz dosya okuma yapılmaz.

### Faz Bazlı Context Haritası

| Hedef Faz | Okuması Gereken Dosyalar | Neden |
|-----------|--------------------------|-------|
| **Faz 1.5** | `analysis/web-analysis-report.html` | Web analizindeki UI ve renk ipuçlarını okumak için |
| **Faz 2** | `analysis/web-analysis-report.html` | Sitenin teknik yapısını anlamak için |
| **Faz 3** | `analysis/web-analysis-report.html` + `docs/architecture-decisions.md` | Analiz + mimari kararları sentezlemek için |
| **Faz 4** | `analysis/web-analysis-report.html` + `docs/ba-document.md` + `docs/brand-tokens.json` | Mevcut UI'ı anlamak + ekranları bilmek + marka token'larını uygulamak için |
| **Faz 5** | `design/components/` + `docs/ba-document.md` + `docs/architecture-decisions.md` + `docs/brand-tokens.json` | Design spec'leri iOS'a çevirirken marka token'larını birebir uygulamak için |
| **Faz 6a** | `docs/architecture-decisions.md` + `docs/ba-document.md` | Tech stack + gereksinimler için |
| **Faz 6b** | `docs/architecture-decisions.md` + `docs/ios-design-spec.md` + `docs/ba-document.md` | iOS core modülleri için |
| **Faz 6c** | `docs/ios-design-spec.md` + `docs/brand-tokens.json` + `design/tokens.json` + `ios/` (mevcut core) | UI katmanı için + marka tutarlılığı + core entegrasyonu |
| **Faz 7a** | `docs/ba-document.md` + `backend/` + `ios/` | AC'lere uygun test yazmak için |
| **Faz 7b** | `backend/` + `ios/` + `tests/` + `docs/architecture-decisions.md` + `docs/ba-document.md` | Kod + mimari + BA uyum kontrolü |
| **Faz 8a** | `docs/architecture-decisions.md` + `backend/` | Deployment altyapısı hazırlamak için |
| **Faz 8b** | `docs/` + `backend/` + `ios/` + `infra/` | Her şeyi belgelemek için |

### Context Boyut Limiti

Büyük dosyalar için özet çıkarma stratejisi:

1. **HTML raporlar** (web-analysis-report.html): Agent doğrudan HTML'i okur, Mermaid diyagramlarını ve tabloları parse eder.
2. **Kod dizinleri** (backend/, ios/): Önce dizin yapısını listele, sonra ana dosyaları oku. Her dosyayı tek tek okuma — önce outline'ı incele.
3. **BA dokümanı** (ba-document.md): Uzun olabilir. Spesifik bölümleri oku (örneğin: sadece kabul kriterlerini çıkar).

---

## 3. Faz Geçiş Protokolü

### Standart Geçiş Adımları

Bir fazdan diğerine geçerken şu adımları izle:

```
1. FAZ TAMAMLAMA
   → Agent çıktıyı belirtilen dosyaya/dizine kaydeder
   → Agent tamamlanma özeti sunar (üretilen dosya adları, istatistikler)

2. KALİTE KAPISI
   → quality-gates.md'deki ilgili faz prompt'unu çalıştır
   → code-reviewer skoru değerlendirir

3. SKOR DEĞERLENDİRME
   → Skor ≥ 70: Sonraki faza geç (adım 5)
   → Skor 50-69: Düzeltme döngüsüne gir (adım 4)
   → Skor < 50: Fazı tamamen tekrar çalıştır (adım 6)

4. DÜZELTME DÖNGÜSÜ (skor 50-69)
   → quality-feedback-faz-N.md'deki sorunları oku
   → Aynı agent'ı düzeltme modu ile çalıştır:
      "[AGENT] subagent'ını kullan.
       ~/ai-dev-team/docs/quality-feedback-faz-[N].md dosyasını oku.
       [FAZ_ÇIKTISI] dosyasını güncelle. Geri bildirimdeki sorunları düzelt."
   → Kalite kapısını tekrar çalıştır
   → Maksimum 3 düzeltme denemesi. 3. denemede hala 70 altındaysa insan müdahalesi iste.

5. SONRAKI FAZA GEÇİŞ
   → Faz çıktısının doğru dizinde olduğunu kontrol et
   → phase-prompts.md'den sonraki fazın prompt'unu al
   → Sonraki fazı başlat

6. TAM TEKRAR (skor < 50)
   → Mevcut faz çıktısını sil veya yeniden adlandır (.bak uzantısı ekle)
   → Fazı baştan çalıştır
   → Maksimum 2 tam tekrar. 2. denemede hala 50 altındaysa insan müdahalesi iste.
```

### Geçiş Kontrol Listesi

Her faz geçişinde kontrol et:

```
□ Çıktı dosyası mevcut ve boş değil
□ Çıktı doğru dizinde
□ Kalite kapısı skoru ≥ 70
□ Önceki fazın çıktısı bozulmamış (read-only olarak kullanıldı)
□ Sonraki fazın tüm girdi dosyaları erişilebilir
```

---

## 4. Hata Durumları ve Retry Mekanizması

### Hata Tipleri

| Hata Tipi | Açıklama | Eylem |
|-----------|----------|-------|
| **AGENT_FAILURE** | Agent çalışması başarısız oldu (timeout, crash) | Aynı prompt ile 1 kez daha dene |
| **INCOMPLETE_OUTPUT** | Çıktı var ama bazı bölümler eksik | Düzeltme prompt'u ile eksikleri tamamla |
| **WRONG_FORMAT** | Çıktı yanlış formatta (örn: HTML yerine MD veya dosya adı yanlış) | Format düzeltme prompt'u ile tekrar çalıştır |
| **QUALITY_FAIL** | Kalite kapısı skoru düşük | Düzeltme döngüsü (§3.4) |
| **DEPENDENCY_MISSING** | Gerekli girdi dosyası bulunamadı | Bağımlı fazı tekrar çalıştır |
| **CONFLICT** | Faz çıktısı önceki kararlarla çelişiyor | İnsan müdahalesi iste |

### Retry Kuralları

```
RETRY_POLİTİKASI:
  max_retry_per_phase: 3          # Düzeltme denemesi
  max_full_restart: 2             # Tam tekrar
  escalation_after: 3 düzeltme veya 2 tam tekrar
  escalation_action: "İnsan müdahalesi iste — sorunları özetle"
  
  retry_prompt_template: |
    [AGENT] subagent'ını kullan.
    
    ÖNCEKİ DENEME BAŞARISIZ OLDU.
    
    Sorun: [HATA_AÇIKLAMASI]
    Geri bildirim: ~/ai-dev-team/docs/quality-feedback-faz-[N].md
    
    Mevcut çıktıyı ([FAZ_ÇIKTISI]) düzelt:
    [SPESİFİK_DÜZELTME_TALİMATLARI]
    
    Düzeltilmiş versiyonu aynı dosyaya kaydet.
```

### Eksik Çıktı için Tamamlama Prompt'u

```
[AGENT] subagent'ını kullan.

[FAZ_ÇIKTISI] dosyasını oku. Şu bölümler eksik:
- [EKSİK_BÖLÜM_1]
- [EKSİK_BÖLÜM_2]

Bu eksik bölümleri tamamla. Mevcut içeriği KORU, sadece ekle.
Dosyayı aynı yola kaydet.
```

### Çelişki Tespit Prompt'u

Faz 6'dan itibaren, çıktının önceki kararlarla uyumunu kontrol et:

```
code-reviewer subagent'ını kullan.

Şu iki dosyayı karşılaştır:
1. ~/ai-dev-team/docs/architecture-decisions.md (mimari kararlar)
2. [YENİ_FAZ_ÇIKTISI]

Çelişki kontrolü yap:
- Mimari kararlarda belirtilen tech stack kullanılmış mı?
- API endpoint yapısı tutarlı mı?
- Naming convention'lar uyumlu mu?

Tespit edilen çelişkileri listele. Çelişki yoksa "UYUMLU" yaz.
```

---

## 5. Paralel Çalışma Kuralları

### Paralel Çalıştırılabilecek Alt Fazlar

| Paralel Grup | Alt Fazlar | Paylaşılan Kaynak | Kural |
|--------------|------------|---------------------|-------|
| **Faz 6** | 6a (backend), 6b (swift-expert), 6c (mobile-dev) | `docs/` dizini (read-only) | 6a ve 6b paralel çalışır. 6c, 6b tamamlandıktan sonra başlar (core modüllere bağımlı) |
| **Faz 7** | 7a (test), 7b (review) | `backend/` + `ios/` (read-only) | Tamamen paralel çalışabilir |
| **Faz 8** | 8a (devops), 8b (docs) | `backend/` (read-only) | Tamamen paralel çalışabilir |

### Paralel Çalışma Kuralları

1. **Read-only ilkesi:** Paralel çalışan agent'lar aynı dosyayı YAZMAZ. Sadece okur.
2. **Ayrı çıktı dizini:** Her agent kendi çıktı dizinine yazar (§1'deki yapıya uygun).
3. **Senkronizasyon noktası:** Paralel alt fazlar tamamlandığında, kalite kapısı tüm çıktıları birlikte değerlendirir.

---

## 6. Pipeline Durum Takibi

Her faz geçişinde aşağıdaki durum dosyasını güncelleyin:

**Dosya:** `~/ai-dev-team/pipeline/pipeline-status.md`

```markdown
# Pipeline Durum Takibi

| Faz | Durum | Skor | Deneme | Başlangıç | Bitiş | Notlar |
|-----|-------|------|--------|-----------|-------|--------|
| 1 | ✅ Tamamlandı | 85 | 1/3 | 2026-03-04 23:50 | 2026-03-05 00:05 | — |
| 1.5 | 🔄 Devam ediyor | — | 1/3 | 2026-03-05 00:06 | — | — |
| 2 | ⏳ Bekliyor | — | — | — | — | — |
| 3 | ⏳ Bekliyor | — | — | — | — | — |
| 4 | ⏳ Bekliyor | — | — | — | — | — |
| 5 | ⏳ Bekliyor | — | — | — | — | — |
| 6 | ⏳ Bekliyor | — | — | — | — | — |
| 7 | ⏳ Bekliyor | — | — | — | — | — |
| 8 | ⏳ Bekliyor | — | — | — | — | — |
```

Durum ikonları:
- ⏳ Bekliyor
- 🔄 Devam ediyor
- ✅ Tamamlandı (skor ≥ 70)
- ⚠️ Düzeltme gerekiyor (skor 50-69)
- ❌ Başarısız (skor < 50)
- 🚫 Atlandı
- 👤 İnsan müdahalesi bekliyor
