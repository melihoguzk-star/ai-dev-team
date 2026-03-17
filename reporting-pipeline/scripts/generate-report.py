#!/usr/bin/env python3
"""
generate-report.py — SunExpress PPTX rapor üretici (template-based)

YAKLAŞIM: Template PPTX'i unpack eder, tablo hücrelerini ve grafik
PNG'lerini CSV verisine göre günceller, tekrar pack eder.

Kullanım:
    python scripts/generate-report.py --week 2026-03-02
    python scripts/generate-report.py --week 2026-03-02 --template templates/SunExpress_template.pptx
"""

import argparse
import io
import os
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd
from lxml import etree

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Branding
# ---------------------------------------------------------------------------
M_NAVY   = "#1B3A5C"
M_ORANGE = "#E85D26"
M_GRID   = "#E0E0E0"
M_DGRAY  = "#333333"

NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS   = {"a": NS_A}


# ---------------------------------------------------------------------------
# Formatting helpers  (match template's exact number style)
# ---------------------------------------------------------------------------

def fmt_date_range(start: str, end: str) -> str:
    """'2026-01-19','2026-01-25' → '19 Jan - 25 Jan'"""
    ds = datetime.strptime(start, "%Y-%m-%d")
    de = datetime.strptime(end,   "%Y-%m-%d")
    return f"{ds.day} {ds.strftime('%b')} - {de.day} {de.strftime('%b')}"


def fmt_date_short(date_str: str) -> str:
    """'2026-01-19' → '19 Jan'"""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{dt.day} {dt.strftime('%b')}"


def _is_empty(val) -> bool:
    """NaN, None, '-', '' → True"""
    if val is None:
        return True
    try:
        import math
        return math.isnan(float(val))
    except (TypeError, ValueError):
        return str(val).strip() in ("-", "", "nan", "NaN", "None")


def fmt_k(val) -> str:
    """21900→'21.9K' | NaN/'-' → '-'"""
    if _is_empty(val):
        return "-"
    s = f"{float(val) / 1000:.2f}".rstrip("0").rstrip(".")
    return s + "K"


def fmt_rating(val) -> str:
    """3.0→'3.0'  3.63→'3.63' | NaN/'-' → '-'"""
    if _is_empty(val):
        return "-"
    s = f"{float(val):.2f}".rstrip("0")
    if "." not in s:   s += ".0"
    elif s.endswith("."): s += "0"
    return s


def fmt_rating_comma(val) -> str:
    """Slide 4 tablo: decimal separator = virgül | NaN/'-' → '-'"""
    r = fmt_rating(val)
    return r.replace(".", ",") if r != "-" else "-"


def fmt_crash(val) -> str:
    """99.8→'99.8'  99.57→'99.57' | NaN/'-' → '-'"""
    if _is_empty(val):
        return "-"
    s = f"{float(val):.2f}".rstrip("0")
    if "." not in s:   s += ".0"
    elif s.endswith("."): s += "0"
    return s


# ---------------------------------------------------------------------------
# XML helpers
# ---------------------------------------------------------------------------

def set_cell_text(cell, new_text: str):
    """
    Write new_text into a table cell.
    If multiple <a:r> runs exist, writes to the first and empties the rest.
    If no runs, inserts a new one.
    """
    runs = cell.findall(".//a:r", NS)
    if not runs:
        para = cell.find(".//a:p", NS)
        if para is None:
            return
        r_elem = etree.SubElement(para, f"{{{NS_A}}}r")
        t_elem = etree.SubElement(r_elem, f"{{{NS_A}}}t")
        t_elem.text = new_text
        return
    written = False
    for r in runs:
        t = r.find("a:t", NS)
        if t is None:
            continue
        if not written:
            t.text = new_text
            written = True
        else:
            t.text = ""


def update_table(tbl_elem, row_data: list):
    """
    Update data rows (skip header row 0).
    row_data: [[cell0_val, cell1_val, ...], ...]   (one list per data row)
    """
    rows = tbl_elem.findall(".//a:tr", NS)
    for ri, cells_data in enumerate(row_data, start=1):
        if ri >= len(rows):
            break
        for ci, val in enumerate(cells_data):
            cells = rows[ri].findall("a:tc", NS)
            if ci < len(cells):
                set_cell_text(cells[ci], str(val))


def write_slide_xml(slide_path: Path, tree: etree._ElementTree):
    """Write modified XML back to file with correct PPTX declaration."""
    tree.write(
        str(slide_path),
        xml_declaration=True,
        encoding="UTF-8",
        standalone=True,
    )


# ---------------------------------------------------------------------------
# Chart generator
# ---------------------------------------------------------------------------

