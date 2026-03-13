#!/usr/bin/env python3
"""
collect-ratings.py — App Store & Google Play haftalık rating toplayıcı

Kullanım:
    python scripts/collect-ratings.py
    python scripts/collect-ratings.py --date 2026-03-02
    python scripts/collect-ratings.py --countries tr,de,gb
"""

import argparse
import json
import time
import warnings
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Dizinler & sabitler
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR  = BASE_DIR / "data" / "raw"

IOS_APP_IDS   = ["6630384355", "1524475114"]
ANDROID_PKGS  = ["com.sunexpress.lite", "com.sunexpress.app"]

# Raporlama hafta aralıkları (Pazartesi–Pazar)
WEEKS = [
    ("2026-01-12", "2026-01-18"),
    ("2026-01-19", "2026-01-25"),
    ("2026-01-26", "2026-02-01"),
    ("2026-02-02", "2026-02-08"),
    ("2026-02-09", "2026-02-15"),
    ("2026-02-16", "2026-02-22"),
    ("2026-02-23", "2026-03-01"),
    ("2026-03-02", "2026-03-08"),
]

MIN_REVIEWS_PER_WEEK = 5   # altında → insufficient_data


# ---------------------------------------------------------------------------
# Haftalık gruplama
# ---------------------------------------------------------------------------
def build_weekly_buckets(reviews: list, date_field="date", score_field="score") -> list:
    """
    Review listesini WEEKS tablosuna göre haftalık bucket'a atar.
    Her bucket: value (ort. rating), review_count, histogram [1★..5★]
    """
    buckets = {ws: [] for ws, _ in WEEKS}

    for r in reviews:
        dt = r.get(date_field)
        score = r.get(score_field)
        if not dt or score is None:
            continue
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        dt_date = dt.date()

        for ws, we in WEEKS:
            ws_d = date.fromisoformat(ws)
            we_d = date.fromisoformat(we)
            if ws_d <= dt_date <= we_d:
                buckets[ws].append(int(score))
                break

    result = []
    for ws, we in WEEKS:
        scores = buckets[ws]
        n = len(scores)
        if n < MIN_REVIEWS_PER_WEEK:
            result.append({
                "week_start":    ws,
                "week_end":      we,
                "value":         None,
                "review_count":  n,
                "histogram":     None,
                "status":        "insufficient_data",
            })
        else:
            avg = round(sum(scores) / n, 2)
            hist = [scores.count(i) for i in range(1, 6)]
            result.append({
                "week_start":    ws,
                "week_end":      we,
                "value":         avg,
                "review_count":  n,
                "histogram":     hist,
                "status":        "ok",
            })
    return result


