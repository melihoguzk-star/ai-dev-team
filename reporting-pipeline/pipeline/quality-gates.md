# Reporting Pipeline — Kalite Kapıları

Her faz tamamlandığında aşağıdaki kalite kontrol prompt'unu Claude Code'a verin.

---

## Faz 1 Kalite Kapısı: Veri Toplama

```
report-reviewer subagent'ını kullan.

~/ai-dev-team/reporting-pipeline/data/raw/ dizinindeki tüm JSON dosyalarını kontrol et.

KONTROL LİSTESİ:
□ Dosya Sayısı: Her platform için 4 metrik dosyası + 2 crashlytics dosyası = minimum 10 dosya mevcut mu?
□ JSON Geçerliliği: Tüm dosyalar geçerli JSON mu?
□ Veri Varlığı: Her dosyada en az 1 haftalık veri var mı?
□ Tarih Aralığı: İstenen hafta kapsamında mı?
□ Değer Aralığı: Rating 1-5 arası mı? Crash-free %90-100 arası mı? Download/Active/Uninstall > 0 mı?
□ API Hataları: Hata içeren yanıt dosyası var mı?

Eksik dosya veya hata varsa listele.
100 üzerinden skor ver.
```

---

## Faz 2 Kalite Kapısı: Veri İşleme

```
report-reviewer subagent'ını kullan.

~/ai-dev-team/reporting-pipeline/data/processed/ dizinindeki CSV dosyalarını kontrol et.
Referans: ~/ai-dev-team/reporting-pipeline/data/raw/ (cross-check için)

KONTROL LİSTESİ:
□ CSV Yapısı: Beklenen column'lar var mı? Header doğru mu?
□ Veri Eşleşmesi: Raw JSON'daki değerler ile CSV'deki değerler tutarlı mı? (rastgele 5 değer kontrol et)
□ WoW Hesaplaması: En az 3 WoW değerini manuel hesapla ve doğrula
□ Eksik Veri: Null veya boş hücre var mı? Varsa interpolasyon doğru yapılmış mı?
□ Sıralama: Haftalar kronolojik sırada mı?
□ Birim Tutarlılığı: Tüm sayılar aynı birimde mi? (K standardize edilmiş mi?)
□ Anomali Flag: Flag'ler alert-thresholds.json'daki eşiklere uygun mu?

100 üzerinden skor ver.
Skor 70 altındaysa geri bildirim raporunu kaydet.
```

---

## Faz 3 Kalite Kapısı: Trend Analizi & Insight

```
report-reviewer subagent'ını kullan.

Şu dosyaları oku:
- ~/ai-dev-team/reporting-pipeline/data/processed/insights-{tarih}.json
- ~/ai-dev-team/reporting-pipeline/data/processed/anomalies-{tarih}.json
- ~/ai-dev-team/reporting-pipeline/data/processed/trend-summary-{tarih}.json

Referans: ~/ai-dev-team/reporting-pipeline/data/processed/weekly-metrics-{tarih}.csv

KONTROL LİSTESİ:
□ Trend Yönü: Her metrik × platform için trend belirlenmiş mi? (toplam 10 trend)
□ Trend Tutarlılığı: Trend yönü verilerle uyumlu mu? (↑ diyorsa değerler gerçekten artıyor mu?)
□ Anomali Gerekçesi: Her anomali için olası neden yazılmış mı?
□ False Positive: Anomali olarak işaretlenen ama normal görünen değer var mı?
□ False Negative: Anomali olması gereken ama işaretlenmemiş değer var mı?
□ Insight Kalitesi: Her insight için (a) gözlem spesifik mi, (b) hipotez mantıklı mı, (c) aksiyon uygulanabilir mi?
□ Insight Kapsam: En az 3, en fazla 7 insight var mı?
□ Öncelik: Kritik anomaliler yüksek öncelikli mi?
□ Korelasyon: Metrikler arası ilişkiler mantıklı mı?
□ JSON Schema: Tüm çıktılar beklenen schema'ya uygun mu?

100 üzerinden skor ver.
Skor 70 altındaysa geri bildirim raporunu kaydet.
```

---

## Faz 4 Kalite Kapısı: Genel Doğrulama

```
report-reviewer subagent'ını kullan.

Tüm pipeline çıktısını uçtan uca doğrula.

Şu dizinleri oku:
- ~/ai-dev-team/reporting-pipeline/data/raw/
- ~/ai-dev-team/reporting-pipeline/data/processed/

KONTROL LİSTESİ:
□ End-to-End Doğruluk: Raw → Processed → Insight zincirinde veri kaybı veya bozulma var mı?
□ Tekrarlanabilirlik: Aynı raw data ile pipeline tekrar çalıştırılsa aynı sonuçlar üretir mi?
□ Mevcut Raporla Uyum: Çıktılar, SunExpress PDF raporundaki formata dönüştürülebilir mi?
□ Completeness: 5 metrik × 2 platform × 7 hafta = 70 veri noktası eksiksiz mi?
□ Tarih Tutarlılığı: Tüm dosyalardaki tarih aralıkları aynı mı?

FINAL SKOR:
- ≥ 80: ✅ Rapor üretimine hazır
- 70-79: ✅ GEÇER ama iyileştirmeler var
- 50-69: ⚠️ Düzeltme gerekli — sorunları listele
- < 50: ❌ Pipeline'ı tekrar çalıştır

Kalite raporunu ~/ai-dev-team/reporting-pipeline/reports/{tarih}/quality-report.md olarak kaydet.
```

---

## Faz 5 Kalite Kapısı: Rapor Üretimi

```
report-reviewer subagent'ını kullan.

~/ai-dev-team/reporting-pipeline/reports/[TARIH]/sunexpress-weekly-report-[TARIH].pptx dosyasını kontrol et.
Referans: ~/ai-dev-team/reporting-pipeline/templates/branding-spec.md + ~/ai-dev-team/reporting-pipeline/data/processed/weekly-metrics-[TARIH].csv

KONTROL LİSTESİ:
- Slide Sayısı: Minimum 9 slide mevcut mu?
- Veri Doğruluğu: Slide 2-3 teki tablo değerleri CSV deki verilerle birebir eşleşiyor mu?
- Grafik Doğruluğu: Slide 4-8 deki grafik data pointleri doğru mu?
- Branding Renkler: Lacivert #1B3A5C, turuncu #E85D26, teal #2ABFBF, arka plan #F0F0F0 kullanılmış mı?
- Branding Fontlar: Başlıklar bold 36-40pt, tablo header 14-16pt mi?
- Branding Footer: Her slide da Loodos (sol alt) ve SunExpress Airlines (sağ alt) logosu var mı?
- Kapak: Dekoratif mint şekil ve doğru başlık var mı?
- Anomali İşaretleme: Warning hücreler sarı, critical hücreler kırmızı arka planlı mı?
- Insight Slide: Trend yönleri doğru mu? Insightlar veriyle destekli mi?
- PDF Çıktı: PDF versiyonu da oluşturulmuş mu?

100 üzerinden skor ver.
Skor 70 altındaysa geri bildirim raporunu kaydet.
```

---

## Skor Karşılaştırma Tablosu

| Faz | Ad | Skor | Durum |
|-----|-----|------|-------|
| 1 | Veri Toplama | — | — |
| 2 | Veri İşleme | — | — |
| 3 | Trend Analizi | — | — |
| 4 | Kalite Kontrol | — | — |
| 5 | Rapor Üretimi | — | — |
| **Ortalama** | — | **—** | — |

> **Pipeline başarı kriteri:** Ortalama skor ≥ 75 ve hiçbir faz 50 altında olmamalı.
