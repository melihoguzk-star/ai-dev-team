# iOS UI/UX Donusum Dokumani — Login Sayfasi

> **Kaynak:** Web Login Sayfasi (Email + Sifre + Hatirla Beni + Giris Butonu)
> **Hedef Platform:** iOS 17+ / SwiftUI
> **HIG Uyumu:** Apple Human Interface Guidelines (2024)

---

## 1. Component Hierarchy

Web bilesenlerinin iOS/SwiftUI karsiliklarina eslenme agaci:

```
LoginView (Ana Ekran)
├── VStack (Ana icerik konteyneri)
│   ├── AppLogoView
│   │   └── Image (Uygulama logosu)
│   ├── Text (Baslik — "Giris Yap")
│   ├── Text (Alt baslik — "Hesabiniza giris yapin")
│   ├── VStack (Form alanlari)
│   │   ├── EmailTextField
│   │   │   ├── Text (Label — "E-posta")
│   │   │   └── TextField (Web text input → iOS TextField)
│   │   ├── PasswordSecureField
│   │   │   ├── Text (Label — "Sifre")
│   │   │   └── SecureField (Web password input → iOS SecureField)
│   │   └── RememberMeToggle
│   │       ├── Toggle (Web checkbox → iOS Toggle)
│   │       └── Text (Label — "Beni Hatirla")
│   ├── LoginButton
│   │   └── Button (Web submit button → iOS Button)
│   └── FooterLinksView
│       ├── Button ("Sifremi Unuttum")
│       └── Button ("Kayit Ol")
```

### Bilesen Eslestirme Tablosu

| Web Bileseni        | iOS/SwiftUI Karsiligi | Notlar                                      |
|----------------------|------------------------|----------------------------------------------|
| `<input type="text">` | `TextField`           | `.textContentType(.emailAddress)` ile        |
| `<input type="password">` | `SecureField`    | Otomatik gizleme, `.textContentType(.password)` |
| `<input type="checkbox">` | `Toggle`         | HIG uyumlu switch stili                      |
| `<button type="submit">` | `Button`          | `.buttonStyle(.borderedProminent)` ile       |
| `<form>`             | `Form` veya `VStack`   | SwiftUI Form yapilandirilmis goruntuleme     |

---

## 2. Ekran Listesi

| # | SwiftUI View Adi         | Aciklama                                    | Tur             |
|---|--------------------------|----------------------------------------------|-----------------|
| 1 | `LoginView`              | Ana giris ekrani, tum bilesenleri icerir     | Screen (Root)   |
| 2 | `EmailTextField`         | E-posta girisi icin ozel TextField bileseni  | Component       |
| 3 | `PasswordSecureField`    | Sifre girisi icin SecureField bileseni       | Component       |
| 4 | `RememberMeToggle`       | Hatirla beni secenegi icin Toggle bileseni   | Component       |
| 5 | `LoginButton`            | Giris butonu bileseni                        | Component       |
| 6 | `AppLogoView`            | Uygulama logosu goruntuleme bileseni         | Component       |
| 7 | `FooterLinksView`        | Alt kisim navigasyon linkleri                | Component       |

---

## 3. Tasarim Token'lari

### 3.1 Renkler

iOS system renkleri kullanilarak HIG uyumu saglanir:

```swift
// MARK: - Color Tokens
extension Color {
    enum Login {
        // Birincil renkler
        static let primaryAction = Color.accentColor          // Giris butonu
        static let primaryText = Color(.label)                // Ana metin
        static let secondaryText = Color(.secondaryLabel)     // Alt baslik, ipucu metni

        // Arka plan renkleri
        static let background = Color(.systemBackground)      // Ekran arka plani
        static let fieldBackground = Color(.secondarySystemBackground) // TextField arka plani
        static let groupedBackground = Color(.systemGroupedBackground)

        // Durum renkleri
        static let error = Color.red                          // Hata mesajlari
        static let success = Color.green                      // Basarili islem
        static let disabled = Color(.quaternaryLabel)         // Devre disi durumu

        // Cizgi ve sinir renkleri
        static let border = Color(.separator)                 // Alan sinirlari
        static let focusBorder = Color.accentColor            // Odaklanma durumu
    }
}
```

### 3.2 Tipografi

iOS Dynamic Type destegi ile:

