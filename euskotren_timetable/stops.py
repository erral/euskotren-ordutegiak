"""Canonical stop lists from the winter-2026 inventory.

There is no City entity. Stops that share a municipality are distinct.
"""

from dataclasses import dataclass

E1_STOPS = [
    "Pasaia",
    "Altza (Donostia)",
    "Herrera (Donostia)",
    "Intxaurrondo (Donostia)",
    "Loiola (Donostia)",
    "Anoeta (Donostia)",
    "Amara Donostia",
    "Kontxa-Zentroa (Donostia)",
    "Benta-Berri (Donostia)",
    "Lugaritz (Donostia)",
    "Añorga (Donostia)",
    "Errekalde (Donostia)",
    "Usurbil",
    "Aia-Orio",
    "San Pelaio (Zarautz)",
    "Zarautz",
    "Zumaia",
    "Arroa (Zestoa)",
    "Deba",
    "Mendaro",
    "Altzola (Elgoibar)",
    "Toletxegain (Elgoibar)",
    "Elgoibar",
    "Azitain (Eibar)",
    "Eibar",
    "Ardantza (Eibar)",
    "Amaña (Eibar)",
    "Unibertsitatea (Eibar)",
    "San Lorentzo (Ermua)",
    "Errotabarri (Ermua)",
    "Ermua",
    "Zaldibar",
    "Berriz",
    "Traña Abadiño",
    "Durango",
    "Euba (Amorebieta)",
    "Amorebieta Geltokia",
    "Lemoa",
    "Bedia",
    "Usansolo",
    "Zuhatzu (Galdakao)",
    "Ariz (Basauri)",
    "Etxebarri",
    "Kukullaga-Etxebarri",
    "Otxarkoaga (Bilbao)",
    "Txurdinaga (Bilbao)",
    "Zurbaranbarri (Bilbao)",
    "Zazpikaleak/Casco Viejo (Bilbao)",
    "Uribarri (Bilbao)",
    "Matiko-Bilbao",
]

E2_STOPS = [
    "Hendaia",
    "Irun Ficoba",
    "Irun",
    "Belaskoenea (Irun)",
    "Bentak (Irun)",
    "Gaintxurizketa (Lezo)",
    "Oiartzun",
    "Fanderia (Errenteria)",
    "Errenteria",
    "Galtzaraborda (Errenteria)",
    "Pasaia",
    "Altza (Donostia)",
    "Herrera (Donostia)",
    "Intxaurrondo (Donostia)",
    "Loiola (Donostia)",
    "Anoeta (Donostia)",
    "Amara Donostia",
    "Kontxa-Zentroa (Donostia)",
    "Benta-Berri (Donostia)",
    "Lugaritz (Donostia)",
    "Añorga (Donostia)",
    "Errekalde (Donostia)",
    "Lasarte-Oria",
]

E3L3_STOPS = [
    "Lezama",
    "Kurtzea (Lezama)",
    "Zamudio",
    "Lekunbiz (Zamudio)",
    "Derio",
    "Elotxelerri (Loiu)",
    "Larrondo (Loiu)",
    "Sondika",
    "Ola (Sondika)",
    "Matiko-Bilbao",
    "Uribarri (Bilbao)",
    "Zazpikaleak/Casco Viejo (Bilbao)",
    "Zurbaranbarri (Bilbao)",
    "Txurdinaga (Bilbao)",
    "Otxarkoaga (Bilbao)",
    "Kukullaga-Etxebarri",
]

E4_STOPS = [
    "Matiko-Bilbao",
    "Uribarri (Bilbao)",
    "Zazpikaleak/Casco Viejo (Bilbao)",
    "Zurbaranbarri (Bilbao)",
    "Txurdinaga (Bilbao)",
    "Otxarkoaga (Bilbao)",
    "Kukullaga-Etxebarri",
    "Etxebarri",
    "Ariz (Basauri)",
    "Zuhatzu (Galdakao)",
    "Usansolo",
    "Bedia",
    "Lemoa",
    "Amorebieta Geralekua",
    "Zugastieta (Muxika)",
    "Muxika",
    "Lurgorri (Gernika)",
    "Gernika",
    "Institutua (Gernika)",
    "Forua",
    "S. Kristobal (Busturia)",
    "Axpe (Busturia)",
    "Itsasbegi (Busturia)",
    "Mundaka",
    "Bermeo",
]

LINE_STOPS = {
    "E1": E1_STOPS,
    "E2-T1": E2_STOPS,
    "E3-L3": E3L3_STOPS,
    "E4": E4_STOPS,
}

