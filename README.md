<h1 align="center">
<img src="./branding/napse_black.svg" />
</h1><br>

<p align="center">
  <a href="https://twitter.com/NapseInvest">
    <img src="https://img.shields.io/twitter/follow/NapseInvest?style=flat&label=%40NapseInvest&logo=twitter&color=0bf&logoColor=fff" alt="Twitter" />
  </a>
  <a>
    <img src="https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/napse-investment/40fac957532fe3b731c99067467de842/raw/django-napse-coverage.json" alt="Coverage" />
  </a>
  <a>
    <img src="https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/napse-investment/40fac957532fe3b731c99067467de842/raw/django-napse-version.json" alt="Version" />
  </a>
</p>


<p align="center">
  <a href="#django-napse"><strong>Django Napse</strong></a> ·
</p>
<br/>

# django-napse
...

# Usefull commands
Unless otherwise specified, all commands are to be run at the root folder of the project.

## Create a new project
- Unix \
```source setup-unix.sh```

- Windows \
```.\setup-windows.ps1```

## Run a test version of the project

```python test/test_app/manage.py makemigrations``` \
```python test/test_app/manage.py migrate``` \
```python test/test_app/manage.py runserver```

## Run coverage tests

```coverage run test/test_app/manage.py test -v2 --keepdb && coverage html && open ~/<path_to_project>/django-napse/htmlcov/index.html```