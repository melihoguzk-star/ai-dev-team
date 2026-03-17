# web-analyzer Memory
Son güncelleme: 2026-03-05

## Convention'lar
- HTML çıktı dosya adı: 01-site-analysis.html (proje klasörüne yazılır)
- Proje klasörü: ~/ai-dev-team/projects/[proje-adi]/
- Tüm bölümler sidebar'da menü öğesi olarak listelenmeli
- Kartlar varsayılan olarak expanded (display:block) gelir
- Tahmin edilen bilgiler warn-box veya "Tahmin" etiketi ile işaretlenir

## Hatalar ve Çözümler
- WebFetch bu ortamda devre dışı: WebSearch ile çoklu sorgu kombinasyonu kullan
- Grep tool'da file_path parametresi desteklenmiyor, path kullanılmalı
- Paralel tool çağrılarında biri hata verirse diğeri de iptal olur — bağımsız çağrıları dikkatli yönet

## Kahve Dünyası Projesi Tespitleri
- TR site: kahvedunyasi.com | UK site: kahvedunyasi.co.uk
- Teknoloji stack: Vue.js + Vuex + Laravel/PHP + PostgreSQL + Google Cloud (tahmin)
- Mobil geliştirici partner: İnomera
- Push/CRM: Netmera Mobile Interaction Platform
- Loyalty: Çekirdek sistemi (1 Çekirdek = 1 TL), 6 Damga = ücretsiz kahve
- Mobil app iOS ID: 1364478029, Android: com.kahvedunyasi.app
- Mevcut iOS min: 14.0; yeni geliştirme iOS 17+ olacak
- UK'de mağaza: 200 Piccadilly, London W1J 9HU
- URL pattern: /urun/[slug]-p-[id], /[kategori]-c-[id]
- Kritik UK riski: API altyapısının UK için mevcut olup olmadığı belirsiz

## Tercihler
- Kullanıcı "professional görünümlü" ve "Türkçe" HTML istiyor
- UK adaptasyon notu her ilgili bölümde note-box veya warn-box ile belirtilmeli
- Riskler severity badge'leri (Kritik, Yüksek, Orta, Düşük) ile gösterilmeli
- Self-validation checklist üretimden sonra Grep ile doğrulanmalı
