# Reporting Pipeline — Faz Prompt'ları

Her faz için Claude Code'a verilecek hazır prompt'lar. `[BÜYÜK_HARF]` ile belirtilen kısımları konfigürasyonunuza göre değiştirin.

---

## Faz 1a: iOS Veri Toplama

```
data-collector subagent'ını kullan.

App Store Connect API'den SunExpress iOS uygulamasının haftalık metriklerini topla.

Konfigürasyon:
- Credentials: ~/ai-dev-team/reporting-pipeline/config/credentials.json
- Metrik tanımları: ~/ai-dev-team/reporting-pipeline/config/metrics-config.json
- Tarih aralığı: [HAFTA_BAŞI] — [HAFTA_SONU] (varsayılan: son 7 gün)

Toplanacak metrikler:
1. App Rating (ortalama yıldız puanı)
2. Weekly Downloads (toplam indirme)
3. Weekly Active Users (aktif kullanıcı sayısı)
4. Weekly Uninstalls (silme sayısı)

Her metrik için:
- Raw JSON yanıtını data/raw/ios_{metrik}_{tarih}.json olarak kaydet
- API rate limit'lere uy (429 durumunda exponential backoff)
- Hata durumunda 3 retry yap, sonra hata raporla

Çıktı dizini: ~/ai-dev-team/reporting-pipeline/data/raw/

Tamamlandığında şu istatistikleri raporla:
- Başarılı API çağrısı sayısı
- Toplanan metrik sayısı
- Veri tarih aralığı
- Varsa hata/uyarılar
```

---

## Faz 1b: Android Veri Toplama

```
data-collector subagent'ını kullan.

Google Play Console API'den SunExpress Android uygulamasının haftalık metriklerini topla.

Konfigürasyon:
- Credentials: ~/ai-dev-team/reporting-pipeline/config/credentials.json (Google Service Account)
- Metrik tanımları: ~/ai-dev-team/reporting-pipeline/config/metrics-config.json
- App Package: [PACKAGE_NAME] (com.sunexpress.mobile)
- Tarih aralığı: [HAFTA_BAŞI] — [HAFTA_SONU]

Toplanacak metrikler:
1. App Rating (ortalama yıldız puanı)
2. Weekly Downloads (toplam indirme — yeni cihaz kurulumları)
3. Weekly Active Users (30-gün aktif kullanıcı → 7-güne normalize et)
4. Weekly Uninstalls (silme sayısı)

Her metrik için:
- Raw JSON yanıtını data/raw/android_{metrik}_{tarih}.json olarak kaydet
- Google Play Console'un veri gecikmesini hesaba kat (48 saat)
- Hata durumunda 3 retry yap

Çıktı dizini: ~/ai-dev-team/reporting-pipeline/data/raw/

Tamamlandığında aynı istatistik formatını kullan.
```

---

## Faz 1c: Crashlytics Veri Toplama

```
data-collector subagent'ını kullan.

Firebase Crashlytics'ten SunExpress iOS ve Android uygulamalarının crash verilerini topla.

Konfigürasyon:
- Credentials: ~/ai-dev-team/reporting-pipeline/config/credentials.json (Firebase Admin SDK)
- iOS Bundle ID: [IOS_BUNDLE_ID]
- Android Package: [ANDROID_PACKAGE]
- Tarih aralığı: [HAFTA_BAŞI] — [HAFTA_SONU]

Toplanacak metrikler:
1. Crash Free User Rate (%) — iOS
2. Crash Free User Rate (%) — Android
3. Top 5 Crash (opsiyonel — insight için)

Her platform için:
- Raw JSON'u data/raw/{platform}_crashlytics_{tarih}.json olarak kaydet
- Crash-free rate'i session bazlı hesapla (crash-free sessions / total sessions × 100)

Çıktı dizini: ~/ai-dev-team/reporting-pipeline/data/raw/

Tamamlandığında:
- Her platform için crash-free rate
- Varsa kritik crash artışı uyarısı
```

---

## Faz 2: Veri İşleme & Normalizasyon

