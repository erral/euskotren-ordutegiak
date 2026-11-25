# Euskotren ordutegiak

**Español** · [English](README.md) · [Euskara](README-eu.md)

**Sitio HTML:** [erral.github.io/euskotren-ordutegiak](https://erral.github.io/euskotren-ordutegiak/)

Un horario único de Euskotren para el invierno de 2026, generado a partir de los PDF oficiales y publicado como:

- un **libro de Excel** canónico;
- un **sitio HTML** estático y con búsqueda.

El euskera es el idioma principal; las etiquetas de la interfaz son bilingües euskera/español. Los nombres de las paradas son solo en euskera; los alias en español se omiten intencionadamente.

El libro de Excel es la fuente de verdad. El sitio HTML es una vista adicional construida a partir de los mismos datos `Service` y el mismo contrato de ordenación.

## Funciones

### Datos del horario

- **2.225 servicios** en **E1, E2-T1, E4 y E3-L3**, en ambos sentidos.
- **Calendarios:** laborables, sábados, domingos/festivos, fin de semana combinado, noche del viernes y noche del sábado.
- Circulación pasante y pertenencia entre líneas: un servicio aparece en todos los corredores por los que pasa, como los servicios E1 en el tramo compartido de Donostia de E2-T1.
- Servicios parciales y especiales: E1 Pasaia–Zumaia, Zaldibar–Matiko/Traña, Elgoibar–Matiko y Eibar–Ermua; lanzaderas de Añorga de la E2; variantes y cortos de Gernika de la E4; la columna de transbordo de Amorebieta Geltokia; y los bloques nocturnos.
- Ordenación canónica compartida por Excel y HTML: **calendario → salida → línea → sentido → ID de servicio**. En las páginas de corredor, la línea propia del corredor va primero cuando hay servicios con la misma salida.
- **215 comprobaciones estructurales** y **166 pruebas unitarias**.

### Libro de Excel

`output/euskotren_timetables_winter_2026_v12.xlsx` contiene 17 hojas:

- `README`, `Stops`, `Calendars`, `Manifest`, `Coverage` y `Source notes`;
- `Master` con una fila canónica por servicio;
- ocho hojas de corredor con servicios en filas y paradas en columnas;
- `Frequency rules` con reglas de frecuencia comprimidas y servicios expandidos;
- `Validation` con las comprobaciones estructurales de la ejecución.

Los bloques de calendario se apilan en cada hoja de corredor. La hoja `Coverage` marca cada patrón línea/calendario como `Included` o `Pending`. `Source notes` conserva las notas textuales en euskera/español de los carteles.

### Sitio HTML

`make html` escribe `output/html/` con:

- un índice con enlaces de línea, sentido y calendario, vigencia y descargas;
- una página por cada combinación no vacía de línea/sentido/calendario;
- un selector de calendario, cabecera fija y desplazamiento horizontal; la primera columna se desplaza con la tabla;
- un filtro de paradas Desde / Hasta que muestra solo los servicios que pasan por ambas paradas en orden de viaje, con las columnas de paradas intermedias plegadas tras un botón para expandirlas y un enlace pre-filtrado al sentido inverso cuando las paradas se seleccionan en orden inverso;
- columnas de parada ordenables con un indicador visible de orden ascendente/descendente; la tabla se ordena por defecto por la primera parada (o por la parada Desde seleccionada) para que los horarios visibles queden en orden;
- un conmutador de metadatos para ID de servicio, línea, patrón, origen, destino, salida y llegada;
- una página Master con búsqueda de texto y filtros de línea, calendario, origen, destino y salida;
- `data/services.json` (versión de esquema 1) y la descarga del libro;
- estilos de impresión, enlace para saltar al contenido, regiones de desplazamiento accesibles por teclado y contadores de resultados con `aria-live`;
- enlaces relativos, para que el sitio funcione desde una URL de Pages de proyecto;
- ningún PDF de origen en el artefacto publicado.

### Automatización

- GitHub Actions ejecuta Ruff, la suite completa de pruebas, la compilación del libro/sitio y la puerta de validación del sitio.
- El trabajo `deploy` publica `output/html` en GitHub Pages solo desde `main`.

## Inicio rápido

Requisitos: **Python 3.12+** y **Poppler** (`pdftotext`).

```bash
python3 -m pip install -e ".[dev]"
python3 -m euskotren_timetable.cli all
```

`all` descarga los PDF oficiales, compila el libro y el sitio HTML.

O con Make:

```bash
make workbook   # solo el libro de Excel
make html       # libro + sitio estático en output/html
```

`make workbook` y `make html` esperan los PDF de origen en `data/pdfs/`. En una copia nueva, ejecuta primero el comando manifest.

### Comandos individuales

```bash
python3 -m euskotren_timetable.cli manifest
python3 -m euskotren_timetable.cli build-weekday
python3 -m euskotren_timetable.cli build-html
python3 -m euskotren_timetable.cli validate-site --output output/html
```

### Salidas

- `output/euskotren_timetables_winter_2026_v12.xlsx`
- `output/html/` — el sitio estático del horario
- `output/validation.md`
- `data/manifest.json`
- `data/pdfs/*.pdf`

## Publicación en GitHub Pages

El repositorio es **`euskotren-ordutegiak`**, y el sitio se sirve en:

`https://erral.github.io/euskotren-ordutegiak/`

Si hay que configurar Pages:

1. Sube la rama `main`.
2. Abre **Settings → Pages**.
3. Configura **Source** como **GitHub Actions**.

El flujo de trabajo ejecuta las pruebas, compila y valida el sitio, y publica `output/html`. Si falla la validación, la publicación se bloquea.

## Pruebas, linting y validación

```bash
make test
make lint
python3 -m euskotren_timetable.cli validate-site --output output/html
```

La validación del sitio comprueba enlaces y anclas internas, IDs duplicados, la carga JSON y la ausencia de PDF en `output/html`. La suite cubre los parsers del horario, la ordenación, los contratos del libro y el sitio generado.

## Estructura

| Ruta | Propósito |
|---|---|
| `euskotren_timetable/cli.py` | CLI, orquestación de compilación y flujo del manifest |
| `euskotren_timetable/parse_*.py` | Parsers de tablas PDF basados en coordenadas |
| `euskotren_timetable/corridors.py` | Ocho definiciones de corredor y pertenencia entre líneas |
| `euskotren_timetable/model.py` | Registros normalizados `Service` / `StopTime` |
| `euskotren_timetable/service_order.py` | Contrato de ordenación canónica compartido |
| `euskotren_timetable/validate.py` | 215 comprobaciones estructurales |
| `euskotren_timetable/workbook.py` | Renderizador de Excel |
| `euskotren_timetable/site.py` | Generador del sitio HTML estático y validador de enlaces |
| `euskotren_timetable/templates/` | Plantillas Jinja2 del sitio |
| `euskotren_timetable/assets/` | Hoja de estilos y scripts de Master/tabla de corredor |
| `euskotren_timetable/manifest.py`, `pdf.py` | Descarga, procedencia y extracción de PDF |
| `euskotren_timetable/stops.py`, `source_notes.py` | Paradas canónicas y notas de carteles |
| `data/manifest.json`, `data/corrections.yaml` | URL de origen y correcciones auxiliares |
| `tests/` | Pruebas unitarias y del sitio generado |

## Leyenda

- Celda vacía = no para.
- `?` = hora no publicada en la fuente; se muestra en rojo en el sitio HTML.
- `>` = el tren pasa sin parar.
- Las horas están en formato de 24 horas. Las horas posteriores a medianoche usan `24:xx`/`25:xx`; un tren de las 00:30 del domingo pertenece a la noche del sábado.
- `FN` = noche del viernes y vísperas de festivo; `SN` = noche del sábado.

## Fuente

Los datos del horario proceden de los PDF oficiales de Euskotren del invierno de 2026. El manifest de origen registra cada URL y su hash SHA-256.

## Aviso legal

Este es un proyecto no oficial y no está afiliado a Euskotren. Consulta siempre el horario oficial de Euskotren antes de viajar.

El proyecto se construyó con [OpenCode](https://opencode.ai) usando las [skills de Matt Pocock](https://github.com/mattpocock/skills) y [DeepSeek Flash 4-flash](https://www.deepseek.com/).

## Licencia

GPL-2.0. Consulta [LICENSE](LICENSE).
