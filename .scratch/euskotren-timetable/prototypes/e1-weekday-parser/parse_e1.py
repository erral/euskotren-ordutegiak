#!/usr/bin/env python3
"""Prototype parser for one E1 weekday direction.

Source: the 21 November 2026 `E1 Pasaia -> Matiko Bilbao` PDF.
The full-line table omits stops where every train stops (the Pasaia-Aia/Orio note).
Those times come from the `Pasaia -> Zumaia` partial table on the same page.
`Traña Abadiño` is a single stop. This script proves the geometry-based extraction
and the merge for the 05:35 through service.

Usage:
    python3 parse_e1.py /path/to/E1_Pasaia_-_Matiko_4.pdf

Outputs (next to this script):
    e1_weekday_wide.csv   one row per full-line weekday service, stops as columns
    e1_weekday_0535.csv   normalized records for the merged 05:35 service
    e1_weekday_0535.md    vertical view of the merged 05:35 service
"""

import csv
import re
import subprocess
import sys
import tempfile
from pathlib import Path

PDF = sys.argv[1] if len(sys.argv) > 1 else "E1_Pasaia_-_Matiko_4.pdf"
OUT = Path(__file__).resolve().parent

# Columns present in the full-line table, left to right.
FULL_42 = [
    "Pasaia", "Anoeta", "Amara Donostia", "Kontxa-Zentroa", "Benta-Berri",
    "Aia-Orio", "San Pelaio", "Zarautz", "Zumaia", "Arroa", "Deba", "Mendaro",
    "Altzola", "Toletxegain", "Elgoibar", "Azitain", "Eibar", "Ardantza",
    "Amaña", "Unibertsitatea", "San Lorentzo", "Errotabarri", "Ermua",
    "Zaldibar", "Berriz", "Traña Abadiño", "Durango", "Euba", "Amorebieta Geltokia",
    "Lemoa", "Bedia", "Usansolo", "Zuhatzu", "Ariz", "Etxebarri",
    "Kukullaga-Etxebarri", "Otxarkoaga", "Txurdinaga", "Zurbaranbarri",
    "Zazpikaleak/Casco Viejo", "Uribarri", "Matiko-Bilbao",
]

# Columns present in the Pasaia -> Zumaia partial table.
PARTIAL_17 = [
    "Pasaia", "Altza", "Herrera", "Intxaurrondo", "Loiola", "Anoeta",
    "Amara Donostia", "Kontxa-Zentroa", "Benta-Berri", "Lugaritz", "Añorga",
    "Errekalde", "Usurbil", "Aia-Orio", "San Pelaio", "Zarautz", "Zumaia",
]

# The complete validated direction. The nine stops missing from the full-line
# table are inserted here so the merge can fill them from the partial table.
FULL_51 = [
    "Pasaia", "Altza", "Herrera", "Intxaurrondo", "Loiola", "Anoeta",
    "Amara Donostia", "Kontxa-Zentroa", "Benta-Berri", "Lugaritz", "Añorga",
    "Errekalde", "Usurbil", "Aia-Orio", "San Pelaio", "Zarautz", "Zumaia",
    "Arroa", "Deba", "Mendaro", "Altzola", "Toletxegain", "Elgoibar",
    "Azitain", "Eibar", "Ardantza", "Amaña", "Unibertsitatea", "San Lorentzo",
    "Errotabarri", "Ermua", "Zaldibar", "Berriz", "Traña Abadiño",
    "Durango", "Euba", "Amorebieta Geltokia", "Lemoa", "Bedia", "Usansolo",
    "Zuhatzu", "Ariz", "Etxebarri", "Kukullaga-Etxebarri", "Otxarkoaga",
    "Txurdinaga", "Zurbaranbarri", "Zazpikaleak/Casco Viejo", "Uribarri",
    "Matiko-Bilbao",
]

CELL = re.compile(r"^\d{1,2}:\d{2}$|^[>\-]$")


