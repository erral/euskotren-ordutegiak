(function () {
  "use strict";

  document.documentElement.classList.add("js");

  const byId = (id) => document.getElementById(id);

  function minutes(value) {
    const match = /^(\d{1,2}):(\d{2})$/.exec(value.trim());
    if (!match) {
      return null;
    }
    const hours = Number(match[1]);
    const mins = Number(match[2]);
    if (mins > 59) {
      return null;
    }
    return hours * 60 + mins;
  }

  function initMasterFilters() {
    const rows = Array.from(document.querySelectorAll("tbody tr[data-line]"));
    const count = byId("filter-count");
    if (!count || rows.length === 0) {
      return;
    }

    function apply() {
      const text = byId("filter-text").value.trim().toLowerCase();
      const line = byId("filter-line").value;
      const calendar = byId("filter-calendar").value;
      const origin = byId("filter-origin").value;
      const destination = byId("filter-destination").value;
      const from = minutes(byId("filter-departure-from").value);
      const to = minutes(byId("filter-departure-to").value);

      let visible = 0;
      for (const row of rows) {
        const departure = Number(row.dataset.departure);
        const matches =
          (!text || row.dataset.search.includes(text)) &&
          (!line || row.dataset.line === line) &&
          (!calendar || row.dataset.calendar === calendar) &&
          (!origin || row.dataset.origin === origin) &&
          (!destination || row.dataset.destination === destination) &&
          (from === null || departure >= from) &&
          (to === null || departure <= to);
        row.hidden = !matches;
        if (matches) {
          visible += 1;
        }
      }
      count.textContent = `${visible} / ${rows.length}`;
    }

    const controls = [
      "filter-text",
      "filter-line",
      "filter-calendar",
      "filter-origin",
      "filter-destination",
      "filter-departure-from",
      "filter-departure-to",
    ];
    for (const id of controls) {
      const element = byId(id);
      element.addEventListener("input", apply);
      element.addEventListener("change", apply);
    }
    apply();
  }

  function initCorridorTable() {
    const from = byId("journey-from");
    const to = byId("journey-to");
    const count = byId("journey-count");
    const empty = byId("journey-empty");
    const clear = byId("journey-clear");
    const toggle = byId("journey-toggle");
    const table = byId("timetable");
    const reverse = byId("journey-reverse");
    const reverseLink = byId("journey-reverse-link");
    const reverseBase = reverseLink ? reverseLink.getAttribute("href") : null;
    if (!from || !to || !count || !empty || !clear || !toggle || !table) {
      return;
    }

    const headers = Array.from(table.querySelectorAll("thead th[data-stop]"));
    if (headers.length === 0) {
      return;
    }
    const headerByStop = new Map(
      headers.map((header) => [header.dataset.stop, header])
    );
    const stopOrder = new Map(
      headers.map((header, index) => [header.dataset.stop, index])
    );
    const stopNames = headers.map((header) => header.dataset.stop);
    const tbody = table.querySelector("tbody");
    const bodyCells = Array.from(table.querySelectorAll("tbody td[data-stop]"));
    const rows = Array.from(tbody.querySelectorAll("tr")).map((row, index) => {
      const calls = new Map();
      if (row.dataset.calls) {
        row.dataset.calls.split(",").forEach((value, position) => {
          const stop = stopNames[Number(value)];
          if (stop !== undefined) {
            calls.set(stop, position);
          }
        });
      }
      const cells = new Map();
      for (const cell of row.querySelectorAll("td[data-stop]")) {
        cells.set(cell.dataset.stop, cell);
      }
      return { row, calls, cells, order: index };
    });

    let expanded = false;
    let sortStop = null;
    let sortDirection = "asc";

    function defaultSortStop() {
      if (from.value) {
        return from.value;
      }
      if (to.value) {
        return to.value;
      }
      return stopNames[0];
    }

    function applyRequestedStops() {
      const params = new URLSearchParams(window.location.search);
      const requestedFrom = params.get("from");
      const requestedTo = params.get("to");
      if (
        requestedFrom &&
        requestedTo &&
        requestedFrom !== requestedTo &&
        stopOrder.has(requestedFrom) &&
        stopOrder.has(requestedTo)
      ) {
        from.value = requestedFrom;
        to.value = requestedTo;
        return;
      }
      if (requestedFrom && stopOrder.has(requestedFrom)) {
        from.value = requestedFrom;
      } else if (requestedTo && stopOrder.has(requestedTo)) {
        to.value = requestedTo;
      }
    }

    function syncUrl() {
      const url = new URL(window.location.href);
      if (from.value) {
        url.searchParams.set("from", from.value);
      } else {
        url.searchParams.delete("from");
      }
      if (to.value) {
        url.searchParams.set("to", to.value);
      } else {
        url.searchParams.delete("to");
      }
      try {
        history.replaceState(null, "", url.href);
      } catch {
        // file:// and other opaque origins reject history updates.
      }
    }

    function syncOptions() {
      for (const [select, other] of [
        [from, to],
        [to, from],
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

    function columnState() {
      const fromStop = from.value;
      const toStop = to.value;
      if (!fromStop || !toStop) {
        return null;
      }
      const fromIndex = stopOrder.get(fromStop);
      const toIndex = stopOrder.get(toStop);
      if (fromIndex === undefined || toIndex === undefined) {
        return null;
      }
      return {
        fromIndex,
        toIndex,
        start: Math.min(fromIndex, toIndex),
        end: Math.max(fromIndex, toIndex),
      };
    }

    function toggleColumn(element, state) {
      const index = stopOrder.get(element.dataset.stop);
      const isEnd =
        state !== null && (index === state.fromIndex || index === state.toIndex);
      const isBetween =
        state !== null && index > state.start && index < state.end;
      const hidden = state !== null && !isEnd && (!isBetween || !expanded);
      element.classList.toggle("journey-hidden", hidden);
      element.classList.toggle("journey-end", isEnd);
      element.classList.toggle("journey-between", isBetween);
    }

    function applyColumns(state) {
      for (const header of headers) {
        toggleColumn(header, state);
      }
      for (const cell of bodyCells) {
        toggleColumn(cell, state);
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

    function matches(calls) {
      const fromStop = from.value;
      const toStop = to.value;
      if (!fromStop && !toStop) {
        return true;
      }
      if (fromStop && !calls.has(fromStop)) {
        return false;
      }
      if (toStop && !calls.has(toStop)) {
        return false;
      }
      if (fromStop && toStop) {
        const fromPosition = calls.get(fromStop);
        const toPosition = calls.get(toStop);
        if (!(fromPosition < toPosition)) {
          return false;
        }
      }
      return true;
    }

    function sortValue(entry, stop) {
      const cell = entry.cells.get(stop);
      if (!cell) {
        return { group: 2, minutes: 0 };
      }
      if (cell.classList.contains("time")) {
        const value = minutes(cell.textContent);
        return {
          group: 0,
          minutes: value === null ? Number.MAX_SAFE_INTEGER : value,
        };
      }
      if (cell.classList.contains("unpublished")) {
        return { group: 1, minutes: 0 };
      }
      return { group: 2, minutes: 0 };
    }

    function applySort() {
      if (!sortStop) {
        return;
      }
      const direction = sortDirection === "asc" ? 1 : -1;
      const ordered = rows.slice().sort((a, b) => {
        const aValue = sortValue(a, sortStop);
        const bValue = sortValue(b, sortStop);
        if (aValue.group !== bValue.group) {
          return aValue.group - bValue.group;
        }
        if (aValue.group === 0 && aValue.minutes !== bValue.minutes) {
          return (aValue.minutes - bValue.minutes) * direction;
        }
        return a.order - b.order;
      });
      const fragment = document.createDocumentFragment();
      for (const entry of ordered) {
        fragment.appendChild(entry.row);
      }
      tbody.appendChild(fragment);
    }

    function applyFilter() {
      let visible = 0;
      for (const entry of rows) {
        const show = matches(entry.calls);
        entry.row.hidden = !show;
        if (show) {
          visible += 1;
        }
      }
      const filtering = from.value !== "" || to.value !== "";
      count.textContent = `${visible} / ${rows.length}`;
      empty.hidden = !filtering || visible > 0;
      clear.hidden = !filtering;
    }

    function updateSortIndicators() {
      for (const header of headers) {
        const active = header.dataset.stop === sortStop;
        header.setAttribute(
          "aria-sort",
          active ? (sortDirection === "asc" ? "ascending" : "descending") : "none"
        );
      }
    }

    function resetSort() {
      sortStop = defaultSortStop();
      sortDirection = "asc";
    }

    function updateReverseHint() {
      if (!reverse || !reverseLink || !reverseBase) {
        return;
      }
      const fromIndex = stopOrder.get(from.value);
      const toIndex = stopOrder.get(to.value);
      const reversed =
        from.value !== "" &&
        to.value !== "" &&
        fromIndex !== undefined &&
        toIndex !== undefined &&
        toIndex < fromIndex;
      reverse.hidden = !reversed;
      if (!reversed) {
        return;
      }
      const url = new URL(reverseBase, window.location.href);
      url.searchParams.set("from", from.value);
      url.searchParams.set("to", to.value);
      reverseLink.href = url.href;
    }

    function render() {
      syncOptions();
      const state = columnState();
      applyColumns(state);
      const activeHeader = sortStop ? headerByStop.get(sortStop) : null;
      if (activeHeader && activeHeader.classList.contains("journey-hidden")) {
        resetSort();
      }
      applySort();
      applyFilter();
      updateToggle(state);
      updateSortIndicators();
      updateReverseHint();
    }

    function handleSort(stop) {
      if (sortStop === stop) {
        sortDirection = sortDirection === "asc" ? "desc" : "asc";
      } else {
        sortStop = stop;
        sortDirection = "asc";
      }
      render();
    }

    for (const header of headers) {
      const button = header.querySelector(".sort-button");
      if (button) {
        button.disabled = false;
        button.addEventListener("click", () => handleSort(header.dataset.stop));
      }
    }

    for (const select of [from, to]) {
      select.addEventListener("change", () => {
        expanded = false;
        syncOptions();
        resetSort();
        syncUrl();
        render();
      });
    }
    toggle.addEventListener("click", () => {
      expanded = !expanded;
      render();
    });
    clear.addEventListener("click", () => {
      from.value = "";
      to.value = "";
      expanded = false;
      syncOptions();
      resetSort();
      syncUrl();
      render();
      from.focus();
    });

    applyRequestedStops();
    syncOptions();
    resetSort();
    render();
    syncUrl();
  }

  initMasterFilters();
  initCorridorTable();
})();
