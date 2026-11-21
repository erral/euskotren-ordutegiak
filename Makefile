.PHONY: format lint test

format:
	ruff format .
	ruff check --fix .

lint:
	ruff format --check .
	ruff check .

test:
	python3 -m unittest discover -s tests