# The full-line E1 table has 42 columns: it omits stops where every train stops.
E1_FULL_42 = [
    "Pasaia",
    "Anoeta (Donostia)",
    "Amara Donostia",
    "Kontxa-Zentroa (Donostia)",
    "Benta-Berri (Donostia)",
    "Aia-Orio",
    "San Pelaio (Zarautz)",
    "Zarautz",
    "Zumaia",
    "Arroa (Zestoa)",
    "Deba",
    "Mendaro",
    "Altzola (Elgoibar)",
    "Toletxegain (Elgoibar)",
    "Elgoibar",
    "Azitain (Eibar)",
    "Eibar",
    "Ardantza (Eibar)",
    "Amaña (Eibar)",
    "Unibertsitatea (Eibar)",
    "San Lorentzo (Ermua)",
    "Errotabarri (Ermua)",
    "Ermua",
    "Zaldibar",
    "Berriz",
    "Traña Abadiño",
    "Durango",
    "Euba (Amorebieta)",
    "Amorebieta Geltokia",
    "Lemoa",
    "Bedia",
    "Usansolo",
    "Zuhatzu (Galdakao)",
    "Ariz (Basauri)",
    "Etxebarri",
    "Kukullaga-Etxebarri",
    "Otxarkoaga (Bilbao)",
    "Txurdinaga (Bilbao)",
    "Zurbaranbarri (Bilbao)",
    "Zazpikaleak/Casco Viejo (Bilbao)",
    "Uribarri (Bilbao)",
    "Matiko-Bilbao",
]

# The Pasaia -> Zumaia partial table supplies the omitted Topo times.
E1_PARTIAL_17 = [
    "Pasaia",
    "Altza (Donostia)",
    "Herrera (Donostia)",
    "Intxaurrondo (Donostia)",
    "Loiola (Donostia)",
    "Anoeta (Donostia)",
    "Amara Donostia",
    "Kontxa-Zentroa (Donostia)",
    "Benta-Berri (Donostia)",
    "Lugaritz (Donostia)",
    "Añorga (Donostia)",
    "Errekalde (Donostia)",
    "Usurbil",
    "Aia-Orio",
    "San Pelaio (Zarautz)",
    "Zarautz",
    "Zumaia",
]

assert len(E1_STOPS) == 50
assert len(E1_FULL_42) == 42
assert len(E1_PARTIAL_17) == 17
assert set(E1_FULL_42).issubset(E1_STOPS)
assert set(E1_PARTIAL_17).issubset(E1_STOPS)

E1_TOP0_MISSING = [stop for stop in E1_STOPS if stop not in E1_FULL_42]
assert len(E1_TOP0_MISSING) == 8

SHARED_TRUNKS = {
    "E1-E2": [
        "Pasaia",
        "Altza (Donostia)",
        "Herrera (Donostia)",
        "Intxaurrondo (Donostia)",
        "Loiola (Donostia)",
        "Anoeta (Donostia)",
        "Amara Donostia",
        "Kontxa-Zentroa (Donostia)",
        "Benta-Berri (Donostia)",
        "Lugaritz (Donostia)",
        "Añorga (Donostia)",
        "Errekalde (Donostia)",
    ],
    "E1-E4": [
        "Lemoa",
        "Bedia",
        "Usansolo",
        "Zuhatzu (Galdakao)",
        "Ariz (Basauri)",
        "Etxebarri",
        "Kukullaga-Etxebarri",
        "Otxarkoaga (Bilbao)",
        "Txurdinaga (Bilbao)",
        "Zurbaranbarri (Bilbao)",
        "Zazpikaleak/Casco Viejo (Bilbao)",
        "Uribarri (Bilbao)",
        "Matiko-Bilbao",
    ],
    "E1-E3L3-E4": [
        "Matiko-Bilbao",
        "Uribarri (Bilbao)",
        "Zazpikaleak/Casco Viejo (Bilbao)",
        "Zurbaranbarri (Bilbao)",
        "Txurdinaga (Bilbao)",
        "Otxarkoaga (Bilbao)",
        "Kukullaga-Etxebarri",
    ],
}


@dataclass(frozen=True)
class Stop:
    stop_id: str
    name: str
    lines: tuple[str, ...]


def _build_registry() -> dict[str, Stop]:
    order: list[str] = []
    memberships: dict[str, list[str]] = {}
    for line, stops in LINE_STOPS.items():
        for stop in stops:
            if stop not in memberships:
                memberships[stop] = []
                order.append(stop)
            if line not in memberships[stop]:
                memberships[stop].append(line)
    return {
        name: Stop(f"S{i:03d}", name, tuple(memberships[name])) for i, name in enumerate(order, 1)
    }


STOP_REGISTRY = _build_registry()


def stop_id(name: str) -> str:
    return STOP_REGISTRY[name].stop_id
