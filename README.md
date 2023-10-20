<h1 align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/napse-invest/Napse/blob/main/desktop-app/renderer/public/images/NapseInvestLogoSVGWhite.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/napse-invest/Napse/blob/main/desktop-app/renderer/public/images/NapseInvestLogoSVG.svg">
  <img alt="Napse's logo" src="" width=500>
</picture>

<!-- <img src="./branding/napse_white.svg" width=500/> -->
</h1><br>

<p align="center">
  <a href="https://twitter.com/NapseInvest">
    <img src="https://img.shields.io/twitter/follow/NapseInvest?style=flat&label=%40NapseInvest&logo=twitter&color=0bf&logoColor=fff" alt="Twitter" />
  </a>
  <a>
    <img src="https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/napse-investment/40fac957532fe3b731c99067467de842/raw/django-napse-coverage.json" alt="Coverage" />
  </a>
  <a>  
    <img src="https://img.shields.io/github/v/release/napse-invest/django-napse" alt="Release" />
  </a>
</p>

<p align="center">
  <a href="#django-napse"><strong>Django Napse</strong></a> ·
  <a href="#usefull-commands"><strong>Usefull commands</strong></a> .
  <a href="#how-to-contribute"><strong>How to contribute</strong></a>
</p>
<br/>

## django-napse
....

## Useful commands
Unless otherwise specified, all commands are to be run at the root folder of the project.

### Create a new project
- Unix \
```source setup-unix.sh```

- Windows \
```.\setup-windows.ps1```

### Run a test version of the project

- Build migrations \
```make makemigrations```
- Apply migrations \
```make migrate``` 
- Run server \
```make runserver```

### Run coverage tests

- Run tests \
```test-napse```
- Run tests with coverage \
```coverage```
- Run tests with coverage and open coverage report \
```coverage-open```

## Documentation

[Docs](https://napse-invest.github.io/django-napse/)

Run mkdocs server:
```
make mkdocs
```