# ProfileCard Component Specification

> **Versiyon:** 1.0.0  
> **Son Güncelleme:** 2026-03-04  
> **Durum:** Draft  
> **Uyumluluk:** WCAG 2.1 AA

---

## ProfileCard

**Amaç:** Kullanıcı profil bilgilerini kompakt kart formatında gösteren bileşen. Avatar, kullanıcı adı, rol/başlık ve aksiyonlar gibi temel profil öğelerini tutarlı bir düzen içinde sunar.

### Anatomisi

```
┌─────────────────────────────────┐
│  ┌──────┐                       │
│  │Avatar│  Kullanıcı Adı        │
│  │      │  Rol / Başlık         │
│  └──────┘  Konum (opsiyonel)    │
│                                 │
│  Bio açıklaması (opsiyonel)     │
│                                 │
│  [Aksiyon 1]   [Aksiyon 2]     │
└─────────────────────────────────┘
```

---

### Varyantlar

| Varyant | Açıklama | Kullanım |
|---------|----------|----------|
| **default** | Avatar, ad, rol ve tek seviye aksiyon butonu içerir. Standart kart boyutunda (`320px` genişlik) render edilir. | Kullanıcı listeleri, yorum bölümleri, ekip sayfaları gibi genel kullanım alanları. |
| **compact** | Yalnızca avatar (küçük, `32px`) ve kullanıcı adını yan yana gösterir. Bio ve aksiyon alanları gizlenir. | Navbar, sidebar, mention dropdown, yorum satırları gibi dar alanlar. |
| **expanded** | Tüm profil alanlarını gösterir: büyük avatar (`96px`), ad, rol, konum, bio, istatistikler (takipçi/takip edilen/gönderi sayısı) ve birden fazla aksiyon butonu. | Profil detay sayfaları, modal profil görünümleri, kullanıcı hover card'ları. |

---

### Props

| Prop | Tip | Zorunlu | Varsayılan | Açıklama |
|------|-----|---------|------------|----------|
| `variant` | `'default' \| 'compact' \| 'expanded'` | Hayır | `'default'` | Kart varyantını belirler. |
| `avatarUrl` | `string` | Hayır | `undefined` | Avatar görseli URL'i. Yoksa initials fallback kullanılır. |
| `name` | `string` | Evet | — | Kullanıcının görünen adı. |
| `role` | `string` | Hayır | `undefined` | Kullanıcının rolü veya başlığı. |
| `location` | `string` | Hayır | `undefined` | Konum bilgisi (yalnızca `expanded` varyantında gösterilir). |
| `bio` | `string` | Hayır | `undefined` | Kısa biyografi (yalnızca `default` ve `expanded` varyantlarında gösterilir). |
| `stats` | `{ followers: number; following: number; posts: number }` | Hayır | `undefined` | İstatistikler (yalnızca `expanded` varyantında gösterilir). |
| `actions` | `ActionItem[]` | Hayır | `[]` | Aksiyon butonları listesi. |
| `disabled` | `boolean` | Hayır | `false` | Kartın etkileşimsiz durumunu aktifleştirir. |
| `onClick` | `() => void` | Hayır | `undefined` | Karta tıklama handler'ı. Tanımlanırsa kart tıklanabilir olur. |

---

### Design Tokens

#### Renkler

| Token | Değer (Light) | Değer (Dark) | Kullanım |
|-------|---------------|--------------|----------|
| `--profile-card-color-primary` | `#1A1A2E` | `#F0F0F5` | Kullanıcı adı, başlık metni |
| `--profile-card-color-secondary` | `#6B7280` | `#9CA3AF` | Rol, konum, istatistik etiketi |
| `--profile-card-color-border` | `#E5E7EB` | `#374151` | Kart kenar çizgisi |
| `--profile-card-color-background` | `#FFFFFF` | `#1F2937` | Kart arka planı |
| `--profile-card-color-background-hover` | `#F9FAFB` | `#263043` | Hover durumunda arka plan |
| `--profile-card-color-accent` | `#3B82F6` | `#60A5FA` | Aksiyon butonları, focus ring |
| `--profile-card-color-disabled` | `#D1D5DB` | `#4B5563` | Disabled durumunda metin ve border |

#### Tipografi

| Token | Değer | Kullanım |
|-------|-------|----------|
| `--profile-card-font-heading` | `600 16px/1.25 'Inter', sans-serif` | Kullanıcı adı (`expanded` varyantında `600 20px/1.3`) |
| `--profile-card-font-body` | `400 14px/1.5 'Inter', sans-serif` | Bio, konum metni |
| `--profile-card-font-caption` | `500 12px/1.4 'Inter', sans-serif` | Rol, istatistik etiketi, tarih bilgisi |

#### Spacing

