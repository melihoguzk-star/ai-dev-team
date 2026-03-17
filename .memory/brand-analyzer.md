# Brand Analyzer — Agent Hafızası

## CSS Framework Pattern'leri

### Next.js / CSS Modules
- Sınıf adları: `style-module-scss-module__[hash]__[className]`
- Global CSS variables (:root) derleme anında inject edilir, HTML kaynak kodunda bulunmaz
- CSS dosyaları /_next/static/chunks/ altında hash'li — render sonrası değişir
- Font token'ı HTML class'ında görünür: `gothamfont_69ec362c-module__lHbljW__className`

### Renk Variable İsimlendirme
- `--primary-700` → ana marka rengi (buton bg, footer bg, aktif state)
- `--secondary-700` → ikincil vurgu rengi (başlık metni, secondary-red buton)
- `--neutral-50` → en açık gri arka plan
- `--neutral-100` → border/divider
- `--neutral-400` → placeholder / ikincil metin
- `--neutral-800` → focus border, input aktif
- `--error-700` → hata rengi
- `--black` → birincil metin
- `--white` → kart ve sayfa arka planı

## Kahve Dunyasi Marka Özeti (2026-03-05)

| Token | Değer | Notlar |
|---|---|---|
| primary | #8B1538 | Bordo kırmızı — footer, buton, fiyat |
| secondary | #C0182E | Canlı kırmızı — h1, ikincil CTA |
| accent | #6B0E26 | Hover/pressed state |
| font | Gotham | Custom licensed, iOS: Poppins/SF Rounded |
| button radius | 12px | |
| button height | 52px | |
| input radius | 15px | |
| input height | 55px | |
| shadow | 0 2px 4px rgba(0,0,0,0.05-0.10) | Çok hafif gölgeler |

## Renk Çıkarma Stratejileri

1. HTML'den CSS variable isimlerini yakala (var(--xxx) pattern)
2. CSS dosyasındaki kullanım bağlamından renk işlevini anla (footer bg → primary, error message → error)
3. Brandfetch / whatthelogo.com'dan logo renklerini çapraz doğrula
4. Buton/footer/aktif state bağlamından primary rengi tanımla
5. computed styles = gerçek değerler, Next.js'te :root inject edildiğinden curl ile alınamaz

## Font Eşleştirme

- Gotham → Poppins (Google Fonts, ücretsiz, geometric) veya SF Pro Rounded (iOS native)
- Geometric sans-serif → SF Pro Rounded en yakın iOS sistem fontu
- Web: custom font class adını HTML source'da ara

## İpuçları

- Next.js sitelerinde :root değerleri SSR/hydration sırasında inject edilir, statik HTML'de yok
- CSS dosyaları WAF korumalı olabilir (Request Rejected) — farklı hash'li dosya dene
- Font: HTML root element class adında font token görünür
- Marka tonu: footer rengi, buton rengi ve başlık rengi üçlüsü marka paletini belirler
