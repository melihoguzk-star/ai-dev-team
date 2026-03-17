# UX Auditor Agent — Kalıcı Hafıza

## Kahve Dünyası Kiosk Benchmarks (2026-03-06)

### robotpos Kiosk Platformu Notları
- Next.js App Router (RSC streaming) + Tailwind CSS v3 + react-simple-keyboard
- Multi-tenant routing: /kiosk/[tenantId]/[branchId]/
- Dışarıdan 404 döndürür — yalnızca mağaza içi ağda erişilebilir
- 32" PCAP kapasitif dokunmatik ekran + 80mm termal yazıcı
- CSS: iki ayrı stylesheet, blob animasyonu (attract screen), glass-effect mevcut
- Gerçek sayfa içeriği JS bundle çalışmadan görülemiyor

### Kiosk UX Benchmark Skorları
- Kahve Dünyası kiosk genel: 56/100 (ORTA)
- Akış: 5.5/10 | UI/UX: 5.4/10 | Performans: 6.2/10
- Kiosk akış ideali: ≤4 dokunuş | Gerçekleşen: 6 dokunuş (ana akış)

### Sık Karşılaşılan Kiosk Sorunları
1. Font boyutu: web'den taşınan text-xs/text-sm kiosk mesafesinde okunamaz (min 24px gerekli)
2. Metin arama (ekran klavyesi) kiosk'ta ciddi UX sorunu — görsel navigasyonla değiştirilmeli
3. Timeout/inaktivite mekanizması eksik — kiosk'ta zorunlu (60sn kuralı)
4. Glass morphism efekti parlak mağaza ortamında okunabilirliği düşürür
5. Yardım çağırma butonu yokluğu — tüm ekranlarda sabit floating buton gerekli
6. Offline/ağ kesintisi senaryosu: Service Worker olmadan kırılganlık
7. Dokunma hedefi tutarsızlığı: h-10 (40px) < kiosk min 48px

### Kiosk Standartları (Referans)
- Dokunma hedefi: min 48x48px, ideal 56x56px
- Font body: min 24px, başlık: min 32px
- Kontrast: WCAG AAA (7:1)
- Akış: ≤4 dokunuş hedef
- İnaktivite timeout: 60-90 saniye
- Sayfa geçiş: <500ms, dokunma yanıt: <100ms

### Analiz Metodolojisi
Sayfa lokal ağa kısıtlıysa: CSS dosyaları + JS bundle + platform docs + marka analizi kombinasyonu
CSS'den tespitler: buton boyutları (.h-10, .h-14), animasyonlar, font sınıfları, renk değişkenleri
