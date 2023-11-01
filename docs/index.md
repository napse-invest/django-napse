
![Napse logo](theme/assets/napse_invest_logo_black.svg#only-light)
![Napse logo](theme/assets/napse_invest_logo_white.svg#only-dark)

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

## Installation

To install the latest version of django-napse:
```bash
pip install django-napse
```

### Setup initial exchange accounts

To make full use of the project, we recommend that you fill in the API keys of at least one exchange (among the django-napse [compabile exchanges](#compatible-exchanges)).

At the root of your project, build a `secret.json` file. Here is an exemple with Binance:
```json
{
    "Exchange Accounts": {
        "Binance EA_NAME": {
            "exchange": "BINANCE",     # Name of your exchange (BINANCE, DYDX, ...)
            "testing": true,
            "public_key": "YOUR_PUBLIC_KEY",
            "private_key": "YOUR_PRIVATE_KEY"
        }
    }
}
```
We **strongly** recommand you to add the `secret.json` file to your `.gitignore`.


## Use django-napse

After the installation step, in a `.py` file you can use django-napse after importing it:
```python
from django_napse.core.models import ExchangeAccount

exchange_account_query = ExchangeAccount.objects.all()
```

## Miscellaneous

### Compatible exchanges

django-napse is compatible with a few exchanges (for now):

- [Binance]()