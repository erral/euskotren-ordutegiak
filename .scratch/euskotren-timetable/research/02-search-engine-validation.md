# Reverse-engineering the official Euskotren timetable search engine

- **Ticket**: [02 — Reverse-engineer the official timetable search engine](../issues/02-search-engine-validation.md)
- **Researched**: 2026-11-21 (Europe/Madrid), against the live site
- **Scope**: feasibility + validation suitability only. No production scraper was built.
- **Primary source**: `https://www.euskotren.eus/eu/tren`, `https://www.euskotren.eus/eu/tren/ordutegiak`, and the live `/eu/horarios/resultados` responses.

## Verdict (short)

**Scriptable: yes.** The engine is a server-rendered Drupal 8 site. The search form needs no CSRF token and sets no cookies for anonymous users, and the final form submit 302-redirects to a **plain GET URL** keyed by stop IDs. A single unauthenticated `GET` returns the full result set for a date and stop pair. The only scripting cost is a one-time municipality→stop-ID lookup (42 municipalities, one AJAX POST each).

**Suitable as a validation source: only as a spot-check, not as an oracle.** The engine exposes only **boarding and alighting times** (departure at origin, arrival at destination), plus interchange times for transfer itineraries. It does **not** expose intermediate stop times, a trip/service ID, or a line code. It also has a ~31-day forward horizon, unreliable past dates, zero results on some weekday holidays, and a different after-midnight convention from the PDFs. It is good for confirming that a terminus-to-terminus service exists at a given time on a given day type; it cannot validate a full calling pattern without many chained queries that are not reliably joinable.

**PDFs remain canonical.** Use the engine to sample-check a handful of services per line/day type, not to drive the workbook.

---

## 1. What the page is

`https://www.euskotren.eus/eu/tren` is Drupal 8 (`X-Generator: Drupal 8`). The search is a custom form, not a View and not a client-side app.

Form (`train.html`, line 500):

```html
<form class="buscador-horarios-tren-form"
      data-drupal-selector="buscador-horarios-tren-form"
      action="/eu/tren" method="post"
      id="buscador-horarios-tren-form" accept-charset="UTF-8">
```

Fields:

| Field | Meaning | Notes |
|---|---|---|
| `municipiOrigen` | origin municipality ID | note the typo: `municipi`, not `municipio` |
| `parada_origen` | origin stop ID | **not present initially**; injected by AJAX |
| `municipioDestino` | destination municipality ID | |
| `parada_destino` | destination stop ID | **not present initially**; injected by AJAX |
| `fecha-hora` | date | `<input type="date">`, default = today |
| `op` | submit button | value `Bilatu` |
| `form_build_id` | Drupal form build id | hidden; rotates on every AJAX rebuild |
| `form_id` | `buscador_horarios_tren_form` | hidden |

There is **no `form_token`** in the rendered form, and the initial `GET` sets **no cookies** (the cookie jar stayed empty). Anonymous scripting therefore needs no session and no CSRF token.

The AJAX handlers are declared in `drupalSettings` (`train.html`, line 1145):

```json
"ajax": {
  "edit-municipiodestino": { "callback": "::cargarParadasDestino", "wrapper": "parada-destino",
                             "event": "change", "url": "/eu/tren?ajax_form=1",
                             "submit": { "_triggering_element_name": "municipioDestino" } },
  "edit-municipiorigen":   { "callback": "::cargarParadasOrigen",  "wrapper": "parada-origen",
                             "event": "change", "url": "/eu/tren?ajax_form=1",
                             "submit": { "_triggering_element_name": "municipiOrigen" } }
}
```

So the municipality selects call back into the same route with `?ajax_form=1`.

---

## 2. Request flow

```
GET /eu/tren
  └─ form_build_id B0
       │
       ├─ POST /eu/tren?ajax_form=1   (_triggering_element_name=municipiOrigen, ...)
       │     └─ JSON: update_build_id B0→B1; insert <select name="parada_origen">…</select>
       │
       ├─ POST /eu/tren?ajax_form=1   (_triggering_element_name=municipioDestino, ...)
       │     └─ JSON: update_build_id B1→B2; insert <select name="parada_destino">…</select>
       │
       └─ POST /eu/tren   (parada_origen + parada_destino + fecha-hora + op=Bilatu, form_build_id=B2)
             └─ 302 Location: /eu/horarios/resultados?parada_origen=…&parada_destino=…&fecha-hora=…&modo=41
                   └─ GET that URL → full HTML results table
```

