SHELL := /bin/bash
.PHONY: setup
OS := $(shell uname)

all: setup-testing-environment makemigrations migrate runserver

setup:
ifeq ($(OS),Darwin)        # Mac OS X
	./setup/setup-osx.sh
else ifeq ($(OS),Linux)
	./setup/setup-unix.sh
else 
	powershell -NoProfile -ExecutionPolicy Bypass -File ".\setup\setup-windows.ps1"
endif

setup-testing-environment:
	cd tests/test_app && ./setup_secrets.sh

makemigrations:
	source .venv/bin/activate && python tests/test_app/manage.py makemigrations

migrate:
	source .venv/bin/activate && python tests/test_app/manage.py migrate

reset-makemigrations:
	cd django_napse && find . -path "*/migrations/*.py" -not -name "__init__.py" -delete && find . -path "*/migrations/*.pyc"  -delete && cd .. && rm tests/test_app/db.sqlite3

runserver:
	source .venv/bin/activate && python tests/test_app/manage.py runserver_plus

up:
	make makemigrations && make migrate && make runserver

clean:
	rm tests/test_app/db.sqlite3

celery:
	source .venv/bin/activate && watchfiles --filter python celery.__main__.main --args "-A tests.test_app worker --beat -l INFO" --verbosity info

shell:
	source .venv/bin/activate && python tests/test_app/manage.py shell

test:
	source .venv/bin/activate && python tests/test_app/manage.py test -v2 --keepdb --parallel

coverage:
	source .venv/bin/activate && coverage run tests/test_app/manage.py test -v2 --keepdb && coverage html && coverage report

coverage-open: coverage
	open htmlcov/index.html

mkdocs:
	source .venv/bin/activate && mkdocs serve --dev-addr=0.0.0.0:8005
