SHELL := /bin/bash

makemigrations:
	source .venv/bin/activate && python tests/test_app/manage.py makemigrations

migrate:
	source .venv/bin/activate && python tests/test_app/manage.py migrate

runserver:
	source .venv/bin/activate && python tests/test_app/manage.py runserver_plus

up:
	make makemigrations && make migrate && make runserver

celery:
	source .venv/bin/activate && watchfiles --filter python celery.__main__.main --args "-A tests.test_app worker --beat -l INFO"

test:
	source .venv/bin/activate && python tests/test_app/manage.py test -v2 --keepdb --parallel

coverage:
	source .venv/bin/activate && coverage run tests/test_app/manage.py test -v2 --keepdb && coverage html && coverage report

coverage-open:
	source .venv/bin/activate && coverage run tests/test_app/manage.py test -v2 --keepdb && coverage html && coverage report && open htmlcov/index.html

reset-makemigrations:
	cd django_napse && find . -path "*/migrations/*.py" -not -name "__init__.py" -delete && find . -path "*/migrations/*.pyc"  -delete && cd .. && rm tests/test_app/db.sqlite3