# ---------------------------------------------------------------------------
# iOS — App Store RSS feed (tüm sayfalar)
# ---------------------------------------------------------------------------
def fetch_ios_reviews_rss(app_id: str, country: str = "tr") -> list:
    """iTunes RSS customerreviews — max 10 sayfa × 50 = 500 entry."""
    all_reviews = []
    for page in range(1, 11):
        url = (f"https://itunes.apple.com/{country}/rss/customerreviews"
               f"/page={page}/id={app_id}/sortBy=mostRecent/json")
        try:
            r = requests.get(url, timeout=12,
                             headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            data = r.json()
            entries = data.get("feed", {}).get("entry", [])
            if not entries:
                break
            if not isinstance(entries, list):
                entries = [entries]

            for e in entries:
                if not isinstance(e, dict):
                    continue
                raw_date = e.get("updated", {}).get("label", "")
                raw_score = e.get("im:rating", {}).get("label")
                if not raw_date or raw_score is None:
                    continue
                try:
                    dt = datetime.fromisoformat(raw_date)
                    score = int(raw_score)
                    all_reviews.append({"date": dt, "score": score,
                                        "version": e.get("im:version", {}).get("label", "")})
                except Exception:
                    continue

            time.sleep(0.3)
        except Exception as e:
            print(f"    ⚠ RSS p{page} [{country}]: {e}")
            break

    return all_reviews


def collect_ios(today_str: str) -> dict:
    print("\n── iOS Rating (App Store RSS) ──────────────────────────")

    reviews_all = []
    used_id = None

    for app_id in IOS_APP_IDS:
        print(f"  ID {app_id} deneniyor...")
        revs = fetch_ios_reviews_rss(app_id, "tr")
        if revs:
            used_id = app_id
            reviews_all = revs
            print(f"  ✓ {len(revs)} review alındı (ID: {app_id})")
            break
        else:
            print(f"  ✗ Review yok")

    if not reviews_all:
        print("  ✗ iOS review çekilemedi.")
        return {}

    # Tarih filtresi: period içindeki reviewlar
    period_start = date.fromisoformat(WEEKS[0][0])
    period_end   = date.fromisoformat(WEEKS[-1][1])
    in_period    = [r for r in reviews_all
                    if period_start <= r["date"].date() <= period_end]

    print(f"  Period içinde ({WEEKS[0][0]} – {WEEKS[-1][1]}): {len(in_period)} review")

    weekly = build_weekly_buckets(in_period)

    # iTunes lookup — genel rating için
    general_rating = None
    try:
        lu = requests.get(
            f"https://itunes.apple.com/lookup?id={used_id}&country=tr",
            timeout=10, headers={"User-Agent": "Mozilla/5.0"}
        ).json()
        if lu.get("resultCount", 0) > 0:
            r0 = lu["results"][0]
            general_rating = {
                "overall": round(r0.get("averageUserRating", 0), 2),
                "total_count": r0.get("userRatingCount", 0),
                "version": r0.get("version", "N/A"),
                "app_name": r0.get("trackName", "N/A"),
            }
            print(f"  Genel rating: {general_rating['overall']} ★"
                  f"  ({general_rating['total_count']:,} yorum)"
                  f"  v{general_rating['version']}")
    except Exception as e:
        print(f"  ⚠ iTunes lookup: {e}")

    return {
        "app_name":        "SunExpress",
        "app_id":          used_id,
        "platform":        "ios",
        "metric":          "rating",
        "collection_date": datetime.now(timezone.utc).isoformat(),
        "source":          "app_store_rss",
        "live":            True,
        "general":         general_rating,
        "period": {
            "start":       WEEKS[0][0],
            "end":         WEEKS[-1][1],
            "granularity": "weekly",
        },
        "data": weekly,
    }


# ---------------------------------------------------------------------------
# Android — google-play-scraper
# ---------------------------------------------------------------------------
def collect_android(today_str: str) -> dict:
    print("\n── Android Rating (Google Play Scraper) ────────────────")

    try:
        from google_play_scraper import app as gplay_app, reviews as gplay_reviews, Sort
    except ImportError:
        print("  ✗ google-play-scraper kurulu değil.")
        return {}

    reviews_all = []
    used_pkg    = None
    app_info    = None

    for pkg in ANDROID_PKGS:
        print(f"  {pkg} deneniyor...")
        try:
            app_info = gplay_app(pkg, lang="tr", country="tr")
            # Review'ları çek — count=500 en son yorumlar
            result, _ = gplay_reviews(pkg, lang="tr", country="tr",
                                      sort=Sort.NEWEST, count=500)
            reviews_all = result
            used_pkg    = pkg
            print(f"  ✓ {len(reviews_all)} review alındı ({pkg})")
            break
        except Exception as e:
            print(f"  ✗ {e}")

    if not reviews_all:
        print("  ✗ Android review çekilemedi.")
        return {}

    # Normalize format
    normalized = []
    for r in reviews_all:
        at = r.get("at")
        if not at:
            continue
        if isinstance(at, str):
            at = datetime.fromisoformat(at)
        if at.tzinfo is None:
            at = at.replace(tzinfo=timezone.utc)
        normalized.append({"date": at, "score": r.get("score", 0)})

    # Tarih filtresi
    period_start = date.fromisoformat(WEEKS[0][0])
    period_end   = date.fromisoformat(WEEKS[-1][1])
    in_period    = [r for r in normalized
                    if period_start <= r["date"].date() <= period_end]

    print(f"  Period içinde ({WEEKS[0][0]} – {WEEKS[-1][1]}): {len(in_period)} review")

    weekly = build_weekly_buckets(in_period)

    if app_info:
        print(f"  Genel rating: {round(app_info.get('score',0),2)} ★"
              f"  ({app_info.get('ratings',0):,} yorum)"
              f"  v{app_info.get('version','N/A')}")

    return {
        "app_name":        "SunExpress",
        "package_name":    used_pkg,
        "platform":        "android",
        "metric":          "rating",
        "collection_date": datetime.now(timezone.utc).isoformat(),
        "source":          "google_play_scraper",
        "live":            True,
        "general": {
            "overall":     round(app_info.get("score", 0), 2) if app_info else None,
            "total_count": app_info.get("ratings", 0) if app_info else 0,
            "version":     app_info.get("version", "N/A") if app_info else "N/A",
            "installs":    app_info.get("installs", "N/A") if app_info else "N/A",
        },
        "period": {
            "start":       WEEKS[0][0],
            "end":         WEEKS[-1][1],
            "granularity": "weekly",
        },
        "data": weekly,
    }


# ---------------------------------------------------------------------------
# Mock veri oku
# ---------------------------------------------------------------------------
def load_mock(platform: str) -> dict:
    path = RAW_DIR / f"{platform}_rating_2026-03-02.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    return {entry["week_start"]: entry["value"] for entry in d.get("data", [])}


# ---------------------------------------------------------------------------
# Karşılaştırma tablosu
# ---------------------------------------------------------------------------
def print_comparison(ios_data: dict, android_data: dict):
    ios_mock     = load_mock("ios")
    android_mock = load_mock("android")

    ios_live     = {e["week_start"]: e for e in ios_data.get("data", [])}
    android_live = {e["week_start"]: e for e in android_data.get("data", [])}

    col_w = [17, 12, 12, 16, 16]
    header = (f"{'Hafta':<{col_w[0]}} {'iOS (mock)':>{col_w[1]}} {'iOS (live)':>{col_w[2]}}"
              f" {'Android (mock)':>{col_w[3]}} {'Android (live)':>{col_w[4]}}")

    print(f"\n{'─'*80}")
    print("  KARŞILAŞTIRMA TABLOSU — Mock vs Canlı")
    print(f"{'─'*80}")
    print(f"  {header}")
    print(f"  {'─'*78}")

    def fmt_live(entry):
        if not entry:
            return "no data"
        if entry.get("status") == "insufficient_data":
            return f"insuf. (n={entry['review_count']})"
        v = entry.get("value")
        n = entry.get("review_count", 0)
        return f"{v:.2f} (n={n})" if v else "—"

    for ws, we in WEEKS:
        label = f"{ws[5:]} – {we[5:]}"
        ios_m   = ios_mock.get(ws)
        and_m   = android_mock.get(ws)
        ios_l   = ios_live.get(ws)
        and_l   = android_live.get(ws)

        ios_m_str  = f"{ios_m:.1f}"  if ios_m  else "—"
        and_m_str  = f"{and_m:.1f}" if and_m else "—"
        ios_l_str  = fmt_live(ios_l)
        and_l_str  = fmt_live(and_l)

        # Fark göster
        delta_ios = ""
        if ios_m and ios_l and ios_l.get("value"):
            d = ios_l["value"] - ios_m
            delta_ios = f" ({'+' if d>=0 else ''}{d:.2f})"

        delta_and = ""
        if and_m and and_l and and_l.get("value"):
            d = and_l["value"] - and_m
            delta_and = f" ({'+' if d>=0 else ''}{d:.2f})"

        print(f"  {label:<{col_w[0]}} {ios_m_str:>{col_w[1]}} "
              f"{(ios_l_str + delta_ios):>{col_w[2]+8}} "
              f"{and_m_str:>{col_w[3]}} "
              f"{(and_l_str + delta_and):>{col_w[4]+8}}")

    print(f"  {'─'*78}\n")


# ---------------------------------------------------------------------------
# JSON kaydet
# ---------------------------------------------------------------------------
def save_json(data: dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    print(f"  → {path.name}  ({path.stat().st_size/1024:.1f} KB)")


# ---------------------------------------------------------------------------
# Ana akış
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Haftalık rating toplayıcı")
    parser.add_argument("--date", default="2026-03-02",
                        help="Çıktı dosyası tarih etiketi (varsayılan: 2026-03-02)")
    parser.add_argument("--countries", default="tr,de,gb",
                        help="Ülke kodları (iOS lookup için)")
    args = parser.parse_args()
    file_date = args.date

    print(f"\n{'='*60}")
    print(f"  collect-ratings.py — haftalık mod")
    print(f"  Period: {WEEKS[0][0]} → {WEEKS[-1][1]}")
    print(f"{'='*60}")

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    ios_data     = collect_ios(file_date)
    android_data = collect_android(file_date)

    print(f"\n── Dosyalar kaydediliyor...")
    if ios_data:
        save_json(ios_data,     RAW_DIR / f"ios_rating_live_{file_date}.json")
    if android_data:
        save_json(android_data, RAW_DIR / f"android_rating_live_{file_date}.json")

    print_comparison(ios_data, android_data)

    # Haftalık özet
    print("  VERİ KALİTESİ")
    print(f"  {'─'*40}")
    for platform, data in [("iOS", ios_data), ("Android", android_data)]:
        if not data:
            print(f"  {platform}: veri yok")
            continue
        weeks_ok     = sum(1 for e in data["data"] if e["status"] == "ok")
        weeks_insuf  = sum(1 for e in data["data"] if e["status"] == "insufficient_data")
        total_rev    = sum(e["review_count"] for e in data["data"])
        general      = data.get("general", {}) or {}
        print(f"  {platform}: {weeks_ok}/{len(data['data'])} hafta yeterli veri"
              f"  |  toplam {total_rev} period review"
              f"  |  genel rating {general.get('overall','—')} ★")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
