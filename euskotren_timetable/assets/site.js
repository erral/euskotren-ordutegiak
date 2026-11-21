(function () {
  "use strict";

  document.documentElement.classList.add("js");

  const byId = (id) => document.getElementById(id);

  function normalize(value) {
    return value
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, " ")
      .trim();
  }

  function initMasterFilters() {
    const rows = Array.from(document.querySelectorAll("tbody tr[data-line]"));
    const count = byId("filter-count");
    if (!count || rows.length === 0) {
      return;
    }

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

  function initStopFilter() {
    const input = byId("stop-filter");
    const count = byId("stop-filter-count");
    const clear = byId("stop-filter-clear");
    const table = document.querySelector("table.timetable");
    if (!input || !count || !table) {
      return;
    }

    const headers = Array.from(table.querySelectorAll("thead th[data-stop]"));
    if (headers.length === 0) {
      return;
    }
    const stopNames = headers.map((header) => header.dataset.stop);
    const normalizedStops = stopNames.map(normalize);
    const cells = Array.from(table.querySelectorAll("tbody td[data-stop]"));
    const rows = Array.from(table.querySelectorAll("tbody tr")).map((row) => {
      const served = new Set();
      for (const cell of row.querySelectorAll("td[data-stop]")) {
        if (
          cell.classList.contains("time") ||
          cell.classList.contains("unpublished")
        ) {
          served.add(cell.dataset.stop);
        }
      }
      return { row, served };
    });

    function apply() {
      const query = normalize(input.value);
      const matched = new Set();
      if (query) {
        const exact = stopNames.filter(
          (stop, index) => normalizedStops[index] === query
        );
        if (exact.length > 0) {
          exact.forEach((stop) => matched.add(stop));
        } else {
          stopNames.forEach((stop, index) => {
            if (normalizedStops[index].includes(query)) {
              matched.add(stop);
            }
          });
        }
      }

      let visible = 0;
      for (const entry of rows) {
        const show =
          !query || Array.from(matched).some((stop) => entry.served.has(stop));
        entry.row.hidden = !show;
        if (show) {
          visible += 1;
        }
      }

      for (const header of headers) {
        header.classList.toggle("stop-match", matched.has(header.dataset.stop));
      }
      for (const cell of cells) {
        cell.classList.toggle("stop-match", matched.has(cell.dataset.stop));
      }

      if (clear) {
        clear.hidden = input.value.trim() === "";
      }
      if (!query) {
        count.textContent = `${rows.length} / ${rows.length}`;
      } else if (matched.size === 0) {
        count.textContent = `0 / ${rows.length} · ez da geltokirik aurkitu / no se encontró parada`;
      } else {
        count.textContent = `${visible} / ${rows.length}`;
      }
      return matched;
    }

    function scrollToFirst(matched) {
      if (matched.size === 0) {
        return;
      }
      const scroller = table.closest(".table-scroll");
      const first = headers.find((header) => matched.has(header.dataset.stop));
      if (!first || !scroller) {
        return;
      }
      const scrollerRect = scroller.getBoundingClientRect();
      const headerRect = first.getBoundingClientRect();
      const left =
        scroller.scrollLeft +
        headerRect.left -
        scrollerRect.left -
        (scroller.clientWidth - headerRect.width) / 2;
      scroller.scrollTo({ left: Math.max(0, left), behavior: "smooth" });
    }

    let scrollTimer;
    input.addEventListener("input", () => {
      const matched = apply();
      clearTimeout(scrollTimer);
      scrollTimer = setTimeout(() => {
        if (matched.size === 1) {
          scrollToFirst(matched);
        }
      }, 350);
    });
    input.addEventListener("change", () => {
      scrollToFirst(apply());
    });
    if (clear) {
      clear.addEventListener("click", () => {
        input.value = "";
        apply();
        input.focus();
      });
    }
    apply();
  }

  initMasterFilters();
  initStopFilter();
})();
