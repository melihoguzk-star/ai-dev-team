#!/usr/bin/env python3
"""
collect-crashlytics.py — Firebase Crashlytics crash-free user rate toplayıcı

Credential: keys/firebase-admin-sdk.json
Kullanım:
    python scripts/collect-crashlytics.py
    python scripts/collect-crashlytics.py --date 2026-03-09
"""

import argparse
import json
import sys
from datetime import datetime, timezone, date, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR  = BASE_DIR / "data" / "raw"
KEY_FILE = BASE_DIR / "keys" / "firebase-admin-sdk.json"

# Rapor haftaları
WEEKS = [
    ("2026-01-19", "2026-01-25"),
    ("2026-01-26", "2026-02-01"),
    ("2026-02-02", "2026-02-08"),
    ("2026-02-09", "2026-02-15"),
    ("2026-02-16", "2026-02-22"),
    ("2026-02-23", "2026-03-01"),
    ("2026-03-02", "2026-03-08"),
]


# ---------------------------------------------------------------------------
# Credential & token yardımcıları
# ---------------------------------------------------------------------------
def load_project_id() -> str:
    with open(KEY_FILE, encoding="utf-8") as f:
        return json.load(f)["project_id"]


def get_credentials():
    from google.oauth2 import service_account
    scopes = [
        "https://www.googleapis.com/auth/firebase.readonly",
        "https://www.googleapis.com/auth/cloud-platform",
    ]
    return service_account.Credentials.from_service_account_file(
        str(KEY_FILE), scopes=scopes
    )


def get_token(creds) -> str:
    from google.auth.transport.requests import Request
    if not creds.valid:
        creds.refresh(Request())
    return creds.token


# ---------------------------------------------------------------------------
# Firebase Management API — app listesi
# ---------------------------------------------------------------------------
def list_firebase_apps(project_id: str, token: str) -> dict:
    """
    iOS ve Android appId değerlerini döner.
    {"ios": [...], "android": [...]}
    """
    import requests as rq
    headers = {"Authorization": f"Bearer {token}"}
    apps = {"ios": [], "android": []}

    for platform in ("iosApps", "androidApps"):
        url = f"https://firebase.googleapis.com/v1beta1/projects/{project_id}/{platform}"
        try:
            r = rq.get(url, headers=headers, timeout=15)
            if r.ok:
                key = "ios" if "ios" in platform.lower() else "android"
                for a in r.json().get("apps", []):
                    apps[key].append(a.get("appId", ""))
                print(f"  {key} apps: {apps[key]}")
            else:
                print(f"  ⚠ {platform}: {r.status_code} {r.text[:80]}")
        except Exception as e:
            print(f"  ⚠ {platform}: {e}")
    return apps


# ---------------------------------------------------------------------------
# Yöntem A — Crashlytics v1beta1 REST  (çeşitli endpoint'ler dene)
# ---------------------------------------------------------------------------
CRASHLYTICS_ENDPOINTS = [
    # Endpoint formatları: (url_template, params_fn)
    (
        "https://firebasecrashlytics.googleapis.com/v1beta1/projects/{project}/apps/{app}/crashFreeTrend",
        lambda ws, we: {"startTime": f"{ws}T00:00:00Z", "endTime": f"{we}T23:59:59Z"},
    ),
    (
        "https://firebasecrashlytics.googleapis.com/v1beta1/projects/{project}/apps/{app}/trends/crashFreeUsersRate",
        lambda ws, we: {"startTime": f"{ws}T00:00:00Z", "endTime": f"{we}T23:59:59Z"},
    ),
    (
        "https://firebasecrashlytics.googleapis.com/v1beta1/projects/{project}/apps/{app}/crashFreeUsersMetric",
        lambda ws, we: {
            "startTime": f"{ws}T00:00:00Z",
            "endTime":   f"{we}T23:59:59Z",
            "granularity": "WEEKLY",
        },
    ),
]


