import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from euskotren_timetable.site import build_site, validate_site
from tests.support import make_service

MANIFEST = {
    "files": [
        {
            "label": "test",
            "url": "https://example.com/test.pdf",
            "sha256": "abc",
            "season": "Winter 2026",
            "valid_from": "2026-11-21",
            "valid_to": None,
        }
    ]
}


def sample_services():
    e1 = make_service(
        "E1-WD-0535",
        "WD",
        "E1",
        "Pasaia-Matiko",
        "5:35",
        stops=("Pasaia", "Altza (Donostia)", "Herrera (Donostia)"),
    )
    e1.stop_times[1].disposition = "unpublished"
    e1.stop_times[1].time = "?"
    e1.stop_times[2].disposition = "pass"
    e1.stop_times[2].time = None
    e2 = make_service(
        "E2-WD-0535",
        "WD",
        "E2-T1",
        "Hendaia-Lasarte",
        "5:35",
        stops=("Pasaia", "Altza (Donostia)"),
    )
    saturday = make_service(
        "E1-SA-0800",
        "SA",
        "E1",
        "Pasaia-Matiko",
        "8:00",
        stops=("Pasaia", "Altza (Donostia)"),
    )
    return [e2, saturday, e1]


class SiteTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.output = Path(self.temp.name) / "site"
        self.services = sample_services()
        build_site(
            self.services,
            self.output,
            MANIFEST,
            generated_at="2026-11-21T00:00:00+00:00",
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_files_and_json(self):
        self.assertTrue((self.output / "index.html").exists())
        self.assertTrue((self.output / "master.html").exists())
        self.assertTrue((self.output / "assets" / "site.css").exists())
        self.assertTrue((self.output / ".nojekyll").exists())
        data = json.loads((self.output / "data" / "services.json").read_text())
        self.assertEqual(data["schema_version"], 1)
        self.assertEqual(len(data["services"]), 3)
        self.assertEqual(data["services"][0]["service_id"], "E1-WD-0535")
        self.assertEqual(data["meta"]["generated_at"], "2026-11-21T00:00:00+00:00")

    def test_corridor_pages_and_order(self):
        weekday = (self.output / "line" / "e1" / "pasaia-matiko" / "weekday.html").read_text()
        saturday = (self.output / "line" / "e1" / "pasaia-matiko" / "saturday.html").read_text()
        self.assertIn('id="E1-WD-0535"', weekday)
        self.assertIn('id="E2-WD-0535"', weekday)
        self.assertLess(weekday.index('id="E1-WD-0535"'), weekday.index('id="E2-WD-0535"'))
        self.assertIn('id="E1-SA-0800"', saturday)
        cross_line = (
            self.output / "line" / "e2-t1" / "hendaia-lasarte" / "saturday.html"
        ).read_text()
        self.assertIn('id="E1-SA-0800"', cross_line)
        self.assertNotIn('id="E2-SA-', cross_line)

    def test_cell_states_and_accessibility(self):
        page = (self.output / "line" / "e1" / "pasaia-matiko" / "weekday.html").read_text()
        self.assertIn('class="unpublished">?</td>', page)
        self.assertIn('class="pass">&gt;</td>', page)
        self.assertIn('scope="row"', page)
        self.assertIn('scope="col"', page)
        self.assertIn("<caption>", page)
        self.assertIn('id="show-metadata"', page)
        self.assertIn('class="service-id metadata-col"', page)
        self.assertIn('class="metadata-col"', page)
        self.assertIn('class="stop-first"', page)
        self.assertIn('class="time stop-first"', page)

    def test_master_rows_and_attributes(self):
        page = (self.output / "master.html").read_text()
        self.assertEqual(page.count('data-line="'), 3)
        self.assertIn('data-search="e1-wd-0535', page)
        self.assertIn('data-departure="335"', page)
        self.assertIn('href="line/e1/pasaia-matiko/weekday.html"', page)
        self.assertNotIn('id="show-metadata"', page)

    def test_index_links_only_available_calendars(self):
        page = (self.output / "index.html").read_text()
        self.assertIn('href="line/e1/pasaia-matiko/weekday.html"', page)
        self.assertNotIn('id="show-metadata"', page)
        self.assertIn('href="line/e1/pasaia-matiko/saturday.html"', page)
        self.assertNotIn('href="line/e1/pasaia-matiko/sunday-holiday.html"', page)

    def test_site_validates(self):
        self.assertEqual(validate_site(self.output), [])
        self.assertEqual(list(self.output.rglob("*.pdf")), [])

    def test_workbook_download(self):
        workbook = Path(self.temp.name) / "book.xlsx"
        workbook.write_bytes(b"fake workbook")
        output = Path(self.temp.name) / "site-with-workbook"
        build_site(
            self.services,
            output,
            MANIFEST,
            workbook_path=workbook,
            generated_at="2026-11-21T00:00:00+00:00",
        )
        self.assertTrue((output / "downloads" / "euskotren_timetables_winter_2026.xlsx").exists())
        self.assertEqual(validate_site(output), [])

    def test_validate_site_reports_broken_link(self):
        index = self.output / "index.html"
        index.write_text(
            index.read_text().replace("</body>", '<a href="missing.html">x</a></body>')
        )
        errors = validate_site(self.output)
        self.assertTrue(any("broken link" in error for error in errors))

    def test_validate_site_reports_duplicate_ids(self):
        page = self.output / "line" / "e1" / "pasaia-matiko" / "weekday.html"
        page.write_text(page.read_text().replace('<tr id="E2-WD-0535">', '<tr id="E1-WD-0535">'))
        errors = validate_site(self.output)
        self.assertTrue(any("duplicate id" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
