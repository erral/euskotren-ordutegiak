"""Command-line entry point."""

import argparse
import json
from datetime import date, datetime
from pathlib import Path

from .corridors import assign_membership
from .gtfs import load_gtfs_services
from .manifest import MANIFEST_PATH, build_manifest
from .parse_e1 import parse_e1_weekday, to_minutes
from .parse_e1_eibar import parse_e1_eibar
from .parse_e1_elgoibar import parse_e1_elgoibar
from .parse_e1_night import parse_e1_night, parse_e1_night_reverse
from .parse_e1_partial import (
    FORWARD_SATURDAY,
    FORWARD_SUNDAY,
    FORWARD_WEEKDAY,
    REVERSE_SATURDAY,
    REVERSE_SUNDAY,
    REVERSE_WEEKDAY,
    build_partial_services,
)
from .parse_e1_refuerzo import parse_e1_refuerzos
from .parse_e1_reverse import parse_e1_reverse
from .parse_e1_weekend import parse_e1_weekend, parse_e1_weekend_reverse
from .parse_e2 import parse_e2_reverse, parse_e2_weekday
from .parse_e2_shuttle_weekend import parse_e2_shuttle_weekend
from .parse_e2_weekend import parse_e2_weekend, parse_e2_weekend_reverse
from .parse_e3 import (
    parse_e3_reverse,
    parse_e3_weekday,
    parse_e3_weekend,
    parse_e3_weekend_reverse,
)
from .parse_e4 import (
    GERNIKA_WD_FORWARD,
    GERNIKA_WD_REVERSE,
    GERNIKA_WE_FORWARD,
    GERNIKA_WE_REVERSE,
    parse_e4_gernika_turns,
    parse_e4_reverse,
    parse_e4_weekday,
    parse_e4_weekend,
    parse_e4_weekend_reverse,
)
from .parse_l3 import (
    parse_l3_reverse,
    parse_l3_weekday,
    parse_l3_weekend,
    parse_l3_weekend_reverse,
)
from .parse_l3_night import parse_e3_night, parse_l3_night
from .parse_night import (
    parse_e2_night,
    parse_e2_night_reverse,
    parse_e4_night,
    parse_e4_night_reverse,
)
from .site import SITE_DIR, WORKBOOK_FILENAME, build_site, validate_site
from .validate import validate, write_report
from .workbook import build_workbook

DEFAULT_OUTPUT = "output/euskotren_timetables_winter_2026_v12.xlsx"
DEFAULT_SITE_OUTPUT = str(SITE_DIR)
DEFAULT_GTFS = "data/gtfs/gtfs_euskotren.zip"
DEFAULT_GTFS_WORKBOOK = "output/euskotren_timetables_winter_2026_gtfs.xlsx"
DEFAULT_GTFS_SITE_OUTPUT = "output/html-gtfs"


