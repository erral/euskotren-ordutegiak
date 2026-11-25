# Licence and attribution for the Euskotren GTFS (Open Data Euskadi / Moveuskadi)

- **Ticket**: [06 — Confirm Open Data Euskadi licence and attribution](../issues/06-license-attribution.md)
- **Researched**: 2026-11-25 (Europe/Madrid), against the live portals and the feed published that day.
- **Scope**: licence, attribution, redistribution constraints. Not legal advice.
- **Primary sources**: the Open Data Euskadi dataset record (human page + DCAT RDF + schema.org JSON-LD), the Open Data Euskadi legal notice, the portal's own legal report, and the GTFS zip itself.

## Verdict (short)

**The dataset is licensed CC BY 4.0 (Creative Commons Attribution 4.0 International).** The licence is stated explicitly, and machine-readably, in the catalogue record for the Moveuskadi dataset — of which the Euskotren GTFS is one distribution:

1. the dataset card's *Lizentzia / Licencia* field renders a **CC BY badge** whose `title`/`alt` is `Attribution CC BY` / `Reconocimiento CC BY` and whose `href` is `https://creativecommons.org/licenses/by/4.0/`;
2. the DCAT RDF export declares `<dct:license rdf:resource="https://creativecommons.org/licenses/by/4.0/"/>` (identical in the `eu` and `es` exports);
3. the page's embedded schema.org JSON-LD says `"https://schema.org/license": "https://creativecommons.org/licenses/by/4.0/"`.

The GTFS zip itself contains **no licence statement**: `feed_info.txt` and `attributions.txt` name the publisher/operator but carry no licence field (GTFS `attributions.txt` has no licence field at all), and the archive has no `LICENSE` file. So the licence has to be taken from the catalogue record, not from the feed.

**Redistribution is allowed, including derived works and commercial use**, provided attribution is given and changes are indicated. The derived workbook/HTML/JSON can be published; they should carry the attribution notice below and must not be relicensed under more restrictive terms.

**Caveats** (details in §7): there is no dataset-specific human-readable licence page beyond the badge; the badge's neighbouring "Lege-informazioa / Información legal" link points at the *general* euskadi.eus all-rights-reserved notice, not the Open Data notice; and the Open Data legal notice carries a legacy "do not alter the content" clause that sits awkwardly with CC BY 4.0's permission to adapt. None of these contradict the CC BY 4.0 grant, which is the specific and machine-readable one.

---

## 1. What the feed says (and does not say)

`https://opendata.euskadi.eus/transport/moveuskadi/euskotren/gtfs_euskotren.zip`
→ 301 → `https://s3.itbatera.euskadi.eus/.../transport/moveuskadi/euskotren/gtfs_euskotren.zip`

Archive contents: 16 standard GTFS files, no `LICENSE`, `COPYING`, `NOTICE`, `README` or similar. Confirmed by `unzip -l`.

`feed_info.txt` (verbatim):

```
feed_publisher_name,feed_publisher_url,feed_lang,default_lang,feed_start_date,feed_end_date,feed_version,feed_contact_email,feed_contact_url
Eusko Trenbideak,https://www.euskotren.eus/eu/atencion-a-la-clientela/sugerencias,eu,en,20261125,20261230,20261125043408,,https://www.euskotren.eus/eu
```

- Publisher named: **Eusko Trenbideak** (the operator/trading entity Euskotren).
- No licence, copyright or terms field. GTFS `feed_info.txt` has no such field.
- `feed_version` = `20261125043408`; feed window 2026-11-25 → 2026-12-30.

`attributions.txt` (verbatim):

```
attribution_id,agency_id,route_id,trip_id,organization_name,is_producer,is_operator,is_authority,attribution_url,attribution_email,attribution_phone
ES:Euskotren:Responsibility:1:,ES:Euskotren:Operator:EUS_Funi:,,,Eusko Trenbideak,0,1,0,https://gardentasuna.euskotren.eus/eu,,
ES:Euskotren:Responsibility:2:,ES:Euskotren:Operator:EUS_TrBi:,,,Eusko Trenbideak,0,1,0,https://gardentasuna.euskotren.eus/eu,,
ES:Euskotren:Responsibility:3:,ES:Euskotren:Operator:EUS_TrGa:,,,Eusko Trenbideak,0,1,0,https://gardentasuna.euskotren.eus/eu,,
ES:Euskotren:Responsibility:4:,ES:Euskotren:Operator:EUS_Tren:,,,Eusko Trenbideak,0,1,0,https://gardentasuna.euskotren.eus/eu,,
```

