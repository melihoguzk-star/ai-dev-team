# Mini Pazar Analizi: Küçük Kahve Dükkanının Online Satışa Geçişi

**Tarih:** Mart 2026  
**Kapsam:** Fiziksel mağazadan e-ticarete geçiş stratejisi

---

## 1. Mevcut Durum Analizi

| Parametre | Durum |
|---|---|
| **İş Modeli** | Tek şubeli fiziksel kahve dükkanı |
| **Müşteri Kitlesi** | Yerel halk, düzenli müdavimler, ofis çalışanları |
| **Ürün Yelpazesi** | Hazır kahve servisi, paketli kahve çekirdeği, öğütülmüş kahve, kahve ekipmanları |
| **Güçlü Yönler** | Sadık müşteri tabanı, ürün bilgisi, marka bilinirliği (yerel) |
| **Zayıf Yönler** | Coğrafi kısıtlılık, dijital altyapı eksikliği, sınırlı erişim |

Online satışa geçişte mevcut fiziksel müşteri tabanı ilk dönüşüm havuzunu oluşturacaktır. Paketli kahve, çekirdek kahve ve ekipman gibi kargoya uygun ürünler dijital kanalın temelini oluşturmalıdır.

---

## 2. Online Geçiş Gereksinimleri

### 2.1 E-Ticaret Platformu Seçimi

| Platform | Avantajlar | Dezavantajlar |
|---|---|---|
| **Shopify** | Hızlı kurulum, geniş eklenti ekosistemi, güvenilir altyapı | Aylık abonelik maliyeti, işlem komisyonu, Türkçe destek sınırlı |
| **WooCommerce (WordPress)** | Açık kaynak, düşük başlangıç maliyeti, tam özelleştirme | Teknik bilgi gerektirir, hosting/bakım sorumluluğu sizde |
| **Trendyol / Hepsiburada Mağaza** | Hazır trafik, güven algısı, entegre kargo | Yüksek komisyon oranları, marka bağımsızlığı düşük, fiyat rekabeti baskısı |

**Öneri:** MVP aşamasında **WooCommerce** ile kendi mağazanızı kurup, paralelde **Trendyol** üzerinden pazar yeri görünürlüğünden faydalanmak en dengeli stratejidir.

### 2.2 Ödeme Yöntemleri

- **Sanal POS:** iyzico veya PayTR entegrasyonu (kredi/banka kartı)
- **Havale/EFT:** Banka entegrasyonu ile otomatik onay
- **Kapıda Ödeme:** İlk dönemde güven inşası için sunulmalı (belirli tutarın altında)
- **Mobil Cüzdan:** Papara, Tosla gibi alternatif yöntemler (genç kitle için)

### 2.3 Kargo ve Teslimat Çözümleri

| Yöntem | Kapsam | Not |
|---|---|---|
| **Anlaşmalı Kargo (Yurtiçi, Aras, MNG)** | Ülke geneli | Hacme göre fiyat anlaşması yapılmalı |
| **Kurye ile Aynı Gün Teslimat** | Şehir içi | Getir, Trendyol Go veya yerel kurye ile |
| **Mağazadan Teslim (Click & Collect)** | Yerel | Ek maliyet yok, müşteri trafiği artışı sağlar |

---

## 3. Teknik Karar Noktaları

### 3.1 Domain Stratejisi

- **Ana domain:** `[markaadi].com.tr` formatında tescil edilmeli
- **SSL sertifikası:** Zorunlu (güvenlik ve SEO için)
- **Alt alan adı:** `shop.markaadi.com.tr` veya doğrudan ana domain üzerinden mağaza

### 3.2 Ürün Kataloğu Yönetimi

- Her ürün için profesyonel fotoğraf (minimum 3 açı)
- Net gramaj/adet bilgisi, menşei, tat profili açıklaması
- Kategori yapısı: Çekirdek Kahve → Öğütülmüş Kahve → Ekipman → Aksesuar
- SEO uyumlu ürün başlıkları ve açıklamaları