| Token | Değer | Kullanım |
|-------|-------|----------|
| `--profile-card-padding` | `16px` (`compact`: `8px 12px`) | Kart iç boşluğu |
| `--profile-card-gap` | `12px` (`compact`: `8px`) | Elemanlar arası dikey boşluk |
| `--profile-card-avatar-gap` | `12px` | Avatar ile metin bloğu arası yatay boşluk |
| `--profile-card-margin` | `0` | Dış boşluk (container tarafından yönetilir) |

#### Border & Shadow

| Token | Değer | Kullanım |
|-------|-------|----------|
| `--profile-card-border-radius` | `12px` (`compact`: `8px`) | Kart köşe yuvarlama |
| `--profile-card-border-width` | `1px` | Kenar çizgisi kalınlığı |
| `--profile-card-shadow` | `0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)` | Varsayılan gölge |
| `--profile-card-shadow-hover` | `0 4px 12px rgba(0,0,0,0.12), 0 2px 4px rgba(0,0,0,0.08)` | Hover gölgesi |
| `--profile-card-avatar-radius` | `50%` | Avatar yuvarlama (dairesel) |

---

### States

| State | Görsel Davranış | Açıklama |
|-------|----------------|----------|
| **Default** | Düz arka plan (`background`), `1px` solid border, varsayılan shadow. Metin renkleri standart token değerlerinde. | Kartın başlangıç durumu. Etkileşim bekleniyor. |
| **Hover** | Arka plan `background-hover` rengine geçer. Shadow `shadow-hover` değerine yükselir. Geçiş süresi `150ms ease-in-out`. İmleç `pointer` olur (tıklanabilirse). | Kullanıcı fare ile kartın üzerine geldiğinde. Yalnızca `onClick` tanımlıysa aktif olur. |
| **Active** | Arka plan `background-hover` üzerine `opacity: 0.95` uygulanır. Shadow varsayılana geri döner. Kart `scale(0.98)` ile hafifçe küçülür. Geçiş süresi `50ms`. | Kullanıcı karta bas-tıkla anında. Fiziksel geri bildirim sağlar. |
| **Disabled** | Tüm metinler `color-disabled` değerine döner. Border `color-disabled`. Arka plan `background` kalır. `opacity: 0.6` uygulanır. Shadow kaldırılır. İmleç `not-allowed`. | `disabled={true}` olduğunda. Tüm pointer event'ler devre dışı kalır. |
| **Focus** | `3px` solid outline, renk `color-accent`, offset `2px`. Border değişmez. Gölge ve arka plan default kalır. | Klavye ile navigate edildiğinde (`:focus-visible`). Mouse focus'ta outline gösterilmez. |

---

### Erişilebilirlik

#### ARIA Rolleri ve Attribute'ları

| Özellik | Değer | Koşul |
|---------|-------|-------|
| `role` | `article` | Her zaman. Kart bağımsız bir içerik bloğunu temsil eder. |
| `role` | `button` | `onClick` prop'u tanımlıysa `article` yerine kullanılır. |
| `aria-label` | `"{name} profil kartı"` | Her zaman. Screen reader'lar için açıklayıcı etiket. |
| `aria-disabled` | `"true"` | `disabled={true}` olduğunda. |
| `tabindex` | `0` | Kart tıklanabilirse. Klavye erişimi sağlar. |
| `tabindex` | `-1` | Kart disabled ise. Focus sırasından çıkarılır. |

#### Klavye Navigasyonu

| Tuş | Davranış |
|-----|----------|
| `Tab` | Karta focus verir (tıklanabilir ise). Sonraki Tab kart içindeki aksiyon butonlarına geçer. |
| `Enter` / `Space` | `onClick` handler'ını tetikler (kart tıklanabilir ise). |
| `Escape` | Eğer kart bir popover/modal içindeyse kapatma işlemini tetikler. |

#### Kontrast Oranları (WCAG 2.1 AA)

| Eleman | Ön Plan | Arka Plan | Oran | Minimum | Durum |
|--------|---------|-----------|------|---------|-------|
| Kullanıcı adı (light) | `#1A1A2E` | `#FFFFFF` | **15.4:1** | 4.5:1 | Geçer |
| Kullanıcı adı (dark) | `#F0F0F5` | `#1F2937` | **13.1:1** | 4.5:1 | Geçer |
| Rol/caption (light) | `#6B7280` | `#FFFFFF` | **5.0:1** | 4.5:1 | Geçer |
| Rol/caption (dark) | `#9CA3AF` | `#1F2937` | **5.8:1** | 4.5:1 | Geçer |
| Disabled metin (light) | `#D1D5DB` | `#FFFFFF` | **1.8:1** | — | Beklenen (disabled) |
| Focus ring | `#3B82F6` | `#FFFFFF` | **4.7:1** | 3:1 (UI) | Geçer |

#### Screen Reader Desteği

