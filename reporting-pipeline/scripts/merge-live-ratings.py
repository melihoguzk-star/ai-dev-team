#!/usr/bin/env python3
"""
merge-live-ratings.py — Live rating verisi ile mock metriklerini birleştirir.

Strateji:
  - Rating: Live dosyasından al (n >= MIN_REVIEWS); yetersizse mock'a dön
  - Crash Free / Downloads / Active Users / Uninstalls: mock data'dan al
  - Yeni hafta için (mock'ta yok) son haftanın değerlerini kullan

Kullanım:
    python scripts/merge-live-ratings.py --week 2026-03-09
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR      = Path(__file__).resolve().parent.parent
RAW_DIR       = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Report haftası: son 7 hafta (bu hafta dahil)
REPORT_WEEKS = [
    ("2026-01-26", "2026-02-01"),
    ("2026-02-02", "2026-02-08"),
    ("2026-02-09", "2026-02-15"),
    ("2026-02-16", "2026-02-22"),
    ("2026-02-23", "2026-03-01"),
    ("2026-03-02", "2026-03-08"),
    ("2026-03-09", "2026-03-15"),
]

MIN_REVIEWS = 5  # Bu eşiğin altında → mock'a geri dön

# Mock data kaynağı: bir önceki raporun CSV'si
MOCK_CSV_DATE = "2026-03-02"


def load_live_ratings(platform: str, file_date: str) -> dict:
    """Live rating JSON → {week_start: (value, count, status)} dict."""
    path = RAW_DIR / f"{platform}_rating_live_{file_date}.json"
    if not path.exists():
        print(f"  ⚠ {path.name} bulunamadı.")
        return {}
    d = json.loads(path.read_text())
    result = {}
    for e in d.get("data", []):
        ws = e["week_start"]
        result[ws] = {
            "value":  e["value"],
            "count":  e["review_count"],
            "status": e["status"],
        }
    # Genel rating (fallback için)
    g = d.get("general") or {}
    result["__general__"] = g.get("overall")
    return result


def load_mock_csv(week: str) -> pd.DataFrame:
    """Mevcut mock weekly-metrics CSV'yi yükle."""
    path = PROCESSED_DIR / f"weekly-metrics-{week}.csv"
    if not path.exists():
        print(f"  ⚠ Mock CSV bulunamadı: {path.name}")
        return pd.DataFrame()
    return pd.read_csv(path)


