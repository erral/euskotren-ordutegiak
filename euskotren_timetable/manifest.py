"""Download the timetable PDFs and record their provenance."""

import hashlib
import html as html_module
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests

from . import __version__

TIMETABLE_URL = "https://euskotren.eus/eu/tren/ordutegiak"
BASE = "https://www.euskotren.eus"
DATA_DIR = Path("data")
PDF_DIR = DATA_DIR / "pdfs"
MANIFEST_PATH = DATA_DIR / "manifest.json"


def fetch_html(url: str = TIMETABLE_URL) -> str:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.text


def extract_pdf_links(html: str, base: str = BASE) -> list[str]:
    links = re.findall(r'href="([^"]+\.pdf[^"]*)"', html, re.IGNORECASE)
    out = []
    seen = set()
    for link in links:
        absolute = urljoin(base, link)
        if absolute not in seen:
            seen.add(absolute)
            out.append(absolute)
    return out


def find_link_by_text(page: str, needle: str) -> str:
    pattern = re.compile(r'<a[^>]+href="([^"]+\.pdf[^"]*)"[^>]*>(.*?)</a>', re.S | re.I)
    for match in pattern.finditer(page):
        text = html_module.unescape(re.sub(r"<[^>]+>", "", match.group(2))).strip()
        if needle in text:
            return urljoin(BASE, match.group(1))
    raise LookupError(f"PDF link containing {needle!r} not found on the timetable page")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def download(url: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    path.write_bytes(response.content)


def page_count(path: Path) -> int:
    import subprocess

    out = subprocess.run(
        ["pdfinfo", str(path)], check=True, capture_output=True, text=True
    ).stdout
    match = re.search(r"^Pages:\s+(\d+)", out, re.MULTILINE)
    return int(match.group(1)) if match else 0


def build_manifest() -> dict:
    page = fetch_html()
    targets = [
        ("e1_pasaia_matiko", find_link_by_text(page, "E1 Pasaia"), PDF_DIR / "e1_pasaia_matiko.pdf"),
        ("e1_matiko_pasaia", find_link_by_text(page, "E1 Matiko - Pasaia"), PDF_DIR / "e1_matiko_pasaia.pdf"),
        ("e2_t1_hendaia_lasarte", find_link_by_text(page, "T1 Hendaia"), PDF_DIR / "e2_t1_hendaia_lasarte.pdf"),
        ("e2_t1_lasarte_hendaia", find_link_by_text(page, "T1 Lasarte"), PDF_DIR / "e2_t1_lasarte_hendaia.pdf"),
        ("e4_bilbao_bermeo", find_link_by_text(page, "E4 Bermeo"), PDF_DIR / "e4_bilbao_bermeo.pdf"),
        ("e3_l3", find_link_by_text(page, "E3 - L3"), PDF_DIR / "e3_l3.pdf"),
    ]
    entries = []
    now = datetime.now(timezone.utc).isoformat()
    for label, url, path in targets:
        download(url, path)
        entries.append(
            {
                "label": label,
                "url": url,
                "path": str(path),
                "sha256": sha256_file(path),
                "fetched_at": now,
                "page_count": page_count(path),
                "season": "Winter 2026",
                "valid_from": "2026-11-21",
                "valid_to": None,
                "generator_version": __version__,
            }
        )
    manifest = {"generated_at": now, "files": entries}
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    return manifest
