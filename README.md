![coverage](https://github.com/napse-invest/django-napse/blob/dev/badges/coverage.svg)

# django-napse

### Usefull commands
Unless otherwise specified, all commands are to be run at the root folder of the project.
#### Create a new project
- Unix \
```source setup-unix.sh```

- Windows \
```.\setup-windows.ps1```

#### Run a test version of the project

```python test/test_app/manage.py makemigrations``` \
```python test/test_app/manage.py migrate``` \
```python test/test_app/manage.py runserver```

#### Run coverage tests

```coverage run test/test_app/manage.py test -v2 --keepdb && coverage html && open ~/<path_to_project>/django-napse/htmlcov/index.html```