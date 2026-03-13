# SunExpress Rapor Branding Spesifikasyonu

Bu doküman, SunExpress Sun Mobile haftalık performans raporlarının görsel kimliğini tanımlar.
`generate-report.py` ve `report-generator` agent'ı bu spesifikasyona uygun çıktı üretmelidir.

---

## Renk Paleti

| Rol | Hex Kodu | Açıklama / Kullanım Yeri |
|-----|----------|--------------------------|
| Birincil / Başlıklar | `#1B3A5C` | Koyu lacivert — slide başlıkları, tablo header arka planı, iOS grafik çizgisi |
| Vurgu / Platform | `#E85D26` | SunExpress turuncu — "iOS"/"Android" kelimesi, Android grafik çizgisi |
| Loodos | `#2ABFBF` | Teal/mint — Loodos logosu, kapak dekoratif şekil |
| Arka Plan | `#F0F0F0` | Açık gri — slide arka planı |
| Tablo Header Metin | `#FFFFFF` | Beyaz |
| Tablo İçerik Metin | `#333333` | Koyu gri |
| Tablo Border | `#CCCCCC` | Açık gri |
| Warning Hücre | `#FFF3CD` | Sarı arka plan — anomali uyarı (WoW eşik aşımı) |
| Critical Hücre | `#F8D7DA` | Kırmızı arka plan — kritik anomali |
| Trend Yukarı | `#28A745` | Yeşil — artan trend etiketi |
| Trend Aşağı | `#DC3545` | Kırmızı — düşen trend etiketi |
| Trend Stabil | `#6C757D` | Gri — stabil trend etiketi |

---

## Tipografi

Tüm metin öğeleri **Calibri** fontu kullanır.

| Öğe | Font | Boyut | Ağırlık | Renk |
|-----|------|-------|---------|------|
| Kapak Başlık | Calibri | 44–48pt | Bold | `#1B3A5C` |
| Slide Başlık | Calibri | 36–40pt | Bold | `#1B3A5C` |
| Platform Adı (başlıkta) | Calibri | 36–40pt | Bold | `#E85D26` |
| "Performance Overview" | Calibri | 36–40pt | Regular | `#1B3A5C` |
| Tablo Header | Calibri | 14–16pt | Bold | `#FFFFFF` |
| Tablo İçerik | Calibri | 12–14pt | Regular | `#333333` |
| Grafik Label / Data Label | Calibri | 10–12pt | Regular | `#333333` |
| Footer | Calibri | 10pt | Regular | — |

---

## Slide Layout

| Parametre | Değer |
|-----------|-------|
| Boyut | 16:9 — 13.33" × 7.5" |
| Arka Plan | `#F0F0F0` |
| Margin (minimum) | 0.5" |
| Footer — Sol Alt | `"loodos"` metni, `#2ABFBF`, 10pt |
| Footer — Sağ Alt | `"SunExpress Airlines"` metni, `#1B3A5C`, 10pt |

---

## Kapak Slide (Slide 1)

| Konum | İçerik | Stil |
|-------|--------|------|
| Sol üst | SunExpress Airlines logosu (metin placeholder) | Küçük, `#1B3A5C` |
| Orta sol | `"SunExpress"` | Bold, 48pt, `#1B3A5C` |
| Orta sol (alt satır) | `"Performance Overview"` | Regular, 40pt, `#1B3A5C` |
| Orta sol (3. satır) | Tarih aralığı | Regular, 18pt, `#E85D26` |
| Sağ yarı | Büyük dekoratif geometrik şekil — yarım daire/arch | `#2ABFBF` (mint/teal) |
| Sol alt | Loodos logosu | `#2ABFBF`, 12pt |

---

## Veri Tablosu Stili

| Öğe | Değer |
|-----|-------|
| Header satır arka plan | `#1B3A5C` |
| Header satır metin | `#FFFFFF`, Bold |
| Veri satır arka plan | `#FFFFFF` |
| Veri satır metin | `#333333`, Regular |
| Header satır yüksekliği | 0.5" |
| Veri satır yüksekliği | 0.4" |
| Hücre padding | 0.05" |
| Border kalınlık | 0.5pt |
| Border rengi | `#CCCCCC` |
| Warning hücre arka planı | `#FFF3CD` |
| Critical hücre arka planı | `#F8D7DA` |

---

## Grafik Stili

| Öğe | Değer |
|-----|-------|
| Arka plan | `#FFFFFF` (beyaz) |
| Grid | Yatay çizgiler, `#E0E0E0`, açık gri |
| iOS çizgi rengi | `#1B3A5C` |
| iOS çizgi kalınlığı | 2.5pt |
| iOS marker | Yuvarlak (circle) |
| Android çizgi rengi | `#E85D26` |
| Android çizgi kalınlığı | 2.5pt |
| Android marker | Yuvarlak (circle) |
| Legend konumu | Üst orta, yatay |
| Legend içeriği | ● iOS  ● Android |
| Data label | Her nokta üzerinde değer, 9pt, `#333333` |
| Y ekseni | Veri aralığına göre auto-scale (sıfırdan başlamayabilir) |
| X ekseni | Hafta başlangıç tarihleri, "D MMM" formatı |

---

## Grafik + Tablo Layout (Slide 4–8)

```
┌──────────────────────────────────────────────────────────────┐
│  Başlık Bandı (#1B3A5C)                                       │
├────────────────────────────────┬─────────────────────────────┤
│                                │                              │
│   Çizgi Grafik                 │   Karşılaştırma Tablosu     │
│   (sol %60)                    │   Date | iOS | Android       │
│                                │   (sağ %40)                  │
│                                │                              │
├────────────────────────────────┴─────────────────────────────┤
│  WoW Kutuları  |  Trend Etiketleri                            │
├──────────────────────────────────────────────────────────────┤
│  Footer                                                       │
└──────────────────────────────────────────────────────────────┘
```

| Alan | Genişlik | Soldan offset |
|------|----------|---------------|
| Grafik (PNG embed) | %60 — ~7.8" | 0.3" |
| Boşluk | 0.3" | — |
| Tablo | %40 — ~4.7" | 8.4" |

---

## Slide Yapısı (9 Slide)

| # | Slide | İçerik |
|---|-------|--------|
| 1 | Kapak | SunExpress branding, tarih aralığı, Loodos logo |
| 2 | iOS Performance Overview | 7 hafta × 5 metrik tablo, anomali hücre renklendirme |
| 3 | Android Performance Overview | Aynı format, Android verileri |
| 4 | App Rating | Çizgi grafik + tablo + WoW + trend |
| 5 | Crash Free User | Çizgi grafik + tablo + WoW + trend |
| 6 | Download (Weekly) | Çizgi grafik + tablo + WoW + trend |
| 7 | Active User (Weekly) | Çizgi grafik + tablo + WoW + trend |
| 8 | Uninstall Count (Weekly) | Çizgi grafik + tablo + WoW + trend |
| 9 | Trend Summary & Key Insights | Trend özeti (↑↓→ + R²) + top 5 insight + anomali uyarı bandı |

---

*Güncelleme tarihi: 2026-03-13 — Loodos Reporting Pipeline v1.0*
