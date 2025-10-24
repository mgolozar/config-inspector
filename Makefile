.PHONY: format lint e2e test run watch

format:
	ruff check --select I --fix . || true

lint:
	ruff check .
	test -f pyproject.toml && mypy src || true

e2e:
	python -m config_validator --path examples --report report.json

test:
	pytest  --cov=src --cov-report=term-missing

run:
	python -m config_validator --path . --report report.json

watch:
	python -m config_validator --path . --watch