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

## Skor Karşılaştırma Tablosu

| Faz | Ad | Skor | Durum |
|-----|-----|------|-------|
| 1 | Veri Toplama | — | — |
| 2 | Veri İşleme | — | — |
| 3 | Trend Analizi | — | — |
| 4 | Kalite Kontrol | — | — |
| **Ortalama** | — | **—** | — |

> **Pipeline başarı kriteri:** Ortalama skor ≥ 75 ve hiçbir faz 50 altında olmamalı.