def make_placeholder_chart(label: str, w_px=876, h_px=530) -> bytes:
    """Veri olmayan slide'lar için 'Veri henüz mevcut değil' placeholder PNG."""
    DPI = 96
    fig, ax = plt.subplots(figsize=(w_px / DPI, h_px / DPI), dpi=DPI)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#F8F8F8")
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_color("#CCCCCC")
    ax.text(0.5, 0.55, "Veri henüz mevcut değil",
            transform=ax.transAxes, ha="center", va="center",
            fontsize=16, color="#888888", fontweight="bold")
    ax.text(0.5, 0.42, f"({label})",
            transform=ax.transAxes, ha="center", va="center",
            fontsize=11, color="#AAAAAA")
    ax.text(0.5, 0.30, "App Store Connect / Google Play Console\ncredential eklendiğinde otomatik doldurulacak",
            transform=ax.transAxes, ha="center", va="center",
            fontsize=9, color="#BBBBBB", linespacing=1.6)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", facecolor="white", dpi=DPI)
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def make_chart(ios_v, and_v, x_labels, ylabel,
               y_min=None, y_max=None, fmt_fn=None,
               w_px=876, h_px=530) -> bytes:
    """Generate a line chart PNG at (w_px × h_px) matching template style.
    If all values are empty/NaN, returns a placeholder chart."""
    import math

    def clean(v):
        """NaN/'-'/None → None, else float"""
        if v is None:
            return None
        try:
            f = float(v)
            return None if math.isnan(f) else f
        except (TypeError, ValueError):
            return None

    ios_clean = [clean(v) for v in ios_v]
    and_clean = [clean(v) for v in and_v]
    has_data  = any(v is not None for v in ios_clean + and_clean)

    if not has_data:
        return make_placeholder_chart(ylabel, w_px=w_px, h_px=h_px)

    # Filter to non-None pairs for plotting
    valid_x   = []
    valid_ios = []
    valid_and = []
    for x, iv, av in zip(x_labels, ios_clean, and_clean):
        if iv is not None or av is not None:
            valid_x.append(x)
            valid_ios.append(iv)
            valid_and.append(av)

    DPI = 96
    fig, ax = plt.subplots(figsize=(w_px / DPI, h_px / DPI), dpi=DPI)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    lbl = fmt_fn or (lambda v: f"{v:.0f}")

    # Only plot non-None segments
    def plot_series(vals, color):
        xs, ys = [], []
        for x, v in zip(valid_x, vals):
            if v is not None:
                xs.append(x)
                ys.append(v)
        if xs:
            ax.plot(xs, ys, color=color, lw=2.5, marker="o", ms=7, zorder=3)
        return xs, ys

    ios_xs, ios_ys = plot_series(valid_ios, M_NAVY)
    and_xs, and_ys = plot_series(valid_and, M_ORANGE)

    for x, v in zip(ios_xs, ios_ys):
        ax.annotate(lbl(v), (x, v), xytext=(0, 9), textcoords="offset points",
                    ha="center", fontsize=8, color=M_NAVY, fontweight="bold")
    for x, v in zip(and_xs, and_ys):
        ax.annotate(lbl(v), (x, v), xytext=(0, -14), textcoords="offset points",
                    ha="center", fontsize=8, color=M_ORANGE, fontweight="bold")

    if y_min is not None and y_max is not None:
        ax.set_ylim(y_min, y_max)
    elif y_min is not None:
        ax.set_ylim(bottom=y_min)

    ax.set_ylabel(ylabel, fontsize=9, color=M_DGRAY)
    ax.tick_params(labelsize=8, colors=M_DGRAY)
    ax.grid(axis="y", color=M_GRID, lw=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color(M_GRID)
    ax.spines["bottom"].set_color(M_GRID)
    plt.xticks(rotation=0, ha="center", fontsize=8)

    handles = [
        Line2D([0], [0], color=M_NAVY,   lw=2.5, marker="o", ms=7, label="● iOS"),
        Line2D([0], [0], color=M_ORANGE, lw=2.5, marker="o", ms=7, label="● Android"),
    ]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 1.12),
              ncol=2, frameon=False, fontsize=10)

    fig.subplots_adjust(left=0.10, right=0.97, top=0.87, bottom=0.13)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", facecolor="white", dpi=DPI)
    plt.close(fig)
    buf.seek(0)
    return buf.read()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="SunExpress PPTX rapor üretici")
    parser.add_argument("--week",     default="2026-03-02")
    parser.add_argument("--template", default=None)
    parser.add_argument("--output",   default=None)
    args = parser.parse_args()
    week = args.week

    template = (Path(args.template) if args.template
                else BASE_DIR / "templates" / "SunExpress_template.pptx")
    out_dir  = BASE_DIR / "reports" / week
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (args.output or f"sunexpress-weekly-report-{week}.pptx")

    print(f"\n{'='*60}")
    print(f"  generate-report.py (template-based)  week: {week}")
    print(f"  Template : {template.name}")
    print(f"{'='*60}")

    # ── 1. Load CSV data ───────────────────────────────────────────────────
    print("\n[1/4] Veriler yükleniyor...")
    proc = BASE_DIR / "data" / "processed"
    df   = pd.read_csv(proc / f"weekly-metrics-{week}.csv")
    print(f"  ✓ {len(df)} hafta")

    date_range = [fmt_date_range(r["week_start"], r["week_end"]) for _, r in df.iterrows()]
    date_short = [fmt_date_short(r["week_start"])               for _, r in df.iterrows()]

    # ── 2. Pre-build table row data ────────────────────────────────────────
    def rows_overview_ios():
        out = []
        for i, (_, r) in enumerate(df.iterrows()):
            out.append([date_range[i],
                        fmt_rating(r["ios_rating"]),
                        fmt_crash(r["ios_crash_free_user"]),
                        fmt_k(r["ios_downloads"]),
                        fmt_k(r["ios_active_users"]),
                        fmt_k(r["ios_uninstalls"])])
        return out

    def rows_overview_android():
        out = []
        for i, (_, r) in enumerate(df.iterrows()):
            out.append([date_range[i],
                        fmt_rating(r["android_rating"]),
                        fmt_crash(r["android_crash_free_user"]),
                        fmt_k(r["android_downloads"]),
                        fmt_k(r["android_active_users"]),
                        fmt_k(r["android_uninstalls"])])
        return out

    def rows_metric(col_ios, col_and, fmt_fn):
        out = []
        for i, (_, r) in enumerate(df.iterrows()):
            out.append([date_range[i], fmt_fn(r[col_ios]), fmt_fn(r[col_and])])
        return out

    TABLE_DATA = {
        2: rows_overview_ios(),
        3: rows_overview_android(),
        4: rows_metric("ios_rating",        "android_rating",        fmt_rating_comma),
        5: rows_metric("ios_crash_free_user","android_crash_free_user", fmt_crash),
        6: rows_metric("ios_downloads",     "android_downloads",     fmt_k),
        7: rows_metric("ios_active_users",  "android_active_users",  fmt_k),
        8: rows_metric("ios_uninstalls",    "android_uninstalls",    fmt_k),
    }

    # Chart specs: (slide, image_file, ios_col, and_col, ylabel, ymin, ymax, fmt_fn, w, h)
    CHART_SPECS = [
        (4, "image4.png",
         df["ios_rating"].tolist(),        df["android_rating"].tolist(),
         "Rating", 0, 4, fmt_rating, 876, 530),
        (5, "image1.png",
         df["ios_crash_free_user"].tolist(),df["android_crash_free_user"].tolist(),
         "Crash-Free (%)", 98, 100, fmt_crash, 996, 716),
        (6, "image5.png",
         df["ios_downloads"].tolist(),     df["android_downloads"].tolist(),
         "Downloads", 0, None, fmt_k, 1245, 531),
        (7, "image8.png",
         df["ios_active_users"].tolist(),  df["android_active_users"].tolist(),
         "Active Users", 0, None, fmt_k, 1200, 742),
        (8, "image9.png",
         df["ios_uninstalls"].tolist(),    df["android_uninstalls"].tolist(),
         "Uninstalls", 0, None, fmt_k, 1162, 720),
    ]

    # ── 3. Unpack template ─────────────────────────────────────────────────
    print("\n[2/4] Template açılıyor...")
    tmp = Path(tempfile.mkdtemp(prefix="sunex_"))
    with zipfile.ZipFile(template) as z:
        z.extractall(tmp)
    print(f"  ✓ {tmp.name}")

    # ── 4. Update slide XML tables ─────────────────────────────────────────
    print("\n[3/4] Tablolar güncelleniyor...")
    for slide_num, row_data in TABLE_DATA.items():
        slide_path = tmp / "ppt" / "slides" / f"slide{slide_num}.xml"
        tree = etree.parse(str(slide_path))
        tbl  = tree.getroot().findall(f".//{{{NS_A}}}tbl")[0]
        update_table(tbl, row_data)
        write_slide_xml(slide_path, tree)
        print(f"  ✓ Slide {slide_num} ({len(row_data)} satır)")

    # ── 5. Replace chart PNGs ──────────────────────────────────────────────
    print("\n  Grafikler oluşturuluyor...")
    for slide_num, img_file, ios_v, and_v, ylabel, ymin, ymax, fmt_fn, w, h in CHART_SPECS:
        png = make_chart(ios_v, and_v, date_short, ylabel,
                         y_min=ymin, y_max=ymax, fmt_fn=fmt_fn, w_px=w, h_px=h)
        (tmp / "ppt" / "media" / img_file).write_bytes(png)
        print(f"  ✓ Slide {slide_num} → {img_file} ({w}×{h}px, {len(png)//1024}KB)")

    # ── 6. Repack PPTX ─────────────────────────────────────────────────────
    print("\n[4/4] PPTX paketleniyor...")
    all_files = []
    for dirpath, _, filenames in os.walk(tmp):
        for fname in filenames:
            fp  = Path(dirpath) / fname
            arc = str(fp.relative_to(tmp))
            all_files.append((fp, arc))

    # [Content_Types].xml must be first entry for strict readers
    all_files.sort(key=lambda x: (not x[1].startswith("[Content_Types]"), x[1]))

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zout:
        for fp, arc in all_files:
            zout.write(fp, arc)

    shutil.rmtree(tmp)

    size_kb = out_path.stat().st_size / 1024
    print(f"  ✓ {out_path.name}  ({size_kb:.1f} KB)")
    print(f"\n  Rapor: {out_path}")
    print(f"{'='*60}\n")
    return str(out_path)


if __name__ == "__main__":
    main()
