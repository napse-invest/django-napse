#!/bin/bash


if [ -f .env ]; then
    export $(xargs < .env)
else
    cat << EOF > .env
BINANCE_PUBLIC_KEY=
BINANCE_PRIVATE_KEY=
EOF
    echo "Please fill in the .env file with your API keys."
fi
if [ ! -f secrets.json ]; then
    cat << EOF > secrets.json
{
    "Exchange Accounts": {}
}
EOF
fi

python3 << EOF
import json
with open('secrets.json', 'r') as f:
    secrets = json.load(f)
    secrets['Exchange Accounts']['BINANCE Test Account'] = {
        'exchange': 'BINANCE',
        'testing': True,
        'public_key': '$BINANCE_PUBLIC_KEY',
        'private_key': '$BINANCE_PRIVATE_KEY'
    }
with open('secrets.json', 'w') as f:
    json.dump(secrets, f, indent=4)
EOF
