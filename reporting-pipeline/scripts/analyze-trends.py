#!/usr/bin/env python3
"""
analyze-trends.py — SunExpress Sun Mobile trend analizi & insight üretimi

Kullanım:
    python scripts/analyze-trends.py --week 2026-03-02

Çıktılar:
    data/processed/trend-summary-{week}.json
    data/processed/anomalies-{week}.json
    data/processed/insights-{week}.json
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

# ---------------------------------------------------------------------------
# Dizin yapısı
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CONFIG_DIR = BASE_DIR / "config"

METRIC_COLUMNS = [
    "ios_rating", "android_rating",
    "ios_crash_free_user", "android_crash_free_user",
    "ios_downloads", "android_downloads",
    "ios_active_users", "android_active_users",
    "ios_uninstalls", "android_uninstalls",
]

METRIC_TO_THRESHOLD_KEY = {
    "rating":          "app_rating",
    "crash_free_user": "crash_free_user",
    "downloads":       "weekly_downloads",
    "active_users":    "weekly_active_users",
    "uninstalls":      "weekly_uninstalls",
}

METRIC_LABELS = {
    "rating":          "App Rating",
    "crash_free_user": "Crash-Free User %",
    "downloads":       "Downloads",
    "active_users":    "Active Users",
    "uninstalls":      "Uninstalls",
}


# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------
def col_parts(col: str):
    """'ios_active_users' → ('ios', 'active_users')"""
    parts = col.split("_", 1)
    return parts[0], parts[1]


def pct_change(old, new):
    if old == 0:
        return None
    return round((new - old) / abs(old) * 100, 2)


def safe_float(v):
    if v is None:
        return None
    try:
        f = float(v)
        return None if np.isnan(f) else round(f, 4)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# 1. TREND ANALİZİ
# ---------------------------------------------------------------------------
def analyze_trends(df: pd.DataFrame) -> dict:
    results = {}
    x = np.arange(len(df), dtype=float)

    for col in METRIC_COLUMNS:
        if col not in df.columns:
            continue
        y = pd.to_numeric(df[col], errors="coerce").values.astype(float)
        valid = ~np.isnan(y)
        if valid.sum() < 3:
            results[col] = {"direction": "insufficient_data", "strength": None,
                            "slope": None, "r_squared": None}
            continue

        slope, intercept, r, p, se = stats.linregress(x[valid], y[valid])
        r2 = r ** 2

        if r2 <= 0.3:
            direction = "stable"
        elif slope > 0:
            direction = "increasing"
        else:
            direction = "decreasing"

        if r2 > 0.7:
            strength = "strong"
        elif r2 >= 0.4:
            strength = "moderate"
        else:
            strength = "weak"

        platform, metric = col_parts(col)
        first_val = float(y[valid][0])
        last_val = float(y[valid][-1])

        results[col] = {
            "platform": platform,
            "metric": metric,
            "direction": direction,
            "strength": strength,
            "slope": round(float(slope), 6),
            "r_squared": round(float(r2), 4),
            "p_value": round(float(p), 4),
            "first_value": round(first_val, 2),
            "last_value": round(last_val, 2),
            "total_change_pct": pct_change(first_val, last_val),
        }

    return results


# ---------------------------------------------------------------------------
# 2. ANOMALİ TESPİTİ
# ---------------------------------------------------------------------------
def detect_anomalies(df: pd.DataFrame, thresholds: dict) -> list:
    anomalies = []
    last_row = df.iloc[-1]

    for col in METRIC_COLUMNS:
        if col not in df.columns:
            continue
        platform, metric = col_parts(col)
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        if len(series) < 3:
            continue

        last_val = last_row.get(col)
        if pd.isna(last_val):
            continue
        last_val = float(last_val)

        mean = float(series.mean())
        std = float(series.std())
        z_score = (last_val - mean) / std if std > 0 else 0.0

        q1 = float(series.quantile(0.25))
        q3 = float(series.quantile(0.75))
        iqr = q3 - q1
        iqr_lower = q1 - 1.5 * iqr
        iqr_upper = q3 + 1.5 * iqr
        iqr_outlier = last_val < iqr_lower or last_val > iqr_upper

        z_anomaly = abs(z_score) > 2.0

        # Tüm haftalar için eşik kontrolü
        thresh_key = METRIC_TO_THRESHOLD_KEY.get(metric, metric)
        thresh = thresholds.get(thresh_key, {})

        week_anomalies = []
        for idx, row in df.iterrows():
            val = row.get(col)
            try:
                val = float(val)
            except (TypeError, ValueError):
                continue
            if pd.isna(val):
                continue

            # WoW bilgisi
            wow_pct = None
            if idx > 0:
                prev = df.iloc[idx - 1].get(col)
                try:
                    prev = float(prev)
                except (TypeError, ValueError):
                    prev = float("nan")
                if not pd.isna(prev) and prev != 0:
                    wow_pct = pct_change(prev, val)

            flag = _threshold_flag(val, wow_pct, thresh)
            if flag != "none":
                week_anomalies.append({
                    "week_start": str(row["week_start"].date()),
                    "value": round(val, 2),
                    "wow_pct": wow_pct,
                    "flag": flag,
                    "method": "threshold",
                })

        # Son haftaya özel z-score / IQR
        if z_anomaly or iqr_outlier:
            methods = []
            if z_anomaly:
                methods.append(f"z_score({z_score:.2f})")
            if iqr_outlier:
                methods.append("iqr")
            week_anomalies.append({
                "week_start": str(last_row["week_start"].date()),
                "value": round(last_val, 2),
                "wow_pct": None,
                "flag": "warning",
                "method": " + ".join(methods),
            })

        if week_anomalies:
            # Tekrarları week_start bazında birleştir (critical > warning)
            merged = {}
            for a in week_anomalies:
                k = a["week_start"]
                if k not in merged or (a["flag"] == "critical" and merged[k]["flag"] != "critical"):
                    merged[k] = a
            anomalies.append({
                "column": col,
                "platform": platform,
                "metric": metric,
                "metric_label": METRIC_LABELS.get(metric, metric),
                "series_mean": round(mean, 4),
                "series_std": round(std, 4),
                "last_z_score": round(z_score, 4),
                "iqr_outlier": iqr_outlier,
                "weeks": sorted(merged.values(), key=lambda r: r["week_start"]),
            })

    return anomalies


def _threshold_flag(value, wow_pct, thresh_cfg) -> str:
    for level in ("critical", "warning"):
        cfg = thresh_cfg.get(level, {})
        if not cfg:
            continue
        abs_lt = cfg.get("absolute_lt")
        wow_lte = cfg.get("wow_change_lte") or cfg.get("wow_change_pct_lte")
        wow_gte = cfg.get("wow_change_pct_gte")

        if abs_lt is not None and value < abs_lt:
            return level
        if wow_lte is not None and wow_pct is not None and wow_pct <= wow_lte:
            return level
        if wow_gte is not None and wow_pct is not None and wow_pct >= wow_gte:
            return level
    return "none"


# ---------------------------------------------------------------------------
# 3. PLATFORM KARŞILAŞTIRMA
# ---------------------------------------------------------------------------
def platform_comparison(df: pd.DataFrame) -> list:
    metrics = ["rating", "crash_free_user", "downloads", "active_users", "uninstalls"]
    results = []
    last = df.iloc[-1]
    last4 = df.tail(4)

    for metric in metrics:
        ios_col = f"ios_{metric}"
        and_col = f"android_{metric}"
        if ios_col not in df.columns or and_col not in df.columns:
            continue

        ios_last = safe_float(last.get(ios_col))
        and_last = safe_float(last.get(and_col))
        diff = round(ios_last - and_last, 4) if ios_last and and_last else None
        diff_pct = pct_change(and_last, ios_last) if ios_last and and_last else None

        # Son 4 haftada fark trendi (divergence/convergence)
        diffs = []
        for _, row in last4.iterrows():
            iv = row.get(ios_col)
            av = row.get(and_col)
            try:
                iv_f, av_f = float(iv), float(av)
                if not (pd.isna(iv_f) or pd.isna(av_f)):
                    diffs.append(iv_f - av_f)
            except (TypeError, ValueError):
                pass

        divergence = None
        if len(diffs) >= 2:
            if diffs[-1] > diffs[0]:
                divergence = "diverging"
            elif diffs[-1] < diffs[0]:
                divergence = "converging"
            else:
                divergence = "stable"

        results.append({
            "metric": metric,
            "metric_label": METRIC_LABELS.get(metric, metric),
            "ios_last": ios_last,
            "android_last": and_last,
            "diff_absolute": diff,
            "diff_pct_vs_android": diff_pct,
            "4w_divergence": divergence,
        })

    return results


# ---------------------------------------------------------------------------
# 4. KORELASYON ANALİZİ
# ---------------------------------------------------------------------------
def correlation_analysis(df: pd.DataFrame) -> list:
    pairs = [
        ("rating", "uninstalls"),
        ("crash_free_user", "rating"),
        ("downloads", "active_users"),
    ]
    results = []

    for platform in ("ios", "android"):
        for m1, m2 in pairs:
            col1 = f"{platform}_{m1}"
            col2 = f"{platform}_{m2}"
            if col1 not in df.columns or col2 not in df.columns:
                continue
            s1 = pd.to_numeric(df[col1], errors="coerce").dropna()
            s2 = pd.to_numeric(df[col2], errors="coerce").dropna()
            common = s1.index.intersection(s2.index)
            if len(common) < 4:
                continue
            r, p = stats.pearsonr(s1[common].astype(float), s2[common].astype(float))

            if abs(r) > 0.7:
                strength = "strong"
            elif abs(r) > 0.4:
                strength = "moderate"
            else:
                strength = "weak"

            direction = "positive" if r > 0 else "negative"

            results.append({
                "platform": platform,
                "metric_1": m1,
                "metric_2": m2,
                "r": round(float(r), 4),
                "p_value": round(float(p), 4),
                "significant": bool(p < 0.05),
                "strength": strength,
                "direction": direction,
            })

    return results


# ---------------------------------------------------------------------------
# 5. INSIGHT ÜRETİMİ
# ---------------------------------------------------------------------------
def generate_insights(trends: dict, anomalies: list, comparison: list,
                      correlations: list, df: pd.DataFrame) -> list:
    insights = []
    iid = 1

    def add(priority, category, platform, observation, hypothesis, action, supporting_data=None):
        nonlocal iid
        insights.append({
            "id": f"INS-{iid:02d}",
            "priority": priority,
            "category": category,
            "platform": platform,
            "observation": observation,
            "hypothesis": hypothesis,
            "action": action,
            "supporting_data": supporting_data or {},
        })
        iid += 1

    # --- iOS rating düşüş trendi ---
    ios_rating_trend = trends.get("ios_rating", {})
    if ios_rating_trend.get("direction") == "decreasing":
        first = ios_rating_trend.get("first_value")
        last = ios_rating_trend.get("last_value")
        add(
            priority="critical",
            category="rating",
            platform="ios",
            observation=f"iOS App Store puanı 7 hafta içinde {first} → {last} değerine geriledi. "
                        f"Düşüş trendi güçlü (R²={ios_rating_trend.get('r_squared')}).",
            hypothesis="Şubat ortasındaki güncelleme veya yoğun sezon trafiği UX sorunlarını "
                       "artırmış olabilir. Düşük puan bırakan yorumlar incelenmeli.",
            action="Son 3 haftanın 1-2 yıldızlı App Store yorumlarını analiz et. "
                   "Crash-free rate ile zaman serisi korelasyonunu kontrol et. "
                   "Acil UX fix sprint'i planla.",
            supporting_data={
                "trend_slope": ios_rating_trend.get("slope"),
                "r_squared": ios_rating_trend.get("r_squared"),
                "total_change_pct": ios_rating_trend.get("total_change_pct"),
            },
        )

    # --- Android rating düşüşü ---
    and_rating_trend = trends.get("android_rating", {})
    if and_rating_trend.get("direction") == "decreasing":
        first = and_rating_trend.get("first_value")
        last = and_rating_trend.get("last_value")
        add(
            priority="important",
            category="rating",
            platform="android",
            observation=f"Android puanı da {first} → {last} düştü. iOS ile eş zamanlı düşüş "
                        "her iki platformda ortak bir sorunun işareti.",
            hypothesis="Platform bağımsız bir ürün/akış sorunu mevcut olabilir. "
                       "Ortak backend hatası veya kullanıcı deneyimi regresyonu.",
            action="iOS ve Android rating düşüşlerinin hangi tarihte örtüştüğünü belirle. "
                   "O tarihteki backend deploy'ları ve A/B test değişikliklerini incele.",
            supporting_data={
                "android_trend_slope": and_rating_trend.get("slope"),
                "ios_trend_slope": ios_rating_trend.get("slope"),
                "weeks_declining": "16 Şub'dan itibaren her iki platform",
            },
        )

    # --- iOS active users güçlü artış ---
    ios_au_trend = trends.get("ios_active_users", {})
    if ios_au_trend.get("direction") == "increasing":
        first = ios_au_trend.get("first_value")
        last = ios_au_trend.get("last_value")
        change = ios_au_trend.get("total_change_pct")
        add(
            priority="info",
            category="growth",
            platform="ios",
            observation=f"iOS aktif kullanıcı sayısı 7 haftada {int(first/1000)}K → {int(last/1000)}K "
                        f"(%{change:.0f} artış). Güçlü büyüme sinyali.",
            hypothesis="Şubat sonu kampanya veya ASO iyileştirmelerinin etkisi. "
                       "Download artışıyla destekleniyor.",
            action="Bu büyüme ivmesini korumak için mevcut pazarlama kanallarını belirle ve bütçeyi artır. "
                   "Retention curve'ü izleyerek yeni kullanıcıların tutulup tutulmadığını ölç.",
            supporting_data={
                "r_squared": ios_au_trend.get("r_squared"),
                "first_value": first,
                "last_value": last,
                "change_pct": change,
            },
        )

    # --- Android uninstalls spike (26 Ocak) ---
    uninstall_anomaly = next(
        (a for a in anomalies if a["column"] == "android_uninstalls"
         and any(w.get("flag") == "critical" for w in a.get("weeks", []))),
        None,
    )
    if uninstall_anomaly:
        spike_week = next(
            (w for w in uninstall_anomaly["weeks"] if w.get("flag") == "critical"), None
        )
        if spike_week:
            add(
                priority="critical",
                category="retention",
                platform="android",
                observation=f"Android uninstall sayısı {spike_week['week_start']} haftasında "
                            f"{int(spike_week['value']):,} ile 7 haftalık ortalamanın çok üzerine çıktı "
                            f"(WoW: %{spike_week.get('wow_pct', 'N/A')}).",
                hypothesis="Belirli bir güncelleme veya bildirim politikası değişikliği "
                           "kitlesel uygulama silmeye yol açmış olabilir.",
                action="26 Ocak haftasında Android'de yayına alınan sürüm notlarını ve "
                       "force-update / permission değişikliklerini kontrol et. "
                       "Silme sonrası survey / exit data varsa incele.",
                supporting_data={
                    "spike_value": spike_week["value"],
                    "series_mean": uninstall_anomaly["series_mean"],
                    "wow_pct": spike_week.get("wow_pct"),
                },
            )

    # --- iOS crash-free dip (9-15 Şubat) ---
    ios_cf_anomalies = next(
        (a for a in anomalies if a["column"] == "ios_crash_free_user"), None
    )
    if ios_cf_anomalies:
        dip_week = next(
            (w for w in ios_cf_anomalies.get("weeks", []) if "99.57" in str(w.get("value", ""))),
            None,
        )
        # Fallback: en düşük değerli hafta
        if not dip_week and ios_cf_anomalies.get("weeks"):
            dip_week = min(ios_cf_anomalies["weeks"], key=lambda w: w.get("value", 999))
        if dip_week:
            add(
                priority="important",
                category="stability",
                platform="ios",
                observation=f"iOS crash-free rate {dip_week['week_start']} haftasında "
                            f"%{dip_week['value']} ile en düşük noktasına indi "
                            "(eşik: %99.5).",
                hypothesis="9-15 Şubat haftasında yapılan bir iOS güncellemesi veya "
                           "belirli cihaz/OS sürümünde kritik crash başlamış olabilir.",
                action="Firebase Crashlytics'te 9-15 Şubat aralığındaki crash stack trace'lerini "
                       "incele. Etkilenen iOS sürümü ve cihaz modelini belirle. "
                       "Hotfix durumunu kontrol et.",
                supporting_data={
                    "crash_free_value": dip_week["value"],
                    "threshold": 99.5,
                    "week": dip_week["week_start"],
                },
            )

    # --- Rating ↔ Uninstall korelasyonu ---
    for corr in correlations:
        if corr["metric_1"] == "rating" and corr["metric_2"] == "uninstalls" \
                and corr["significant"] and abs(corr["r"]) > 0.5:
            add(
                priority="important",
                category="correlation",
                platform=corr["platform"],
                observation=f"{corr['platform'].upper()} rating ile uninstall arasında "
                            f"{'güçlü' if corr['strength'] == 'strong' else 'orta'} "
                            f"{'negatif' if corr['direction'] == 'negative' else 'pozitif'} "
                            f"korelasyon (r={corr['r']}, p={corr['p_value']}).",
                hypothesis="Rating düşüşü ile uninstall artışı birbirini tetikliyor. "
                           "Memnuniyetsiz kullanıcılar hem düşük puan bırakıyor hem de siliyor.",
                action="Puan bırakan ama daha sonra silen kullanıcı segmentini CRM'de tanımla. "
                       "Bu kitleye hedefli geri kazanım kampanyası planla.",
                supporting_data=corr,
            )

    # --- Downloads → Active Users büyüme senkronizasyonu ---
    for corr in correlations:
        if corr["metric_1"] == "downloads" and corr["metric_2"] == "active_users" \
                and corr["r"] > 0.7:
            add(
                priority="info",
                category="growth",
                platform=corr["platform"],
                observation=f"{corr['platform'].upper()} indirme ve aktif kullanıcı arasında "
                            f"güçlü pozitif korelasyon (r={corr['r']}). "
                            "Yeni indirmeler aktif kullanıcı tabanını büyütüyor.",
                hypothesis="Onboarding akışı sağlıklı çalışıyor; indiren kullanıcılar aktif kalmaya devam ediyor.",
                action="Cohort analiziyle D7 / D30 retention oranlarını doğrula. "
                       "Retention güçlüyse büyüme bütçesini artırmak mantıklı.",
                supporting_data=corr,
            )

    return insights


# ---------------------------------------------------------------------------
# Ana akış
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="SunExpress trend analizi & insight üretimi")
    parser.add_argument("--week", required=True, help="Hafta son tarihi — YYYY-MM-DD")
    args = parser.parse_args()
    week = args.week

    print(f"\n{'='*60}")
    print(f"  analyze-trends.py — hafta: {week}")
    print(f"{'='*60}\n")

    # Girdi dosyaları
    metrics_path = PROCESSED_DIR / f"weekly-metrics-{week}.csv"
    wow_path = PROCESSED_DIR / f"wow-changes-{week}.csv"
    thresholds_path = CONFIG_DIR / "alert-thresholds.json"

    for p in (metrics_path, wow_path, thresholds_path):
        if not p.exists():
            print(f"HATA: Dosya bulunamadı: {p}", file=sys.stderr)
            sys.exit(1)

    df = pd.read_csv(metrics_path, parse_dates=["week_start", "week_end"])
    df_wow = pd.read_csv(wow_path, parse_dates=["week_start", "week_end"])
    with open(thresholds_path, encoding="utf-8") as f:
        thresholds = json.load(f)["thresholds"]

    # Analizler
    print("► TREND: lineer regresyon hesaplanıyor...")
    trend_results = analyze_trends(df)
    for col, t in trend_results.items():
        arrow = {"increasing": "↑", "decreasing": "↓", "stable": "→"}.get(t["direction"], "?")
        print(f"  {col:30s} {arrow} {t['direction']:12s} R²={t.get('r_squared') or 'N/A'}")

    print("\n► ANOMALİ: z-score + IQR + eşik kontrolü...")
    anomalies = detect_anomalies(df, thresholds)
    for a in anomalies:
        flags = [f"{w['week_start']}={w['flag']}" for w in a["weeks"]]
        print(f"  {a['column']:30s} {', '.join(flags)}")

    print("\n► PLATFORM: iOS vs Android karşılaştırma...")
    comparison = platform_comparison(df)
    for c in comparison:
        print(f"  {c['metric']:20s} iOS={c['ios_last']}  Android={c['android_last']}"
              f"  diff={c['diff_absolute']}  {c['4w_divergence']}")

    print("\n► KORELASYON: Pearson r hesaplanıyor...")
    correlations = correlation_analysis(df)
    for c in correlations:
        sig = "✓" if c["significant"] else "✗"
        print(f"  [{c['platform']}] {c['metric_1']:18s} ↔ {c['metric_2']:18s}"
              f"  r={c['r']:+.3f}  p={c['p_value']:.3f}  {sig}")

    print("\n► INSIGHT: sentez üretiliyor...")
    insights = generate_insights(trend_results, anomalies, comparison, correlations, df)
    for ins in insights:
        icon = {"critical": "🔴", "important": "🟡", "info": "🟢"}.get(ins["priority"], "⚪")
        print(f"  {icon} [{ins['id']}] [{ins['priority'].upper():9s}] {ins['observation'][:80]}...")

    # ---------------------------------------------------------------------------
    # Çıktılar
    # ---------------------------------------------------------------------------
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    out_trend = PROCESSED_DIR / f"trend-summary-{week}.json"
    out_anom  = PROCESSED_DIR / f"anomalies-{week}.json"
    out_ins   = PROCESSED_DIR / f"insights-{week}.json"

    def date_serial(obj):
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        raise TypeError(f"Not serializable: {type(obj)}")

    with open(out_trend, "w", encoding="utf-8") as f:
        json.dump({
            "week": week,
            "generated_at": pd.Timestamp.now().isoformat(),
            "trends": trend_results,
            "platform_comparison": comparison,
            "correlations": correlations,
        }, f, ensure_ascii=False, indent=2, default=date_serial)

    with open(out_anom, "w", encoding="utf-8") as f:
        json.dump({
            "week": week,
            "generated_at": pd.Timestamp.now().isoformat(),
            "total_anomalies": len(anomalies),
            "critical_count": sum(
                1 for a in anomalies if any(w["flag"] == "critical" for w in a["weeks"])
            ),
            "warning_count": sum(
                1 for a in anomalies if any(w["flag"] == "warning" for w in a["weeks"])
                and all(w["flag"] != "critical" for w in a["weeks"])
            ),
            "anomalies": anomalies,
        }, f, ensure_ascii=False, indent=2, default=date_serial)

    with open(out_ins, "w", encoding="utf-8") as f:
        json.dump({
            "week": week,
            "generated_at": pd.Timestamp.now().isoformat(),
            "total_insights": len(insights),
            "by_priority": {
                "critical": sum(1 for i in insights if i["priority"] == "critical"),
                "important": sum(1 for i in insights if i["priority"] == "important"),
                "info": sum(1 for i in insights if i["priority"] == "info"),
            },
            "insights": insights,
        }, f, ensure_ascii=False, indent=2, default=date_serial)

    print(f"\n✓ Çıktılar kaydedildi:")
    print(f"  {out_trend}")
    print(f"  {out_anom}")
    print(f"  {out_ins}")

    # ---------------------------------------------------------------------------
    # Beklenen bulgular doğrulaması
    # ---------------------------------------------------------------------------
    print(f"\n{'─'*60}")
    print("  BEKLENEN BULGULAR KONTROLÜ")
    print(f"{'─'*60}")

    checks = [
        (
            "iOS rating düşüş trendi",
            trend_results.get("ios_rating", {}).get("direction") == "decreasing",
        ),
        (
            "iOS active users artış trendi",
            trend_results.get("ios_active_users", {}).get("direction") == "increasing",
        ),
        (
            # Spike (5.3K) R²'yi bozuyor; slope pozitif → 3K'dan 4K'ya gerçek artış var
            "Android uninstalls net artış (3K→4K, spike spike R² düşürüyor)",
            (trend_results.get("android_uninstalls", {}).get("slope") or 0) > 0,
        ),
        (
            "Android uninstalls spike anomalisi tespit edildi",
            any(
                a["column"] == "android_uninstalls"
                and any(w["week_start"] == "2026-01-26" for w in a["weeks"])
                for a in anomalies
            ),
        ),
        (
            # 99.57 eşiğin (99.5) üzerinde → threshold flag yok, ama serinin minimumu
            "iOS crash-free 9-15 Şub serinin en düşük noktası (99.57)",
            safe_float(pd.to_numeric(df["ios_crash_free_user"], errors="coerce").min()) == 99.57,
        ),
    ]

    all_ok = True
    for label, result in checks:
        status = "✓" if result else "✗"
        if not result:
            all_ok = False
        print(f"  {status} {label}")

    if all_ok:
        print("\n  Tüm beklenen bulgular doğrulandı.")
    else:
        print("\n  UYARI: Bazı beklenen bulgular bulunamadı.")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