def words_from_pdf(pdf: str):
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        html = tmp.name
    subprocess.run(
        ["pdftotext", "-bbox-layout", "-f", "1", "-l", "1", pdf, html],
        check=True,
        stderr=subprocess.DEVNULL,
    )
    text = Path(html).read_text()
    raw = re.findall(
        r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>',
        text,
    )
    out = []
    for x0, y0, _x1, _y1, word in raw:
        word = word.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&")
        out.append((float(x0), float(y0), word))
    return out


def cluster_rows(words, x_min, x_max, y_min, y_max, min_cells, first_x_max, y_tol=7):
    cells = [
        (x, y, w)
        for x, y, w in words
        if x_min <= x <= x_max and y_min <= y <= y_max and CELL.match(w)
    ]
    cells.sort(key=lambda item: (item[1], item[0]))
    groups = []
    for cell in cells:
        if not groups or abs(cell[1] - groups[-1][0][1]) > y_tol:
            groups.append([cell])
        else:
            groups[-1].append(cell)
    rows = []
    for group in groups:
        group.sort(key=lambda item: item[0])
        if len(group) >= min_cells and group[0][0] <= first_x_max:
            rows.append(group)
    return rows


def build_grid(row, stops):
    """Use a complete row to fix each stop's x position."""
    assert len(row) == len(stops), f"{len(row)} cells for {len(stops)} stops"
    return [(cell[0], stop) for cell, stop in zip(row, stops)]


def row_to_dict(row, grid, tol=16):
    out = {}
    for x, _y, word in row:
        gx, stop = min(grid, key=lambda item: abs(item[0] - x))
        if abs(gx - x) <= tol:
            out[stop] = word
    return out


def main():
    words = words_from_pdf(PDF)

    full_rows = cluster_rows(words, 40, 1420, 430, 570, 20, 110)
    partial_rows = cluster_rows(words, 650, 1420, 1620, 1700, 10, 700)

    if not full_rows or not partial_rows:
        raise SystemExit(f"could not find rows: full={len(full_rows)} partial={len(partial_rows)}")

    full_grid = build_grid(full_rows[0], FULL_42)
    partial_grid = build_grid(partial_rows[0], PARTIAL_17)

    full_services = []
    for row in full_rows:
        values = row_to_dict(row, full_grid)
        departure = values.get("Pasaia", "?")
        full_services.append((departure, values))

    partial = {}
    for row in partial_rows:
        values = row_to_dict(row, partial_grid)
        partial[values.get("Pasaia", "?")] = values

    merged = {}
    for departure, values in full_services:
        record = {stop: values.get(stop, "") for stop in FULL_51}
        source = {stop: "full" if record[stop] else "missing" for stop in FULL_51}
        if departure in partial:
            for stop, value in partial[departure].items():
                if not record.get(stop):
                    record[stop] = value
                    source[stop] = "partial"
        merged[departure] = (record, source)

    # Wide CSV, one row per full-line weekday service.
    with (OUT / "e1_weekday_wide.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Pasaia departure"] + FULL_51)
        for departure, (record, _source) in sorted(merged.items()):
            writer.writerow([departure] + [record[stop] for stop in FULL_51])

    # Normalized records for the 05:35 service.
    target = "5:35"
    record, source = merged[target]
    with (OUT / "e1_weekday_0535.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["service", "stop_order", "stop", "time_or_symbol", "source"])
        for i, stop in enumerate(FULL_51, 1):
            writer.writerow([f"E1-{target}", i, stop, record[stop], source[stop]])

    # Vertical Markdown view.
    lines = [
        "# E1 05:35 Pasaia → Matiko Bilbao (weekday)",
        "",
        "| # | Stop | Time | Source |",
        "|---|---|---|---|",
    ]
    for i, stop in enumerate(FULL_51, 1):
        lines.append(f"| {i} | {stop} | {record[stop]} | {source[stop]} |")
    (OUT / "e1_weekday_0535.md").write_text("\n".join(lines) + "\n")

    print(f"full-line weekday services: {[d for d, _ in full_services]}")
    print(f"partial weekday services: {sorted(partial)}")
    print(f"merged services: {sorted(merged)}")
    print(f"05:35 stops: {len(record)}, missing: {[s for s in FULL_51 if source[s] != 'full' and source[s] != 'partial']}")


if __name__ == "__main__":
    main()