Per the GTFS reference, `attributions.txt` only records *who* the data is attributed to and in what role (`is_operator=1`), plus a URL. It is **not** a licence instrument and cannot be read as one. It does tell us the credit line the feed's authors expect: **Eusko Trenbideak**, linking to the transparency portal `https://gardentasuna.euskotren.eus/eu`.

## 2. The catalogue record (the actual licence statement)

The GTFS is not catalogued as a standalone dataset. It is one distribution of a single catalogue entry covering all operators and all formats:

- Dataset (eu): `https://opendata.euskadi.eus/katalogoa/-/moveuskadi-euskadiko-garraio-publikoaren-sarearen-datuak-operadoreak-ordutegiak-geltokiak-egutegia-tarifak-etab/`
- Dataset (es): `https://opendata.euskadi.eus/catalogo/-/moveuskadi-datos-de-la-red-de-transporte-publico-de-euskadi-operadores-horarios-paradas-calendario-tarifas-etc/`

Title (es): *"Moveuskadi. Datos de la red de transporte público de Euskadi: operadores, horarios, paradas, calendario, tarifas, etc."*
Description covers static and real-time public-transport data for the whole network, published in GTFS, GTFS-RT, NeTEx and SIRI, and cites Delegated Regulation (EU) 2017/1926.

The card's licence block (eu, verbatim HTML, de-indented):

```html
<div class="x46f-detailLabel">Lizentzia</div>
<div class="x46f-detailContent">
  <a href="https://creativecommons.org/licenses/by/4.0/" title="Attribution CC BY">
    <img class="x46f-licenseIcon" src="/AVComun/r01gContainerVA/images/opendata/licencias/r01_cc.png" alt="Attribution CC BY">
  </a>
  <p><a href="https://www.euskadi.eus/informazioa/-/lege-informazioa/">Lege-informazioa</a></p>
</div>
```

The Spanish card is the same, with `title="Reconocimiento CC BY"`, `alt="Reconocimiento CC BY"` and `Información legal` linking to `https://www.euskadi.eus/informacion/-/informacion-legal/`.

Machine-readable metadata, from the *Metadatos: RDF* link on the card:

- eu: `https://opendata.euskadi.eus/contenidos/ds_movilidad/md_ideeu_moveuskadi/eu_def/r01DCATDataset.rdf`
- es: `https://opendata.euskadi.eus/contenidos/ds_movilidad/md_ideeu_moveuskadi/es_def/r01DCATDataset.rdf`

Both contain, on the `dcat:Dataset` node:

```xml
<dct:license rdf:resource="https://creativecommons.org/licenses/by/4.0/"/>
<dct:publisher rdf:resource="https://datos.gob.es/recurso/sector-publico/org/Organismo/A16050214"/>
```

and the page's JSON-LD repeats `"https://schema.org/license" : "https://creativecommons.org/licenses/by/4.0/"`.

Other recorded facts worth keeping:

| Field | Value |
|---|---|
| `dct:issued` | 2014-01-01 |
| `dct:modified` | 2026-11-24 (RDF) / card says updated 2026-11-25 |
| `dct:accrualPeriodicity` | hourly ("Horario"), card says "Denbora errealean" / "En tiempo real" |
| Publisher | `A16050214` (Basque Government body); card's breadcrumb "Datuen iturria: Eusko Jaurlaritza > Garraioak > Mugikortasuna" |
| Spatial | País Vasco / Euskadi |
| Themes | `transporte`, `urbanismo-infraestructuras` |

The DCAT export lists only two distributions (the SHP/FTP directory and `data-index.json`); GTFS/GTFS-RT/NeTEx/SIRI are exposed through the index. This does not create a separate licence for the GTFS: the dataset-level `dct:license` is the licence of every distribution in the record, and the card's own GTFS download is part of that record.

