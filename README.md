# Evmos.me Backend

NOTE: this repo was archived, the changes after the hackatom were made in a private repo to avoid scams to just deploy a similar website.

Most of the javascript functions were moved to [evmosjs](https://github.com/tharsis/evmosjs). The new evmos.me version doesn't use a backend to proxy to node responses

A `#HackAtom` 2021 project: a wallet integration for evmos.

## Requirements

- Evmos endpoints for `gprc`
- `Python3`

## Usage

```python
pip install -r requirements.txt
python main.py
```

## Usage with env variables

```bash
WEB3_ENDPOINT=https://evmos-testnet.gateway.pokt.ne
twork/v1/lb/61afa495a6f4fb0039968571 GRPC_ENDPOINT=10.128.0.33:9090 CHAIN_ID=evmos_9000-2 python main.py
```

## TODO

List all the env variables that can be set:

- FRONTEND_WEBPAGE: (Allowed origin) default = "\*"
