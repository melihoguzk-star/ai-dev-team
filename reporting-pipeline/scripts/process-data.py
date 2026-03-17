#!/usr/bin/env python3
"""
process-data.py — SunExpress Sun Mobile haftalık metrik işleyici

Kullanım:
    python scripts/process-data.py --week 2026-03-02

Çıktılar:
    data/processed/weekly-metrics-{week}.csv
    data/processed/wow-changes-{week}.csv
    data/processed/platform-comparison-{week}.csv
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# Dizin yapısı
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CONFIG_DIR = BASE_DIR / "config"

# Live veri destekli metrikler (slug → metric_id)
# Credential olmayan metrikler (downloads, active_users, uninstalls) BOŞ bırakılır
LIVE_SLUGS  = {"rating", "crashlytics"}   # live dosya aranır
EMPTY_SLUGS = {"downloads", "active_users", "uninstalls"}  # credential yok → "-"

# Metrik kaynak izleme (process sırasında doldurulur)
_DATA_SOURCES: dict = {}  # "platform_metric_id" → "live" | "empty"

# ---------------------------------------------------------------------------
# Metrik adı normalizasyonu (dosya adı → config id)
# ---------------------------------------------------------------------------
# Dosya slug → sütun adı (COLUMN_ORDER ile uyumlu kısa isimler)
FILE_TO_METRIC_ID = {
    "rating":       "rating",
    "crashlytics":  "crash_free_user",
    "downloads":    "downloads",
    "active_users": "active_users",
    "uninstalls":   "uninstalls",
}

# Sütun metrik adı → alert-thresholds.json config anahtarı
METRIC_TO_THRESHOLD_KEY = {
    "rating":          "app_rating",
    "crash_free_user": "crash_free_user",
    "downloads":       "weekly_downloads",
    "active_users":    "weekly_active_users",
    "uninstalls":      "weekly_uninstalls",
}

COLUMN_ORDER = [
    "ios_rating",
    "android_rating",
    "ios_crash_free_user",
    "android_crash_free_user",
    "ios_downloads",
    "android_downloads",
    "ios_active_users",
    "android_active_users",
    "ios_uninstalls",
    "android_uninstalls",
]


# Rapor haftaları (collect-ratings.py ile senkron)
REPORT_WEEKS = [
    ("2026-01-19", "2026-01-25"),
    ("2026-01-26", "2026-02-01"),
    ("2026-02-02", "2026-02-08"),
    ("2026-02-09", "2026-02-15"),
    ("2026-02-16", "2026-02-22"),
    ("2026-02-23", "2026-03-01"),
    ("2026-03-02", "2026-03-08"),
]


# ---------------------------------------------------------------------------
# 1. PARSE — raw JSON → DataFrame satırları  (live only, no mock fallback)
# ---------------------------------------------------------------------------
def _find_live_file(platform: str, slug: str) -> tuple[Path | None, dict | None]:
    """
    live:true ve data list şemasına sahip en yeni dosyayı döner.
    Döner: (path, raw_dict) | (None, None)
    """
    candidates = sorted(RAW_DIR.glob(f"{platform}_{slug}_live_*.json"), reverse=True)
    for path in candidates:
        try:
            with open(path, encoding="utf-8") as f:
                raw = json.load(f)
            if raw.get("live", False) and isinstance(raw.get("data"), list):
                return path, raw
        except Exception:
            continue
    return None, None


def _load_weekly_list(raw: dict) -> list[dict]:
    """
    JSON data → haftalık liste.
    Sadece weekly list şeması desteklenir (collect-ratings.py yeni formatı).
    """
    data = raw.get("data", [])
    if isinstance(data, list):
        return data
    return []


def _empty_weeks_df(platform: str, metric_id: str) -> pd.DataFrame:
    """Veri olmayan metrik için NaN dolu DataFrame döner (REPORT_WEEKS boyutunda)."""
    rows = [{"week_start": ws, "week_end": we, "value": np.nan}
            for ws, we in REPORT_WEEKS]
    df = pd.DataFrame(rows)
    df["week_start"]  = pd.to_datetime(df["week_start"])
    df["week_end"]    = pd.to_datetime(df["week_end"])
    df["platform"]    = platform
    df["metric_id"]   = metric_id
    df["column"]      = f"{platform}_{metric_id}"
    df["data_source"] = "empty"
    return df


def parse_raw_files(week: str) -> pd.DataFrame:
    """
    Her (platform, slug) için:
      - LIVE_SLUGS   → live dosya ara; live:true ise kullan, değilse boş
      - EMPTY_SLUGS  → hiç dosya arama, NaN döner
    _DATA_SOURCES sözlüğünü günceller.
    """
    global _DATA_SOURCES
    _DATA_SOURCES = {}

    platforms = ["ios", "android"]
    frames    = []

    for platform in platforms:
        for slug, metric_id in FILE_TO_METRIC_ID.items():
            col = f"{platform}_{metric_id}"

            if slug in EMPTY_SLUGS:
                # Credential yok → boş
                df = _empty_weeks_df(platform, metric_id)
                frames.append(df)
                print(f"  {col:30s} [EMPTY — credential yok]")
                _DATA_SOURCES[col] = "empty"
                continue

            # LIVE_SLUGS
            live_path, raw = _find_live_file(platform, slug)
            if live_path and raw is not None:
                rows = _load_weekly_list(raw)
                if rows:
                    df = pd.DataFrame(rows)
                    df["week_start"]  = pd.to_datetime(df["week_start"])
                    df["week_end"]    = pd.to_datetime(df["week_end"])
                    df["platform"]    = platform
                    df["metric_id"]   = metric_id
                    df["column"]      = col
                    df["data_source"] = "live"
                    df["value"] = pd.to_numeric(df["value"], errors="coerce")
                    frames.append(df)
                    non_null = df["value"].notna().sum()
                    print(f"  {col:30s} [LIVE: {live_path.name}] "
                          f"({non_null}/{len(df)} hafta dolu)")
                    _DATA_SOURCES[col] = "live"
                    continue

            # Live yoksa → boş
            df = _empty_weeks_df(platform, metric_id)
            frames.append(df)
            reason = "live dosya yok" if live_path is None else "data listesi boş"
            print(f"  {col:30s} [EMPTY — {reason}]")
            _DATA_SOURCES[col] = "empty"

    if not frames:
        print("HATA: İşlenecek veri bulunamadı.", file=sys.stderr)
        sys.exit(1)

    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------------------------
# 2. MERGE — pivot: satır=hafta, sütun=platform_metrik
# ---------------------------------------------------------------------------
def merge_metrics(long_df: pd.DataFrame) -> pd.DataFrame:
    """Long-format DataFrame'i pivot ederek geniş formata çevirir."""
    pivot = long_df.pivot_table(
        index=["week_start", "week_end"],
        columns="column",
        values="value",
        aggfunc="first",
    ).reset_index()

    pivot.columns.name = None
    pivot = pivot.sort_values("week_start").reset_index(drop=True)

    # Beklenen sütunları sıraya koy, eksikleri NaN olarak ekle
    for col in COLUMN_ORDER:
        if col not in pivot.columns:
            pivot[col] = np.nan

    ordered_cols = ["week_start", "week_end"] + COLUMN_ORDER
    pivot = pivot[[c for c in ordered_cols if c in pivot.columns]]

    # data_source sütunları ekle (her metrik için live/mock)
    for col in COLUMN_ORDER:
        pivot[f"{col}_source"] = _DATA_SOURCES.get(col, "unknown")

    return pivot


