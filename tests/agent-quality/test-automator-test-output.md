# Login Fonksiyonu - Unit Test Senaryolari

> **Hedef Fonksiyon:** `login(email, password) → { success: boolean, token?: string, error?: string }`
>
> **Framework:** Jest + TypeScript
>
> **Pattern:** AAA (Arrange, Act, Assert)

---

## 1. Jest Konfigurasyonu

Testleri calistirmak icin gereken minimal Jest + TypeScript yapilandirmasi:

```typescript
// jest.config.ts
import type { Config } from "jest";

const config: Config = {
  preset: "ts-jest",
  testEnvironment: "node",
  roots: ["<rootDir>/src"],
  testMatch: ["**/__tests__/**/*.test.ts"],
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/src/$1",
  },
  clearMocks: true,
  collectCoverage: true,
  coverageDirectory: "coverage",
  coverageThresholds: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};

export default config;
```

---

## 2. Tip Tanimlari ve Mock Yapisi

Testlerde kullanilan tip tanimlari ve mock nesneleri:

```typescript
// src/types/auth.ts
export interface LoginResponse {
  success: boolean;
  token?: string;
  error?: string;
}

export interface AuthService {
  validateCredentials(email: string, password: string): Promise<boolean>;
  generateToken(email: string): Promise<string>;
}
```

```typescript
// src/__tests__/login.test.ts
import { login } from "../auth/login";
import type { AuthService } from "../types/auth";

// --- Mock Setup ---
// AuthService mock'u: validateCredentials ve generateToken fonksiyonlarini taklit eder.
// Her test oncesinde davranislari bagimsiz olarak ayarlanir.
const mockAuthService: jest.Mocked<AuthService> = {
  validateCredentials: jest.fn(),
  generateToken: jest.fn(),
};
```

---

## 3. Test Senaryolari

### TEST-01: Basarili Giris (Gecerli Email + Gecerli Sifre)

| Alan              | Deger                                                        |
| ----------------- | ------------------------------------------------------------ |
| **Test Adi**      | `should return success with token for valid credentials`     |
| **Precondition**  | Veritabaninda kayitli bir kullanici mevcut                   |
| **Test Adimlari** | 1) Mock servisi basarili donecek sekilde ayarla 2) `login()` cagir |
| **Beklenen Sonuc**| `{ success: true, token: "mocked-jwt-token" }`              |

```typescript
describe("login", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should return success with token for valid credentials", async () => {
    // -------------------------------------------------------
    // Arrange
    // -------------------------------------------------------
    // Gecerli kullanici bilgileri hazirlaniyor.
    // Mock servis, kimlik dogrulamayi onaylayacak ve token uretecek.
    const email = "user@example.com";
    const password = "SecurePass123!";
    const expectedToken = "mocked-jwt-token";

    mockAuthService.validateCredentials.mockResolvedValue(true);
    mockAuthService.generateToken.mockResolvedValue(expectedToken);

    // -------------------------------------------------------
    // Act
    // -------------------------------------------------------
    // login fonksiyonu gecerli parametrelerle cagriliyor.
    const result = await login(email, password, mockAuthService);

    // -------------------------------------------------------
    // Assert
    // -------------------------------------------------------
    // Basarili giris: success true, token dolu, error yok.
    expect(result.success).toBe(true);
    expect(result.token).toBe(expectedToken);
    expect(result.error).toBeUndefined();

    // Mock fonksiyonlarin dogru parametrelerle cagrildigini dogrula.
    expect(mockAuthService.validateCredentials).toHaveBeenCalledWith(
      email,
      password
    );
    expect(mockAuthService.validateCredentials).toHaveBeenCalledTimes(1);
    expect(mockAuthService.generateToken).toHaveBeenCalledWith(email);
    expect(mockAuthService.generateToken).toHaveBeenCalledTimes(1);
  });
});
```

---

### TEST-02: Basarisiz Giris (Gecerli Email + Yanlis Sifre)

| Alan              | Deger                                                            |
| ----------------- | ---------------------------------------------------------------- |
| **Test Adi**      | `should return failure with error for invalid password`          |
| **Precondition**  | Kullanici kayitli ancak sifre eslesmeyecek                       |
| **Test Adimlari** | 1) Mock servisi basarisiz donecek sekilde ayarla 2) `login()` cagir |
| **Beklenen Sonuc**| `{ success: false, error: "Invalid email or password" }`         |

```typescript
describe("login", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should return failure with error for invalid password", async () => {
    // -------------------------------------------------------
    // Arrange
    // -------------------------------------------------------
    // Gecerli email, yanlis sifre.
    // Mock servis kimlik dogrulamayi reddedecek.
    const email = "user@example.com";
    const password = "WrongPassword!";

    mockAuthService.validateCredentials.mockResolvedValue(false);

    // -------------------------------------------------------
    // Act
    // -------------------------------------------------------
    // login fonksiyonu yanlis sifre ile cagriliyor.
    const result = await login(email, password, mockAuthService);

    // -------------------------------------------------------
    // Assert
    // -------------------------------------------------------
    // Basarisiz giris: success false, token yok, hata mesaji var.
    expect(result.success).toBe(false);
    expect(result.token).toBeUndefined();
    expect(result.error).toBe("Invalid email or password");

    // validateCredentials cagirilmali, generateToken CAGRILMAMALI.
    expect(mockAuthService.validateCredentials).toHaveBeenCalledWith(
      email,
      password
    );
    expect(mockAuthService.validateCredentials).toHaveBeenCalledTimes(1);
    expect(mockAuthService.generateToken).not.toHaveBeenCalled();
  });
});
```