def try_crashlytics_rest(project_id: str, app_id: str, token: str) -> tuple[list, str]:
    """
    Çeşitli Crashlytics endpoint'lerini dener.
    Döner: (weekly_data_list, used_endpoint)  — başarısızsa ([], "")
    """
    import requests as rq
    headers = {"Authorization": f"Bearer {token}"}

    for url_tmpl, params_fn in CRASHLYTICS_ENDPOINTS:
        url = url_tmpl.format(project=project_id, app=app_id)
        # Tüm haftalar için bir arada sorgu yap
        params = params_fn(WEEKS[0][0], WEEKS[-1][1])
        print(f"    Deneniyor: {url.split('v1beta1/')[-1]}")
        try:
            r = rq.get(url, headers=headers, params=params, timeout=15)
            if r.status_code == 200:
                body = r.json()
                print(f"    ✓ 200 OK → {str(body)[:120]}")
                # Haftalık değer ayıklamayı dene
                data = body.get("data") or body.get("trendData") or body.get("metrics", [])
                if data:
                    return data, url
                # Tek değer
                for key in ("crashFreeRate", "value", "crashFreeUsersRate"):
                    val = body.get(key)
                    if val is not None:
                        return [{"value": float(val) * 100}], url
            else:
                print(f"    ✗ {r.status_code}: {r.text[:100]}")
        except Exception as e:
            print(f"    ✗ Exception: {e}")

    return [], ""


def parse_crashlytics_data(raw_data: list, endpoint_url: str) -> list:
    """
    API ham verisini WEEKS formatına dönüştürür.
    """
    if not raw_data:
        return []

    # Basit tek değer → tüm haftalara uygula
    if len(raw_data) == 1 and "week_start" not in str(raw_data[0]):
        val = None
        item = raw_data[0]
        for k in ("value", "crashFreeRate", "crashFreeUsersRate"):
            if k in item:
                val = float(item[k])
                if val <= 1.0:
                    val = round(val * 100, 2)
                else:
                    val = round(val, 2)
                break
        if val:
            return [{"week_start": ws, "week_end": we, "value": val}
                    for ws, we in WEEKS]

    # Tarihli liste → WEEKS'e eşle
    results = {ws: None for ws, _ in WEEKS}
    for item in raw_data:
        # Farklı tarih field'larını dene
        item_date = None
        for k in ("startTime", "date", "week_start", "weekStart"):
            v = item.get(k, "")
            if v:
                item_date = str(v)[:10]
                break
        val = None
        for k in ("value", "crashFreeRate", "crashFreeUsersRate"):
            if k in item:
                val = float(item[k])
                if val <= 1.0:
                    val = round(val * 100, 2)
                else:
                    val = round(val, 2)
                break
        if item_date and val:
            for ws, we in WEEKS:
                if ws <= item_date <= we:
                    results[ws] = val
                    break

    return [{"week_start": ws, "week_end": we, "value": results[ws]}
            for ws, we in WEEKS]


# ---------------------------------------------------------------------------
# Çıktı oluşturma
# ---------------------------------------------------------------------------
def build_output(platform: str, data: list, source: str,
                 live: bool, collection_date: str) -> dict:
    return {
        "app_name":        "SunExpress",
        "platform":        platform,
        "metric":          "crash_free_user",
        "collection_date": collection_date,
        "source":          source,
        "live":            live,
        "period": {
            "start":       WEEKS[0][0],
            "end":         WEEKS[-1][1],
            "granularity": "weekly",
        },
        "data": data,
    }


def save_json(obj: dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)
    print(f"  → {path.name}  ({path.stat().st_size / 1024:.1f} KB)")