### 2.1 Municipality → stop AJAX

Request (origin; destination is identical with `municipioDestino` / `cargarParadasDestino`):

```
POST /eu/tren?ajax_form=1
X-Requested-With: XMLHttpRequest
Content-Type: application/x-www-form-urlencoded

form_build_id=form-…
form_id=buscador_horarios_tren_form
_triggering_element_name=municipiOrigen
_triggering_element_value=220
_drupal_ajax=1
municipiOrigen=220
```

The extra form fields (`municipioDestino`, `fecha-hora`, the other select) are optional; the minimal request above was verified to work. No cookies required.

Response is `application/json` and is a Drupal AJAX command array, **not** a data API:

```json
[
  {"command":"update_build_id","old":"form-YhLlp9…","new":"form-W8Chwv…"},
  {"command":"insert","method":null,"selector":null,
   "data":"<div class=\"form-item …\">…<select id=\"parada-origen\" name=\"parada_origen\">\n<option value=\"0\">Jatorriko geltokia</option>\n<option value=\"2635\">AMAÑA-EIBAR</option>…",
   "settings":{…}}
]
```

The stop list lives inside the HTML string in `data`, not in structured JSON. Parse `<option value="ID">NAME</option>` out of it.

### 2.2 Final submit

The final POST must use the `form_build_id` returned by the **last** AJAX call (B2 above). Posting with the original B0 does not redirect — the form re-renders with HTTP 200 because the AJAX-injected stop fields are not yet registered.

Verified final submit:

```
POST /eu/tren
Content-Type: application/x-www-form-urlencoded

form_build_id=form-jaAC1kW…   (from the last AJAX response)
form_id=buscador_horarios_tren_form
municipiOrigen=220
parada_origen=2619
municipioDestino=104
parada_destino=2597
fecha-hora=2026-11-23
op=Bilatu
```

Response:

```
HTTP/1.1 302
Location: /eu/horarios/resultados?parada_origen=2619&parada_destino=2597&fecha-hora=2026-11-23&modo=41
```

The body is also a meta-refresh page pointing at the same URL, so a browser and a redirect-following client land in the same place.

**Key consequence:** the POST is only a way to mint the GET URL. Nothing in the GET depends on the POST, the session, or the build id. If you already know the stop IDs, you can skip steps 1–3 entirely.

### 2.3 Results page

`GET /eu/horarios/resultados?...` returns server-rendered HTML. There is no XHR on the results page, no detail link, and no hidden form. The relevant structure (per service row) is:

```html
<table id="tablaResultados">
  <tr><td><div id="horario">
    <div id="horariosGeneral">
      <div id="horaSalida"><h2>16:11</h2></div>      <!-- overall departure -->
      …
      <div id="horaLlegada"><h2>17:25</h2></div>     <!-- overall arrival -->
      <div id="precioViaje"><h2>4.50€</h2></div>     <!-- fare -->
    </div>
    <div id="resultados">                             <!-- one block per leg -->
      <h3>Trena</h3>
      <p><b>Jatorria :</b> EIBAR</p>
      <p><b>Helmuga :</b> MATIKO-BILBAO</p>
      <p><b>Irteera ordua :</b> 16:11</p>
      <p><b>Iritsiera ordua :</b> 17:25</p>
    </div>
    <div id="iconos-bottom">…</div>
  </div></td></tr>
  …
</table>
```

Notes for parsing:

- IDs are **repeated per row** (`id="horariosGeneral"`, `id="resultados"`, `id="precioViaje"`), so scope the parse to each `<tr>`, not to the document.
- A **direct** service has one `#resultados` block.
- A **transfer** itinerary has multiple `#resultados` blocks (one per leg) and a `Garraio-aldaketak` ("transfers") label. Example (Bermeo → Amara, 2026-11-23): leg 1 Bermeo→Lemoa 06:18–07:11, leg 2 Lemoa→Amara 07:22–09:43. This is the only way intermediate points appear: as leg endpoints.
- The engine sometimes returns **two alternative routings with identical overall times** (e.g. Eibar→Hendaia 06:11–08:27 via Añorga and via Pasaia). Deduplicate on `(departure, arrival)` for validation.
- Empty-result message (Basque): `Badirudi, geltoki hauen artean egun eta ordu honetarako ez dagoela emaitzarik. Egin beste bilaketa bat.` ("It seems there are no results between these stops for this day and time.")