```
data-processor subagent'ını kullan.

~/ai-dev-team/reporting-pipeline/data/raw/ dizinindeki tüm JSON dosyalarını oku ve normalize et.

İşleme adımları:

1. PARSE: Her JSON dosyasını platforma göre parse et
   - iOS: App Store Connect API response format
   - Android: Google Play Console API response format
   - Crashlytics: Firebase REST API response format

2. NORMALIZE:
   - Tarihler: ISO 8601 formatına çevir, hafta başlangıcı Pazartesi
   - Sayılar: Tam sayıya yuvarla (downloads, active users, uninstalls)
   - Yüzdeler: 2 ondalık basamak (crash-free rate)
   - Rating: 1 ondalık basamak

3. MERGE: Platform bazlı birleştir
   - Her hafta için: tarih | iOS_değer | Android_değer | toplam
   - 7 haftalık sliding window (mevcut hafta + önceki 6 hafta)

4. HESAPLA:
   - WoW (Week over Week) değişim: (bu_hafta - geçen_hafta) / geçen_hafta × 100
   - 4 haftalık ortalama (moving average)
   - Platform delta: iOS_değer - Android_değer (veya oran)

5. FLAG: Anomali adaylarını işaretle
   - ~/ai-dev-team/reporting-pipeline/config/alert-thresholds.json'daki eşiklere göre

Çıktılar:
- ~/ai-dev-team/reporting-pipeline/data/processed/weekly-metrics-{tarih}.csv
- ~/ai-dev-team/reporting-pipeline/data/processed/platform-comparison-{tarih}.csv
- ~/ai-dev-team/reporting-pipeline/data/processed/wow-changes-{tarih}.csv

CSV formatı:
week_start,metric,ios_value,android_value,total,ios_wow_pct,android_wow_pct,ios_4w_avg,android_4w_avg,anomaly_flag
```

---

## Faz 3: Trend Analizi & Insight Üretimi

```
trend-analyzer subagent'ını kullan.

Şu dosyaları oku:
1. ~/ai-dev-team/reporting-pipeline/data/processed/weekly-metrics-{tarih}.csv
2. ~/ai-dev-team/reporting-pipeline/data/processed/wow-changes-{tarih}.csv
3. ~/ai-dev-team/reporting-pipeline/config/alert-thresholds.json

Aşağıdaki analizleri yap:

1. TREND ANALİZİ (her metrik × her platform):
   - Son 7 haftanın lineer regresyon eğimi
   - Trend yönü: ↑ Yükseliş (eğim > 0.5σ), ↓ Düşüş (eğim < -0.5σ), → Stabil
   - Trend gücü: Güçlü (R² > 0.7), Orta (0.4-0.7), Zayıf (< 0.4)

2. ANOMALİ TESPİTİ:
   - Z-Score analizi: Son haftanın değeri, 7 haftalık ortalamadan kaç σ uzakta?
   - IQR yöntemi: Q1 - 1.5×IQR altı veya Q3 + 1.5×IQR üstü mü?
   - Her anomali için olası neden öner (mevsimsellik, uygulama güncellemesi, kampanya etkisi)

3. PLATFORM KARŞILAŞTIRMA:
   - iOS vs Android performans farkı (hangi platform daha iyi/kötü?)
   - Divergence tespiti: Platformlar arasında ayrışma trendi var mı?
   - Rating, crash, download için ayrı ayrı karşılaştır

4. KORELASYON ANALİZİ:
   - Rating ↔ Uninstall ilişkisi
   - Crash Rate ↔ Rating ilişkisi
   - Download ↔ Active User retansiyonu
   - Pearson korelasyon katsayısı + yorum

5. INSIGHT ÜRETİMİ:
   - Yukarıdaki analizlere dayanarak 3-5 actionable insight üret
   - Her insight için: Gözlem + Sebep Hipotezi + Önerilen Aksiyon
   - Öncelik sıralaması: Kritik > Önemli > Bilgi

Çıktılar:
- ~/ai-dev-team/reporting-pipeline/data/processed/insights-{tarih}.json
- ~/ai-dev-team/reporting-pipeline/data/processed/anomalies-{tarih}.json
- ~/ai-dev-team/reporting-pipeline/data/processed/trend-summary-{tarih}.json

Insight JSON formatı:
{
  "generated_at": "ISO8601",
  "period": "YYYY-MM-DD to YYYY-MM-DD",
  "insights": [
    {
      "id": "INS-001",
      "priority": "critical|important|info",
      "category": "rating|crash|download|active_user|uninstall|cross_metric",
      "platform": "ios|android|both",
      "observation": "iOS App Rating 3.0'dan 2.7'ye düştü (son 3 hafta)",
      "hypothesis": "Son güncelleme ile gelen UI değişikliği kullanıcı memnuniyetini olumsuz etkilemiş olabilir",
      "action": "App Store review'larını analiz et, son güncelleme ile ilgili şikayetleri filtrele",
      "supporting_data": { "metric": "app_rating", "values": [3.0, 2.8, 2.7], "wow_change": -3.7 }
    }
  ],
  "anomalies": [...],
  "trend_summary": {...}
}
```

---

## Faz 4: Kalite Kontrol & Doğrulama

