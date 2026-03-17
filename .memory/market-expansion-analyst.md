# market-expansion-analyst Memory
Son güncelleme: 2026-03-05

## Convention'lar
- HTML cikti tek dosyada, inline CSS, Tailwind CDN + Inter font + Lucide icons
- Sidebar fixed 260px, main margin-left 260px
- Teal #0D9488 primary accent renk
- Karar noktalari her zaman secenek tablosu formatinda (avantaj/dezavantaj/tavsiye)
- Onerilen secenek: class="recommended-row" ile vurgulanir (teal sol border)
- Risk tablosunda etki + olasilik badge'leri ayri kolonlarda gosterilir
- Timeline icin .timeline/.timeline-item/.timeline-dot/.timeline-card class yapisi
- toggleCard(this) fonksiyonu ile expand/collapse; card-body.collapsed display:none
- stat-card'larda buyuk teal rakam + kucuk gri aciklama

## Kahve Dunyasi UK Projesi Notlari
- Proje dizini: /Users/melihoguz/ai-dev-team/projects/kahvedunyasi-uk/
- kahvedunyasi.co.uk zaten mevcut (fiziksel magaza rehberi); e-ticaret sub-domain onerisi: shop.kahvedunyasi.co.uk
- Piccadilly Circus magazasi 2011'den beri var — marka bilinirlik avantaji
- Taze urunler (pastane/dondurma) cross-border gonderilemez — kritik kisitlama
- UK GDPR: yurt disi sirket icin ilk satisdan itibaren zorunlu; ICO kaydi + UK temsilci
- VAT: yurt disi sirketler icin £90,000 esik UYGULANMAZ; ilk satisdan kayit zorunlu
- UK food labelling: 1 Ocak 2024'ten itibaren UK FBO fiziksel adresi zorunlu
- Fulfillment: UK 3PL deposu onerilen (cross-border degil)
- Odeme: Stripe UK onerilen (1.5% + £0.20 UK kartlar)
- UK-Turkey STA: 1 Ocak 2021 yururlukte; kavurulmus kahvede gomruk vergisi %0

## Hatalar ve Cozumler
- WebFetch araç iznin olmadigi ortamda: Yalnizca WebSearch ile calismak gerekir
- Paralel WebSearch + WebFetch cagrisi yapinca her iki arac da iptal oluyor; once WebFetch dene, basarisizsa WebSearch'e gec

## Tercihler
- Cikti dili: Turkce (teknik terimler Ingilizce kalabilir)
- Raporda emoji kullanilmaz
- Tum tablolar data-table class ile, zebra striping dahil
- Risk tablosunda en az 10+ risk; kategorilere gore ayri badge'ler
- Her karar noktasi kendi decision-card bloğunda
- Self-validation checklist: pazar buyuklugu rakamlarla, 3+ rakip, yasal analiz, kulturel uyum, 5+ risk badge'li, karar noktalari secenekli, fazli yol haritasi, maliyet tahmini, dashboard stat kartlari
