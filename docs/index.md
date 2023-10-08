

<h1 align="center">
<!-- ![test](theme/assets/images/NapseInvestLogoSVGWhite.png#only-light)
![test](theme/assets/images/NapseInvestLogoSVG.png#only-dark) -->

<picture>
  <source media="(prefers-color-scheme: light)" srcset="theme/assets/images/NapseInvestLogoSVGWhite.svg">
  <source media="(prefers-color-scheme: dark)" srcset="theme/assets/images/NapseInvestLogoSVG.svg">
  <img alt="Test" src="theme/assets/images/NapseInvestLogoSVGWhite.svg">
</picture>

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
<br/>



# Welcome to django-napse's documentation!

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
```shell
make mkdocs
```