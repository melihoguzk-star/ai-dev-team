# Kullanıcı Giriş Ekranı — BA Dokümanı

## 1. Modül Açıklaması

Kullanıcı Giriş Ekranı, sisteme erişim sağlamak isteyen kullanıcıların kimlik doğrulama işlemini gerçekleştirdiği ekrandır. Kullanıcılar e-posta adresi ve parola bilgilerini girerek sisteme giriş yapar. Bu modül, yetkisiz erişimlerin önlenmesi ve kullanıcı oturumlarının güvenli biçimde başlatılması amacıyla tasarlanmıştır.

Modül; giriş formu, hata bildirimleri ve parola sıfırlama yönlendirmesi olmak üzere üç temel bileşenden oluşur. Başarılı giriş sonrasında kullanıcı ana sayfaya yönlendirilirken, başarısız giriş denemelerinde kullanıcıya anlaşılır bir hata mesajı gösterilir. Tüm giriş denemeleri sistem tarafından kayıt altına alınır.

---

## 2. Fonksiyonel Gereksinimler

| ID    | Gereksinim |
|-------|-----------|
| FR-01 | Giriş ekranı; e-posta adresi alanı, parola alanı ve "Giriş Yap" butonu içermelidir. E-posta alanı maksimum 254 karakter, parola alanı maksimum 128 karakter kabul etmelidir. |
| FR-02 | Kullanıcı geçerli e-posta ve parola ile giriş yaptığında sistem 3 saniye içinde kimlik doğrulaması yapmalı ve kullanıcıyı ana sayfaya (/dashboard) yönlendirmelidir. |
| FR-03 | Geçersiz e-posta veya parola girildiğinde ekranda "E-posta adresi veya parola hatalı." şeklinde kırmızı renkli bir hata mesajı gösterilmelidir. Hata mesajı, giriş formunun hemen üstünde yer almalıdır. |

---

## 3. İş Kuralları

| ID    | Kural |
|-------|-------|
| BR-01 | Bir kullanıcı art arda 5 başarısız giriş denemesi yaptığında, ilgili kullanıcı hesabı 15 dakika süreyle geçici olarak kilitlenir. Kilitleme süresi dolmadan yeni giriş denemesi yapılamaz. |
| BR-02 | Başarılı giriş sonrasında oluşturulan kullanıcı oturumu, 30 dakika boyunca herhangi bir işlem yapılmazsa otomatik olarak sonlandırılır ve kullanıcı giriş ekranına yönlendirilir. |

---

## 4. Kabul Kriterleri

| ID    | Kriter |
|-------|--------|
| AC-01 | Sistemde kayıtlı geçerli bir e-posta ve parola ile giriş yapıldığında, kullanıcı 3 saniye içinde ana sayfaya (/dashboard) yönlendirilmelidir. |
| AC-02 | Art arda 5 hatalı giriş denemesi yapıldığında, 6. denemede sistem "Hesabınız geçici olarak kilitlenmiştir. Lütfen 15 dakika sonra tekrar deneyiniz." mesajını göstermeli ve giriş işlemini engellemelidir. |