def _build_weekday(
    manifest_path: str,
    output: str,
    site_output: str | None = None,
    compare: bool = False,
    gtfs_url: str | None = None,
    workbook_name: str = WORKBOOK_FILENAME,
) -> None:
    path = Path(manifest_path)
    if not path.exists():
        raise SystemExit(
            f"manifest not found: {manifest_path}\nRun `python3 -m euskotren_timetable.cli manifest` first."
        )
    manifest = json.loads(path.read_text())
    entries = {entry["label"]: entry for entry in manifest["files"]}
    labels = (
        "e1_pasaia_matiko",
        "e1_matiko_pasaia",
        "e2_t1_hendaia_lasarte",
        "e2_t1_lasarte_hendaia",
        "e4_bilbao_bermeo",
        "e3_l3",
    )
    try:
        e1w, e1e, e2w, e2e, e4, e3 = (entries[label] for label in labels)
    except KeyError as exc:
        raise SystemExit(f"manifest is missing {exc}; rerun the manifest") from exc

    e1w_services, e1w_rule = parse_e1_weekday(e1w["path"], e1w["url"])
    e1e_services, e1e_rule = parse_e1_reverse(e1e["path"], e1e["url"])
    e1we_services, e1we_rule = parse_e1_weekend(e1w["path"], e1w["url"])
    e1ww_services, e1ww_rule = parse_e1_weekend_reverse(e1e["path"], e1e["url"])
    e1snw_services = parse_e1_night(e1w["path"], e1w["url"])
    e1sne_services = parse_e1_night_reverse(e1e["path"], e1e["url"])
    e1w_times = {service.departure for service in e1w_services}
    e1we_times = {service.departure for service in e1we_services}
    e1e_zumaia = {
        next(st.time for st in service.stop_times if st.stop_name == "Zumaia")
        for service in e1e_services
    }
    e1ww_zumaia = {
        next(st.time for st in service.stop_times if st.stop_name == "Zumaia")
        for service in e1ww_services
    }
    e1r_services = parse_e1_refuerzos(e1w["path"], e1e["path"], e1w["url"], e1e["url"])
    e1elg_services = parse_e1_elgoibar(e1w["path"], e1e["path"], e1w["url"], e1e["url"])
    e1eib_services, e1eib_rules = parse_e1_eibar(e1w["path"], e1e["path"], e1w["url"], e1e["url"])
    e1p_services = (
        build_partial_services(
            e1w["path"],
            e1w["url"],
            FORWARD_WEEKDAY,
            e1w_times,
            "Pasaia-Matiko",
            "PASAIA-ZUMAIA",
        )
        + build_partial_services(
            e1w["path"],
            e1w["url"],
            FORWARD_SATURDAY,
            e1we_times,
            "Pasaia-Matiko",
            "PASAIA-ZUMAIA",
        )
        + build_partial_services(
            e1w["path"],
            e1w["url"],
            FORWARD_SUNDAY,
            e1we_times,
            "Pasaia-Matiko",
            "PASAIA-ZUMAIA",
        )
        + build_partial_services(
            e1e["path"],
            e1e["url"],
            REVERSE_WEEKDAY,
            e1e_zumaia,
            "Matiko-Pasaia",
            "ZUMAIA-PASAIA",
        )
        + build_partial_services(
            e1e["path"],
            e1e["url"],
            REVERSE_SATURDAY,
            e1ww_zumaia,
            "Matiko-Pasaia",
            "ZUMAIA-PASAIA",
        )
        + build_partial_services(
            e1e["path"],
            e1e["url"],
            REVERSE_SUNDAY,
            e1ww_zumaia,
            "Matiko-Pasaia",
            "ZUMAIA-PASAIA",
        )
    )
    e2w_services, e2w_rules = parse_e2_weekday(e2w["path"], e2w["url"])
    e2e_services, e2e_rules = parse_e2_reverse(e2e["path"], e2e["url"])
    e2we_services, e2we_rule = parse_e2_weekend(e2w["path"], e2w["url"])
    e2ww_services, e2ww_rule = parse_e2_weekend_reverse(e2e["path"], e2e["url"])
    e2sh_services, e2sh_rules = parse_e2_shuttle_weekend(
        e2w["path"], e2e["path"], e2w["url"], e2e["url"]
    )
    e4e_services, e4e_rule = parse_e4_weekday(e4["path"], e4["url"])
    e4w_services, e4w_rule = parse_e4_reverse(e4["path"], e4["url"])
    e4we_services, e4we_rule = parse_e4_weekend(e4["path"], e4["url"])
    e4ww_services, e4ww_rule = parse_e4_weekend_reverse(e4["path"], e4["url"])
    e2snw_services = parse_e2_night(e2w["path"], e2w["url"])
    e2sne_services = parse_e2_night_reverse(e2e["path"], e2e["url"])
    e4snw_services = parse_e4_night(e4["path"], e4["url"])
    e4sne_services = parse_e4_night_reverse(e4["path"], e4["url"])
    e4ger_services = (
        parse_e4_gernika_turns(e4["path"], e4["url"], GERNIKA_WD_FORWARD)
        + parse_e4_gernika_turns(e4["path"], e4["url"], GERNIKA_WE_FORWARD)
        + parse_e4_gernika_turns(e4["path"], e4["url"], GERNIKA_WD_REVERSE)
        + parse_e4_gernika_turns(e4["path"], e4["url"], GERNIKA_WE_REVERSE)
    )
    e3e_services, e3e_rule = parse_e3_weekday(e3["path"], e3["url"])
    e3w_services, e3w_rule = parse_e3_reverse(e3["path"], e3["url"])
    e3we_services, e3we_rule = parse_e3_weekend(e3["path"], e3["url"])
    e3ww_services, e3ww_rule = parse_e3_weekend_reverse(e3["path"], e3["url"])
    l3e_services, l3e_rule = parse_l3_weekday(e3["path"], e3["url"])
    l3w_services, l3w_rule = parse_l3_reverse(e3["path"], e3["url"])
    l3we_services, l3we_rule = parse_l3_weekend(e3["path"], e3["url"])
    l3ww_services, l3ww_rule = parse_l3_weekend_reverse(e3["path"], e3["url"])
    l3night_services, l3night_rules = parse_l3_night(e3["path"], e3["url"])
    e3night_services = parse_e3_night(e3["path"], e3["url"])

    services = (
        e1w_services
        + e1e_services
        + e1we_services
        + e1ww_services
        + e1snw_services
        + e1sne_services
        + e1p_services
        + e1r_services
        + e1elg_services
        + e1eib_services
        + e2w_services
        + e2e_services
        + e2we_services
        + e2ww_services
        + e2sh_services
        + e2snw_services
        + e2sne_services
        + e4w_services
        + e4e_services
        + e4we_services
        + e4ww_services
        + e4snw_services
        + e4sne_services
        + e4ger_services
        + e3w_services
        + e3e_services
        + e3we_services
        + e3ww_services
        + e3night_services
        + l3w_services
        + l3e_services
        + l3we_services
        + l3ww_services
        + l3night_services
    )
    services.sort(
        key=lambda service: (to_minutes(service.departure), service.primary_line, service.direction)
    )
    assign_membership(services)
    rules = (
        [e1w_rule, e1e_rule, e1we_rule, e1ww_rule]
        + e2w_rules
        + e2e_rules
        + [e2we_rule, e2ww_rule]
        + e2sh_rules
        + [e4w_rule, e4e_rule, e4we_rule, e4ww_rule]
        + [e3w_rule, e3e_rule, e3we_rule, e3ww_rule]
        + [l3w_rule, l3e_rule, l3we_rule, l3ww_rule]
        + l3night_rules
        + e1eib_rules
    )
    checks = validate(services, rules)
    write_report(checks)
    target = build_workbook(output, services, rules, checks, manifest)

    passed = sum(check.status == "PASS" for check in checks)
    print(f"E1 west services: {len(e1w_services)}")
    print(f"E1 east services: {len(e1e_services)}")
    print(f"E1 weekend west services: {len(e1we_services)}")
    print(f"E1 weekend east services: {len(e1ww_services)}")
    print(f"E1 Saturday night west services: {len(e1snw_services)}")
    print(f"E1 Saturday night east services: {len(e1sne_services)}")
    print(f"E1 Pasaia-Zumaia partial services: {len(e1p_services)}")
    print(f"E1 refuerzo services: {len(e1r_services)}")
    print(f"E1 Elgoibar partial services: {len(e1elg_services)}")
    print(f"E1 Eibar-Ermua partial services: {len(e1eib_services)}")
    print(f"E2 west services: {len(e2w_services)}")
    print(f"E2 east services: {len(e2e_services)}")
    print(f"E2 weekend west services: {len(e2ww_services)}")
    print(f"E2 weekend east services: {len(e2we_services)}")
    print(
        "E2 Saturday shuttle services: "
        f"{sum(1 for service in e2sh_services if service.calendar == 'SA')}"
    )
    print(
        "E2 Sunday shuttle services: "
        f"{sum(1 for service in e2sh_services if service.calendar == 'SU')}"
    )
    print(f"E4 west services: {len(e4w_services)}")
    print(f"E4 east services: {len(e4e_services)}")
    print(f"E4 weekend west services: {len(e4ww_services)}")
    print(f"E4 weekend east services: {len(e4we_services)}")
    print(f"E2 Saturday night west services: {len(e2snw_services)}")
    print(f"E2 Saturday night east services: {len(e2sne_services)}")
    print(f"E4 Saturday night west services: {len(e4snw_services)}")
    print(f"E4 Saturday night east services: {len(e4sne_services)}")
    print(f"E4 Gernika short-turn services: {len(e4ger_services)}")
    print(f"E3 west services: {len(e3w_services)}")
    print(f"E3 east services: {len(e3e_services)}")
    print(f"E3 weekend west services: {len(e3ww_services)}")
    print(f"E3 weekend east services: {len(e3we_services)}")
    print(f"L3 west services: {len(l3w_services)}")
    print(f"L3 east services: {len(l3e_services)}")
    print(f"L3 weekend west services: {len(l3ww_services)}")
    print(f"L3 weekend east services: {len(l3we_services)}")
    print(f"L3 night services: {len(l3night_services)}")
    print(f"E3 night services: {len(e3night_services)}")
    print(f"total services: {len(services)}")
    print(f"checks: {passed}/{len(checks)} passed")
    print(f"workbook: {target}")
    print("validation: output/validation.md")
    if passed != len(checks):
        raise SystemExit(1)
    if site_output:
        extra_context = {}
        if compare:
            extra_context["compare_url"] = "compare.html"
        if gtfs_url:
            extra_context["gtfs_url"] = gtfs_url
        site_path = build_site(
            services,
            site_output,
            manifest,
            workbook_path=target,
            extra_context=extra_context or None,
            build_compare=compare,
            workbook_name=workbook_name,
        )
        print(f"site: {site_path}")