---

## 3. Minimal reproducible request

**One GET, no cookies, no headers, no token** — using the stop IDs from §8:

```bash
curl -s 'https://www.euskotren.eus/eu/horarios/resultados?parada_origen=2619&parada_destino=2597&fecha-hora=2026-11-23T00:00'
```

This returns 32 departure/arrival rows for Eibar → Matiko-Bilbao on Monday 2026-11-23 (winter weekday).

`modo=41` is optional; omitting it returns the same data. `modo=1`, `4`, `42`, `99` return zero rows, so `41` appears to be the train mode code but is not required.

**One-time stop-ID lookup** (only needed to build the municipality→stop map):

```bash
FBID=$(curl -s 'https://www.euskotren.eus/eu/tren' \
  | grep -o 'name="form_build_id" value="[^"]*"' | sed 's/.*value="//;s/"//')

curl -s -X POST 'https://www.euskotren.eus/eu/tren?ajax_form=1' \
  -H 'X-Requested-With: XMLHttpRequest' \
  --data-urlencode "form_build_id=$FBID" \
  --data-urlencode 'form_id=buscador_horarios_tren_form' \
  --data-urlencode '_triggering_element_name=municipiOrigen' \
  --data-urlencode '_triggering_element_value=220' \
  --data-urlencode '_drupal_ajax=1' \
  --data-urlencode 'municipiOrigen=220'
# -> Drupal AJAX JSON with <option value="2619">EIBAR</option>, etc.
```

**Short parser** (Python 3 stdlib only):

```python
import re, urllib.parse, urllib.request

def departures(origin_id, dest_id, date):
    url = "https://www.euskotren.eus/eu/horarios/resultados?" + urllib.parse.urlencode({
        "parada_origen": origin_id,
        "parada_destino": dest_id,
        "fecha-hora": date,          # e.g. "2026-11-23T00:00"
    })
    html = urllib.request.urlopen(url).read().decode()
    rows = []
    for block in re.findall(
            r'<div id="horariosGeneral">(.*?)<div id="iconos-bottom">', html, re.S):
        dep = re.search(r'id="horaSalida">\s*<h2>([^<]+)</h2>', block)
        arr = re.search(r'id="horaLlegada">\s*<h2>([^<]+)</h2>', block)
        if dep:
            rows.append((dep.group(1), arr.group(1) if arr else None))
    return rows

print(departures("2619", "2597", "2026-11-23T00:00")[:3])
# [('06:11', '07:25'), ('06:41', '07:55'), ('07:11', '08:25')]
```

The `fecha-hora` value matters (see §6.4): append `T00:00` to force the **whole day**, including for today.

---

## 4. JSON / XML endpoints the page uses

**There are none.** The page exposes no JSON or XML timetable API.

- The only AJAX on the site is the two Drupal form callbacks at `POST /eu/tren?ajax_form=1`. They return Drupal AJAX command JSON whose payload is an HTML `<select>` fragment; they carry **no times**.
- The results are server-rendered by the custom route `/eu/horarios/resultados`; there is no client-side fetch, no iframe, no XHR on the results page.
- `?_format=json` on the results route returns **HTTP 406**; `/jsonapi`, `/eu/jsonapi` and `/rest` return **404**. JSON:API/REST is not enabled.
- `robots.txt` does not disallow `/eu/horarios/resultados`.

So any validation tool must parse HTML. There is no upstream feed to query directly from this page.

> If a public GTFS/GTFS-RT feed exists elsewhere on Euskotren/open-data portals, it was not referenced by this page and was out of scope here. It would be a different (and probably better) validation channel.

---

## 5. Coverage: lines and services

The train search covers the Euskotren **rail** network. The official timetable page (`/eu/tren/ordutegiak`) labels the current winter-2026 PDFs as:

