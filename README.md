# Evmos.me Backend

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