```
report-reviewer subagent'ını kullan.

Şu dosyaları oku ve cross-check yap:
1. ~/ai-dev-team/reporting-pipeline/data/raw/ (ham veriler)
2. ~/ai-dev-team/reporting-pipeline/data/processed/ (işlenmiş veriler)

KONTROL LİSTESİ:

□ VERİ DOĞRULUĞU:
  - Raw JSON'daki değerler ile processed CSV'deki değerler eşleşiyor mu?
  - Her metrik × her platform × her hafta için cross-check yap
  - WoW hesaplamaları doğru mu? (manuel hesapla ve karşılaştır)

□ VERİ BÜTÜNLÜĞÜ:
  - Eksik hafta var mı? (7 haftalık pencerede gap kontrolü)
  - Null veya sıfır değer var mı? (beklenmedik)
  - Tarih sıralaması doğru mu?

□ ANOMALİ DOĞRULAMASI:
  - Flag'lenen anomaliler gerçekten anomali mi? (false positive kontrolü)
  - Eşik değerleri aşan ama flag'lenmeyen değer var mı? (false negative)

□ INSIGHT KALİTESİ:
  - Her insight veriye dayalı mı? (supporting_data dolu mu?)
  - Önerilen aksiyonlar spesifik ve uygulanabilir mi?
  - Öncelik sıralaması mantıklı mı?

□ FORMAT UYUMU:
  - JSON schema'lar doğru mu?
  - CSV header'ları tutarlı mı?
  - Tarih formatları ISO 8601 mi?

100 üzerinden skor ver.
- ≥ 70: ✅ GEÇER
- 50-69: ⚠️ Düzeltme gerekli
- < 50: ❌ Pipeline'ı tekrar çalıştır

Geri bildirim raporunu ~/ai-dev-team/reporting-pipeline/reports/{tarih}/quality-report.md olarak kaydet.
```

---

## Pipeline Çalıştırma

### Tam Pipeline (Sıralı)

```bash
cd ~/ai-dev-team/reporting-pipeline
./scripts/run-pipeline.sh --week "2026-03-02"
```

### Paralel Veri Toplama + Sıralı İşleme

```bash
# Faz 1: Paralel veri toplama (3 kaynak aynı anda)
./scripts/run-pipeline.sh --phase 1 --parallel

# Faz 2-4: Sıralı işleme
./scripts/run-pipeline.sh --phase 2
./scripts/run-pipeline.sh --phase 3
./scripts/run-pipeline.sh --phase 4
```

### Tek Faz Çalıştırma

```bash
./scripts/run-pipeline.sh --phase 3 --week "2026-03-02"
```

---

## Faz 5: Rapor Üretimi

```
report-generator subagent'ını kullan.

~/ai-dev-team/reporting-pipeline/templates/branding-spec.md dosyasını oku — rapor branding kurallarını oradan al.

Şu veri dosyalarını oku:
1. ~/ai-dev-team/reporting-pipeline/data/processed/weekly-metrics-[TARIH].csv
2. ~/ai-dev-team/reporting-pipeline/data/processed/insights-[TARIH].json
3. ~/ai-dev-team/reporting-pipeline/data/processed/anomalies-[TARIH].json
4. ~/ai-dev-team/reporting-pipeline/data/processed/trend-summary-[TARIH].json

Bu verilerden SunExpress branded PPTX rapor üret.

Slide yapısı:
1. Kapak — SunExpress Performance Overview + tarih aralığı + dekoratif mint şekil
2. iOS Performance Overview — 7 haftalık tam tablo (anomali hücreleri renkli)
3. Android Performance Overview — aynı format
4. App Rating — çizgi grafik (iOS lacivert, Android turuncu) + karşılaştırma tablosu
5. Crash Free User — grafik + tablo (Y ekseni dar aralık: 99.5-100)
6. Download (Weekly) — grafik + tablo
7. Active User (Weekly) — grafik + tablo
8. Uninstall Count (Weekly) — grafik + tablo
9. Trend Özeti ve Insightlar — trend ikonları + top insightlar + anomali uyarıları

Grafikleri matplotlib ile PNG olarak oluştur, slide'a embed et.
Her slide'da footer: sol alt loodos (teal), sağ alt SunExpress Airlines (lacivert+turuncu).

Çıktı: ~/ai-dev-team/reporting-pipeline/reports/[TARIH]/sunexpress-weekly-report-[TARIH].pptx

Oluşturduktan sonra:
1. PPTX'i PDF'e çevir
2. Slide'ları JPG'ye çevir ve görsel QA yap
3. Veri doğruluğunu kontrol et (tablodaki sayılar CSV ile eşleşmeli)
4. Branding uyumunu kontrol et (renkler, fontlar, layout)
```