| Official label on the timetable page | Corridor | Engine verified |
|---|---|---|
| `E1 Matiko - Pasaia` / `E1 Pasaia - Matiko` | Matiko ↔ Pasaia (Bilbao–Donostia–Pasaia trunk) | yes |
| `E2 Lasarte/Oria - Hendaia` / `E2 Hendaia - Lasarte/Oria` | Lasarte-Oria ↔ Hendaia | yes |
| `T1 Lasarte/Oria - Hendaia` / `T1 Hendaia - Lasarte/Oria` | same corridor, T1-branded services | yes (corridor) |
| `E3 - L3 Lezama / Kukullaga-Etxebarri / Lezama` | Lezama ↔ Kukullaga/Etxebarri (Bilbao metro L3) | yes |
| `E4 Bermeo / Matiko / Bermeo` | Bermeo ↔ Matiko | yes |
| `Lutxana-Sondika 2026` | Lutxana–Sondika shuttle | yes (out of project scope) |

Verified end-to-end stop pairs (winter Monday 2026-11-23, full day):

| Corridor | Query | Rows |
|---|---|---|
| E1 | Matiko (2597) → Pasaia (2667) | 15 |
| E1 | Pasaia (2667) → Matiko (2597) | 15 |
| E1 | Eibar (2619) → Matiko (2597) | 32 |
| E2/T1 | Lasarte-Oria (2580) → Hendaia (2582) | 34 |
| E2/T1 | Hendaia (2582) → Lasarte-Oria (2580) | 33 |
| E3/L3 | Lezama (2607) → Kukullaga (2639) | 61 |
| E4 | Bermeo (2579) → Matiko (2597) | 31 |
| Lutxana–Sondika | Lutxana (2576) → Sondika (2595) | 17 |

The engine also plans **transfers** across corridors (e.g. Bermeo → Amara, Eibar → Hendaia), returning multi-leg itineraries.

Important coverage caveats:

- **No line label in the output.** Every result is just `Trena`. E2 and T1 are indistinguishable, and a result cannot be attributed to a PDF table by the page itself.
- **No trip/service ID.** Results are anonymous `(departure, arrival, legs)` tuples.
- **Short turns are included.** For example `Matiko→Pasaia` has 15 through services, while `Eibar→Matiko` has 32 because the engine also returns services that start/end at Eibar or Donostia. A single PDF table may list fewer services than the engine returns for an intermediate pair.
- **Different mode searches are separate.** Tram, funicular and bus have their own sections (`/eu/tranbia`, etc.) and are not part of `/eu/tren`.
- **Out of scope for the project:** Lutxana–Sondika is returned by the engine but is explicitly excluded from the workbook.

The official page's labels also clarify the map's shorthand: **E2/T1** is one physical corridor (Lasarte-Oria–Hendaia) with two service brands, **E3/L3** is Lezama–Kukullaga/Etxebarri, and **E4** is Bermeo–Matiko. The engine covers all of them. (This note is for the parent; `map.md` was not edited.)

---

## 6. Data semantics and limitations

### 6.1 Only boarding and alighting times

For a direct service the engine returns exactly two times: departure at the origin stop and arrival at the destination stop. It does **not** return the intermediate calling pattern. The only extra stop information comes from transfer itineraries, where each leg's endpoints are shown.

To validate an intermediate stop you must:

1. query each consecutive stop pair `(A→B)`, `(B→C)`, …;
2. match services across queries by time, because there is no trip ID.

This is feasible for a few spot checks but fragile: services can have different departure times at each stop, short turns appear/disappear, and the matching is heuristic. It is not a practical way to validate a whole workbook.

### 6.2 Day types and season

The engine holds a **seasonal** timetable, not a year-round one. Observed for Eibar (2619) → Matiko (2597):

