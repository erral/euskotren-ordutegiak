import unittest

from euskotren_timetable.source_notes import SOURCE_NOTES


class SourceNotesTests(unittest.TestCase):
    def test_pasaia_aia_orio_notes(self):
        texts = " ".join(note["note_es"] for note in SOURCE_NOTES)
        self.assertIn("desde Pasaia a Aia-Orio", texts)
        self.assertIn("desde Aia-Orio a Pasaia", texts)

    def test_usansolo_matiko_notes(self):
        texts = " ".join(note["note_es"] for note in SOURCE_NOTES)
        self.assertIn("desde Usansolo a Matiko", texts)
        self.assertIn("desde Matiko a Usansolo", texts)

    def test_every_note_has_basque_and_spanish(self):
        for note in SOURCE_NOTES:
            self.assertTrue(note["note_eu"])
            self.assertTrue(note["note_es"])
            self.assertTrue(note["meaning"])


if __name__ == "__main__":
    unittest.main()