# ---------------------------------------------------------------------------
# 3. WoW hesaplama
# ---------------------------------------------------------------------------
def compute_wow(pivot: pd.DataFrame) -> pd.DataFrame:
    """Her metrik sütunu için WoW % değişimini hesaplar."""
    wow = pivot[["week_start", "week_end"]].copy()

    for col in COLUMN_ORDER:
        if col not in pivot.columns:
            continue
        series = pivot[col]
        prev = series.shift(1)
        wow_col = ((series - prev) / prev.abs() * 100).round(2)
        wow[f"{col}_wow_pct"] = wow_col  # İlk hafta NaN kalır

    return wow


# ---------------------------------------------------------------------------
# 4. Hareketli ortalama (4 hafta)
# ---------------------------------------------------------------------------
def compute_moving_avg(pivot: pd.DataFrame, window: int = 4) -> pd.DataFrame:
    """4 haftalık hareketli ortalama sütunlarını pivot'a ekler."""
    result = pivot.copy()
    for col in COLUMN_ORDER:
        if col not in pivot.columns:
            continue
        result[f"{col}_ma4"] = (
            pivot[col].rolling(window=window, min_periods=1).mean().round(2)
        )
    return result


# ---------------------------------------------------------------------------
# 5. Anomali flag (eşik tabanlı)
# ---------------------------------------------------------------------------
def load_thresholds() -> dict:
    path = CONFIG_DIR / "alert-thresholds.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)["thresholds"]