| Date | Day | Rows | Reading |
|---|---|---|---|
| 2026-11-20 | Fri | 17 | previous (autumn) weekday timetable |
| 2026-11-21 | Sat | 15 with `T00:00` | winter 2026 season start (PDFs say "azaroaren 21etik aurrera") |
| 2026-11-22 | Sun | 18 | winter Sunday |
| 2026-11-23 | Mon | 32 | winter weekday (frequency increases) |
| 2026-11-28 | Sat | 15 | winter Saturday |
| 2026-12-06 | Sun | 18 | Sunday |
| 2026-12-07 | Mon | **0** | weekday public holiday |
| 2026-12-08 | Tue | **0** | weekday public holiday |
| 2026-12-09 | Wed | 32 | normal |
| 2026-12-22 | Tue | 32 | last date inside the horizon |
| 2026-12-23 | Wed | **0** | beyond the ~31-day horizon |
| 2027-01-15 | Fri | **0** | beyond the horizon |

The weekday frequency jump (17 → 32) between 2026-11-20 and 2026-11-23 is consistent with the winter-2026 timetable starting on Saturday 2026-11-21, the first weekday of which is Monday 2026-11-23. Validate only dates inside the season and inside the horizon.

### 6.3 Forward horizon ≈ 31 days

On 2026-11-21, `today+31` (2026-12-22) returned data and `today+32` (2026-12-23) returned none, as did every later date tested (2027-01-15, 2027-06-01). Treat the horizon as **about one month ahead**; it is either a rolling ~31-day cap or the end of the loaded season. In practice, you can only validate the first month of the winter-2026 PDF at a time.

### 6.4 `fecha-hora` accepts a datetime, and the time component changes behaviour

The visible form submits a date only (`type="date"`). But the route accepts a datetime string, and its presence changes the result window:

| `fecha-hora` | Result |
|---|---|
| `2026-11-21` (today) | 7 rows — only departures **after the server's current time** |
| `2026-11-21T00:00` (today) | 15 rows — **whole day** |
| `2026-11-21T23:00` (today) | 15 rows — still the whole day |
| `2026-11-23` (future) | 32 rows — whole day |
| `2026-11-23T08:00` (future) | 32 rows — whole day (time ignored) |

So: **always append `T00:00`** to get the full day. Without it, a query for "today" silently drops already-departed services. The time component is not a departure-after filter; it merely bypasses the "from now" behaviour.

### 6.5 Past dates are unreliable

Past dates inside the current season are incomplete:

| Date | Day | Rows |
|---|---|---|
| 2026-11-01 | Sun | 4 |
| 2026-11-08 | Sun | 5 |
| 2026-11-15 | Sun | 5 |
| 2026-11-22 | Sun | 18 |

Weekday past dates looked complete (17), but past Sundays were missing most of the day. Do not use the engine to back-validate dates before "today" or before the season start.

### 6.6 Weekday holidays can return zero

2026-12-07 (Mon) and 2026-12-08 (Tue) returned **0 rows**, while 2026-12-06 (Sun, also a holiday) returned 18 and 2026-12-09 (Wed) returned 32. Whatever the internal cause (missing holiday calendar entry / no special timetable loaded), the engine cannot be trusted for **holiday** validation. This matters because the PDFs include a Sunday/holiday day type; the engine only reliably gives Sunday service.

### 6.7 After-midnight services use the civil next day

The engine shows after-midnight trains as early-morning times on the **following calendar day**, not as `24:xx`/`25:xx`:

- Sunday 2026-11-22 Eibar → Matiko starts at `02:05` and `04:05`.
- Saturday 2026-11-28 starts at `08:11`; it does **not** list `24:xx`/`25:xx`.

This is the Saturday-night → Sunday group in the glossary, but presented with a day offset already applied. When comparing to the PDF's `24:xx`/`25:xx` notation, you must shift the day and add 24 h.

### 6.8 No stable identity for a service

Because there is no trip ID and no line code, a validation tool can only assert **set-level** facts:

- "for this date and stop pair, the engine has a departure at HH:MM arriving at HH:MM";
- "the engine has N departures between these two stops on this day type".

It cannot assert "PDF service #123 has the same stops/times as engine service X", except by time matching.

### 6.9 HTML parsing quirks

- Duplicate `id` values per row — scope to `<tr>`.
- Transfer alternatives can duplicate the same overall `(departure, arrival)` — dedupe.
- Results are sorted by departure time.
- The page is `no-store` / uncacheable; no caching layer to worry about, but also no ETag-based polling.
- Locale prefixes (`/eu/`, `/es/`, `/en/`, `/fr/`) return the same data and structure; stop IDs are locale-independent.

