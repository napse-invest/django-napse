SHELL := /bin/bash

runserver:
	source .venv/bin/activate && python tests/test_app/manage.py runserver

celery:
	source .venv/bin/activate && watchfiles --filter python celery.__main__.main --args "-A tests.test_app worker --beat -l INFO"

test-napse:
	source .venv/bin/activate && python tests/test_app/manage.py test -v2

coverage:
	source .venv/bin/activate && coverage run tests/test_app/manage.py test -v2 --keepdb && coverage html && coverage report

coverage-open:
	source .venv/bin/activate && coverage run tests/test_app/manage.py test -v2 --keepdb && coverage html && coverage report && open htmlcov/index.html