# ---------------------------------------------------------------------------
# Ana akış
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Firebase Crashlytics toplayıcı")
    parser.add_argument("--date", default="2026-03-09",
                        help="Çıktı tarih etiketi (varsayılan: 2026-03-09)")
    args = parser.parse_args()
    file_date   = args.date
    now_iso     = datetime.now(timezone.utc).isoformat()
    success     = False
    error_msg   = ""

    print(f"\n{'='*65}")
    print(f"  collect-crashlytics.py — Firebase Crashlytics")
    print(f"  Hafta aralığı: {WEEKS[0][0]} → {WEEKS[-1][1]}")
    print(f"{'='*65}")

    ios_data     = None
    android_data = None

    try:
        if not KEY_FILE.exists():
            raise FileNotFoundError(f"Key dosyası bulunamadı: {KEY_FILE}")

        project_id = load_project_id()
        print(f"\n  Project ID : {project_id}")

        # Firebase Admin SDK başlat
        import firebase_admin
        from firebase_admin import credentials
        if not firebase_admin._apps:
            cred = credentials.Certificate(str(KEY_FILE))
            firebase_admin.initialize_app(cred)
            print("  ✓ Firebase Admin SDK başlatıldı")

        # Token al
        creds = get_credentials()
        token = get_token(creds)
        print(f"  ✓ OAuth2 token alındı ({token[:20]}...)")

        # App listesi
        print("\n  App listesi alınıyor...")
        apps = list_firebase_apps(project_id, token)
        ios_ids     = apps.get("ios", [])
        android_ids = apps.get("android", [])

        # iOS Crashlytics
        for app_id in ios_ids:
            print(f"\n  [iOS] {app_id} Crashlytics sorgulanıyor...")
            raw, endpoint = try_crashlytics_rest(project_id, app_id, token)
            if raw:
                weekly = parse_crashlytics_data(raw, endpoint)
                non_null = [w for w in weekly if w.get("value") is not None]
                if non_null:
                    ios_data = build_output("ios", weekly, "firebase_crashlytics",
                                            True, now_iso)
                    success = True
                    print(f"  ✓ iOS Crashlytics: {len(non_null)} hafta veri alındı")
                    break

        # Android Crashlytics
        for app_id in android_ids:
            print(f"\n  [Android] {app_id} Crashlytics sorgulanıyor...")
            raw, endpoint = try_crashlytics_rest(project_id, app_id, token)
            if raw:
                weekly = parse_crashlytics_data(raw, endpoint)
                non_null = [w for w in weekly if w.get("value") is not None]
                if non_null:
                    android_data = build_output("android", weekly,
                                                "firebase_crashlytics", True, now_iso)
                    success = True
                    print(f"  ✓ Android Crashlytics: {len(non_null)} hafta veri alındı")
                    break

    except Exception as e:
        error_msg = str(e)
        print(f"\n  ✗ Firebase bağlantı hatası: {error_msg}")

    # Başarısız platform → boş veri (NaN) ile kaydet
    empty_weeks = [{"week_start": ws, "week_end": we, "value": None}
                   for ws, we in WEEKS]

    if ios_data is None:
        ios_data = build_output("ios", empty_weeks, "unavailable", False, now_iso)
        print("  iOS Crashlytics: boş veri (credential erişimi yok)")

    if android_data is None:
        android_data = build_output("android", empty_weeks, "unavailable", False, now_iso)
        print("  Android Crashlytics: boş veri (credential erişimi yok)")

    # Kaydet
    print(f"\n── Dosyalar kaydediliyor...")
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    save_json(ios_data,     RAW_DIR / f"ios_crashlytics_live_{file_date}.json")
    save_json(android_data, RAW_DIR / f"android_crashlytics_live_{file_date}.json")

    # Durum raporu
    print(f"\n{'='*65}")
    print("  CRASHLYTICS DURUMU")
    print(f"{'─'*65}")
    if success:
        print("  ✓ Firebase Crashlytics bağlantısı BAŞARILI")
        for platform, d in [("iOS", ios_data), ("Android", android_data)]:
            vals = [w["value"] for w in d["data"] if w.get("value") is not None]
            print(f"  {platform}: {len(vals)}/{len(d['data'])} hafta, "
                  f"ort. %{sum(vals)/len(vals):.2f}" if vals else f"  {platform}: veri yok")
    else:
        print("  ✗ Firebase Crashlytics bağlantısı BAŞARISIZ")
        if error_msg:
            print(f"  Hata: {error_msg}")
        print("  → Crash-free alanları boş bırakıldı ('-')")
    print(f"{'='*65}\n")

    return success


if __name__ == "__main__":
    main()
