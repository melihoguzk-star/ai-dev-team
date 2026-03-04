# Prompt Kalite Analizi: documentation-engineer.md

**Analiz Tarihi:** 2026-03-04
**Analiz Edilen Dosya:** `~/.claude/agents/documentation-engineer.md`
**Prompt Uzunluğu:** 297 satır

---

## 1. GENEL SKOR: 6.5 / 10

---

## 2. KRİTER PUANLARI

| # | Kriter | Puan | Açıklama |
|---|--------|------|----------|
| 1 | **Açıklık (Clarity)** | 7 | Rol tanımı ve genel amaç net ancak checklist maddelerinin çoğu bağlamsız anahtar kelime listeleri olarak kalmış, ne yapılacağı değil ne hakkında olduğu yazılmış. |
| 2 | **Yapılandırılmışlık (Structure)** | 6 | Üç fazlı iş akışı (Analysis → Implementation → Excellence) mantıklı bir iskelet sunuyor; ancak faz öncesindeki 10+ madde işaretli liste bloğu herhangi bir hiyerarşi veya öncelik sırası olmadan art arda dizilmiş, bu da okunabilirliği düşürüyor. |
| 3 | **Kapsam (Completeness)** | 8 | Dokümantasyon mühendisliğinin neredeyse tüm alt alanları (API docs, tutorial, search, versioning, contribution, testing) listelenmiş; kapsam oldukça geniş. |
| 4 | **Kısıtlamalar (Constraints)** | 5 | Sayfa yükleme süresi (<2s) ve WCAG AA gibi birkaç somut kısıt var ama çoğu alan için sınır tanımsız: maksimum sayfa sayısı, doküman başına hedef uzunluk, hangi durumlarda görevi reddetmesi gerektiği gibi kritik kısıtlar eksik. |
| 5 | **Çıktı Formatı (Output Format)** | 7 | Son bölümdeki dizin yapısı ve naming conventions iyi tanımlanmış; ancak her fazın sonunda beklenen ara çıktı formatı (örneğin analiz raporunun şablonu) belirtilmemiş. |
| 6 | **Token Verimliliği (Efficiency)** | 4 | En zayıf noktalardan biri. "Documentation architecture", "API documentation automation", "Tutorial creation" vb. bölümler birbirine benzer 8'er maddelik listeler halinde tekrar ediyor. Aynı kavramlar (search optimization, performance, analytics) en az 3-4 farklı yerde geçiyor. ~297 satırın yaklaşık %40'ı anlamlı bilgi tekrarı. |
| 7 | **Hata Dayanıklılığı (Robustness)** | 6 | "Hata dayanıklılığı" başlığı altında üç temel senaryo (dosya bulunamama, spec yokluğu, belirsiz gereksinim) ele alınmış; bu pozitif. Ancak büyük projeler, çakışan dokümanlar, dil/lokalizasyon hataları, izin sorunları gibi edge case'ler düşünülmemiş. |
| 8 | **Tutarlılık (Consistency)** | 9 | Terminoloji genel olarak tutarlı; İngilizce-Türkçe ayrımı son bölümde açıkça belirtilmiş ve prompt boyunca büyük ölçüde bu kurala uyulmuş. Küçük bir tutarsızlık: bazı başlıklar İngilizce iken "Hata dayanıklılığı" ve "ÇIKTI FORMATI" Türkçe. |

---

## 3. İYİLEŞTİRME ÖNERİLERİ (Öncelik Sırasıyla)

### Öneri 1: Madde Listelerini Daralt ve Eyleme Dönüştür (Token Verimliliği - Kritik)

**Sorun:** Prompt'un büyük kısmı bağlamsız anahtar kelime listeleri. "Search optimization" başlığı altında "Full-text search, Faceted search, Search analytics..." gibi 8 madde var ama LLM'e bunlarla ne yapması gerektiği söylenmiyor. Bu listeler çıktıyı yönlendirmekten çok token harcıyor.

**Öneri:** Her listeyi "ne zaman, ne yap" formatına dönüştür. Örneğin:

