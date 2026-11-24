# Euskotren ordutegiak

**Euskara** · [English](README.md) · [Español](README-es.md)

**HTML gunea:** [erral.github.io/euskotren-ordutegiak](https://erral.github.io/euskotren-ordutegiak/)

Euskotrenen 2026ko neguko ordutegi normalizatu bakarra, jatorrizko PDFetatik sortua eta honela argitaratua:

- **Excel lan-koaderno** kanonikoa;
- **HTML gune** estatiko eta bilaketaduna.

Euskara da hizkuntza nagusia; interfazeko etiketak euskaraz eta gaztelaniaz daude. Geltokien izenak euskarazkoak dira soilik; gaztelaniazko aliasak nahita baztertu dira.

Lan-koadernoa da erreferentzia nagusia. HTML gunea `Service` datu normalizatu berberetatik eta ordenamendu-kontratu beretik sortutako ikuspegi gehigarria da.

## Ezaugarriak

### Ordutegi-datuak

- **2.227 zerbitzu** **E1, E2-T1, E4 eta E3-L3** lineetan, bi noranzkoetan.
- **Egutegiak:** astegunak, larunbatak, igandeak/jaiegunak, asteburu osoa, ostiral gaua eta larunbat gaua.
- Lineaz haraindiko ibilbideak: zerbitzua igarotzen duen korridore guztietan agertzen da; adibidez, E1eko zerbitzuak E2-T1eko Donostia inguruko tarte partekatuan.
- Zerbitzu partzial eta bereziak: E1 Pasaia–Zumaia, Zaldibar–Matiko/Traña, Elgoibar–Matiko eta Eibar–Ermua; E2ko Añorgako anezkak; E4ko Gernika aldaerak eta ibilbide laburrak; Amorebieta Geltokia transbordo-zutabea; eta gaueko blokeak.
- Excelek eta HTMLak partekatutako ordenamendu kanonikoa: **egutegia → irteera → linea → noranzkoa → zerbitzu IDa**. Korridore-orrietan, korridorearen linea propioa lehenesten da irteera bereko zerbitzuen artean.
- **212 egitura-egiaztapen** eta **163 unitate-proba**.

### Excel lan-koadernoa

`output/euskotren_timetables_winter_2026_v12.xlsx` fitxategiak 17 orri ditu:

- `README`, `Stops`, `Calendars`, `Manifest`, `Coverage` eta `Source notes`;
- `Master`, zerbitzu bakoitzeko errenkada kanoniko batekin;
- zortzi korridore-orri, zerbitzuak errenkadetan eta geltokiak zutabeetan;
- `Frequency rules`, iturburuko maiztasun-arau trinkoekin eta zabaldutako zerbitzuekin;
- `Validation`, exekuzioaren egitura-egiaztapenekin.

Egutegi-blokeak pilatuta daude korridore-orri bakoitzean. `Coverage` orriak linea/egutegi eredu bakoitza `Included` edo `Pending` gisa markatzen du. `Source notes` orriak kartelen euskarazko/gaztelaniazko ohar berberak jasotzen ditu.

### HTML gunea

`make html` komandoak `output/html/` sortzen du:

- hasierako orri bat linea, noranzko eta egutegi estekekin, baliozkotasunarekin eta deskargekin;
- linea/noranzko/egutegi konbinazio ez-huts bakoitzeko orri bat;
- egutegi-hautatzailea, goiburu itsaskorra eta horizontalean korritzea; lehen zutabea ez da finkatzen;
- Nondik / Nora geltoki-iragazkia, bi geltokietatik bidaiaren ordenan igarotzen diren zerbitzuak soilik erakusten dituena, eta tarteko geltokien zutabeak tolestuta uzten dituena, zabaltzeko botoi baten atzean, eta alderantzizko noranzkoaren esteka aurrez iragazia, geltokiak ordena inversoan hautatzen direnean;
- geltoki-zutabeak ordenatzeko aukera, gorantz/behera adierazle ikusgaiarekin; taula lehen geltokiaren arabera ordenatzen da modu lehenetsian (edo hautatutako Nondik geltokiaren arabera), ikusgai dauden orduak ordenan egon daitezen;
- metadatuen etengailua: Service ID, linea, eredua, jatorria, helmuga, irteera eta iritsiera;
- Master orria testu-bilaketarekin eta linea, egutegi, jatorri, helmuga eta irteera iragazkiekin;
- `data/services.json` (1. schema bertsioa) eta lan-koadernoaren deskarga;
- inprimatzeko estiloak, edukira salto egiteko esteka, teklatu bidezko korritze-eremuak eta `aria-live` emaitza-kontagailuak;
- esteka erlatiboak, proiektu baten Pages URLtik funtziona dezan;
- argitaratutako artefaktuan iturburuko PDFrik ez.

### Automatizazioa

- GitHub Actions-ek Ruff, proba-multzo osoa, lan-koadernoaren/gunearen eraikuntza eta gunearen baliozkotze-atea exekutatzen ditu.
- `deploy` lanak `main` adarretik soilik argitaratzen du `output/html` GitHub Pages-en.

## Abiarazte azkarra

Baldintzak: **Python 3.12+** eta **Poppler** (`pdftotext`).

```bash
python3 -m pip install -e ".[dev]"
python3 -m euskotren_timetable.cli all
```

`all` komandoak jatorrizko PDFak deskargatzen ditu, eta lan-koadernoa eta HTML gunea eraikitzen ditu.

Edo Make erabiliz:

```bash
make workbook   # Excel lan-koadernoa soilik
make html       # lan-koadernoa + gune estatikoa output/html karpetan
```

`make workbook` eta `make html` komandoek `data/pdfs/` karpetan jatorrizko PDFak daudela espero dute. Kopia berri batean, exekutatu manifest komandoa lehenago.

### Komando indibidualak

```bash
python3 -m euskotren_timetable.cli manifest
python3 -m euskotren_timetable.cli build-weekday
python3 -m euskotren_timetable.cli build-html
python3 -m euskotren_timetable.cli validate-site --output output/html
```

### Irteerak

- `output/euskotren_timetables_winter_2026_v12.xlsx`
- `output/html/` — ordutegi-gune estatikoa
- `output/validation.md`
- `data/manifest.json`
- `data/pdfs/*.pdf`

## GitHub Pages-en argitaratzea

Biltegiaren izena **`euskotren-ordutegiak`** da, eta gunea helbide honetan dago:

`https://erral.github.io/euskotren-ordutegiak/`

Pages konfiguratu behar bada:

1. Igo `main` adarra.
2. Ireki **Settings → Pages**.
3. Ezarri **Source** aukera **GitHub Actions** gisa.

Lan-fluxuak probak exekutatzen ditu, gunea eraiki eta baliozkotzen du, eta `output/html` argitaratzen du. Baliozkotzeak huts egiten badu, argitaratzea blokeatuta geratzen da.

## Probak, linting eta baliozkotzea

```bash
make test
make lint
python3 -m euskotren_timetable.cli validate-site --output output/html
```

Gunearen baliozkotzeak esteka eta aingura internak, ID bikoiztuak, JSON karga eta `output/html` karpetan PDFrik ez dagoela egiaztatzen ditu. Proba-multzoak ordutegi-parserak, ordenamendua, lan-koadernoaren kontratuak eta sortutako gunea hartzen ditu.

## Egitura

| Bidea | Helburua |
|---|---|
| `euskotren_timetable/cli.py` | CLI, eraikuntza-orkestrazioa eta manifest lan-fluxua |
| `euskotren_timetable/parse_*.py` | Koordenatuetan oinarritutako PDF taulen parserak |
| `euskotren_timetable/corridors.py` | Zortzi korridore-definizio eta lineaz haraindiko kidetza |
| `euskotren_timetable/model.py` | `Service` / `StopTime` erregistro normalizatuak |
| `euskotren_timetable/service_order.py` | Partekatutako ordenamendu kanonikoaren kontratua |
| `euskotren_timetable/validate.py` | 212 egitura-egiaztapen |
| `euskotren_timetable/workbook.py` | Excel errendatzailea |
| `euskotren_timetable/site.py` | HTML gune estatikoaren sortzailea eta esteken baliozkotzailea |
| `euskotren_timetable/templates/` | Gunearen Jinja2 txantiloiak |
| `euskotren_timetable/assets/` | Gunearen estilo-orria eta Master/korridore-taula scriptak |
| `euskotren_timetable/manifest.py`, `pdf.py` | PDF deskarga, jatorria eta erauzketa |
| `euskotren_timetable/stops.py`, `source_notes.py` | Geltoki kanonikoak eta kartelen oharrak |
| `data/manifest.json`, `data/corrections.yaml` | Iturburuko URLak eta alboko zuzenketak |
| `tests/` | Unitate-probak eta sortutako gunearen probak |

## Legenda

- Zelula hutsa = ez da gelditzen.
- `?` = ordua ez dago iturrian argitaratuta; HTML gunean gorriz agertzen da.
- `>` = trena gelditu gabe pasatzen da.
- Orduak 24 orduko formatuan daude. Gauerdi osteko orduak `24:xx`/`25:xx` gisa erabiltzen dira; igandeko 00:30eko trena larunbat gauari dagokio.
- `FN` = ostiral gaua eta jaiegun bezperak; `SN` = larunbat gaua.

## Iturria

Ordutegi-datuak Euskotrenen 2026ko neguko jatorrizko PDFetatik eratorriak dira. Iturburu-manifestak URL bakoitza eta SHA-256 hash-a erregistratzen ditu.

## Lege-oharra

Proiektu hau ez da ofiziala eta ez dago Euskotrenekin lotuta. Bidaiatu aurretik, egiaztatu beti Euskotrenen ordutegi ofiziala.

Proiektua [OpenCode](https://opencode.ai) erabiliz eraiki da, [Matt Pococken skillak](https://github.com/mattpocock/skills) eta [DeepSeek Flash 4-flash](https://www.deepseek.com/) baliatuta.

## Lizentzia

GPL-2.0. Ikusi [LICENSE](LICENSE).
