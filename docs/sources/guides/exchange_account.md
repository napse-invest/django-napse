# Exchange account

An exchange account is directly link to an `Exchange`. First, you must retrieve the `Exchange` of your choice. To have the full list of available exchanges:
```python
from django_napse.core.models import Exchange
all_exchanges = Exchange.objects.all()
```


### Get the exchange
For the remainder of this guide, we will assume that the BINANCE exchange is in your database.

```python
from django_napse.core.models import Exchange
binance_exchange = Exchange.objects.get(name = "BINANCE")
```

### Build a new BINANCE exchange account

```python
from django_napse.core.models import ExchangeAccount

new_binance_exchange_account = ExchangeAccount.objects.create(
                                    exchange=binance_exchange,
                                    testing=True
                                    name="binance_test_exchange_account",
                                    description="This is a test exchange account for Binance."
                                    )
```