---

## 7. Suitability for validating PDF-derived data

**Recommended use:** a *spot-check* validator, run manually or as a pre-merge sanity check, on a small sample:

- For each in-scope line and each day type, pick 1–3 terminus-to-terminus services and confirm the engine returns a departure at the origin and an arrival at the destination at the PDF's times.
- Confirm the **count of departures** at a terminus for a day type matches the PDF (after de-duplicating transfer alternatives and allowing for short turns).
- Optionally chain a few adjacent stop pairs to check intermediate times on one service.

**Do not use it to:**

- validate the full calling pattern of every service (no intermediate stops);
- validate holiday services (zero results on weekday holidays);
- validate dates beyond ~31 days ahead;
- validate dates before today / before the season start;
- attribute a service to a specific PDF table (no line code, no trip ID);
- validate after-midnight notation without a day-shift transform;
- replace PDF extraction as the source of truth.

**Bottom line:** the engine is a useful, cheap, unauthenticated second opinion for departure/arrival times at endpoints. It is not a complete or authoritative mirror of the PDF timetable, and it is not suitable as the primary validation source. Treat a mismatch as a prompt to re-check the PDF, and a match as weak corroboration.

If stronger validation is needed later, look for an official GTFS/GTFS-RT or open-data feed (not exposed by this page) rather than expanding HTML scraping.

---

## 8. Stop-ID map (municipality → engine stop IDs)

Generated by one AJAX lookup per municipality on 2026-11-21. Names are the engine's uppercase Basque labels. This is the mapping a validation tool needs; it is stable but should be re-fetched if the engine changes.

<details>
<summary>All 42 municipalities / 84 stops (click to expand)</summary>

| Municipality (ID) | Stops (ID = name) |
|---|---|
| Abadiño (77) | 2603 = TRAÑA-ABADIÑO |
| Aia (191) | 2592 = AIA-ORIO |
| Amorebieta-Etxano (81) | 2637 = AMOREBIETA GELTOKIA; 2586 = AMOREBIETA GERALEKUA; 2606 = EUBA-AMOREBIETA |
| Basauri (98) | 2646 = ARIZ-BASAURI |
| Bedia (99) | 2620 = BEDIA |
| Bermeo (101) | 2579 = BERMEO |
| Berriz (103) | 2600 = BERRIZ |
| Bilbao (104) | 2597 = MATIKO-BILBAO; 2663 = OTXARKOAGA-BILBAO; 2609 = TXURDINAGA-BILBAO; 2641 = URIBARRI-BILBAO; 2577 = ZAZPIKALEAK/CASCO VIEJO-BILBAO; 2617 = ZURBARANBARRI-BILBAO |
| Busturia (105) | 2615 = AXPE-BUSTURIA; 2599 = ITSASBEGI-BUSTURIA; 2660 = SAN KRISTOBAL-BUSTURIA |
| Deba (218) | 2633 = DEBA |
| Derio (106) | 2614 = DERIO |
| Donostia-San Sebastián (219) | 2631 = ALTZA-DONOSTIA; 2802 = AMARA-DONOSTIA; 2590 = ANOETA-DONOSTIA; 2647 = AÑORGA-DONOSTIA; 2803 = BENTABERRI-DONOSTIA; 2651 = ERREKALDE-DONOSTIA; 2624 = HERRERA-DONOSTIA; 2648 = INTXAURRONDO-DONOSTIA; 2804 = KONTXA-ZENTROA-DONOSTIA; 2608 = LOIOLA-DONOSTIA; 2621 = LUGARITZ-DONOSTIA |
| Durango (108) | 2618 = DURANGO |
| Eibar (220) | 2635 = AMAÑA-EIBAR; 2656 = ARDANTZA-EIBAR; 2640 = AZITAIN-EIBAR; 2619 = EIBAR; 2594 = UNIBERTSITATEA-EIBAR |
| Elgoibar (223) | 2626 = ALTZOLA-ELGOIBAR; 2622 = ELGOIBAR; 2658 = TOLETXEGAIN-ELGOIBAR |
| Erandio (112) | 2576 = LUTXANA-ERANDIO |
| Ermua (114) | 2666 = ERMUA; 2602 = ERROTABARRI-ERMUA; 2627 = SAN LORENTZO-ERMUA |
| Errenteria (224) | 2665 = ERRENTERIA; 2625 = FANDERIA-ERRENTERIA; 2610 = GALTZARABORDA-ERRENTERIA |
| Etxebarri (116) | 2591 = ETXEBARRI; 2639 = KUKULLAGA-ETXEBARRI |
| Forua (118) | 2643 = FORUA |
| Galdakao (120) | 2598 = ZUHATZU-GALDAKAO |
| Gernika-Lumo (126) | 2645 = GERNIKA; 2593 = INSTITUTOA-GERNIKA; 2588 = LURGORRI-GERNIKA |
| Hendaia (277) | 2582 = HENDAIA |
| Irun (238) | 2636 = BELASKOENEA-IRUN; 2632 = BENTAK-IRUN; 2649 = FICOBA-IRUN; 2589 = IRUN |
| Lasarte-Oria (242) | 2580 = LASARTE-ORIA |
| Lemoa (144) | 2587 = LEMOA |
| Lezama (146) | 2638 = KURTZEA-LEZAMA; 2607 = LEZAMA |
| Lezo (248) | 2654 = GAINTXURIZKETA-LEZO |
| Loiu (147) | 2629 = ELOTXELERRI-LOIU; 2601 = LARRONDO-LOIU |
| Mendaro (250) | 2650 = MENDARO |
| Mundaka (156) | 2616 = MUNDAKA |
| Muxika (161) | 2596 = MUXIKA; 2657 = ZUGAZTIETA-MUXIKA |
| Oiartzun (253) | 2612 = OIARTZUN |
| Pasaia (261) | 2667 = PASAIA |
| Sondika (171) | 2585 = OLA-SONDIKA; 2595 = SONDIKA; 2611 = ZANGROIZ-SONDIKA |
| Usansolo (288) | 2661 = USANSOLO |
| Usurbil (267) | 2653 = USURBIL |
| Zaldibar (181) | 2655 = ZALDIBAR |
| Zamudio (183) | 2652 = LEKUNBIZ-ZAMUDIO; 2642 = ZAMUDIO |
| Zarautz (270) | 2584 = SAN PELAIO-ZARAUTZ; 2664 = ZARAUTZ |
| Zestoa (273) | 2613 = ARROA-ZESTOA |
| Zumaia (275) | 2604 = ZUMAIA |

