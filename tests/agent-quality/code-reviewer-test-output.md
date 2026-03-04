# Kod Review Raporu

**Tarih:** 2026-03-04  
**Reviewer:** Dvina Code — Kıdemli Kod Review Uzmanı  
**Hedef:** `~/ai-dev-team/` dizini + sağlanan Python kodu  

---

## 1. OZET

| Metrik | Deger |
|---|---|
| Taranan dizin dosya sayisi | 8 (script/kaynak dosya yok — HTML, MD, JSON, DS_Store) |
| Incelenen kod | Kullanici tarafindan saglanan Python snippet (4 fonksiyon, ~30 satir) |
| **Toplam sorun** | **9** |
| Critical | 2 |
| High | 3 |
| Medium | 3 |
| Low | 1 |

> Kodda **2 kritik guvenlik acigi** tespit edildi. Uretim ortamina alinmadan once bunlarin giderilmesi zorunludur.

---

## 2. SORUNLAR LISTESI

### CRITICAL

#### C1 — Hardcoded API Key (Guvenlik)
- **Severity:** CRITICAL
- **Kategori:** Security — Secret Exposure
- **Satir:** `API_KEY = "sk-1234567890abcdef"`
- **Aciklama:** API anahtari kaynak kodda plain-text olarak saklanmis. Bu kod bir Git reposuna push edildiginde anahtar tamamen aciga cikar. Saldirganlar `git log`, GitHub arama veya leak veritabanlari (truffleHog, GitGuardian) ile bu anahtari dakikalar icinde bulabilir.
- **Oneri:**
  ```python
  import os
  API_KEY = os.environ.get("API_KEY")
  if not API_KEY:
      raise RuntimeError("API_KEY environment variable is not set")
  ```
  Ek olarak: `.env` dosyasi + `python-dotenv` kullanin, `.gitignore` icine `.env` ekleyin. Eger bu anahtar gercekse **derhal revoke edin**.

#### C2 — Sifre Plain-Text Olarak Kaydediliyor (Guvenlik)
- **Severity:** CRITICAL
- **Kategori:** Security — Credential Storage
- **Satir:** `new_user = {"name": name, "email": email, "password": password, "active": True}`
- **Aciklama:** Kullanici sifresi hicbir hashing islemi yapilmadan dumduz JSON dosyasina yaziliyor. Bu, OWASP Top 10 — A02:2021 (Cryptographic Failures) ihlalidir. Dosyaya erisebilen herkes tum kullanici sifrelerini gorebilir.
- **Oneri:**
  ```python
  import bcrypt

  def save_user(name, email, password):
      hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
      new_user = {
          "name": name,
          "email": email,
          "password": hashed.decode('utf-8'),
          "active": True
      }
      # ...
  ```

---

### HIGH

#### H1 — Dosya Handle Leak (Resource Management)
- **Severity:** HIGH
- **Kategori:** Reliability — Resource Leak
- **Satirlar:** `f = open("users.json")` ve `f = open("users.json", "w")`
- **Aciklama:** Her iki fonksiyonda da `open()` ile acilan dosya **hicbir zaman kapatilmiyor**. `f.close()` cagrisi yok, `with` statement kullanilmamis. Bu, dosya descriptor leak'ine yol acar; uzun sureli calismalarda "Too many open files" hatasina neden olabilir. Ayrica yazma isleminde program crash ederse veri kaybi riski vardir.
- **Oneri:**
  ```python
  def get_users():
      with open("users.json", "r", encoding="utf-8") as f:
          data = json.load(f)
      # ...

  def save_user(name, email, password):
      # ...
      with open("users.json", "w", encoding="utf-8") as f:
          json.dump(users, f, indent=2)
  ```

#### H2 — Hata Yonetimi Yok (Error Handling)
- **Severity:** HIGH
- **Kategori:** Reliability — Error Handling
- **Aciklama:** Hicbir fonksiyonda `try/except` blogu yok. Dosya bulunamazsa (`FileNotFoundError`), JSON bozuksa (`json.JSONDecodeError`), veya `data[i]` icinde beklenen key yoksa (`KeyError`) program kontrolsuz sekilde crash eder.
- **Oneri:**
  ```python
  def get_users():
      try:
          with open("users.json", "r", encoding="utf-8") as f:
              data = json.load(f)
      except FileNotFoundError:
          return []
      except json.JSONDecodeError as e:
          raise ValueError(f"users.json is corrupted: {e}")
      # ...
  ```

#### H3 — Input Validation Yok (Guvenlik)
- **Severity:** HIGH
- **Kategori:** Security — Input Validation
- **Satir:** `def save_user(name, email, password):`
- **Aciklama:** `save_user` fonksiyonu gelen parametreleri hicbir sekilde dogrulamiyor. Bos string, None, veya injection iceren degerler kabul edilir. Email formati kontrol edilmiyor.
- **Oneri:**
  ```python
  import re

  def save_user(name: str, email: str, password: str) -> dict:
      if not name or not name.strip():
          raise ValueError("Name cannot be empty")
      if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
          raise ValueError(f"Invalid email format: {email}")
      if len(password) < 8:
          raise ValueError("Password must be at least 8 characters")
      # ...
  ```

---

### MEDIUM