```swift
// MARK: - Typography Tokens
enum LoginTypography {
    // Baslik — ekran basliginda kullanilir
    static let title: Font = .largeTitle.bold()               // 34pt, Bold

    // Alt baslik — aciklama metni
    static let subtitle: Font = .subheadline                  // 15pt, Regular

    // Alan etiketi — TextField/SecureField label
    static let fieldLabel: Font = .subheadline.weight(.medium) // 15pt, Medium

    // Alan ici metin — kullanici girisi
    static let fieldInput: Font = .body                       // 17pt, Regular

    // Alan ici ipucu — placeholder metni
    static let fieldPlaceholder: Font = .body                 // 17pt, Regular (secondaryLabel)

    // Buton metni — Giris butonu
    static let buttonLabel: Font = .headline                  // 17pt, Semibold

    // Alt link — Sifremi unuttum, Kayit Ol
    static let footerLink: Font = .footnote                   // 13pt, Regular
}
```

### 3.3 Spacing & Layout

```swift
// MARK: - Spacing Tokens
enum LoginSpacing {
    // Genel ekran kenar boslugu (HIG: 16-20pt onerisi)
    static let horizontalPadding: CGFloat = 20

    // Bilesenler arasi dikey bosluk
    static let sectionSpacing: CGFloat = 32       // Bolumler arasi
    static let fieldSpacing: CGFloat = 16         // Alanlar arasi
    static let labelToFieldSpacing: CGFloat = 6   // Etiket → alan arasi
    static let inlineSpacing: CGFloat = 8         // Satir ici oge arasi

    // Buton boyutlari (HIG: minimum 44pt dokunma alani)
    static let buttonHeight: CGFloat = 50
    static let buttonCornerRadius: CGFloat = 12

    // TextField boyutlari
    static let fieldHeight: CGFloat = 48
    static let fieldCornerRadius: CGFloat = 10
    static let fieldInternalPadding: CGFloat = 12

    // Logo
    static let logoSize: CGFloat = 80
    static let logoTopPadding: CGFloat = 60
    static let logoBottomPadding: CGFloat = 24
}
```

### 3.4 Minimum Dokunma Alani

Apple HIG gerekliligi: Tum interaktif bilesenlerin minimum **44x44 pt** dokunma alanina sahip olmasi zorunludur.

```swift
// Tum buton ve toggle bilesenleri bu minimum boyutu karsilamalidir
// .frame(minHeight: 44) veya yeterli padding ile saglanir
```

---

## 4. Component Detaylari — SwiftUI Kod Taslaklari

### 4.1 EmailTextField

Web `<input type="email">` bileseninin iOS karsiligi. `textContentType(.emailAddress)` ile AutoFill destegi saglanir.

```swift
import SwiftUI

/// E-posta girisi icin ozel TextField bileseni.
/// Web'deki `<input type="email">` bileseninin iOS karsiligi.
///
/// Ozellikler:
/// - Otomatik e-posta klavyesi (.emailAddress)
/// - AutoFill destegi (.textContentType(.emailAddress))
/// - Hata durumu gosterimi
/// - iOS HIG uyumlu minimum 44pt dokunma alani
struct EmailTextField: View {
    @Binding var email: String
    var errorMessage: String?

    @FocusState private var isFocused: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: LoginSpacing.labelToFieldSpacing) {
            // Alan etiketi
            Text("E-posta")
                .font(LoginTypography.fieldLabel)
                .foregroundStyle(Color.Login.primaryText)

            // Email TextField
            TextField("ornek@email.com", text: $email)
                .font(LoginTypography.fieldInput)
                .textContentType(.emailAddress)       // AutoFill destegi
                .keyboardType(.emailAddress)           // E-posta klavyesi
                .textInputAutocapitalization(.never)   // Otomatik buyuk harf kapali
                .autocorrectionDisabled(true)          // Otomatik duzeltme kapali
                .focused($isFocused)
                .padding(LoginSpacing.fieldInternalPadding)
                .frame(height: LoginSpacing.fieldHeight)
                .background(Color.Login.fieldBackground)
                .clipShape(RoundedRectangle(cornerRadius: LoginSpacing.fieldCornerRadius))
                .overlay(
                    RoundedRectangle(cornerRadius: LoginSpacing.fieldCornerRadius)
                        .stroke(borderColor, lineWidth: 1)
                )

            // Hata mesaji (varsa)
            if let errorMessage {
                Text(errorMessage)
                    .font(.caption)
                    .foregroundStyle(Color.Login.error)
            }
        }
    }

    /// Odaklanma ve hata durumuna gore sinir rengini belirler.
    private var borderColor: Color {
        if errorMessage != nil {
            return Color.Login.error
        }
        return isFocused ? Color.Login.focusBorder : Color.Login.border
    }
}

// MARK: - Preview
#Preview {
    EmailTextField(email: .constant(""), errorMessage: nil)
        .padding()
}
```