### 3.3 Stok Yönetimi

- Fiziksel mağaza ve online mağaza stokları **tek havuzda** izlenmeli
- Minimum stok seviyesi alarmları tanımlanmalı
- Barkod/SKU sistemi oluşturulmalı
- Başlangıçta Excel tabanlı takip yeterli; büyüme ile birlikte ERP entegrasyonuna geçilmeli

---

## 4. Risk Analizi

| # | Risk Adı | Etki | Olasılık | Azaltma Stratejisi |
|---|---|---|---|---|
| 1 | **Kargo sürecinde ürün hasarı** (özellikle cam ekipman, öğütücü) | Kritik | Orta | Özel kahve ambalajı tasarımı, kırılacak ürünler için sigortalı kargo, hasar durumunda koşulsuz iade politikası |
| 2 | **Düşük online trafik ve dönüşüm oranı** | Yüksek | Yüksek | Mevcut müşteri tabanına e-posta/SMS kampanyası, sosyal medya içerik stratejisi, Google My Business optimizasyonu, ilk sipariş indirimi |
| 3 | **Stok uyumsuzluğu** (fiziksel ve online satışlar arası senkronizasyon hatası) | Yüksek | Orta | Tek stok havuzu kullanımı, günlük stok mutabakatı, kritik ürünlerde online stok tamponu bırakma |
| 4 | **Fiyat rekabeti baskısı** (büyük zincir ve pazar yeri satıcıları) | Orta | Yüksek | Niş ürün pozisyonlaması (single origin, özel kavurma), hikaye anlatımı ile marka farklılaştırma, fiyat yerine değer odaklı pazarlama |
| 5 | **Teknik altyapı sorunları** (site çökmesi, ödeme hataları) | Kritik | Düşük | Güvenilir hosting seçimi, düzenli yedekleme, ödeme altyapısı için iki alternatif entegrasyon, 7/24 uptime izleme |

---

## 5. Yol Haritası

### Faz 1 — MVP (Ay 1–2)

- Domain tescili ve hosting kurulumu
- WooCommerce mağaza kurulumu (temel tema)
- 15–20 temel ürünün kataloga eklenmesi
- iyzico ödeme entegrasyonu
- Tek kargo firması anlaşması
- Google Analytics ve Facebook Pixel kurulumu
- Mevcut müşterilere lansman duyurusu

**Hedef:** İlk online siparişin alınması, temel altyapının çalışır duruma gelmesi.

### Faz 2 — Genişleme (Ay 3–6)

- Ürün kataloğunun genişletilmesi (abonelik kutuları, hediye paketleri)
- Trendyol / Hepsiburada mağaza açılışı
- Sosyal medya reklam kampanyaları başlatma
- Blog içerik stratejisi (SEO amaçlı: demleme rehberleri, kahve kültürü)
- İkinci kargo firması entegrasyonu
- Müşteri yorumları ve puanlama sistemi

**Hedef:** Aylık düzenli sipariş hacmine ulaşmak, marka bilinirliğini şehir dışına taşımak.

### Faz 3 — Optimizasyon (Ay 7–12)

- Dönüşüm oranı optimizasyonu (A/B test, sepet terk e-postaları)
- Kahve abonelik modeli lansmanı (haftalık/aylık otomatik teslimat)
- Stok yönetimi için ERP entegrasyonu
- Müşteri sadakat programı
- Mobil uygulama değerlendirmesi
- Kurumsal satış kanalı açılması (ofislere toplu kahve)

**Hedef:** Karlılık optimizasyonu, tekrar eden gelir modeline geçiş, operasyonel verimlilik.

---

*Bu analiz, küçük ölçekli bir kahve dükkanının online satış kanalına geçişi için hazırlanmış stratejik bir yol haritası niteliğindedir.*