#### M1 — Hardcoded Dosya Yolu (Maintainability)
- **Severity:** MEDIUM
- **Kategori:** Maintainability — Configuration
- **Satirlar:** `"users.json"` 3 farkli yerde tekrarlaniyor
- **Aciklama:** Dosya yolu string literal olarak dagilmis durumda. Dosya adi veya konumu degistiginde birden fazla yerde guncelleme yapmak gerekir (DRY ihlali).
- **Oneri:**
  ```python
  USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")
  ```

#### M2 — Anti-Pythonic Dongu Kullanimi (Code Quality)
- **Severity:** MEDIUM
- **Kategori:** Code Quality — Idioms
- **Satirlar:** `for i in range(len(data)):` ve `if data[i]["active"] == True:`
- **Aciklama:** Python'da `range(len(...))` pattern'i anti-pattern kabul edilir. Ayrica `== True` karsilastirmasi gereksizdir; `bool` deger zaten truthy/falsy olarak calisir.
- **Oneri:**
  ```python
  def get_users():
      with open(USERS_FILE, "r", encoding="utf-8") as f:
          data = json.load(f)
      return [user for user in data if user.get("active")]
  ```

#### M3 — Asiri Nesting / Deeply Nested Loops (Code Quality)
- **Severity:** MEDIUM
- **Kategori:** Code Quality — Complexity
- **Satir:** `process_data` fonksiyonu — 4 seviye nesting (for > for > for > if)
- **Aciklama:** 3+ seviye ic ice dongu, kodu okumasi ve test etmesi zor hale getirir. Cyclomatic complexity yuksektir. Bu yapida hata ayiklama zorlasir.
- **Oneri:**
  ```python
  def process_data(data: list[dict]) -> list[int]:
      """Extract positive values from nested children, doubled."""
      values = (
          val
          for item in data
          for sub in item.get("children", [])
          for val in sub.get("values", [])
          if val > 0
      )
      return [v * 2 for v in values]
  ```

---

### LOW

#### L1 — Type Hints ve Docstrings Eksik (Documentation)
- **Severity:** LOW
- **Kategori:** Documentation — Type Safety
- **Aciklama:** Hicbir fonksiyonda type hint veya docstring yok. Bu buyuk projelerde IDE destegini ve oto-dokumantasyonu engeller.
- **Oneri:**
  ```python
  def get_users() -> list[dict]:
      """Load and return all active users from the JSON store."""
      ...

  def save_user(name: str, email: str, password: str) -> None:
      """Create a new user and persist to the JSON store."""
      ...
  ```

---

## 3. IYI UYGULAMALAR

Kodda sinirli da olsa bazi olumlu yonler var:

1. **Standart kutuphane kullanimi** — `json` ve `os` modulleri dogru sekilde import edilmis; gereksiz ucuncu parti bagimlilik yok.
2. **Fonksiyon ayirimi** — Okuma (`get_users`) ve yazma (`save_user`) islemleri ayri fonksiyonlara bolunmus. Tek bir "do everything" fonksiyonu yerine sorumluluk ayrimi var.
3. **Basit ve anlasilir yapida** — Kodun amaci ilk bakista anlasilabiliyor; asiri muhendislik (over-engineering) yok.
4. **JSON formati tercih edilmis** — Veri saklama icin okunabilir bir format kullanilmis (prototip asamasi icin uygun).

---

## 4. AKSIYON OGELERI

Oncelik sirasina gore yapilmasi gerekenler:

| Oncelik | Aksiyon | Severity | Tahmini Efor |
|---|---|---|---|
| 1 | API key'i kaynak koddan kaldirin, environment variable'a tasinin. Eger gercek bir key ise **simdi revoke edin**. | CRITICAL | 15 dk |
| 2 | Sifreleri bcrypt/argon2 ile hash'leyin. Mevcut plain-text sifreleri migrasyon scripti ile hash'leyin. | CRITICAL | 1 saat |
| 3 | Tum `open()` cagrilarini `with` statement ile sarin. | HIGH | 15 dk |
| 4 | `try/except` ile hata yonetimi ekleyin (FileNotFoundError, JSONDecodeError, KeyError). | HIGH | 30 dk |
| 5 | `save_user` icin input validation ekleyin (email format, password uzunluk, bos deger kontrolu). | HIGH | 30 dk |
| 6 | Hardcoded dosya yolunu bir constant'a cikartin. | MEDIUM | 10 dk |
| 7 | `range(len(...))` ve `== True` pattern'lerini Pythonic hale getirin. | MEDIUM | 10 dk |
| 8 | `process_data` icindeki nesting'i generator expression ile sadelelestirin. | MEDIUM | 15 dk |
| 9 | Tum fonksiyonlara type hints ve docstrings ekleyin. | LOW | 20 dk |

**Toplam tahmini efor:** ~3.5 saat

---

## Sonuc

Bu kod **prototip asamasinda** kabul edilebilir olsa da, uretim ortamina alinmasi icin **en az 2 kritik guvenlik sorununun** duzeltilmesi sart. Ozellikle hardcoded API key ve plain-text sifre saklama konulari, veri ihlali riski olusturmaktadir.

> **Karar:** Uretim ortamina alinmadan once CRITICAL ve HIGH oncelikli tum sorunlarin giderilmesi **zorunludur**.
