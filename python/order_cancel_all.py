import os 
import click
import json
import requests
from pprint import pprint

# Local imports 
from util import *


@click.command()
@click.option("--account", type=click.Choice(['cash', 'margin']), default="cash")
@click.option("--symbol", type=str, default="BTC/USDT", help="if not provided, cancel all orders.")
@click.option("--config", type=str, default="config.json", help="path to the config file")
def run(account, symbol, config):

    ascdex_cfg = load_config(get_config_or_default(config))['ascendex']

    host = ascdex_cfg['https']
    group = ascdex_cfg['group']
    apikey = ascdex_cfg['apikey']
    secret = ascdex_cfg['secret']

    method = "order/all"

    url = f"{host}/{group}/{ROUTE_PREFIX}/{account}/{method}"
    print(f"User url: {url}")

    params = dict(symbol = symbol)
    print(f"User params: {params}")

    ts = utc_timestamp()
    headers = make_auth_headers(ts, method, apikey, secret)

    res = requests.delete(url, headers=headers, json=params)
    pprint(parse_response(res))


if __name__ == "__main__":
    run()
