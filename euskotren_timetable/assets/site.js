(function () {
  "use strict";

  document.documentElement.classList.add("js");

  const byId = (id) => document.getElementById(id);
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
})();
