import os
import click
import requests
from pprint import pprint

# Local imports 
from util import *


@click.command()
@click.option("--symbol", type=str, default="BTC/USDT")
@click.option("--n", type=int, default=10, help="number of records to request")
@click.option("--config", type=str, default="config.json")
def run(symbol, n, config):

    ascdex_cfg = load_config(get_config_or_default(config))['ascendex']

    host = ascdex_cfg['https']

    url = f"{host}/{ROUTE_PREFIX}/trades"
    params = dict(symbol=symbol, n=n)

    res = requests.get(url, params=params)
    pprint(parse_response(res))


if __name__ == "__main__":
    run()