def compute_anomaly_flags(pivot: pd.DataFrame, wow: pd.DataFrame, thresholds: dict) -> pd.DataFrame:
    """
    Her hafta × metrik × platform için anomali bayrağı üretir.
    Dönen DataFrame: week_start, column, value, wow_pct, anomaly_flag
    """
    records = []

    for col in COLUMN_ORDER:
        if col not in pivot.columns:
            continue

        parts = col.split("_", 1)
        platform = parts[0]
        metric_id = parts[1]  # örn. crash_free_user, rating, active_users

        threshold_key = METRIC_TO_THRESHOLD_KEY.get(metric_id, metric_id)
        thresh = thresholds.get(threshold_key, {})
        warning_cfg = thresh.get("warning", {})
        critical_cfg = thresh.get("critical", {})

        wow_col = f"{col}_wow_pct"

        for i, row in pivot.iterrows():
            value = row[col]
            wow_pct = wow.loc[i, wow_col] if wow_col in wow.columns else np.nan

            flag = "none"

            if pd.notna(value):
                # Critical kontrol
                crit_abs = critical_cfg.get("absolute_lt")
                crit_wow = critical_cfg.get("wow_change_lte") or critical_cfg.get("wow_change_pct_lte")
                crit_wow_gte = critical_cfg.get("wow_change_pct_gte")

                warn_abs = warning_cfg.get("absolute_lt")
                warn_wow = warning_cfg.get("wow_change_lte") or warning_cfg.get("wow_change_pct_lte")
                warn_wow_gte = warning_cfg.get("wow_change_pct_gte")

                # Critical önce kontrol edilir
                if (crit_abs is not None and value < crit_abs) or \
                   (crit_wow is not None and pd.notna(wow_pct) and wow_pct <= crit_wow) or \
                   (crit_wow_gte is not None and pd.notna(wow_pct) and wow_pct >= crit_wow_gte):
                    flag = "critical"
                elif (warn_abs is not None and value < warn_abs) or \
                     (warn_wow is not None and pd.notna(wow_pct) and wow_pct <= warn_wow) or \
                     (warn_wow_gte is not None and pd.notna(wow_pct) and wow_pct >= warn_wow_gte):
                    flag = "warning"

            records.append({
                "week_start": row["week_start"],
                "platform": platform,
                "metric": metric_id,
                "column": col,
                "value": value,
                "wow_pct": wow_pct if pd.notna(wow_pct) else None,
                "anomaly_flag": flag,
            })

    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# 6. Platform karşılaştırma özeti