- Avatar görseli `alt="{name} profil fotoğrafı"` attribute'u taşır. Avatar yoksa `alt` boş bırakılır (`""`) ve dekoratif olarak işaretlenir (`aria-hidden="true"` initials fallback'te).
- İstatistik bloğu `aria-label="İstatistikler: {followers} takipçi, {following} takip edilen, {posts} gönderi"` ile gruplanır.
- Aksiyon butonları kendi `aria-label` değerlerini taşır (ör. `"Takip et"`, `"Mesaj gönder"`).
- `compact` varyantında gizlenen alanlar DOM'dan kaldırılır (yalnızca CSS gizleme değil), screen reader'ların gereksiz içerik okumasını engeller.

---

### Responsive Davranış

| Breakpoint | Davranış |
|------------|----------|
| `≥ 768px` | Kart `320px` sabit genişlik (grid/flex container içinde). |
| `< 768px` | Kart `100%` genişliğe açılır. `expanded` varyantında istatistikler yataydan dikeye geçer. |
| `< 480px` | `default` varyant otomatik olarak `compact` davranışına geçer (opsiyonel, `responsive` prop ile kontrol edilir). |

---

### Uygulama Notu

#### React

```tsx
import { ProfileCard } from '@/components/ProfileCard';

// Default varyant
<ProfileCard
  name="Melih Kayam"
  role="Senior UI Designer"
  avatarUrl="/avatars/melih.jpg"
  bio="Kullanıcı deneyimi ve erişilebilirlik odaklı tasarım."
  actions={[
    { label: 'Takip Et', onClick: handleFollow, variant: 'primary' },
    { label: 'Mesaj', onClick: handleMessage, variant: 'secondary' },
  ]}
  onClick={handleCardClick}
/>

// Compact varyant
<ProfileCard
  variant="compact"
  name="Melih Kayam"
  role="Senior UI Designer"
  avatarUrl="/avatars/melih.jpg"
/>

// Expanded varyant
<ProfileCard
  variant="expanded"
  name="Melih Kayam"
  role="Senior UI Designer"
  avatarUrl="/avatars/melih.jpg"
  location="İstanbul, Türkiye"
  bio="Kullanıcı deneyimi ve erişilebilirlik odaklı tasarım."
  stats={{ followers: 1240, following: 380, posts: 56 }}
  actions={[
    { label: 'Takip Et', onClick: handleFollow, variant: 'primary' },
    { label: 'Mesaj', onClick: handleMessage, variant: 'secondary' },
  ]}
/>

// Disabled durumu
<ProfileCard
  name="Silinmiş Kullanıcı"
  role="—"
  disabled
/>
```

#### SwiftUI

```swift
import SwiftUI

// Default varyant
ProfileCard(
    name: "Melih Kayam",
    role: "Senior UI Designer",
    avatarURL: URL(string: "https://example.com/avatars/melih.jpg"),
    bio: "Kullanıcı deneyimi ve erişilebilirlik odaklı tasarım.",
    actions: [
        .init(label: "Takip Et", style: .primary, action: { followUser() }),
        .init(label: "Mesaj", style: .secondary, action: { openChat() })
    ]
)

// Compact varyant
ProfileCard(
    variant: .compact,
    name: "Melih Kayam",
    role: "Senior UI Designer",
    avatarURL: URL(string: "https://example.com/avatars/melih.jpg")
)

// Expanded varyant
ProfileCard(
    variant: .expanded,
    name: "Melih Kayam",
    role: "Senior UI Designer",
    avatarURL: URL(string: "https://example.com/avatars/melih.jpg"),
    location: "İstanbul, Türkiye",
    bio: "Kullanıcı deneyimi ve erişilebilirlik odaklı tasarım.",
    stats: .init(followers: 1240, following: 380, posts: 56),
    actions: [
        .init(label: "Takip Et", style: .primary, action: { followUser() }),
        .init(label: "Mesaj", style: .secondary, action: { openChat() })
    ]
)
.accessibilityElement(children: .contain)
.accessibilityLabel("Melih Kayam profil kartı")

// Disabled durumu
ProfileCard(
    name: "Silinmiş Kullanıcı",
    role: "—",
    isDisabled: true
)
.disabled(true)
```

---

### Dosya Yapısı (Önerilen)

```
components/
└── ProfileCard/
    ├── ProfileCard.tsx          # Ana bileşen
    ├── ProfileCard.types.ts     # Tip tanımları
    ├── ProfileCard.styles.ts    # Styled-components / CSS modules
    ├── ProfileCard.stories.tsx  # Storybook hikayeleri
    ├── ProfileCard.test.tsx     # Test dosyası
    ├── ProfileCardAvatar.tsx    # Alt bileşen: Avatar
    ├── ProfileCardStats.tsx     # Alt bileşen: İstatistikler
    ├── ProfileCardActions.tsx   # Alt bileşen: Aksiyon butonları
    └── index.ts                 # Barrel export
```