---

### 4.2 PasswordSecureField

Web `<input type="password">` bileseninin iOS karsiligi. `SecureField` ile otomatik metin gizleme saglanir.

```swift
import SwiftUI

/// Sifre girisi icin SecureField bileseni.
/// Web'deki `<input type="password">` bileseninin iOS karsiligi.
///
/// Ozellikler:
/// - Otomatik metin gizleme (SecureField)
/// - Sifre goster/gizle secenegi
/// - AutoFill destegi (.textContentType(.password))
/// - iOS HIG uyumlu minimum dokunma alani
struct PasswordSecureField: View {
    @Binding var password: String
    var errorMessage: String?

    @State private var isPasswordVisible = false
    @FocusState private var isFocused: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: LoginSpacing.labelToFieldSpacing) {
            // Alan etiketi
            Text("Sifre")
                .font(LoginTypography.fieldLabel)
                .foregroundStyle(Color.Login.primaryText)

            // Sifre alani — goster/gizle destegi ile
            HStack(spacing: LoginSpacing.inlineSpacing) {
                Group {
                    if isPasswordVisible {
                        TextField("Sifrenizi girin", text: $password)
                            .textContentType(.password)
                    } else {
                        SecureField("Sifrenizi girin", text: $password)
                            .textContentType(.password)
                    }
                }
                .font(LoginTypography.fieldInput)
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled(true)
                .focused($isFocused)

                // Goster/Gizle butonu
                Button {
                    isPasswordVisible.toggle()
                } label: {
                    Image(systemName: isPasswordVisible ? "eye.slash.fill" : "eye.fill")
                        .foregroundStyle(Color.Login.secondaryText)
                        .frame(minWidth: 44, minHeight: 44) // HIG minimum dokunma alani
                }
                .buttonStyle(.plain)
            }
            .padding(.horizontal, LoginSpacing.fieldInternalPadding)
            .frame(height: LoginSpacing.fieldHeight)
            .background(Color.Login.fieldBackground)
            .clipShape(RoundedRectangle(cornerRadius: LoginSpacing.fieldCornerRadius))
            .overlay(
                RoundedRectangle(cornerRadius: LoginSpacing.fieldCornerRadius)
                    .stroke(borderColor, lineWidth: 1)
                )

            // Hata mesaji (varsa)
            if let errorMessage {
                Text(errorMessage)
                    .font(.caption)
                    .foregroundStyle(Color.Login.error)
            }
        }
    }

    private var borderColor: Color {
        if errorMessage != nil {
            return Color.Login.error
        }
        return isFocused ? Color.Login.focusBorder : Color.Login.border
    }
}

#Preview {
    PasswordSecureField(password: .constant(""), errorMessage: nil)
        .padding()
}
```

---

### 4.3 RememberMeToggle

Web `<input type="checkbox">` bileseninin iOS karsiligi. HIG standartlarina uygun olarak `Toggle` kullanilir (checkbox yerine switch).

```swift
import SwiftUI

/// Hatirla beni secenegi icin Toggle bileseni.
/// Web'deki `<input type="checkbox">` bileseninin iOS karsiligi.
///
/// Ozellikler:
/// - iOS native Toggle (switch) stili
/// - HIG uyumlu: iOS'ta checkbox yerine switch kullanilir
/// - Minimum 44pt dokunma alani
/// - UserDefaults ile durum kaliciligi destegi
struct RememberMeToggle: View {
    @Binding var isRememberMeOn: Bool

    var body: some View {
        Toggle(isOn: $isRememberMeOn) {
            Text("Beni Hatirla")
                .font(LoginTypography.fieldLabel)
                .foregroundStyle(Color.Login.primaryText)
        }
        .toggleStyle(.switch)     // iOS standart switch stili
        .tint(Color.accentColor)  // Aktif durum rengi
        .padding(.vertical, 4)   // Minimum dokunma alani destegi
    }
}

#Preview {
    RememberMeToggle(isRememberMeOn: .constant(true))
        .padding()
}
```

