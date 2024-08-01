test:
	pytest -s -l -vvv tests/

test-cov:
	pytest -s -l -vvv tests/ --cov tests/ --cov-fail-under=85 --cov-report term:skip-covered

style:
	black ./ --line-length=120
	isort ./

check-code:
	isort --check-only stratix_framework/ tests/ \
	&& black --check stratix_framework/ tests/ \
	&& mypy stratix_framework/ tests/ \
	&& pylint stratix_framework/ tests/
