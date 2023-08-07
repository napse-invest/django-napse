#!/bin/bash


if [ -f .env ]; then
    export $(xargs < .env)
fi

cat << EOF > secrets.json
{
    "Exchange Accounts": {
        "BINANCE Test Account": {
            "exchange": "BINANCE",
            "testing": true,
            "public_key": "$BINANCE_PUBLIC_KEY",
            "private_key": "$BINANCE_PRIVATE_KEY"
        }
    }
}
EOF