---

### 4.4 LoginButton

Web `<button type="submit">` bileseninin iOS karsiligi. Yukleniyor durumu ve devre disi durumu desteklenir.

```swift
import SwiftUI

/// Giris butonu bileseni.
/// Web'deki `<button type="submit">` bileseninin iOS karsiligi.
///
/// Ozellikler:
/// - Tam genislikte tasarim (.frame(maxWidth: .infinity))
/// - Yukleniyor durumu (ProgressView spinner)
/// - Devre disi durumu (bos alanlar icin)
/// - HIG uyumlu minimum 44pt yukseklik
/// - Haptic feedback destegi
struct LoginButton: View {
    let action: () -> Void
    var isLoading: Bool = false
    var isDisabled: Bool = false

    var body: some View {
        Button(action: triggerAction) {
            HStack(spacing: LoginSpacing.inlineSpacing) {
                if isLoading {
                    ProgressView()
                        .tint(.white)
                } else {
                    Text("Giris Yap")
                        .font(LoginTypography.buttonLabel)
                }
            }
            .frame(maxWidth: .infinity)
            .frame(height: LoginSpacing.buttonHeight)
            .foregroundStyle(.white)
            .background(buttonBackground)
            .clipShape(RoundedRectangle(cornerRadius: LoginSpacing.buttonCornerRadius))
        }
        .disabled(isDisabled || isLoading)
    }

    private var buttonBackground: Color {
        (isDisabled || isLoading)
            ? Color.Login.disabled
            : Color.Login.primaryAction
    }

    private func triggerAction() {
        // Haptic feedback — iOS kullanici deneyimi icin
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()
        action()
    }
}

#Preview {
    VStack(spacing: 16) {
        LoginButton(action: {}, isLoading: false, isDisabled: false)
        LoginButton(action: {}, isLoading: true, isDisabled: false)
        LoginButton(action: {}, isLoading: false, isDisabled: true)
    }
    .padding()
}
```

---

### 4.5 LoginView — Ana Ekran (Tum Bilesenlerin Birlesimi)

Tum bilesenlerin bir arada kullanildigi ana giris ekrani:

```swift
import SwiftUI

/// Ana giris ekrani.
/// Tum bilesenleri bir araya getirerek tam islevsel bir login akisi saglar.
///
/// Ozellikler:
/// - Keyboard dismiss destegi (arka plana dokunma)
/// - Form dogrulama (email ve sifre bos kontrolu)
/// - Yukleniyor durumu yonetimi
/// - Dynamic Type ve Dark Mode destegi
/// - ScrollView ile kucuk ekran uyumu
struct LoginView: View {
    @State private var email = ""
    @State private var password = ""
    @State private var rememberMe = false
    @State private var isLoading = false
    @State private var emailError: String?
    @State private var passwordError: String?

    var body: some View {
        ScrollView {
            VStack(spacing: LoginSpacing.sectionSpacing) {
                // Logo
                AppLogoView()
                    .padding(.top, LoginSpacing.logoTopPadding)

                // Baslik
                VStack(spacing: 8) {
                    Text("Giris Yap")
                        .font(LoginTypography.title)
                        .foregroundStyle(Color.Login.primaryText)

                    Text("Hesabiniza giris yapin")
                        .font(LoginTypography.subtitle)
                        .foregroundStyle(Color.Login.secondaryText)
                }

                // Form alanlari
                VStack(spacing: LoginSpacing.fieldSpacing) {
                    EmailTextField(
                        email: $email,
                        errorMessage: emailError
                    )

                    PasswordSecureField(
                        password: $password,
                        errorMessage: passwordError
                    )

                    RememberMeToggle(
                        isRememberMeOn: $rememberMe
                    )
                }

                // Giris butonu
                LoginButton(
                    action: handleLogin,
                    isLoading: isLoading,
                    isDisabled: email.isEmpty || password.isEmpty
                )

                // Alt linkler
                FooterLinksView()
            }
            .padding(.horizontal, LoginSpacing.horizontalPadding)
        }
        .background(Color.Login.background)
        .onTapGesture {
            // Klavyeyi kapat — arka plana dokunuldiginda
            UIApplication.shared.sendAction(
                #selector(UIResponder.resignFirstResponder),
                to: nil, from: nil, for: nil
            )
        }
    }

    // MARK: - Actions

    private func handleLogin() {
        // Hata mesajlarini sifirla
        emailError = nil
        passwordError = nil

        // Basit dogrulama
        guard !email.isEmpty else {
            emailError = "E-posta alani bos birakilamaz"
            return
        }
        guard email.contains("@") else {
            emailError = "Gecerli bir e-posta adresi girin"
            return
        }
        guard !password.isEmpty else {
            passwordError = "Sifre alani bos birakilamaz"
            return
        }

        // Giris islemi baslat
        isLoading = true
        // TODO: Auth servisi cagrisi buraya eklenecek
    }
}

// MARK: - Yardimci Bilesenler

struct AppLogoView: View {
    var body: some View {
        Image(systemName: "person.circle.fill")
            .resizable()
            .scaledToFit()
            .frame(width: LoginSpacing.logoSize, height: LoginSpacing.logoSize)
            .foregroundStyle(Color.accentColor)
    }
}

struct FooterLinksView: View {
    var body: some View {
        VStack(spacing: 12) {
            Button("Sifremi Unuttum") {
                // TODO: Sifre sifirlama akisina yonlendir
            }
            .font(LoginTypography.footerLink)
            .foregroundStyle(Color.accentColor)

            HStack(spacing: 4) {
                Text("Hesabiniz yok mu?")
                    .font(LoginTypography.footerLink)
                    .foregroundStyle(Color.Login.secondaryText)
                Button("Kayit Ol") {
                    // TODO: Kayit ekranina yonlendir
                }
                .font(LoginTypography.footerLink.bold())
                .foregroundStyle(Color.accentColor)
            }
        }
    }
}

#Preview {
    LoginView()
}
```

