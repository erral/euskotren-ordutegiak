# Write the service sorting specification

Type: task
Status: resolved
Blocked by: 01, 02, 03
Parent: [Sort services in the output Excel timetable](../map.md)

## Question

Produce the destination artifact: `.scratch/service-sorting/spec.md`, the written sorting specification for the workbook.

It must cover:

- the canonical key, including calendar order, departure/night handling, line order, direction order and the service-ID tie-breaker;
- the sheet-specific rules for `Master` and the eight corridor sheets, including the corridor own-line-first tie-break and the stacked calendar blocks;
- the presentation boundary: keep the `Master` AutoFilter, leave corridor sheets as fixed merged-header views, and do not reorder tabs;
- the documentation decision from the sort-documentation ticket;
- concrete golden examples from the current workbook (same-departure ties, cross-line corridor rows, after-midnight `24:xx` services);
- a validation approach for the order, suitable for a later implementation effort;
- an explicit implementation boundary: this spec changes no generator code.

Resolved when the spec is written and reviewed. The task is AFK to draft and HITL to review.

## Answer

Resolved 2026-11-21.

The specification is written at [`spec.md`](../spec.md). It defines:

- the master key and the corridor key;
- the own-line-first tie-break, applied **after** departure;
- the calendar, line and published-direction orders;
- extended-clock handling for `FN`/`SN`;
- the flat `Master` layout and the stacked corridor calendar blocks;
- the README-only documentation rule;
- edge cases, golden examples, validation checks and implementation notes for the later effort.

Reviewed and confirmed. Implementation remains a separate effort.

## Comments

- Charted 2026-11-21. Blocked by the line-order, direction-order and documentation tickets.
- 2026-11-21: claimed; spec drafted at [`spec.md`](../spec.md). Awaiting review before resolution.
- 2026-11-21: reviewed and confirmed; resolved.