Distribution-level freshness (from `data-index.json`, key `data.Euskotren`):

```json
{ "format": "GTFS",
  "url": "https://opendata.euskadi.eus/transport/moveuskadi/euskotren/gtfs_euskotren.zip",
  "name": "gtfs_euskotren.zip",
  "last-update": "2026-11-25 07:01:19" }
```

HTTP `Last-Modified` for the zip was `Wed, 25 Nov 2026 06:01:19 GMT`. `data-index.json` top-level `last-update` was `2026-11-25 19:22:28`.

## 3. The Open Data Euskadi legal notice

- eu: `https://opendata.euskadi.eus/orokorra/-/opendatako-lege-informazioa/`
- es: `https://opendata.euskadi.eus/general/-/informacion-legal-opendata/`

Key passages (es, verbatim):

> El contenido y la información puesta a disposición a través del portal Open Data que estén sujetos a derechos de propiedad intelectual y cuya titularidad corresponda a la Administración General de la Comunidad Autónoma de Euskadi, estará sujeta a **la licencia Creative Commons que aparece en su página principal**.

> Según el tipo de datos facilitados para su descarga, la persona usuaria se acogerá en cada caso a **la licencia claramente establecida para cada conjunto de datos**. Esta licencia podrá ser de dos tipos: Licencia de reconocimiento de autoría (establecida en una licencia **Creative Commons Reconocimiento 4.0**) o licencia libre y gratuita de reutilización de la información pública.

> La persona usuaria asume en la descarga y posterior utilización de los datos cumpliendo las siguientes obligaciones:
> - Que el contenido de la información no sea alterado.
> - Que no se desnaturalice el sentido de la información.
> - Que **se cite la fuente** y cumpla con los requisitos establecidos en la licencia de uso de los datos.
> - Que **se mencione la fecha de la última actualización**.

This is the structure the portal itself describes: *the per-dataset licence governs*, and one of the two permitted licences is CC BY 4.0 — which is exactly what the Moveuskadi record declares.

The four bullet "obligations" are the classic art. 8 conditions of Ley 37/2007 (Spanish reuse law) and, read literally, the first is stricter than CC BY 4.0 (which permits adaptations). See §7 for how to handle that.

## 4. The portal's own legal report

The "Nola berrerabili / Datos reutilizables" page links a legal report:

