(function () {
  "use strict";

  document.documentElement.classList.add("js");

  const byId = (id) => document.getElementById(id);
  const corridorSelect = byId("compare-corridor");
  const calendarSelect = byId("compare-calendar");
  const fromSelect = byId("compare-from");
  const toSelect = byId("compare-to");
  const toggle = byId("compare-toggle");
  const clear = byId("compare-clear");
  const count = byId("compare-count");
  const empty = byId("compare-empty");
  const reverse = byId("compare-reverse");
  const reverseLink = byId("compare-reverse-link");
  const pdfTable = byId("compare-pdf-table");
  const gtfsTable = byId("compare-gtfs-table");
  const summary = byId("compare-summary");
  const details = byId("compare-details");

  if (
    !corridorSelect ||
    !calendarSelect ||
    !fromSelect ||
    !toSelect ||
    !toggle ||
    !clear ||
    !count ||
    !empty ||
    !reverse ||
    !reverseLink ||
    !pdfTable ||
    !gtfsTable ||
    !summary ||
    !details
  ) {
    return;
  }

  let pdfData;
  let gtfsData;
  let corridor;
  let stopNames = [];
  let pdfEntries = [];
  let gtfsEntries = [];
  let pdfBody;
  let gtfsBody;
  let expanded = false;
  let sortStop = null;
  let sortDirection = "asc";
  let reverseCorridor = null;

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

  function corridorValue(value) {
    return `${value.line}|${value.direction}`;
  }

  function selectedCorridor() {
    const [line, direction] = corridorSelect.value.split("|");
    return pdfData.corridors.find(
      (item) => item.line === line && item.direction === direction
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

  function availableCalendars(sheet) {
    const ids = new Set();
    for (const service of pdfData.services) {
      if (service.appears_in.includes(sheet)) {
        ids.add(service.calendar);
      }
    }
    for (const service of gtfsData.services) {
      if (service.appears_in.includes(sheet)) {
        ids.add(service.calendar);
      }
    }
    return pdfData.calendars
      .filter((calendar) => ids.has(calendar.id))
      .sort((a, b) => a.order - b.order);
  }

  function populateCorridors() {
    corridorSelect.replaceChildren();
    const groups = new Map();
    for (const item of pdfData.corridors) {
      if (!groups.has(item.line)) {
        groups.set(item.line, []);
      }
      groups.get(item.line).push(item);
    }
    for (const [line, items] of groups) {
      const group = document.createElement("optgroup");
      group.label = line;
      for (const item of items) {
        const option = document.createElement("option");
        option.value = corridorValue(item);
        option.textContent = item.direction;
        group.append(option);
      }
      corridorSelect.append(group);
    }
    const first = pdfData.corridors[0];
    if (first) {
      corridorSelect.value = corridorValue(first);
    }
  }

  function fillStopSelects() {
    const values = [{ value: "", label: "—" }].concat(
      stopNames.map((stop) => ({ value: stop, label: stop }))
    );
    const previousFrom = stopNames.includes(fromSelect.value) ? fromSelect.value : "";
    const previousTo = stopNames.includes(toSelect.value) ? toSelect.value : "";
    setOptions(fromSelect, values, previousFrom);
    setOptions(toSelect, values, previousTo);
    syncOptions();
  }

  function syncOptions() {
    for (const [select, other] of [
      [fromSelect, toSelect],
      [toSelect, fromSelect],
    ]) {
      const taken = other.value;
      for (const option of select.options) {
        option.disabled = option.value !== "" && option.value === taken;
      }
      if (select.value !== "" && select.value === taken) {
        select.value = "";
      }
    }
  }

  function defaultSortStop() {
    if (fromSelect.value) {
      return fromSelect.value;
    }
    if (toSelect.value) {
      return toSelect.value;
    }
    return stopNames[0];
  }

  function cellInfo(service, stop) {
    const row = service.stop_times.find((item) => item.stop_name === stop);
    if (!row || row.disposition === "not_served") {
      return { text: "", cls: "empty" };
    }
    if (row.disposition === "unpublished") {
      return { text: "?", cls: "unpublished" };
    }
    if (row.disposition === "pass") {
      return { text: ">", cls: "pass" };
    }
    return { text: row.time || "", cls: row.time ? "time" : "empty" };
  }

  function buildEntries(services) {
    return services.map((service) => {
      const cells = new Map();
      const callIndex = new Map();
      for (const stop of stopNames) {
        cells.set(stop, cellInfo(service, stop));
      }
      service.stop_times.forEach((row, index) => {
        if (
          row.disposition !== "not_served" &&
          row.disposition !== "pass" &&
          row.time
        ) {
          callIndex.set(row.stop_name, index);
        }
      });
      return { service, cells, callIndex, row: null };
    });
  }

  function serviceHref(prefix, serviceId) {
    const lineData = pdfData.lines.find((item) => item.code === corridor.line);
    const calendarData = pdfData.calendars.find(
      (item) => item.id === calendarSelect.value
    );
    if (!lineData || !calendarData) {
      return null;
    }
    return `${prefix}line/${lineData.slug}/${corridor.slug}/${calendarData.slug}.html#${serviceId}`;
  }

  function addHeader(row, text, className) {
    const header = document.createElement("th");
    header.scope = "col";
    if (className) {
      header.className = className;
    }
    header.textContent = text;
    row.append(header);
    return header;
  }

  function addSortHeader(row, stop) {
    const header = document.createElement("th");
    header.scope = "col";
    header.className = "sortable";
    header.dataset.stop = stop;
    header.setAttribute("aria-sort", "none");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "sort-button";
    button.append(document.createTextNode(stop));
    const arrow = document.createElement("span");
    arrow.className = "sort-arrow";
    arrow.setAttribute("aria-hidden", "true");
    button.append(arrow);
    button.addEventListener("click", () => {
      if (sortStop === stop) {
        sortDirection = sortDirection === "asc" ? "desc" : "asc";
      } else {
        sortStop = stop;
        sortDirection = "asc";
      }
      applyState();
    });
    header.append(button);
    row.append(header);
  }

  function addMetadataCell(row, text, className, header) {
    const cell = document.createElement(header ? "th" : "td");
    if (header) {
      cell.scope = "row";
    }
    cell.className = className ? `metadata-col ${className}` : "metadata-col";
    cell.textContent = text;
    row.append(cell);
  }

  function buildTable(table, entries, prefix) {
    table.replaceChildren();
    const head = document.createElement("thead");
    const headerRow = document.createElement("tr");
    addHeader(headerRow, "Service ID", "metadata-col");
    for (const title of ["Line", "Pattern", "Origin", "Destination", "Departure", "Arrival"]) {
      addHeader(headerRow, title, title === "Departure" || title === "Arrival" ? "metadata-col time" : "metadata-col");
    }
    for (const stop of stopNames) {
      addSortHeader(headerRow, stop);
    }
    head.append(headerRow);
    table.append(head);

    const body = document.createElement("tbody");
    for (const entry of entries) {
      const row = document.createElement("tr");
      const serviceId = document.createElement("th");
      serviceId.scope = "row";
      serviceId.className = "metadata-col service-id";
      const href = serviceHref(prefix, entry.service.service_id);
      if (href) {
        const link = document.createElement("a");
        link.href = href;
        link.textContent = entry.service.service_id;
        serviceId.append(link);
      } else {
        serviceId.textContent = entry.service.service_id;
      }
      row.append(serviceId);
      addMetadataCell(row, entry.service.primary_line);
      addMetadataCell(row, (entry.service.pattern || []).join("; "));
      addMetadataCell(row, entry.service.origin);
      addMetadataCell(row, entry.service.destination);
      addMetadataCell(row, entry.service.departure, "time");
      addMetadataCell(row, entry.service.arrival, "time");
      for (const stop of stopNames) {
        const info = entry.cells.get(stop);
        const cell = document.createElement("td");
        cell.dataset.stop = stop;
        cell.className = info.cls;
        cell.textContent = info.text;
        row.append(cell);
      }
      entry.row = row;
      body.append(row);
    }
    table.append(body);
    return body;
  }

  function columnState() {
    const from = fromSelect.value;
    const to = toSelect.value;
    if (!from || !to) {
      return null;
    }
    const fromIndex = stopNames.indexOf(from);
    const toIndex = stopNames.indexOf(to);
    if (fromIndex === -1 || toIndex === -1) {
      return null;
    }
    return {
      fromIndex,
      toIndex,
      start: Math.min(fromIndex, toIndex),
      end: Math.max(fromIndex, toIndex),
    };
  }

  function applyColumns(state) {
    for (const table of [pdfTable, gtfsTable]) {
      for (const element of table.querySelectorAll("[data-stop]")) {
        const index = stopNames.indexOf(element.dataset.stop);
        const isEnd =
          state !== null && (index === state.fromIndex || index === state.toIndex);
        const isBetween =
          state !== null && index > state.start && index < state.end;
        const hidden =
          state !== null && !isEnd && (!isBetween || !expanded);
        element.classList.toggle("journey-hidden", hidden);
        element.classList.toggle("journey-end", isEnd);
        element.classList.toggle("journey-between", isBetween);
      }
    }
  }

  function matches(entry) {
    const from = fromSelect.value;
    const to = toSelect.value;
    if (!from && !to) {
      return true;
    }
    if (from && !entry.callIndex.has(from)) {
      return false;
    }
    if (to && !entry.callIndex.has(to)) {
      return false;
    }
    if (from && to && !(entry.callIndex.get(from) < entry.callIndex.get(to))) {
      return false;
    }
    return true;
  }

  function sortValue(entry, stop) {
    const cell = entry.cells.get(stop);
    if (!cell) {
      return { group: 2, minutes: 0 };
    }
    if (cell.cls === "time") {
      const value = minutes(cell.text);
      return { group: 0, minutes: value === null ? Number.MAX_SAFE_INTEGER : value };
    }
    if (cell.cls === "unpublished") {
      return { group: 1, minutes: 0 };
    }
    return { group: 2, minutes: 0 };
  }

  function applySort(entries, body) {
    if (!sortStop) {
      return;
    }
    const direction = sortDirection === "asc" ? 1 : -1;
    const ordered = entries.slice().sort((a, b) => {
      const aValue = sortValue(a, sortStop);
      const bValue = sortValue(b, sortStop);
      if (aValue.group !== bValue.group) {
        return aValue.group - bValue.group;
      }
      if (aValue.group === 0 && aValue.minutes !== bValue.minutes) {
        return (aValue.minutes - bValue.minutes) * direction;
      }
      return a.service.service_id.localeCompare(b.service.service_id);
    });
    const fragment = document.createDocumentFragment();
    for (const entry of ordered) {
      fragment.append(entry.row);
    }
    body.append(fragment);
  }

  function updateSortIndicators() {
    for (const table of [pdfTable, gtfsTable]) {
      for (const header of table.querySelectorAll("thead th[data-stop]")) {
        const active = header.dataset.stop === sortStop;
        header.setAttribute(
          "aria-sort",
          active ? (sortDirection === "asc" ? "ascending" : "descending") : "none"
        );
      }
    }
  }

  function updateToggle(state) {
    const middle =
      state === null ? 0 : Math.max(0, state.end - state.start - 1);
    toggle.hidden = middle === 0;
    toggle.setAttribute("aria-expanded", expanded ? "true" : "false");
    if (middle > 0) {
      const noun = middle === 1 ? "parada intermedia" : "paradas intermedias";
      const verb = expanded ? "Ezkutatu" : "Erakutsi";
      const verbEs = expanded ? "Ocultar" : "Mostrar";
      toggle.textContent = `${verb} tarteko ${middle} geltoki / ${verbEs} ${middle} ${noun}`;
    }
  }

  function updateReverse(state) {
    reverseCorridor = null;
    if (state === null || !fromSelect.value || !toSelect.value) {
      reverse.hidden = true;
      return;
    }
    const fromIndex = stopNames.indexOf(fromSelect.value);
    const toIndex = stopNames.indexOf(toSelect.value);
    if (fromIndex === -1 || toIndex === -1 || toIndex >= fromIndex) {
      reverse.hidden = true;
      return;
    }
    reverseCorridor = pdfData.corridors.find(
      (item) => item.line === corridor.line && item.direction !== corridor.direction
    );
    if (!reverseCorridor) {
      reverse.hidden = true;
      return;
    }
    reverse.hidden = false;
    reverseLink.textContent =
      `Begiratu alderantzizko noranzkoa: ${reverseCorridor.direction} / ` +
      `Consulta el sentido inverso: ${reverseCorridor.direction}`;
  }

  function departureMap(entries) {
    const map = new Map();
    for (const entry of entries) {
      const key = entry.service.departure || "";
      if (!map.has(key)) {
        map.set(key, []);
      }
      map.get(key).push(entry);
    }
    return map;
  }

  function serviceIds(entries) {
    return entries.map((entry) => entry.service.service_id).join(", ");
  }

  function renderSummary(visiblePdf, visibleGtfs) {
    const pdfByDeparture = departureMap(visiblePdf);
    const gtfsByDeparture = departureMap(visibleGtfs);
    const allDepartures = new Set([
      ...pdfByDeparture.keys(),
      ...gtfsByDeparture.keys(),
    ]);
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
        const pdfSignature = pdfGroup
          .map((entry) => stopNames.map((stop) => entry.cells.get(stop).text).join("|"))
          .sort()
          .join(";");
        const gtfsSignature = gtfsGroup
          .map((entry) => stopNames.map((stop) => entry.cells.get(stop).text).join("|"))
          .sort()
          .join(";");
        if (pdfSignature !== gtfsSignature) {
          changed.push([departure, pdfGroup, gtfsGroup]);
        }
      }
    }

    summary.replaceChildren();
    const counts = document.createElement("p");
    counts.textContent =
      `PDF: ${visiblePdf.length} / ${pdfEntries.length} · ` +
      `GTFS: ${visibleGtfs.length} / ${gtfsEntries.length} · ` +
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
      const item = document.createElement("li");
      item.className = "diff-pdf-only";
      item.textContent = `${departure} — PDF: ${serviceIds(group)}`;
      list.append(item);
      shown += 1;
    }
    for (const [departure, group] of onlyGtfs) {
      if (shown >= limit) break;
      const item = document.createElement("li");
      item.className = "diff-gtfs-only";
      item.textContent = `${departure} — GTFS: ${serviceIds(group)}`;
      list.append(item);
      shown += 1;
    }
    for (const [departure, pdfGroup, gtfsGroup] of changed) {
      if (shown >= limit) break;
      const item = document.createElement("li");
      item.className = "diff-changed";
      item.textContent =
        `${departure} — PDF: ${serviceIds(pdfGroup)} ↔ GTFS: ${serviceIds(gtfsGroup)}`;
      list.append(item);
      shown += 1;
    }
    if (onlyPdf.length + onlyGtfs.length + changed.length > limit) {
      const item = document.createElement("li");
      item.className = "diff-muted";
      item.textContent = "…";
      list.append(item);
    }
    if (shown === 0) {
      const item = document.createElement("li");
      item.className = "diff-muted";
      item.textContent =
        "Ez dago alderik hautatutako egutegian / No hay diferencias en el calendario seleccionado.";
      list.append(item);
    }
  }

  function applyState() {
    syncOptions();
    const state = columnState();
    applyColumns(state);
    if (sortStop && state) {
      const index = stopNames.indexOf(sortStop);
      const hidden =
        index !== state.fromIndex &&
        index !== state.toIndex &&
        (index < state.start ||
          index > state.end ||
          (index > state.start && index < state.end && !expanded));
      if (hidden) {
        sortStop = defaultSortStop();
      }
    }
    applySort(pdfEntries, pdfBody);
    applySort(gtfsEntries, gtfsBody);

    const visiblePdf = [];
    const visibleGtfs = [];
    for (const entry of pdfEntries) {
      const show = matches(entry);
      entry.row.hidden = !show;
      if (show) {
        visiblePdf.push(entry);
      }
    }
    for (const entry of gtfsEntries) {
      const show = matches(entry);
      entry.row.hidden = !show;
      if (show) {
        visibleGtfs.push(entry);
      }
    }

    count.textContent =
      `PDF: ${visiblePdf.length} / ${pdfEntries.length} · ` +
      `GTFS: ${visibleGtfs.length} / ${gtfsEntries.length}`;
    const filtering = fromSelect.value !== "" || toSelect.value !== "";
    empty.hidden = !filtering || visiblePdf.length + visibleGtfs.length > 0;
    clear.hidden = !filtering;
    updateToggle(state);
    updateSortIndicators();
    updateReverse(state);
    renderSummary(visiblePdf, visibleGtfs);
  }

  function rebuildTables() {
    sortStop = defaultSortStop();
    pdfEntries = buildEntries(
      servicesFor(pdfData, corridor.sheet, calendarSelect.value)
    );
    gtfsEntries = buildEntries(
      servicesFor(gtfsData, corridor.sheet, calendarSelect.value)
    );
    pdfBody = buildTable(pdfTable, pdfEntries, "");
    gtfsBody = buildTable(gtfsTable, gtfsEntries, "gtfs/");
    applyState();
  }

  function updateCalendars(preserveFilters) {
    const calendars = availableCalendars(corridor.sheet);
    const previous = calendarSelect.value;
    const fallback = calendars.find((item) => item.id === "WD") || calendars[0];
    setOptions(
      calendarSelect,
      calendars.map((item) => ({
        value: item.id,
        label: `${item.label_eu} / ${item.label_es}`,
      })),
      calendars.some((item) => item.id === previous) ? previous : fallback?.id
    );
    if (!preserveFilters) {
      fromSelect.value = "";
      toSelect.value = "";
      expanded = false;
    }
    fillStopSelects();
    rebuildTables();
  }

  function selectCorridor(value, preserveFilters) {
    corridorSelect.value = value;
    corridor = selectedCorridor();
    if (!corridor) {
      return;
    }
    stopNames = corridor.stops;
    updateCalendars(preserveFilters);
  }

  corridorSelect.addEventListener("change", () => {
    selectCorridor(corridorSelect.value, false);
  });
  calendarSelect.addEventListener("change", () => {
    rebuildTables();
  });
  fromSelect.addEventListener("change", () => {
    expanded = false;
    sortStop = defaultSortStop();
    applyState();
  });
  toSelect.addEventListener("change", () => {
    expanded = false;
    sortStop = defaultSortStop();
    applyState();
  });
  toggle.addEventListener("click", () => {
    expanded = !expanded;
    applyState();
  });
  clear.addEventListener("click", () => {
    fromSelect.value = "";
    toSelect.value = "";
    expanded = false;
    sortStop = defaultSortStop();
    applyState();
    fromSelect.focus();
  });
  reverseLink.addEventListener("click", () => {
    if (!reverseCorridor) {
      return;
    }
    selectCorridor(corridorValue(reverseCorridor), true);
    reverse.hidden = true;
  });

  Promise.all([loadJson("data/services.json"), loadJson("gtfs/data/services.json")])
    .then(([pdf, gtfs]) => {
      pdfData = pdf;
      gtfsData = gtfs;
      populateCorridors();
      corridor = selectedCorridor();
      if (!corridor) {
        throw new Error("no comparisons available");
      }
      stopNames = corridor.stops;
      updateCalendars(false);
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
