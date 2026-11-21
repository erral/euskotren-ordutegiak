# Glossary

## Service

A single scheduled train run from an origin to a destination, calling at an ordered sequence of stops. One row in the wide timetable. `trip` is only a GTFS-alignment alias.

_Avoid_: train (ambiguous with rolling stock).

## Stop

A named place where a service calls. Only stops are modelled; there is no separate City entity. Stops that share a municipality are distinct stations and are modelled separately: `Eibar-Azitain`, `Eibar-Ardantza` and `Eibar` are three different stops. When the municipality label is needed to disambiguate, it is composed into the stop's canonical name. Each distinct stop has a stable ID, a canonical Basque name and a Spanish alias.

## Stop disposition

Whether a service stops at a stop, passes without stopping, or does not serve it in the source. The published wide table collapses all three to a blank cell; the parser may keep the source symbol as provenance.

## Stop time

The scheduled time at which a given service calls at a given stop. A service that does not call at a stop has no stop time there.

## Line

A branded Euskotren train corridor published under a code: E1, E2/T1, E3/L3 or E4. A line has two extremes and a trunk between them.

## Direction

One of the two travel orientations of a line, named by its origin and destination, for example Amara → Matiko.

## Trunk

The continuous stop sequence along a line from one extreme to the other, shared by the line's services.

## Branch

A stop or stop sequence that leaves the trunk and is served by only some services.

## Calling pattern

The ordered set of stops a particular service calls at, including branch and limited-stop variations. A service's calling pattern is independent of the line's display order.

## Display order

The canonical order of stop columns for a line and direction, with branch stops placed inline at their junction. It is a presentation order, not the order in which any particular service calls.

## Timetable

The set of services for a line, direction, day type and season.

## Season

A named validity period for a published timetable, such as winter 2026.

## Frequency rule

A compressed source notation that represents a repeating sequence of services, such as "5:50 to 19:50, every 1 hour". Frequency rules are expanded into explicit services for the workbook, with the original rule retained as provenance.

## Day type

A coarse label used to describe a calendar: weekday, Saturday, Sunday, holiday, or night/eve. Calendars are the primary grouping; a calendar may cover more than one day type.

## Calendar

A named service set that runs on a defined set of operating days, such as Weekday, Saturday, Sunday + holiday, Saturday + Sunday + holiday, Friday night / holiday eve, or Saturday night. Every service belongs to exactly one calendar.

## Service day

The operating day a service belongs to. For an after-midnight service, this is the day the service started: a 00:30 Sunday train belongs to Saturday's service day.

## Holiday eve

The night before a public holiday. It is a distinct calendar condition from an ordinary Friday night.

## Service order

The canonical order of service rows in a timetable sheet. It is a presentation order, separate from service identity and from the calling pattern: it is stable across regenerations and orders services by operating calendar, departure time, line and direction, with a deterministic tie-breaker.

## Timetable version

A published edition of a timetable with a validity start, an open validity end until superseded, a season label and a source document.

## Wide timetable

The published Excel layout: stops as columns in travel order, services as rows, stop times in cells.
