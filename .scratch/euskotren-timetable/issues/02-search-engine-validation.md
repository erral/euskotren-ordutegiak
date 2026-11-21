# Reverse-engineer the official timetable search engine

Type: research
Status: resolved
Blocked by:

## Question

Determine whether the departure search at https://www.euskotren.eus/eu/tren can be scripted to return the stop times of a service for a given date, origin and destination, and whether it is suitable for validating PDF-derived data. Document:

- the request flow (municipality → stop AJAX, form tokens and cookies, final submit);
- any JSON or XML endpoints the page uses;
- which lines and services the engine covers;
- the limitations of using it as a validation source.

Do not build a scraper. Report feasibility and a minimal reproducible request.

## Comments

- Claimed during charting by the search-engine research subagent.
- This is optional validation input, not a source of truth: the PDFs remain canonical.
- Findings: [research/02-search-engine-validation.md](../research/02-search-engine-validation.md).

## Answer

**Feasible: yes — the search is scriptable without a session or CSRF token. Suitable as a validation source: only as a spot-check, not an oracle.**

The form (`buscador_horarios_tren_form`) has no `form_token` and sets no cookies. The municipality→stop AJAX (`POST /eu/tren?ajax_form=1`, callbacks `cargarParadasOrigen` / `cargarParadasDestino`) returns Drupal AJAX JSON containing an HTML `<select>`; its only job is to resolve stop IDs. The final `POST /eu/tren` returns `302 Location: /eu/horarios/resultados?parada_origen=…&parada_destino=…&fecha-hora=…&modo=41`, so **the POST can be skipped entirely** once the stop IDs are known.

Minimal reproducible request (no cookies, no headers, no token):

```bash
curl -s 'https://www.euskotren.eus/eu/horarios/resultados?parada_origen=2619&parada_destino=2597&fecha-hora=2026-11-23T00:00'
```

Returns 32 departure/arrival rows for Eibar → Matiko-Bilbao on a winter weekday. Append `T00:00` to `fecha-hora`: a date-only value for *today* returns only departures after the server's current time.

There is **no JSON/XML data API**. `?_format=json` returns 406; `/jsonapi` and `/rest` return 404. Results are server-rendered HTML, one `<tr>` per service, with `#horaSalida` / `#horaLlegada` (overall times) and one `#resultados` block per leg.

Coverage: the train search covers E1 (Matiko–Pasaia), E2/T1 (Lasarte-Oria–Hendaia), E3/L3 (Lezama–Kukullaga/Etxebarri), E4 (Bermeo–Matiko), plus the out-of-scope Lutxana–Sondika shuttle. Official PDF labels and the map's line shorthand agree.

Key limitations for validation:

- **Only boarding/alighting times**, no intermediate stop times and no calling pattern. Transfers appear as multi-leg itineraries (leg endpoints only).
- **No trip ID and no line code** (every row is just `Trena`), so results can only be matched by time, and E2 vs T1 cannot be distinguished.
- **~31-day forward horizon** (today+31 works, today+32 returns nothing on 2026-11-21); past dates can be incomplete.
- **Weekday public holidays can return zero rows** (2026-12-07 and 2026-12-08 observed), so holiday timetables cannot be validated.
- **After-midnight services are shown on the civil next day** (e.g. 02:05 on Sunday), not as `24:xx`/`25:xx`; a day-shift transform is needed against the PDF.
- **Short turns and duplicate transfer alternatives** mean row counts can exceed a single PDF table.

Recommended use: confirm 1–3 terminus-to-terminus services per line and day type, and optionally chain a few adjacent stop pairs. Do not use it as an exhaustive or authoritative validator. PDFs remain canonical. Full flow, selectors, the 42-municipality/84-stop ID map and caveats are in the research file.
