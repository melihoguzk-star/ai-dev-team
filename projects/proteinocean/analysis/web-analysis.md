# ProteinOcean Web Analizi
**Tarih:** 2026-03-05
**Analizi Yapan:** web-analyzer (Faz 1)
**Hedef URL:** https://proteinocean.com

---

## 1. Site Genel Bilgileri

- **Platform:** ikas Commerce (Next.js/React tabanlı)
- **CDN:** cdn.myikas.com
- **Rendering:** Server-Side Rendering (SSR)
- **Analytics:** Google Tag Manager, Facebook Pixel, Google Analytics

## 2. Kategori Yapısı (Mobil Uygulama Kapsamı)

### Ana Kategoriler (Tab Bar)
| Kategori | URL Slug | Ürün Sayısı (Tahmini) |
|----------|----------|----------------------|
| Protein | /protein, /proteinler | 38+ |
| Vitamin | /vitamin, /vitaminler | 50+ |
| Spor Gıdaları | /spor-gidalari | 38+ |
| Sağlık | /saglik | 27+ |
| Gıda | /gida, /fonksiyonel-gidalar | Çok |
| Aksesuar | /aksesuar | Az |

### Alt Kategoriler (Protein)
- Whey Protein
- Collagen
- Cream of Rice
- BCAA
- Amino Asitler
- L-Carnitine
- Pre-Workout

### Marka Koleksiyonları
- ProteinOcean (kendi marka)
- Relentless
- Flava

## 3. Ürün Kartı Özellikleri

Her ürün kartında görünen bilgiler:
- Ürün görseli (WebP formatı, lazy loading)
- Ürün adı
- Satış fiyatı (TL)
- Orijinal fiyat (indirim varsa üstü çizili)
- İndirim yüzdesi badge
- Rating / değerlendirme sayısı
- Stok durumu
- Aroma/boyut varyant sayısı

## 4. Ürün Listeleme Özellikleri

### Sıralama Seçenekleri
- En Çok Satan (BEST_SELLER)
- En Yeni (LAST_ADDED)
- Fiyat: Düşükten Yükseğe
- Fiyat: Yüksekten Düşüğe

### Filtreleme
- Kategori bazlı filtreleme
- Fiyat aralığı
- Marka filtresi
- Facet-based dinamik filtreler

### Sayfalama
- Sonsuz kaydırma (Infinite Scroll) - varsayılan
- Her sayfada ~24 ürün

## 5. URL Yapısı

```
Ana sayfa:    https://proteinocean.com/
Kategori:     https://proteinocean.com/[slug]
Ürün detay:  https://proteinocean.com/[urun-slug]
```

## 6. Özel Özellikler

- Ücretsiz kargo eşiği: 250 TL
- Aynı gün kargo kampanyası
- WhatsApp destek hattı
- KVKK uyumlu
- Promosyon kodu desteği
- Paket/bundle ürün satışı
- Abonelik planı desteği

## 7. Mobil Uygulama Kapsam Sınırı

Bu proje sadece şunları kapsar:
1. **Kategori Listesi** - Ana kategori görüntüleme ekranı
2. **Ürün Listeleme** - Kategori içinde ürün grid/liste görünümü
3. Filtreleme ve sıralama UI
4. Ürün kartı komponenti

**Kapsam DIŞI:**
- Sepet/ödeme
- Kullanıcı girişi/kayıt
- Ürün detay sayfası (sadece temel)
- Blog, promosyon sayfaları
