![badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/napse-investment/40fac957532fe3b731c99067467de842/raw/django-napse-coverage.json)

![badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/napse-investment/40fac957532fe3b731c99067467de842/raw/django-napse-version.json)

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