---

## 5. iOS HIG Uyum Kontrol Listesi

| Kriter                                  | Durum | Aciklama                                                  |
|-----------------------------------------|-------|-----------------------------------------------------------|
| Minimum 44x44pt dokunma alani           | OK    | Tum buton ve interaktif alanlarda saglanmistir             |
| Dynamic Type destegi                    | OK    | System fontlari kullanilarak otomatik olcekleme            |
| Dark Mode destegi                       | OK    | `Color(.label)`, `Color(.systemBackground)` vb. kullanimi |
| AutoFill destegi                        | OK    | `.textContentType(.emailAddress)` ve `.password`           |
| Uygun klavye tipi                       | OK    | `.keyboardType(.emailAddress)` ile e-posta klavyesi        |
| Haptic feedback                         | OK    | Giris butonunda `UIImpactFeedbackGenerator`                |
| Hata durumu gosterimi                   | OK    | Kirmizi sinir + metin ile gorsel geri bildirim             |
| Odaklanma durumu (focus state)          | OK    | `@FocusState` ile aktif alan vurgulama                     |
| Klavye dismiss davranisi                | OK    | Arka plana dokunma ile klavye kapatma                      |
| ScrollView ile kucuk ekran destegi      | OK    | Kucuk cihazlarda icerik kaydirilabilir                     |
| Erisilebilik (Accessibility)            | OK    | System fontlari ve renkleri ile VoiceOver uyumu            |
| Yukleniyor durumu gosterimi             | OK    | ProgressView spinner ile gorsel geri bildirim              |

---

## 6. Dosya Yapisi Onerisi

```
LoginFeature/
├── Views/
│   ├── LoginView.swift              // Ana ekran
│   ├── Components/
│   │   ├── EmailTextField.swift     // E-posta alani
│   │   ├── PasswordSecureField.swift // Sifre alani
│   │   ├── RememberMeToggle.swift   // Hatirla beni toggle
│   │   ├── LoginButton.swift        // Giris butonu
│   │   ├── AppLogoView.swift        // Logo bileseni
│   │   └── FooterLinksView.swift    // Alt linkler
├── Tokens/
│   ├── LoginColors.swift            // Renk token'lari
│   ├── LoginTypography.swift        // Tipografi token'lari
│   └── LoginSpacing.swift           // Spacing token'lari
└── ViewModels/
    └── LoginViewModel.swift         // Giris is mantigi (MVVM)
```