def _build_gtfs(
    gtfs_path: str,
    output: str,
    site_output: str | None,
    workbook_name: str,
    pdf_url: str | None = None,
    compare_url: str | None = None,
) -> None:
    try:
        services, meta = load_gtfs_services(gtfs_path)
    except (OSError, ValueError) as exc:
        raise SystemExit(f"GTFS build failed: {exc}") from exc
    manifest = meta.as_manifest()
    feed_end = datetime.strptime(meta.feed_end_date, "%Y-%m-%d").date()
    if (feed_end - date.today()).days < 7:
        raise SystemExit(
            f"GTFS feed ends on {meta.feed_end_date}; fewer than 7 days remain. "
            "Refresh the feed before publishing."
        )
    target = build_workbook(output, services, [], [], manifest)
    print(f"source: GTFS {meta.feed_version} ({meta.feed_start_date} → {meta.feed_end_date})")
    print(f"services: {len(services)}")
    print(f"workbook: {target}")
    if site_output:
        extra_context = {"variant_label": "GTFS bertsioa / Versión GTFS"}
        if pdf_url:
            extra_context["pdf_url"] = pdf_url
        if compare_url:
            extra_context["compare_url"] = compare_url
        site_path = build_site(
            services,
            site_output,
            manifest,
            workbook_path=target,
            extra_context=extra_context,
            workbook_name=workbook_name,
        )
        print(f"site: {site_path}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="euskotren-timetable")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("manifest", help="Download/refresh the PDF manifest")
    build = sub.add_parser(
        "build-weekday", help="Parse, validate and render the E1/E2 weekday slice"
    )
    build.add_argument("--manifest", default=str(MANIFEST_PATH))
    build.add_argument("--output", default=DEFAULT_OUTPUT)
    html = sub.add_parser("build-html", help="Build the workbook and the static HTML site")
    html.add_argument("--manifest", default=str(MANIFEST_PATH))
    html.add_argument("--source", choices=("pdf", "gtfs"), default="pdf")
    html.add_argument("--gtfs", default=DEFAULT_GTFS)
    html.add_argument("--output", default=None)
    html.add_argument("--workbook", default=None)
    html.add_argument("--workbook-name", default=None)
    html.add_argument("--compare", action="store_true")
    html.add_argument("--gtfs-url", default=None)
    html.add_argument("--pdf-url", default=None)
    html.add_argument("--compare-url", default=None)
    site_check = sub.add_parser("validate-site", help="Check the generated site")
    site_check.add_argument("--output", default=DEFAULT_SITE_OUTPUT)
    sub.add_parser("all", help="manifest + build-weekday + build-html")
    args = parser.parse_args()

    if args.command == "manifest":
        manifest = build_manifest()
        print(f"manifest: {len(manifest['files'])} file(s)")
        print(f"written: {MANIFEST_PATH}")
        return

    if args.command == "build-html":
        if args.source == "gtfs":
            _build_gtfs(
                args.gtfs,
                args.workbook or DEFAULT_GTFS_WORKBOOK,
                args.output or DEFAULT_GTFS_SITE_OUTPUT,
                args.workbook_name or "euskotren_timetables_winter_2026_gtfs.xlsx",
                pdf_url=args.pdf_url,
                compare_url=args.compare_url,
            )
        else:
            _build_weekday(
                args.manifest,
                args.workbook or DEFAULT_OUTPUT,
                site_output=args.output or DEFAULT_SITE_OUTPUT,
                compare=args.compare,
                gtfs_url=args.gtfs_url,
                workbook_name=args.workbook_name or WORKBOOK_FILENAME,
            )
        return

    if args.command == "validate-site":
        errors = validate_site(args.output)
        if errors:
            for error in errors:
                print(error)
            raise SystemExit(1)
        print(f"site valid: {args.output}")
        return

    if args.command == "all":
        build_manifest()
        _build_weekday(str(MANIFEST_PATH), DEFAULT_OUTPUT, site_output=DEFAULT_SITE_OUTPUT)
        return

    _build_weekday(args.manifest, args.output)


if __name__ == "__main__":
    main()
