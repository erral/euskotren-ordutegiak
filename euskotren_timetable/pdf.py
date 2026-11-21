"""Coordinate-based PDF text extraction.

The Euskotren posters are InDesign layouts with rotated headers. We read words
with `pdftotext -bbox-layout` and map cells to columns by x-coordinate.
"""

import re
import subprocess
import tempfile
from pathlib import Path

CELL = re.compile(r"^\d{1,2}:\d{2}$|^[>\-?]$")


def words_from_pdf(pdf: str | Path, page: int = 1) -> list[tuple[float, float, str]]:
    """Return (x, y, word) for one PDF page."""
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        html = tmp.name
    subprocess.run(
        ["pdftotext", "-bbox-layout", "-f", str(page), "-l", str(page), str(pdf), html],
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


def cluster_rows(
    words: list[tuple[float, float, str]],
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    min_cells: int,
    first_x_max: float,
    y_tol: float = 7,
) -> list[list[tuple[float, float, str]]]:
    """Cluster cell-like words into service rows."""
    cells = [
        (x, y, w)
        for x, y, w in words
        if x_min <= x <= x_max and y_min <= y <= y_max and CELL.match(w)
    ]
    cells.sort(key=lambda item: (item[1], item[0]))
    groups: list[list[tuple[float, float, str]]] = []
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


def build_grid(row: list[tuple[float, float, str]], stops: list[str]) -> list[tuple[float, str]]:
    """Use a complete row to fix each stop's x position."""
    assert len(row) == len(stops), f"{len(row)} cells for {len(stops)} stops"
    return [(cell[0], stop) for cell, stop in zip(row, stops, strict=True)]


def row_to_dict(
    row: list[tuple[float, float, str]],
    grid: list[tuple[float, str]],
    tol: float = 16,
) -> dict[str, str]:
    """Map each cell to its nearest stop column."""
    out: dict[str, str] = {}
    for x, _y, word in row:
        gx, stop = min(grid, key=lambda item: abs(item[0] - x))
        if abs(gx - x) <= tol:
            out[stop] = word
    return out
