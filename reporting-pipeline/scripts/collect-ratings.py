#!/usr/bin/env python3
"""
collect-ratings.py — App Store & Google Play haftalık review ortalaması toplayıcı

Her haftanın kendi ortalama rating'ini hesaplar (review tarihine göre gruplama).
Birden fazla ülkeden review toplayıp birleştirir.

Kullanım:
    python scripts/collect-ratings.py
    python scripts/collect-ratings.py --date 2026-03-09
"""

import argparse
import json
import time
import warnings
from datetime import date, datetime, timezone, timedelta
from pathlib import Path

import requests

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Sabitler
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR  = BASE_DIR / "data" / "raw"

IOS_APP_IDS  = ["6630384355", "1524475114"]
ANDROID_PKGS = ["com.sunexpress.lite", "com.sunexpress.app"]

# Review çekilecek ülkeler (az + çok kullanan pazarlar)
REVIEW_COUNTRIES = ["tr", "de", "gb", "nl", "at", "ch", "fr"]

# Rapor hafta aralıkları (Pazartesi–Pazar)
WEEKS = [
    ("2026-01-19", "2026-01-25"),
    ("2026-01-26", "2026-02-01"),
    ("2026-02-02", "2026-02-08"),
    ("2026-02-09", "2026-02-15"),
    ("2026-02-16", "2026-02-22"),
    ("2026-02-23", "2026-03-01"),
    ("2026-03-02", "2026-03-08"),
]

PERIOD_START = date.fromisoformat(WEEKS[0][0])
PERIOD_END   = date.fromisoformat(WEEKS[-1][1])
MIN_REVIEWS  = 5     # Bu altı → insufficient_data
RATE_SLEEP   = 0.4   # saniye


# ---------------------------------------------------------------------------
# Haftalık gruplama
# ---------------------------------------------------------------------------
def build_weekly_buckets(reviews: list) -> list:
    """
    [{"date": datetime, "score": int}] listesini WEEKS'e göre gruplar.
    Döner: [{"week_start", "week_end", "value", "review_count", "status"}, ...]
    """
    buckets = {ws: [] for ws, _ in WEEKS}

    for r in reviews:
        dt = r.get("date")
        score = r.get("score")
        if not dt or score is None:
            continue
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt)
        d = dt.date() if hasattr(dt, "date") else dt
        for ws, we in WEEKS:
            if date.fromisoformat(ws) <= d <= date.fromisoformat(we):
                buckets[ws].append(int(score))
                break

    result = []
    for ws, we in WEEKS:
        scores = buckets[ws]
        n = len(scores)
        if n < MIN_REVIEWS:
            result.append({
                "week_start":   ws,
                "week_end":     we,
                "value":        None,
                "review_count": n,
                "status":       "insufficient_data",
            })
        else:
            avg = round(sum(scores) / n, 2)
            result.append({
                "week_start":   ws,
                "week_end":     we,
                "value":        avg,
                "review_count": n,
                "status":       "ok",
            })
    return result


# ---------------------------------------------------------------------------
# iOS — app-store-scraper (fallback: iTunes RSS)
# ---------------------------------------------------------------------------
def fetch_ios_reviews_scraper(app_id: str, country: str) -> list:
    """app-store-scraper ile bir ülkeden review çeker."""
    try:
        from app_store_scraper import AppStore
        app = AppStore(country=country, app_name="sunexpress", app_id=int(app_id))
        after_dt = datetime(PERIOD_START.year, PERIOD_START.month, PERIOD_START.day)
        app.review(how_many=500, after=after_dt, sleep=0.3)
        reviews = []
        for r in (app.reviews or []):
            dt = r.get("date")
            score = r.get("rating")
            if dt and score:
                reviews.append({"date": dt, "score": int(score)})
        return reviews
    except Exception as e:
        print(f"    [scraper {country}] ✗ {e}")
        return []


