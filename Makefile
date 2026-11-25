.PHONY: format lint test workbook html gtfs

format:
	ruff format .
	ruff check --fix .

lint:
	ruff format --check .
	ruff check .

test:
	python3 -m unittest discover -s tests

# Build the Excel workbook from the downloaded source PDFs.
workbook:
	python3 -m euskotren_timetable.cli build-weekday

# Build the workbook and then the static HTML site in output/html.
html:
	python3 -m euskotren_timetable.cli build-html

# Build the parallel GTFS site in output/html-gtfs.
gtfs:
	python3 -m euskotren_timetable.cli build-html \
		--source gtfs \
		--gtfs data/gtfs/gtfs_euskotren.zip \
		--output output/html-gtfs \
		--workbook output/euskotren_timetables_winter_2026_gtfs.xlsx \
		--workbook-name euskotren_timetables_winter_2026_gtfs.xlsx