`https://opendata.euskadi.eus/contenidos/informacion/reutilizar_datos/es_def/adjuntos/informe_juridico_opendata_v3.pdf`
(*Informe jurídico. Reutilización de la información. Open Data*, Iurismática Abogados; the PDF's cover says **Versión 2.0, Donostia–San Sebastián, Marzo 2010** despite the `v3` filename.)

It sets out the policy choice in the portal's own words:

> La opción escogida por el Gobierno Vasco en el Open Data en cumplimiento de la Ley 37/2007 … es la modalidad de puesta a disposición sin sujeción a ningún tipo de restricción más allá de las condiciones básicas establecidas en el artículo 8, es decir, aquellas que obligan a **citar la fuente, la fecha de la última actualización, la no alteración y desnaturalización de la información**.

and for content carrying intellectual-property rights:

> la Administración vasca ha optado … por la puesta a disposición con **licencia Creative Commons en su vertiente más abierta (by)**:
> *Reconocimiento (by):* Se permite **cualquier explotación de la obra, incluyendo una finalidad comercial, así como la creación de obras derivadas**, la distribución de las cuales también está permitida sin ninguna restricción.

That is the clearest statement of intent available: **commercial use and derivative works are intended to be allowed**. Caveat: it is from 2010, so it predates CC BY 4.0 (2013) and Directive (EU) 2019/1024; treat it as evidence of policy intent, not as the licence instrument. The instrument is the CC BY 4.0 declaration in §2.

## 5. What this means for this project

| Question | Answer |
|---|---|
| Licence | **CC BY 4.0** (`https://creativecommons.org/licenses/by/4.0/`) — international 4.0, not 3.0/ES. |
| Stated in the feed? | **No.** Stated in the catalogue record only. |
| Attribution required? | **Yes** — creator/publisher, source link, licence link, and an indication that changes were made. The portal additionally asks for the source and the **last-update date**. |
| Commercial use? | Allowed by CC BY 4.0 (and by the portal's legal report). |
| Derivative works (workbook, HTML, JSON)? | **Allowed.** Our transformation is an adaptation, which CC BY 4.0 permits. |
| May we publish the outputs? | **Yes.** Publish with the attribution notice; do not add terms that restrict what CC BY 4.0 allows. |
| Must our outputs be CC BY 4.0? | Not strictly required by the licence (no share-alike), but they must **preserve attribution** and must not be redistributed under terms that forbid what CC BY allows. Publishing them under CC BY 4.0 is the simplest, clearly compatible choice. |
| Relation to the repo's GPL-2.0 | Separate. GPL-2.0 covers the *code*; the data and derived data are not GPL. Do not label the data "GPL-2.0" or imply GPL governs it. Add a data-licence/NOTICE file if the workbook/JSON are committed or served. |
| Database rights | CC BY 4.0 §4 covers sui generis database rights, so extracting/reshaping substantial parts is licensed on the same attribution terms. |
| Endorsement | Must not suggest the Basque Government or Euskotren endorses this project (CC BY 4.0 deed: "not in any way that suggests the licensor endorses you or your use"). |

Note that we *do* materially change the data (merge T0+T1 under E2-T1, drop trams/funicular/FCC, regroup services into `WD/SA/SU/WE/FN/SN`, replace PDF provenance with GTFS). CC BY 4.0 requires indicating that changes were made, and the portal's "no alteración / no desnaturalización" wording is best satisfied by being explicit about the transformation rather than by pretending the output is verbatim.

## 6. Recommended attribution

Give, at minimum: **who**, **what/source URL**, **licence + link**, **last update / feed version**, **changes made**. Keep it in the machine-readable metadata as well as visibly.

Canonical English (for `README`, the HTML footer and a workbook "Source" sheet):

> Timetable data from **Eusko Trenbideak – Euskotren**, published by the Basque Government through **Open Data Euskadi / Moveuskadi**.
> Source: <https://opendata.euskadi.eus/transport/moveuskadi/euskotren/gtfs_euskotren.zip> (feed version `20261125043408`, last updated 2026-11-25).
> Licence: **CC BY 4.0** — <https://creativecommons.org/licenses/by/4.0/>.
> Changes made: the GTFS feed was reformatted and filtered into workbook and HTML timetable tables (lines E1, E2-T1, E4, E3-L3); trams, the funicular and non-Euskotren operators were omitted.
> This project is not endorsed by the Basque Government or Euskotren.

Basque and Spanish variants (matching the repo's `README-eu.md` / `README-es.md`):

> Ordutegi-datuak **Eusko Trenbideak – Euskotren** erakundearenak dira, eta Eusko Jaurlaritzak argitaratzen ditu **Open Data Euskadi / Moveuskadi** bidez. Iturria: <…gtfs_euskotren.zip> (`20261125043408` bertsioa, azken eguneratzea 2026-11-25). Lizentzia: **CC BY 4.0** — <https://creativecommons.org/licenses/by/4.0/>. Aldaketak: GTFS fitxategia berrantolatu eta iragazi egin da lan-koaderno eta HTML ordutegi tauletan.

> Datos de horarios de **Eusko Trenbideak – Euskotren**, publicados por el Gobierno Vasco a través de **Open Data Euskadi / Moveuskadi**. Fuente: <…gtfs_euskotren.zip> (versión `20261125043408`, última actualización 2026-11-25). Licencia: **CC BY 4.0** — <https://creativecommons.org/licenses/by/4.0/>. Cambios: el GTFS se ha reformateado y filtrado en tablas de horarios para cuaderno y HTML.

Where to carry it (implementation is out of scope here, but the spec should name the slots):

- **`services.json` `meta`**: extend the existing `source_manifest` entries with `licence`, `licence_url`, `publisher`, `feed_version`, `retrieved_at`, `last_update`. The current `_meta()` in `euskotren_timetable/site.py` emits only `label`, `url`, `sha256`.
- **HTML**: a visible footer/source line on every generated page (there is currently no source/credit line anywhere in `site.py`).
- **Workbook**: a "Source / Licence" sheet or a header/footer block. Keep the same text as the HTML so the two outputs cannot drift.
- **Repo**: a `NOTICE`/`DATA-LICENSE` file stating that the *data and derived data* are CC BY 4.0 and the *code* is GPL-2.0.

Also keep the feed's own credit intact: **Eusko Trenbideak**, `https://gardentasuna.euskotren.eus/eu` (from `attributions.txt`).

## 7. Uncertainty and missing evidence

Everything material is confirmed, but these are the loose ends:

1. **No dataset-specific prose licence page.** The only human-readable licence artefact is the badge image linking to the CC deed; there is no "this dataset is published under CC BY 4.0 because…" sentence for Moveuskadi.
2. **The "legal info" link next to the badge is the wrong notice.** `Lizentzia → Lege-informazioa` points at `https://www.euskadi.eus/informazioa/-/lege-informazioa/`, which is the *general euskadi.eus* notice and is effectively **all rights reserved** ("los derechos de propiedad intelectual … los tiene la Administración General de la Comunidad Autónoma de Euskadi"). The Open Data–specific notice is a different page (`…/orokorra/-/opendatako-lege-informazioa/`). Read literally, the two links disagree; the machine-readable `dct:license` and the badge resolve it in favour of CC BY 4.0.
3. **"No alteración" vs. CC BY 4.0.** The Open Data legal notice says the content must not be altered; CC BY 4.0 expressly permits adaptations. The report in §4 frames the "no alteración" bullets as the art. 8 baseline and CC BY as the IP-rights modality, so they are alternative regimes rather than cumulative — but the portal never says so explicitly. Mitigation: attribute, state changes, and keep the raw feed's `feed_version`/`sha256` so the exact input can be re-derived.
4. **The legal notice's cross-reference is dangling.** It says content is under "the Creative Commons licence shown on its home page" (`la licencia Creative Commons que aparece en su página principal`). As of 2026-11-25 there is **no CC mark anywhere on either home page** (`/hasiera/`, `/inicio/`). This is a portal maintenance defect, not a revocation.
5. **Publisher identity not fully resolved.** The DCAT `dct:publisher` is the opaque code `A16050214`; the portal's own publisher facets only say "Eusko Jaurlaritza > Garraioak > Mugikortasuna". Datos.gob.es's organism page for the code 404'd, so the exact department name behind `A16050214` is unconfirmed. This does not affect the licence, only how precisely we name the publisher in the credit.
6. **Not checked / out of reach**: the Basque Government's transparency portal (`gardentasuna.euskotren.eus`) terms; any email confirmation from the publisher; the `api.euskadi.eus/sparql` endpoint (returned HTTP 500); whether datos.gob.es has a national-catalogue record mirroring this dataset (its API returned no match by title/keyword/publisher).
7. **The legal report is dated 2010** (v2.0) and predates both CC BY 4.0 and Directive 2019/1024. It is corroborating intent, not the instrument.
8. **No warranty.** The legal notice and CC BY 4.0 both disclaim warranties; the site should not present derived data as official.

If a stronger guarantee is ever needed (e.g. before a commercial redistribution push), the one open action is to email the publisher via the contact route on the dataset page (`Eman iritzia` / "Comenta este conjunto de datos") and ask them to confirm CC BY 4.0 in writing and to fix the "Lege-informazioa" link.

## 8. URLs checked

Catalogue and metadata

- `https://s3.itbatera.euskadi.eus/02-pro-e3525cfb1b3d99109c5220a2b24bcb30-inet/transport/moveuskadi/data-index.json` (200; key `data.Euskotren`)
- `https://opendata.euskadi.eus/transport/moveuskadi/euskotren/gtfs_euskotren.zip` (301 → S3; 200, 1 418 184 bytes)
- `https://opendata.euskadi.eus/katalogoa/-/moveuskadi-euskadiko-garraio-publikoaren-sarearen-datuak-operadoreak-ordutegiak-geltokiak-egutegia-tarifak-etab/` (200; licence badge)
- `https://opendata.euskadi.eus/catalogo/-/moveuskadi-datos-de-la-red-de-transporte-publico-de-euskadi-operadores-horarios-paradas-calendario-tarifas-etc/` (200; `Reconocimiento CC BY`)
- `https://opendata.euskadi.eus/contenidos/ds_movilidad/md_ideeu_moveuskadi/eu_def/r01DCATDataset.rdf` (200; `dct:license` CC BY 4.0)
- `https://opendata.euskadi.eus/contenidos/ds_movilidad/md_ideeu_moveuskadi/es_def/r01DCATDataset.rdf` (200; same)
- `https://www.geo.euskadi.eus/cartografia/DatosDescarga/Transporte/Moveuskadi/Euskotren/` (200; directory listing, `google_transit.zip`, no licence file)
- `https://www.moveuskadi.euskadi.eus/` (200; no licence statement)
- `https://open-data-komunitatea/-/albistea/2025/moveuskadi-garraio-publikoari-buruzko-datuak-denbora-errealean/` (200; launch note, cites GTFS/GTFS-RT/SIRI/NeTEx for reuse)

Legal and policy

- `https://opendata.euskadi.eus/orokorra/-/opendatako-lege-informazioa/` (200; eu legal notice)
- `https://opendata.euskadi.eus/general/-/informacion-legal-opendata/` (200; es legal notice)
- `https://opendata.euskadi.eus/open-datari-buruz/-/open-data-araudia/` (200; regulation list)
- `https://opendata.euskadi.eus/nola-berrerabili/-/datu-irekiak-berrerabili/` (200; reuse guidance, links the legal report)
- `https://opendata.euskadi.eus/contenidos/informacion/reutilizar_datos/es_def/adjuntos/informe_juridico_opendata_v3.pdf` (200; legal report)
- `https://www.euskadi.eus/informazioa/-/lege-informazioa/` (200; general euskadi.eus all-rights-reserved notice)
- `https://www.euskadi.eus/informacion/-/informacion-legal/` (200; Spanish version)
- `https://creativecommons.org/licenses/by/4.0/` (200; deed)
- `https://creativecommons.org/licenses/by/4.0/legalcode.en` (200)
- `https://gtfs.org/documentation/schedule/reference/` (200; `attributions.txt` field list — no licence field)

Dead ends

- `https://api.euskadi.eus/sparql/` — HTTP 500 (NullPointerException) for a simple query.
- `https://datos.gob.es/apidata/catalog/dataset/title/moveuskadi` — 200, zero items; `description/`, `keyword/`, `publisher/A16050214` — zero items.
- `https://datos.gob.es/es/catalogo/organismos` — 404 via curl.
- `https://opendata.euskadi.eus/informacion/aviso-legal/`, `/informazioa/lege-oharra/`, `/informacion/condiciones-de-uso/` — 404 (guessed URLs; the real ones are above).

## 9. How to reproduce

```bash
# 1. licence from the DCAT record (expect creativecommons.org/licenses/by/4.0/)
curl -s https://opendata.euskadi.eus/contenidos/ds_movilidad/md_ideeu_moveuskadi/eu_def/r01DCATDataset.rdf \
  | grep -i 'dct:license'

# 2. licence badge on the dataset card (expect alt="Attribution CC BY")
curl -s 'https://opendata.euskadi.eus/katalogoa/-/moveuskadi-euskadiko-garraio-publikoaren-sarearen-datuak-operadoreak-ordutegiak-geltokiak-egutegia-tarifak-etab/' \
  | grep -o 'creativecommons.org/licenses/by/4.0/'

# 3. the feed carries no licence
curl -sLO https://opendata.euskadi.eus/transport/moveuskadi/euskotren/gtfs_euskotren.zip
unzip -l gtfs_euskotren.zip     # no LICENSE/COPYING
unzip -p gtfs_euskotren.zip feed_info.txt
unzip -p gtfs_euskotren.zip attributions.txt

# 4. last update of the GTFS distribution
curl -s https://s3.itbatera.euskadi.eus/02-pro-e3525cfb1b3d99109c5220a2b24bcb30-inet/transport/moveuskadi/data-index.json \
  | python3 -c 'import json,sys; [print(x) for x in json.load(sys.stdin)["data"]["Euskotren"] if x["format"]=="GTFS"]'
```