---

### TEST-03: Validasyon Hatasi (Bos Email)

| Alan              | Deger                                                          |
| ----------------- | -------------------------------------------------------------- |
| **Test Adi**      | `should return validation error when email is empty`           |
| **Precondition**  | Herhangi bir on kosul yok; girdi dogrudan gecersiz             |
| **Test Adimlari** | 1) Bos email ile `login()` cagir                               |
| **Beklenen Sonuc**| `{ success: false, error: "Email is required" }`               |

```typescript
describe("login", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should return validation error when email is empty", async () => {
    // -------------------------------------------------------
    // Arrange
    // -------------------------------------------------------
    // Email bos string olarak ayarlaniyor.
    // Validasyon katmaninda yakalanmasi gerekir; servis cagirilmamali.
    const email = "";
    const password = "AnyPassword123!";

    // -------------------------------------------------------
    // Act
    // -------------------------------------------------------
    // login fonksiyonu bos email ile cagriliyor.
    const result = await login(email, password, mockAuthService);

    // -------------------------------------------------------
    // Assert
    // -------------------------------------------------------
    // Validasyon hatasi: success false, token yok, uygun hata mesaji.
    expect(result.success).toBe(false);
    expect(result.token).toBeUndefined();
    expect(result.error).toBe("Email is required");

    // Validasyon hatasi oldugu icin AuthService hic cagirilmamali.
    expect(mockAuthService.validateCredentials).not.toHaveBeenCalled();
    expect(mockAuthService.generateToken).not.toHaveBeenCalled();
  });
});
```

---

## 4. Tam Test Dosyasi (Birlestirilmis)

Yukaridaki uc senaryonun tek dosyada birlestirilmis hali:

```typescript
// src/__tests__/login.test.ts
import { login } from "../auth/login";
import type { AuthService } from "../types/auth";

const mockAuthService: jest.Mocked<AuthService> = {
  validateCredentials: jest.fn(),
  generateToken: jest.fn(),
};

describe("login", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // TEST-01
  it("should return success with token for valid credentials", async () => {
    // Arrange
    const email = "user@example.com";
    const password = "SecurePass123!";
    const expectedToken = "mocked-jwt-token";
    mockAuthService.validateCredentials.mockResolvedValue(true);
    mockAuthService.generateToken.mockResolvedValue(expectedToken);

    // Act
    const result = await login(email, password, mockAuthService);

    // Assert
    expect(result.success).toBe(true);
    expect(result.token).toBe(expectedToken);
    expect(result.error).toBeUndefined();
    expect(mockAuthService.validateCredentials).toHaveBeenCalledWith(email, password);
    expect(mockAuthService.generateToken).toHaveBeenCalledWith(email);
  });

  // TEST-02
  it("should return failure with error for invalid password", async () => {
    // Arrange
    const email = "user@example.com";
    const password = "WrongPassword!";
    mockAuthService.validateCredentials.mockResolvedValue(false);

    // Act
    const result = await login(email, password, mockAuthService);

    // Assert
    expect(result.success).toBe(false);
    expect(result.token).toBeUndefined();
    expect(result.error).toBe("Invalid email or password");
    expect(mockAuthService.validateCredentials).toHaveBeenCalledWith(email, password);
    expect(mockAuthService.generateToken).not.toHaveBeenCalled();
  });

  // TEST-03
  it("should return validation error when email is empty", async () => {
    // Arrange
    const email = "";
    const password = "AnyPassword123!";

    // Act
    const result = await login(email, password, mockAuthService);

    // Assert
    expect(result.success).toBe(false);
    expect(result.token).toBeUndefined();
    expect(result.error).toBe("Email is required");
    expect(mockAuthService.validateCredentials).not.toHaveBeenCalled();
    expect(mockAuthService.generateToken).not.toHaveBeenCalled();
  });
});
```

---

## 5. Ozet

| #       | Senaryo                  | Beklenen Sonuc                                    | Pattern |
| ------- | ------------------------ | ------------------------------------------------- | ------- |
| TEST-01 | Basarili giris           | `success: true`, token dolu, error yok            | AAA     |
| TEST-02 | Yanlis sifre             | `success: false`, token yok, hata mesaji var      | AAA     |
| TEST-03 | Bos email (validasyon)   | `success: false`, token yok, validasyon hatasi    | AAA     |

- **Mock Kullanimi:** `jest.Mocked<AuthService>` ile `validateCredentials` ve `generateToken` mock'landi. Her testte `jest.clearAllMocks()` ile sifirlaniyor.
- **AAA Pattern:** Her testte Arrange / Act / Assert bloklari acik sekilde ayrilmis durumda.
- **Kapsam:** Basarili yol, hata yolu ve girdi validasyonu olmak uzere uc temel senaryo kapsaniyor.