def compute_moving_avg(series: list, window: int = 4) -> list:
    result = []
    for i, v in enumerate(series):
        start = max(0, i - window + 1)
        window_vals = [x for x in series[start:i+1] if x is not None]
        result.append(round(sum(window_vals) / len(window_vals), 4) if window_vals else None)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--week", default="2026-03-09")
    args = parser.parse_args()
    target_week = args.week

    print(f"\n{'='*60}")
    print(f"  merge-live-ratings.py  →  weekly-metrics-{target_week}.csv")
    print(f"{'='*60}")

    # ── 1. Live rating yükle ──────────────────────────────────────
    print("\n[1/4] Live rating verileri yükleniyor...")
    ios_live     = load_live_ratings("ios",     target_week)
    android_live = load_live_ratings("android", target_week)

    # ── 2. Mock CSV yükle ─────────────────────────────────────────
    print("[2/4] Mock data yükleniyor...")
    mock_df = load_mock_csv(MOCK_CSV_DATE)
    if mock_df.empty:
        print("  ✗ Mock CSV yüklenemedi. Çıkılıyor.")
        sys.exit(1)

    # mock'u {week_start: row} dict'e çevir
    mock_by_week = {row["week_start"]: row for _, row in mock_df.iterrows()}

    # ── 3. Her hafta için satır oluştur ───────────────────────────
    print("[3/4] Birleştirme yapılıyor...")
    print(f"\n  {'Hafta':<22} {'iOS rating':>12} {'And rating':>12}  Kaynak")
    print(f"  {'─'*60}")

    rows = []
    data_sources = []  # (week_start, ios_src, and_src) for summary

    for ws, we in REPORT_WEEKS:
        # ── Rating: live > mock ──────────────────────────────────
        ios_entry = ios_live.get(ws, {})
        and_entry = android_live.get(ws, {})

        def pick_rating(entry, mock_row, col, platform_label, week_start):
            val   = entry.get("value")
            count = entry.get("count", 0)
            general = (ios_live if "ios" in platform_label else android_live).get("__general__")
            if val is not None and count >= MIN_REVIEWS:
                return val, "LIVE"
            elif mock_row is not None and col in mock_row:
                return mock_row[col], "MOCK(insuf.)" if val is None and count > 0 else "MOCK(no data)"
            elif general:
                return general, "LIVE(genel)"
            else:
                return None, "MISSING"

        mock_row = mock_by_week.get(ws)

        ios_rating, ios_src = pick_rating(ios_entry,  mock_row, "ios_rating",     "ios",     ws)
        and_rating, and_src = pick_rating(and_entry,  mock_row, "android_rating", "android", ws)

        # ── Diğer metrikler: mock veya son hafta tahmini ─────────
        if mock_row is not None:
            ios_crash  = mock_row["ios_crash_free_user"]
            and_crash  = mock_row["android_crash_free_user"]
            ios_dl     = mock_row["ios_downloads"]
            and_dl     = mock_row["android_downloads"]
            ios_au     = mock_row["ios_active_users"]
            and_au     = mock_row["android_active_users"]
            ios_un     = mock_row["ios_uninstalls"]
            and_un     = mock_row["android_uninstalls"]
            other_src  = "MOCK"
        else:
            # Yeni hafta — son mevcut haftadan al
            last_row   = mock_by_week.get("2026-03-08") or mock_by_week.get("2026-03-02")
            if last_row is None:
                last_row = list(mock_by_week.values())[-1]
            ios_crash  = last_row["ios_crash_free_user"]
            and_crash  = last_row["android_crash_free_user"]
            ios_dl     = last_row["ios_downloads"]
            and_dl     = last_row["android_downloads"]
            ios_au     = last_row["ios_active_users"]
            and_au     = last_row["android_active_users"]
            ios_un     = last_row["ios_uninstalls"]
            and_un     = last_row["android_uninstalls"]
            other_src  = "MOCK(est.)"

        src_label = f"rating={ios_src}/{and_src}, other={other_src}"
        print(f"  {ws} – {we[5:]}  {str(ios_rating):>12}  {str(and_rating):>12}  {src_label}")

        rows.append({
            "week_start":             ws,
            "week_end":               we,
            "ios_rating":             ios_rating,
            "android_rating":         and_rating,
            "ios_crash_free_user":    ios_crash,
            "android_crash_free_user": and_crash,
            "ios_downloads":          ios_dl,
            "android_downloads":      and_dl,
            "ios_active_users":       ios_au,
            "android_active_users":   and_au,
            "ios_uninstalls":         ios_un,
            "android_uninstalls":     and_un,
        })
        data_sources.append((ws, ios_src, and_src, other_src))

    # ── 4. Moving average hesapla ─────────────────────────────────
    df = pd.DataFrame(rows)
    metrics = [
        "ios_rating", "android_rating",
        "ios_crash_free_user", "android_crash_free_user",
        "ios_downloads", "android_downloads",
        "ios_active_users", "android_active_users",
        "ios_uninstalls", "android_uninstalls",
    ]
    for m in metrics:
        df[f"{m}_ma4"] = compute_moving_avg(df[m].tolist(), 4)

    # ── 5. WoW değişimleri hesapla ────────────────────────────────
    wow_rows = []
    for m in metrics:
        vals = df[m].tolist()
        for i in range(1, len(vals)):
            prev, cur = vals[i-1], vals[i]
            pct = round((cur - prev) / prev * 100, 2) if prev and prev != 0 else None
            wow_rows.append({
                "week_start": df.iloc[i]["week_start"],
                "week_end":   df.iloc[i]["week_end"],
                "metric":     m,
                "prev_value": prev,
                "curr_value": cur,
                "wow_pct":    pct,
            })
    wow_df = pd.DataFrame(wow_rows)
    wow_path = PROCESSED_DIR / f"wow-changes-{target_week}.csv"
    wow_df.to_csv(wow_path, index=False, float_format="%.2f")

    # ── 6. Kaydet ────────────────────────────────────────────────
    print("\n[4/4] CSV'ler kaydediliyor...")
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / f"weekly-metrics-{target_week}.csv"
    df.to_csv(out_path, index=False, float_format="%.2f")
    print(f"  ✓ {out_path.name}  ({out_path.stat().st_size/1024:.1f} KB)  {len(df)} hafta")
    print(f"  ✓ {wow_path.name}  ({wow_path.stat().st_size/1024:.1f} KB)")

    # ── 6. Kaynak özeti ────────────────────────────────────────────
    print(f"\n  VERİ KAYNAĞI ÖZETİ")
    print(f"  {'─'*50}")
    live_ios = sum(1 for _, s, _, _ in data_sources if s == "LIVE")
    live_and = sum(1 for _, _, s, _ in data_sources if s == "LIVE")
    mock_ios = sum(1 for _, s, _, _ in data_sources if "MOCK" in s)
    mock_and = sum(1 for _, _, s, _ in data_sources if "MOCK" in s)
    print(f"  iOS rating     → LIVE: {live_ios} hafta  |  MOCK fallback: {mock_ios} hafta")
    print(f"  Android rating → LIVE: {live_and} hafta  |  MOCK fallback: {mock_and} hafta")
    print(f"  Diğer metrikler: tümü MOCK (credential bekliyor)")
    print(f"\n  ⚠  UYARI: Aşağıdaki haftalar için iOS rating yetersiz (n<{MIN_REVIEWS}),")
    print(f"     mock değer kullanıldı:")
    for ws, ios_s, _, _ in data_sources:
        if ios_s != "LIVE":
            print(f"     • {ws} ({ios_s})")

    print(f"\n{'='*60}\n")
    return str(out_path)


if __name__ == "__main__":
    main()
