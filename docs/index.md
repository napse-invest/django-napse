
![Napse logo](theme/assets/napse_invest_logo_black.svg#only-light){ width="500" : .center}
![Napse logo](theme/assets/napse_invest_logo_white.svg#only-dark){ width="500" : .center}
<h1 align="center">

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

Django napse is a portfolio management module using trading bots.

## Installation
---

This project can be used as a django module, which you can install as follows:

```bash
pip install django-napse
```

Or you can use it as a local backend for the [Napse desktop application](https://github.com/napse-invest/Napse), by cloning the repo (possibly after forking it).

### Setup initial exchange accounts

To make full use of the project, we recommend that you fill in the API keys of at least one exchange (among the django-napse [compabile exchanges](#compatible-exchanges)).

At the root of your project, build a `secret.json` file. Here is an exemple with Binance:
```json
{
    "Exchange Accounts": {
        "Binance EA_NAME": {
            "exchange": "BINANCE",     # Name of your exchange
            "testing": true,
            "public_key": "YOUR_PUBLIC_KEY",
            "private_key": "YOUR_PRIVATE_KEY"
        }
    }
}
```
??? note "Note for developers"
    We **strongly recommend** to add the `secret.json` file to your `.gitignore` file to avoid sharing your API keys.

## Use django-napse
---

### Local backend

If you want to use django-napse as a local backend for the Napse desktop application, clone the repository and setup the project:
```bash
make setup
```
  
Then, you can run the server:
```bash
make up
```

Please check the documentation for more information about [endpoints](https://napse-invest.github.io/django-napse/api/).

### Django module

After the installation step, in a `.py` file you can use django-napse after importing it:
```python
from django_napse.core.models import ExchangeAccount

exchange_account_query = ExchangeAccount.objects.all()
```

## Miscellaneous
---

### Compatible exchanges

django-napse is compatible with a few exchanges (for now):

- [Binance](https://www.binance.com/en)