```markdown
## Search Optimization
API dokümantasyonu oluştururken:
- Full-text search yapılandırması ekle (Algolia veya built-in)
- Arama analitiğini CHANGELOG'a entegre et
```

Bu yaklaşım token sayısını ~%30 azaltırken talimat netliğini artırır.

### Öneri 2: Faz Çıktılarını Şablonla Tanımla (Çıktı Formatı - Yüksek)

**Sorun:** Her fazın sonunda ne teslim edileceği belirsiz. "Documentation Analysis" fazı bittikten sonra agent'ın üretmesi gereken ara çıktı (audit raporu, gap analizi) tanımlı değil.

**Öneri:** Her faz için beklenen çıktı şablonu ekle:

```markdown
### Faz 1 Çıktısı: Analiz Raporu
- Mevcut durum özeti (coverage %'si)
- Tespit edilen boşluklar listesi (öncelik sıralı)
- Önerilen aksiyon planı
```

### Öneri 3: Somut Kısıtlar ve Sınırlar Ekle (Kısıtlamalar - Yüksek)

**Sorun:** Agent'ın hangi durumlarda durup kullanıcıya danışması gerektiği, kapsam dışı talepleri nasıl ele alacağı belirtilmemiş.

**Öneri:** Şu kısıtları ekle:
- Mevcut kod yapısını değiştirme; yalnızca `/docs` dizini altında çalış
- 50+ sayfayı etkileyen değişikliklerde önce plan sun, onay al
- Mevcut dokümanların içeriğini silme; deprecate olarak işaretle
- Dış servis (analytics, CDN) yapılandırması önerirken kullanıcı onayı bekle

### Öneri 4: Tekrar Eden Bölümleri Birleştir (Token Verimliliği - Orta)

**Sorun:** "Documentation testing", "Documentation excellence checklist" ve "Continuous improvement" bölümlerinde "performance testing/monitoring", "search optimization", "feedback" kavramları tekrar ediyor.

**Öneri:** Bu üç bölümü tek bir "Kalite Güvence ve Sürekli İyileştirme" bölümünde birleştir.

### Öneri 5: Progress Tracking Örneğini Dinamikleştir (Hata Dayanıklılığı - Orta)

**Sorun:** Progress tracking JSON bloğunda sabit değerler var (`"pages_created": 147`). Bu, agent'ın bu değerleri hedef olarak algılamasına veya her projede aynı sayıları raporlamasına yol açabilir.

**Öneri:** Placeholder formatına çevir:

```json
{
  "pages_created": "<gerçek sayı>",
  "api_coverage": "<hesaplanan %>",
  "search_queries_resolved": "<ölçülen %>"
}
```

---

## 4. GÜÇLÜ YÖNLER

1. **Kapsamlı alan haritası:** Dokümantasyon mühendisliğinin neredeyse tüm alt disiplinleri (API docs, tutorial, search, versioning, contribution workflow, testing, localization) tek bir prompt'ta ele alınmış. Bu, agent'ın geniş bir yelpazede görev alabilmesini sağlıyor.

2. **Hata dayanıklılığı farkındalığı:** Birçok agent prompt'unda tamamen ihmal edilen "kaynak bulunamazsa ne yap" senaryoları burada açıkça ele alınmış. `[TODO: ...]` ile taslak oluşturma yaklaşımı pratik ve kullanışlı.

3. **Çıktı dizin yapısı ve naming convention tanımı:** Son bölümdeki `/docs` dizin şablonu, kebab-case kuralı ve "1000+ kelime ise TOC ekle" gibi somut kurallar, agent'ın tutarlı çıktı üretmesini güçlü şekilde yönlendiriyor.

---

## ÖZET TABLO

| Metrik | Değer |
|--------|-------|
| **Genel Skor** | 6.5 / 10 |
| **En Yüksek Puan** | Tutarlılık (9) |
| **En Düşük Puan** | Token Verimliliği (4) |
| **İyileştirme Önerisi Sayısı** | 5 |
| **Tahmini Token Tasarrufu (Öneriler Uygulanırsa)** | ~%25-35 |
