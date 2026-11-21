"""Verbatim side notes printed on the source posters.

These notes explain why some stations are omitted from the wide full-line
tables: every train serves them, so the poster prints only the major stops.
They are kept as data so the workbook can show the source wording.
"""

SOURCE_NOTES = [
    {
        "pdf": "e1_pasaia_matiko.pdf",
        "scope": "E1 Pasaia -> Matiko full-line",
        "note_eu": "Trenek Pasaia eta Aia-Orio arteko geltoki guztietan geldaldia burutuko dute.",
        "note_es": "Los trenes paran en todas las estaciones desde Pasaia a Aia-Orio.",
        "meaning": (
            "Every train serves every station on the Pasaia-Aia-Orio section, "
            "including the eight Topo stops omitted from the 42-column full-line table."
        ),
    },
    {
        "pdf": "e1_matiko_pasaia.pdf",
        "scope": "E1 Matiko -> Pasaia full-line",
        "note_eu": "Trenek Aia-Orio eta Pasaia arteko geltoki guztietan geldaldia burutuko dute.",
        "note_es": "Los trenes paran en todas las estaciones desde Aia-Orio a Pasaia.",
        "meaning": (
            "Every train serves every station on the Aia-Orio-Pasaia section, "
            "including the eight Topo stops omitted from the 42-column full-line table."
        ),
    },
    {
        "pdf": "e1_pasaia_matiko.pdf",
        "scope": "E1 Pasaia -> Matiko full-line",
        "note_eu": "Trenek Usansolo eta Matiko arteko geltoki guztietan geldaldia burutuko dute.",
        "note_es": "Los trenes paran en todas las estaciones desde Usansolo a Matiko.",
        "meaning": "Every train serves every station on the Usansolo-Matiko Bilbao core.",
    },
    {
        "pdf": "e1_matiko_pasaia.pdf",
        "scope": "E1 Matiko -> Pasaia full-line",
        "note_eu": "Trenek Matiko eta Usansolo arteko geltoki guztietan geldaldia burutuko dute.",
        "note_es": "Los trenes paran en todas las estaciones desde Matiko a Usansolo.",
        "meaning": "Every train serves every station on the Matiko-Usansolo Bilbao core.",
    },
]