def fetch_ios_reviews_rss(app_id: str, country: str) -> list:
    """iTunes RSS feed ile bir ülkeden review çeker (fallback)."""
    reviews = []
    for page in range(1, 11):
        url = (f"https://itunes.apple.com/{country}/rss/customerreviews"
               f"/page={page}/id={app_id}/sortBy=mostRecent/json")
        try:
            r = requests.get(url, timeout=12, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            entries = r.json().get("feed", {}).get("entry", [])
            if not entries:
                break
            if not isinstance(entries, list):
                entries = [entries]
            for e in entries:
                if not isinstance(e, dict):
                    continue
                raw_date  = e.get("updated", {}).get("label", "")
                raw_score = e.get("im:rating", {}).get("label")
                if not raw_date or raw_score is None:
                    continue
                try:
                    dt = datetime.fromisoformat(raw_date)
                    if dt.date() < PERIOD_START:
                        return reviews   # kronolojik DESC → daha eski → dur
                    reviews.append({"date": dt, "score": int(raw_score)})
                except Exception:
                    continue
            time.sleep(RATE_SLEEP)
        except Exception as e:
            print(f"    [rss p{page} {country}] ✗ {e}")
            break
    return reviews


def collect_ios(file_date: str) -> dict:
    print("\n── iOS Rating (review tabanlı haftalık ort.) ─────────────────────")

    used_id = None
    for app_id in IOS_APP_IDS:
        try:
            r = requests.get(
                f"https://itunes.apple.com/lookup?id={app_id}&country=tr",
                timeout=10, headers={"User-Agent": "Mozilla/5.0"}
            )
            if r.ok and r.json().get("resultCount", 0) > 0:
                used_id = app_id
                info    = r.json()["results"][0]
                print(f"  ✓ App: {info.get('trackName')} v{info.get('version')} (ID: {app_id})")
                break
        except Exception:
            pass
        time.sleep(RATE_SLEEP)

    if not used_id:
        print("  ✗ iOS app ID bulunamadı.")
        return {}

    # Genel rating (snapshot)
    general_rating = None
    try:
        lu = requests.get(
            f"https://itunes.apple.com/lookup?id={used_id}&country=tr",
            timeout=10, headers={"User-Agent": "Mozilla/5.0"}
        ).json()
        if lu.get("resultCount", 0) > 0:
            r0 = lu["results"][0]
            general_rating = round(r0.get("averageUserRating", 0), 2)
    except Exception:
        pass

    # Tüm ülkelerden review birleştir
    all_reviews = []
    scraper_ok  = False

    for country in REVIEW_COUNTRIES:
        print(f"  [{country}] review çekiliyor...", end=" ", flush=True)
        revs = fetch_ios_reviews_scraper(used_id, country)
        if revs:
            scraper_ok = True
            print(f"{len(revs)} review")
        else:
            # Fallback: RSS
            revs = fetch_ios_reviews_rss(used_id, country)
            print(f"{len(revs)} review (RSS)")
        all_reviews.extend(revs)
        time.sleep(RATE_SLEEP)

    # Dönem filtresi
    in_period = [r for r in all_reviews
                 if PERIOD_START <= r["date"].date() <= PERIOD_END]
    print(f"  Toplam: {len(all_reviews)} review → period içinde: {len(in_period)}")

    weekly = build_weekly_buckets(in_period)
    ok_weeks = sum(1 for w in weekly if w["status"] == "ok")
    print(f"  Haftalık: {ok_weeks}/{len(weekly)} haftada yeterli veri")
    for w in weekly:
        v = f"{w['value']:.2f}" if w['value'] else "—"
        print(f"    {w['week_start']} – {w['week_end']}: {v} ★  (n={w['review_count']})")

    return {
        "app_name":        "SunExpress",
        "app_id":          used_id,
        "platform":        "ios",
        "metric":          "rating",
        "collection_date": datetime.now(timezone.utc).isoformat(),
        "source":          "app_store_scraper" if scraper_ok else "itunes_rss",
        "live":            True,
        "general_rating":  general_rating,
        "review_countries": REVIEW_COUNTRIES,
        "period": {"start": WEEKS[0][0], "end": WEEKS[-1][1], "granularity": "weekly"},
        "data": weekly,
    }


# ---------------------------------------------------------------------------
# Android — google-play-scraper reviews
# ---------------------------------------------------------------------------
def fetch_android_reviews(pkg: str, country: str, lang: str) -> list:
    try:
        from google_play_scraper import reviews as gp_reviews, Sort
        result, _ = gp_reviews(
            pkg, lang=lang, country=country,
            sort=Sort.NEWEST, count=500
        )
        out = []
        for r in result:
            at = r.get("at")
            score = r.get("score")
            if at and score:
                if hasattr(at, "date"):
                    d = at.date()
                else:
                    d = at
                if d >= PERIOD_START:
                    out.append({"date": at if hasattr(at, "date") else
                                datetime.combine(at, datetime.min.time()), "score": int(score)})
        return out
    except Exception as e:
        print(f"    [{country}] ✗ {e}")
        return []


def collect_android(file_date: str) -> dict:
    print("\n── Android Rating (review tabanlı haftalık ort.) ─────────────────")

    try:
        from google_play_scraper import app as gplay_app
    except ImportError:
        print("  ✗ google-play-scraper kurulu değil.")
        return {}

    used_pkg = None
    general_rating = None

    for pkg in ANDROID_PKGS:
        try:
            info = gplay_app(pkg, lang="tr", country="tr")
            used_pkg       = pkg
            general_rating = round(float(info.get("score", 0) or 0), 2)
            print(f"  ✓ App: {info.get('title')} v{info.get('version')} ({pkg})")
            print(f"  Genel rating: {general_rating} ★ ({info.get('ratings',0):,} rating)")
            break
        except Exception as e:
            print(f"  ✗ {pkg}: {e}")
        time.sleep(RATE_SLEEP)

    if not used_pkg:
        print("  ✗ Android paketi bulunamadı.")
        return {}

    all_reviews = []
    for country in REVIEW_COUNTRIES:
        lang = country if len(country) == 2 else "en"
        print(f"  [{country}] review çekiliyor...", end=" ", flush=True)
        revs = fetch_android_reviews(used_pkg, country, lang)
        print(f"{len(revs)} review")
        all_reviews.extend(revs)
        time.sleep(RATE_SLEEP)

    # Dönem filtresi
    in_period = []
    for r in all_reviews:
        dt = r.get("date")
        d  = dt.date() if hasattr(dt, "date") else dt
        if PERIOD_START <= d <= PERIOD_END:
            in_period.append(r)

    print(f"  Toplam: {len(all_reviews)} review → period içinde: {len(in_period)}")

    weekly = build_weekly_buckets(in_period)
    ok_weeks = sum(1 for w in weekly if w["status"] == "ok")
    print(f"  Haftalık: {ok_weeks}/{len(weekly)} haftada yeterli veri")
    for w in weekly:
        v = f"{w['value']:.2f}" if w['value'] else "—"
        print(f"    {w['week_start']} – {w['week_end']}: {v} ★  (n={w['review_count']})")

    return {
        "app_name":        "SunExpress",
        "package_name":    used_pkg,
        "platform":        "android",
        "metric":          "rating",
        "collection_date": datetime.now(timezone.utc).isoformat(),
        "source":          "google_play_scraper",
        "live":            True,
        "general_rating":  general_rating,
        "review_countries": REVIEW_COUNTRIES,
        "period": {"start": WEEKS[0][0], "end": WEEKS[-1][1], "granularity": "weekly"},
        "data": weekly,
    }


# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------
def save_json(data: dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    print(f"  → {path.name}  ({path.stat().st_size / 1024:.1f} KB)")


# ---------------------------------------------------------------------------
# Ana akış
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Haftalık review rating toplayıcı")
    parser.add_argument("--date", default="2026-03-09",
                        help="Çıktı dosyası tarih etiketi (varsayılan: 2026-03-09)")
    args = parser.parse_args()
    file_date = args.date

    print(f"\n{'='*65}")
    print(f"  collect-ratings.py — haftalık review ortalaması")
    print(f"  Period: {WEEKS[0][0]} → {WEEKS[-1][1]}  |  Tarih: {file_date}")
    print(f"{'='*65}")

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    ios_data     = collect_ios(file_date)
    android_data = collect_android(file_date)

    print(f"\n── Dosyalar kaydediliyor...")
    if ios_data:
        save_json(ios_data,     RAW_DIR / f"ios_rating_live_{file_date}.json")
    if android_data:
        save_json(android_data, RAW_DIR / f"android_rating_live_{file_date}.json")

    # Karşılaştırma tablosu
    print(f"\n{'='*65}")
    print("  HAFTALIK KARŞILAŞTIRMA")
    print(f"  {'Hafta':<20} {'iOS':>10} {'Android':>12}")
    print(f"  {'─'*44}")
    ios_weekly = {w["week_start"]: w for w in (ios_data.get("data") or [])}
    and_weekly = {w["week_start"]: w for w in (android_data.get("data") or [])}
    for ws, we in WEEKS:
        iw = ios_weekly.get(ws, {})
        aw = and_weekly.get(ws, {})
        iv = f"{iw['value']:.2f} ★" if iw.get("value") else f"— (n={iw.get('review_count',0)})"
        av = f"{aw['value']:.2f} ★" if aw.get("value") else f"— (n={aw.get('review_count',0)})"
        print(f"  {ws} – {we[5:]}  {iv:>10}  {av:>12}")
    same = all(
        ios_weekly.get(ws, {}).get("value") == and_weekly.get(ws, {}).get("value")
        for ws, _ in WEEKS
        if ios_weekly.get(ws, {}).get("value") and and_weekly.get(ws, {}).get("value")
    )
    print(f"\n  iOS = Android mı?  {'EVET ⚠ (şüpheli)' if same else 'HAYIR ✓ (farklı değerler)'}")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
