.PHONY: format lint test workbook html

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
