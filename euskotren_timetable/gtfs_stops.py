"""GTFS parent-station aliases for the canonical Euskotren stops.

The GTFS feed identifies a station as a ``StopPlace`` (``location_type=1``)
and its platforms as ``Quay`` rows.  This table maps the stop-place IDs used
by the in-scope rail routes to the canonical Basque names in ``stops.py``.

The GTFS name is kept alongside the canonical name for diagnostics only; the
adapter always joins by the stop-place ID.
"""

from __future__ import annotations

GTFS_STOP_ALIASES: dict[str, tuple[str, str]] = {
    "ES:Euskotren:StopPlace:2592:": ("Aia-Orio", "Aia-Orio"),
    "ES:Euskotren:StopPlace:2631:": ("Altza-Donostia", "Altza (Donostia)"),
    "ES:Euskotren:StopPlace:2626:": ("Altzola-Elgoibar", "Altzola (Elgoibar)"),
    "ES:Euskotren:StopPlace:2802:": ("Amara-Donostia", "Amara Donostia"),
    "ES:Euskotren:StopPlace:2635:": ("Amaña-Eibar", "Amaña (Eibar)"),
    "ES:Euskotren:StopPlace:2637:": ("Amorebieta Geltokia", "Amorebieta Geltokia"),
    "ES:Euskotren:StopPlace:2586:": ("Amorebieta Geralekua", "Amorebieta Geralekua"),
    "ES:Euskotren:StopPlace:2590:": ("Anoeta-Donostia", "Anoeta (Donostia)"),
    "ES:Euskotren:StopPlace:2656:": ("Ardantza-Eibar", "Ardantza (Eibar)"),
    "ES:Euskotren:StopPlace:2646:": ("Ariz-Basauri", "Ariz (Basauri)"),
    "ES:Euskotren:StopPlace:2613:": ("Arroa-Zestoa", "Arroa (Zestoa)"),
    "ES:Euskotren:StopPlace:2615:": ("Axpe-Busturia", "Axpe (Busturia)"),
    "ES:Euskotren:StopPlace:2640:": ("Azitain-Eibar", "Azitain (Eibar)"),
    "ES:Euskotren:StopPlace:2647:": ("Añorga-Donostia", "Añorga (Donostia)"),
    "ES:Euskotren:StopPlace:2620:": ("Bedia", "Bedia"),
    "ES:Euskotren:StopPlace:2636:": ("Belaskoenea-Irun", "Belaskoenea (Irun)"),
    "ES:Euskotren:StopPlace:2803:": ("Bentaberri-Donostia", "Benta-Berri (Donostia)"),
    "ES:Euskotren:StopPlace:2632:": ("Bentak-Irun", "Bentak (Irun)"),
    "ES:Euskotren:StopPlace:2579:": ("Bermeo", "Bermeo"),
    "ES:Euskotren:StopPlace:2600:": ("Berriz", "Berriz"),
    "ES:Euskotren:StopPlace:2633:": ("Deba", "Deba"),
    "ES:Euskotren:StopPlace:2614:": ("Derio", "Derio"),
    "ES:Euskotren:StopPlace:2618:": ("Durango", "Durango"),
    "ES:Euskotren:StopPlace:2619:": ("Eibar", "Eibar"),
    "ES:Euskotren:StopPlace:2622:": ("Elgoibar", "Elgoibar"),
    "ES:Euskotren:StopPlace:2629:": ("Elotxelerri-Loiu", "Elotxelerri (Loiu)"),
    "ES:Euskotren:StopPlace:2666:": ("Ermua", "Ermua"),
    "ES:Euskotren:StopPlace:2651:": ("Errekalde-Donostia", "Errekalde (Donostia)"),
    "ES:Euskotren:StopPlace:2665:": ("Errenteria", "Errenteria"),
    "ES:Euskotren:StopPlace:2602:": ("Errotabarri-Ermua", "Errotabarri (Ermua)"),
    "ES:Euskotren:StopPlace:2591:": ("Etxebarri", "Etxebarri"),
    "ES:Euskotren:StopPlace:2606:": ("Euba-Amorebieta", "Euba (Amorebieta)"),
    "ES:Euskotren:StopPlace:2625:": ("Fanderia-Errenteria", "Fanderia (Errenteria)"),
    "ES:Euskotren:StopPlace:2643:": ("Forua", "Forua"),
    "ES:Euskotren:StopPlace:2654:": ("Gaintxurizketa-Lezo", "Gaintxurizketa (Lezo)"),
    "ES:Euskotren:StopPlace:2610:": ("Galtzaraborda-Errenteria", "Galtzaraborda (Errenteria)"),
    "ES:Euskotren:StopPlace:2645:": ("Gernika", "Gernika"),
    "ES:Euskotren:StopPlace:2582:": ("Hendaia", "Hendaia"),
    "ES:Euskotren:StopPlace:2624:": ("Herrera-Donostia", "Herrera (Donostia)"),
    "ES:Euskotren:StopPlace:2593:": ("Institutoa-Gernika", "Institutua (Gernika)"),
    "ES:Euskotren:StopPlace:2648:": ("Intxaurrondo-Donostia", "Intxaurrondo (Donostia)"),
    "ES:Euskotren:StopPlace:2589:": ("Irun", "Irun"),
    "ES:Euskotren:StopPlace:2649:": ("Ficoba-Irun", "Irun Ficoba"),
    "ES:Euskotren:StopPlace:2599:": ("Itsasbegi-Busturia", "Itsasbegi (Busturia)"),
    "ES:Euskotren:StopPlace:2804:": ("Kontxa-Zentroa-Donostia", "Kontxa-Zentroa (Donostia)"),
    "ES:Euskotren:StopPlace:2639:": ("Kukullaga-Etxebarri", "Kukullaga-Etxebarri"),
    "ES:Euskotren:StopPlace:2638:": ("Kurtzea-Lezama", "Kurtzea (Lezama)"),
    "ES:Euskotren:StopPlace:2601:": ("Larrondo-Loiu", "Larrondo (Loiu)"),
    "ES:Euskotren:StopPlace:2580:": ("Lasarte-Oria", "Lasarte-Oria"),
    "ES:Euskotren:StopPlace:2652:": ("Lekunbiz-Zamudio", "Lekunbiz (Zamudio)"),
    "ES:Euskotren:StopPlace:2587:": ("Lemoa", "Lemoa"),
    "ES:Euskotren:StopPlace:2607:": ("Lezama", "Lezama"),
    "ES:Euskotren:StopPlace:2608:": ("Loiola-Donostia", "Loiola (Donostia)"),
    "ES:Euskotren:StopPlace:2621:": ("Lugaritz-Donostia", "Lugaritz (Donostia)"),
    "ES:Euskotren:StopPlace:2588:": ("Lurgorri-Gernika", "Lurgorri (Gernika)"),
    "ES:Euskotren:StopPlace:2597:": ("Matiko-Bilbao", "Matiko-Bilbao"),
    "ES:Euskotren:StopPlace:2650:": ("Mendaro", "Mendaro"),
    "ES:Euskotren:StopPlace:2616:": ("Mundaka", "Mundaka"),
    "ES:Euskotren:StopPlace:2596:": ("Muxika", "Muxika"),
    "ES:Euskotren:StopPlace:2612:": ("Oiartzun", "Oiartzun"),
    "ES:Euskotren:StopPlace:2585:": ("Ola-Sondika", "Ola (Sondika)"),
    "ES:Euskotren:StopPlace:2663:": ("Otxarkoaga-Bilbao", "Otxarkoaga (Bilbao)"),
    "ES:Euskotren:StopPlace:2667:": ("Pasaia", "Pasaia"),
    "ES:Euskotren:StopPlace:2660:": ("San Kristobal-Busturia", "S. Kristobal (Busturia)"),
    "ES:Euskotren:StopPlace:2627:": ("San Lorentzo-Ermua", "San Lorentzo (Ermua)"),
    "ES:Euskotren:StopPlace:2584:": ("San Pelaio-Zarautz", "San Pelaio (Zarautz)"),
    "ES:Euskotren:StopPlace:2595:": ("Sondika", "Sondika"),
    "ES:Euskotren:StopPlace:2658:": ("Toletxegain-Elgoibar", "Toletxegain (Elgoibar)"),
    "ES:Euskotren:StopPlace:2603:": ("Traña-Abadiño", "Traña Abadiño"),
    "ES:Euskotren:StopPlace:2609:": ("Txurdinaga-Bilbao", "Txurdinaga (Bilbao)"),
    "ES:Euskotren:StopPlace:2594:": ("Unibertsitatea-Eibar", "Unibertsitatea (Eibar)"),
    "ES:Euskotren:StopPlace:2641:": ("Uribarri-Bilbao", "Uribarri (Bilbao)"),
    "ES:Euskotren:StopPlace:2661:": ("Usansolo", "Usansolo"),
    "ES:Euskotren:StopPlace:2653:": ("Usurbil", "Usurbil"),
    "ES:Euskotren:StopPlace:2655:": ("Zaldibar", "Zaldibar"),
    "ES:Euskotren:StopPlace:2642:": ("Zamudio", "Zamudio"),
    "ES:Euskotren:StopPlace:2664:": ("Zarautz", "Zarautz"),
    "ES:Euskotren:StopPlace:2577:": (
        "Zazpikaleak/Casco Viejo-Bilbao",
        "Zazpikaleak/Casco Viejo (Bilbao)",
    ),
    "ES:Euskotren:StopPlace:2657:": ("Zugaztieta-Muxika", "Zugastieta (Muxika)"),
    "ES:Euskotren:StopPlace:2598:": ("Zuhatzu-Galdakao", "Zuhatzu (Galdakao)"),
    "ES:Euskotren:StopPlace:2604:": ("Zumaia", "Zumaia"),
    "ES:Euskotren:StopPlace:2617:": ("Zurbaranbarri-Bilbao", "Zurbaranbarri (Bilbao)"),
}


def canonical_stop(parent_station: str, gtfs_name: str | None = None) -> str:
    """Return the canonical stop name for a GTFS parent station."""
    try:
        return GTFS_STOP_ALIASES[parent_station][1]
    except KeyError:
        label = f" ({gtfs_name})" if gtfs_name else ""
        raise ValueError(f"unmapped GTFS parent station {parent_station}{label}") from None