# ---------------------------------------------------------------------------
def compute_platform_comparison(pivot: pd.DataFrame) -> pd.DataFrame:
    """iOS vs Android yan yana karşılaştırma tablosu."""
    rows = []
    metric_ids = list(dict.fromkeys(c.split("_", 1)[1] for c in COLUMN_ORDER))

    for metric_id in metric_ids:
        ios_col = f"ios_{metric_id}"
        and_col = f"android_{metric_id}"

        for _, row in pivot.iterrows():
            ios_val = row.get(ios_col, np.nan)
            and_val = row.get(and_col, np.nan)
            rows.append({
                "week_start": row["week_start"],
                "week_end": row["week_end"],
                "metric": metric_id,
                "ios": ios_val,
                "android": and_val,
            })

    return pd.DataFrame(rows).sort_values(["metric", "week_start"]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Ana akış
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="SunExpress metrik işleyici")
    parser.add_argument(
        "--week",
        required=True,
        help="İşlenecek hafta son tarihi — YYYY-MM-DD formatında (örn. 2026-03-02)",
    )
    args = parser.parse_args()
    week = args.week

    print(f"\n{'='*60}")
    print(f"  process-data.py — hafta: {week}")
    print(f"{'='*60}\n")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Parse
    print("► PARSE: raw JSON dosyaları okunuyor (live öncelikli)...")
    long_df = parse_raw_files(week)
    print(f"  {len(long_df)} veri noktası yüklendi ({long_df['column'].nunique()} metrik×platform)")

    # Kaynak özeti
    live_cols = [c for c, s in _DATA_SOURCES.items() if s == "live"]
    mock_cols = [c for c, s in _DATA_SOURCES.items() if s == "mock"]
    print(f"  LIVE: {', '.join(live_cols) or 'yok'}")
    print(f"  MOCK: {', '.join(mock_cols) or 'yok'}")

    # 2. Merge
    print("► MERGE: pivot tablo oluşturuluyor...")
    pivot = merge_metrics(long_df)
    print(f"  {len(pivot)} hafta × {len(COLUMN_ORDER)} sütun")

    # 3. WoW
    print("► WoW: haftalık değişimler hesaplanıyor...")
    wow = compute_wow(pivot)

    # 4. Hareketli ortalama
    print("► MA4: 4 haftalık hareketli ortalamalar hesaplanıyor...")
    pivot_with_ma = compute_moving_avg(pivot)

    # 5. Anomali flag
    print("► FLAG: anomali eşikleri kontrol ediliyor...")
    thresholds = load_thresholds()
    anomaly_df = compute_anomaly_flags(pivot, wow, thresholds)
    warnings = anomaly_df[anomaly_df["anomaly_flag"] == "warning"]
    criticals = anomaly_df[anomaly_df["anomaly_flag"] == "critical"]
    print(f"  {len(warnings)} warning, {len(criticals)} critical tespit edildi")

    # 6. Platform karşılaştırma
    print("► COMPARE: platform karşılaştırma tablosu oluşturuluyor...")
    comparison = compute_platform_comparison(pivot)

    # ---------------------------------------------------------------------------
    # Çıktılar
    # ---------------------------------------------------------------------------
    out_main = PROCESSED_DIR / f"weekly-metrics-{week}.csv"
    out_wow  = PROCESSED_DIR / f"wow-changes-{week}.csv"
    out_comp = PROCESSED_DIR / f"platform-comparison-{week}.csv"

    # Ana tablo: pivot + MA4  (NaN → "-")
    pivot_with_ma.to_csv(out_main, index=False, float_format="%.2f", na_rep="-")
    # WoW tablosu + anomali flag birleşimi
    wow_with_flags = wow.merge(
        anomaly_df[["week_start", "column", "anomaly_flag"]].pivot_table(
            index="week_start", columns="column", values="anomaly_flag", aggfunc="first"
        ).add_suffix("_flag").reset_index(),
        on="week_start",
        how="left",
    )
    wow_with_flags.to_csv(out_wow, index=False, float_format="%.2f", na_rep="-")
    comparison.to_csv(out_comp, index=False, float_format="%.2f", na_rep="-")

    print(f"\n✓ Çıktılar kaydedildi:")
    print(f"  {out_main}")
    print(f"  {out_wow}")
    print(f"  {out_comp}")

    # ---------------------------------------------------------------------------
    # Veri kaynağı özeti
    # ---------------------------------------------------------------------------
    print(f"\n{'─'*60}")
    print("  VERİ KAYNAĞI ÖZETİ")
    print(f"{'─'*60}")
    live_cols  = [c for c, s in _DATA_SOURCES.items() if s == "live"]
    empty_cols = [c for c, s in _DATA_SOURCES.items() if s == "empty"]
    print(f"  LIVE  ({len(live_cols)}): {', '.join(live_cols) or 'yok'}")
    print(f"  EMPTY ({len(empty_cols)}): {', '.join(empty_cols) or 'yok'}")

    # Rating değerleri farklı mı?
    if "ios_rating" in live_cols and "android_rating" in live_cols:
        ios_vals = pivot["ios_rating"].dropna().tolist()
        and_vals = pivot["android_rating"].dropna().tolist()
        print(f"\n  iOS rating (haftalık)    : {[round(v,2) for v in ios_vals]}")
        print(f"  Android rating (haftalık): {[round(v,2) for v in and_vals]}")
        all_same_ios = len(set(round(v,2) for v in ios_vals)) == 1
        all_same_and = len(set(round(v,2) for v in and_vals)) == 1
        if all_same_ios:
            print("  ⚠ iOS: Tüm haftalar aynı değer — review sayısı yetersiz olabilir")
        else:
            print("  ✓ iOS: Haftalar arasında farklı değerler var")
        if all_same_and:
            print("  ⚠ Android: Tüm haftalar aynı değer — review sayısı yetersiz olabilir")
        else:
            print("  ✓ Android: Haftalar arasında farklı değerler var")

    # Anomali özeti (sadece veri olan metrikler)
    if not criticals.empty:
        print(f"\n  ⚠ KRİTİK ANOMALİLER:")
        for _, r in criticals.iterrows():
            if pd.notna(r["value"]):
                print(f"    [{r['week_start'].date()}] {r['column']}: {r['value']} "
                      f"(WoW: {r['wow_pct']}%)")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