</details>

Note: the municipality list is coarse and sometimes incomplete relative to the PDFs (e.g. it contains 5 Eibar stops, matching the glossary's distinct-stop rule). Stop names are uppercased and municipality-suffixed, so they need normalizing against the PDF's display names.

---

## 9. Method and provenance

- All observations were made on 2026-11-21 against `https://www.euskotren.eus` with plain `curl` / Python `urllib`, no authentication, no cookies.
- The form, AJAX settings and stop lists were read from the HTML of `/eu/tren`.
- The flow, redirect and JSON shapes were verified by replaying the requests (origin AJAX → destination AJAX → final POST → 302 → GET).
- Counts in the tables are the number of `<div id="horariosGeneral">` rows in the results HTML.
- No production scraper was committed. The probe lived in `/tmp/opencode/euskotren-research/` only.
- `modo=41` was observed in the redirect; omitting it gives the same results.

### Reproduce the headline result

```bash
# full winter Monday, Eibar -> Matiko-Bilbao: expect 32 rows
curl -s 'https://www.euskotren.eus/eu/horarios/resultados?parada_origen=2619&parada_destino=2597&fecha-hora=2026-11-23T00:00' \
  | grep -c 'id="horariosGeneral"'
```

### Reproduce the "today" caveat

```bash
# today, date-only: only future departures
curl -s 'https://www.euskotren.eus/eu/horarios/resultados?parada_origen=2619&parada_destino=2597&fecha-hora=2026-11-21' \
  | grep -c 'id="horariosGeneral"'
# today, with T00:00: full day
curl -s 'https://www.euskotren.eus/eu/horarios/resultados?parada_origen=2619&parada_destino=2597&fecha-hora=2026-11-21T00:00' \
  | grep -c 'id="horariosGeneral"'
```
