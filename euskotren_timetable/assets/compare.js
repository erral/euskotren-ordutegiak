(function () {
  "use strict";

  const byId = (id) => document.getElementById(id);
  const lineSelect = byId("compare-line");
  const directionSelect = byId("compare-direction");
  const calendarSelect = byId("compare-calendar");
  const status = byId("compare-status");
  const summary = byId("compare-summary");
  const details = byId("compare-details");
  const pdfTable = byId("compare-pdf-table");
  const gtfsTable = byId("compare-gtfs-table");

  if (
    !lineSelect ||
    !directionSelect ||
    !calendarSelect ||
    !status ||
    !summary ||
    !details ||
    !pdfTable ||
    !gtfsTable
  ) {
    return;
  }

  let pdfData;
  let gtfsData;

  function minutes(value) {
    const match = /^(\d{1,2}):(\d{2})$/.exec(String(value || "").trim());
    if (!match) {
      return null;
    }
    return Number(match[1]) * 60 + Number(match[2]);
  }

  function loadJson(url) {
    return fetch(url, { cache: "no-cache" }).then((response) => {
      if (!response.ok) {
        throw new Error(`${url} (HTTP ${response.status})`);
      }
      return response.json();
    });
  }

  function setStatus(text) {
    status.textContent = text;
  }

  function setOptions(select, values, selected) {
    select.replaceChildren();
    for (const value of values) {
      const option = document.createElement("option");
      option.value = value.value;
      option.textContent = value.label;
      if (value.value === selected) {
        option.selected = true;
      }
      select.append(option);
    }
  }

  function corridorFor(line, direction) {
    return pdfData.corridors.find(
      (corridor) => corridor.line === line && corridor.direction === direction
    );
  }

  function servicesFor(data, sheet, calendar) {
    return data.services
      .filter(
        (service) =>
          service.calendar === calendar && service.appears_in.includes(sheet)
      )
      .sort(
        (a, b) =>
          (minutes(a.departure) || 0) - (minutes(b.departure) || 0) ||
          a.service_id.localeCompare(b.service_id)
      );
  }

  function timeAt(service, stop) {
    const row = service.stop_times.find((item) => item.stop_name === stop);
    if (!row || !row.time) {
      return "";
    }
    return row.time;
  }

  function addCell(row, text, className, header) {
    const cell = document.createElement(header ? "th" : "td");
    if (header) {
      cell.scope = "col";
    }
    if (className) {
      cell.className = className;
    }
    cell.textContent = text;
    row.append(cell);
  }

  function serviceHref(prefix, line, corridor, calendar, serviceId) {
    const lineData = pdfData.lines.find((item) => item.code === line);
    const calendarData = pdfData.calendars.find((item) => item.id === calendar);
    if (!lineData || !calendarData || !corridor) {
      return null;
    }
    return `${prefix}line/${lineData.slug}/${corridor.slug}/${calendarData.slug}.html#${serviceId}`;
  }

  function renderTable(table, services, line, corridor, calendar, prefix) {
    table.replaceChildren();
    const head = document.createElement("thead");
    const headRow = document.createElement("tr");
    for (const title of ["Service ID", "Dep.", "Arr.", "Destination"]) {
      addCell(headRow, title, null, true);
    }
    for (const stop of corridor.stops) {
      addCell(headRow, stop, null, true);
    }
    head.append(headRow);
    table.append(head);

    const body = document.createElement("tbody");
    for (const service of services) {
      const row = document.createElement("tr");
      const idCell = document.createElement("th");
      idCell.scope = "row";
      idCell.className = "service-id";
      const href = serviceHref(prefix, line, corridor, calendar, service.service_id);
      if (href) {
        const link = document.createElement("a");
        link.href = href;
        link.textContent = service.service_id;
        idCell.append(link);
      } else {
        idCell.textContent = service.service_id;
      }
      row.append(idCell);
      addCell(row, service.departure || "", "time");
      addCell(row, service.arrival || "", "time");
      addCell(row, service.destination || "");
      for (const stop of corridor.stops) {
        const value = timeAt(service, stop);
        addCell(row, value, value === "?" ? "unpublished" : value ? "time" : "empty");
      }
      body.append(row);
    }
    table.append(body);
  }

  function signature(services, stops) {
    return services
      .map((service) => stops.map((stop) => timeAt(service, stop)).join("|"))
      .sort()
      .join(";");
  }

  function departureMap(services) {
    const map = new Map();
    for (const service of services) {
      const key = service.departure || "";
      if (!map.has(key)) {
        map.set(key, []);
      }
      map.get(key).push(service);
    }
    return map;
  }

  function serviceIds(services) {
    return services.map((service) => service.service_id).join(", ");
  }

  function addDetail(text, className) {
    const item = document.createElement("li");
    item.textContent = text;
    if (className) {
      item.className = className;
    }
    details.querySelector("ul").append(item);
  }

  function render() {
    const line = lineSelect.value;
    const direction = directionSelect.value;
    const calendar = calendarSelect.value;
    const corridor = corridorFor(line, direction);
    if (!corridor) {
      setStatus("—");
      return;
    }

    const pdfServices = servicesFor(pdfData, corridor.sheet, calendar);
    const gtfsServices = servicesFor(gtfsData, corridor.sheet, calendar);
    renderTable(pdfTable, pdfServices, line, corridor, calendar, "");
    renderTable(gtfsTable, gtfsServices, line, corridor, calendar, "gtfs/");

    const pdfByDeparture = departureMap(pdfServices);
    const gtfsByDeparture = departureMap(gtfsServices);
    const allDepartures = new Set([...pdfByDeparture.keys(), ...gtfsByDeparture.keys()]);
    const onlyPdf = [];
    const onlyGtfs = [];
    const changed = [];
    let common = 0;

    for (const departure of [...allDepartures].sort(
      (a, b) => (minutes(a) || 0) - (minutes(b) || 0) || a.localeCompare(b)
    )) {
      const pdfGroup = pdfByDeparture.get(departure) || [];
      const gtfsGroup = gtfsByDeparture.get(departure) || [];
      if (pdfGroup.length && !gtfsGroup.length) {
        onlyPdf.push([departure, pdfGroup]);
      } else if (!pdfGroup.length && gtfsGroup.length) {
        onlyGtfs.push([departure, gtfsGroup]);
      } else {
        common += 1;
        if (signature(pdfGroup, corridor.stops) !== signature(gtfsGroup, corridor.stops)) {
          changed.push([departure, pdfGroup, gtfsGroup]);
        }
      }
    }

    setStatus(
      `PDF: ${pdfServices.length} · GTFS: ${gtfsServices.length} · ` +
        `irtendako orduak / salidas: ${allDepartures.size}`
    );

    summary.replaceChildren();
    const counts = document.createElement("p");
    counts.textContent =
      `PDF: ${pdfServices.length} zerbitzu / servicios · ` +
      `GTFS: ${gtfsServices.length} zerbitzu / servicios · ` +
      `irteera komunak / salidas comunes: ${common} · ` +
      `PDF soilik / solo PDF: ${onlyPdf.length} · ` +
      `GTFS soilik / solo GTFS: ${onlyGtfs.length} · ` +
      `aldatuak / cambiados: ${changed.length}`;
    summary.append(counts);

    details.replaceChildren();
    const list = document.createElement("ul");
    details.append(list);
    const limit = 80;
    let shown = 0;
    for (const [departure, group] of onlyPdf) {
      if (shown >= limit) break;
      addDetail(`${departure} — PDF: ${serviceIds(group)}`, "diff-pdf-only");
      shown += 1;
    }
    for (const [departure, group] of onlyGtfs) {
      if (shown >= limit) break;
      addDetail(`${departure} — GTFS: ${serviceIds(group)}`, "diff-gtfs-only");
      shown += 1;
    }
    for (const [departure, pdfGroup, gtfsGroup] of changed) {
      if (shown >= limit) break;
      addDetail(
        `${departure} — PDF: ${serviceIds(pdfGroup)} ↔ GTFS: ${serviceIds(gtfsGroup)}`,
        "diff-changed"
      );
      shown += 1;
    }
    if (onlyPdf.length + onlyGtfs.length + changed.length > limit) {
      addDetail("…", "diff-muted");
    }
    if (shown === 0) {
      addDetail("Ez dago alderik hautatutako egutegian / No hay diferencias en el calendario seleccionado.", "diff-muted");
    }
  }

  function updateDirections() {
    const line = lineSelect.value;
    const directions = [];
    const seen = new Set();
    for (const corridor of pdfData.corridors) {
      if (corridor.line !== line || seen.has(corridor.direction)) {
        continue;
      }
      seen.add(corridor.direction);
      directions.push({ value: corridor.direction, label: corridor.direction });
    }
    const previous = directionSelect.value;
    setOptions(
      directionSelect,
      directions,
      directions.some((item) => item.value === previous) ? previous : directions[0]?.value
    );
    updateCalendars();
  }

  function servicesForCorridor(data, sheet) {
    return data.services.filter((service) => service.appears_in.includes(sheet));
  }

  function updateCalendars() {
    const corridor = corridorFor(lineSelect.value, directionSelect.value);
    if (!corridor) {
      return;
    }
    const available = new Set();
    for (const service of servicesForCorridor(pdfData, corridor.sheet)) {
      available.add(service.calendar);
    }
    for (const service of servicesForCorridor(gtfsData, corridor.sheet)) {
      available.add(service.calendar);
    }
    const calendars = pdfData.calendars
      .filter((calendar) => available.has(calendar.id))
      .sort((a, b) => a.order - b.order)
      .map((calendar) => ({
        value: calendar.id,
        label: `${calendar.label_eu} / ${calendar.label_es}`,
      }));
    const fallback = calendars.find((item) => item.value === "WD") || calendars[0];
    const previous = calendarSelect.value;
    setOptions(
      calendarSelect,
      calendars,
      calendars.some((item) => item.value === previous) ? previous : fallback?.value
    );
    render();
  }

  function init() {
    const lines = pdfData.lines.map((line) => ({ value: line.code, label: line.name }));
    setOptions(lineSelect, lines, lines[0]?.value);
    lineSelect.addEventListener("change", updateDirections);
    directionSelect.addEventListener("change", updateCalendars);
    calendarSelect.addEventListener("change", render);
    updateDirections();
  }

  Promise.all([loadJson("data/services.json"), loadJson("gtfs/data/services.json")])
    .then(([pdf, gtfs]) => {
      pdfData = pdf;
      gtfsData = gtfs;
      init();
    })
    .catch((error) => {
      summary.replaceChildren();
      const note = document.createElement("p");
      note.className = "compare-error";
      note.textContent =
        "Ezin izan dira bi datu-multzoak kargatu. Ziurtatu /gtfs eraiki dela. " +
        "No se pudieron cargar los dos conjuntos de datos; asegúrate de que /gtfs se ha generado. ";
      const detail = document.createElement("code");
      detail.textContent = String(error.message || error);
      note.append(detail);
      summary.append(note);
    });
})();
