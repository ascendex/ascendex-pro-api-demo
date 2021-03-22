import os
import click
import requests
from pprint import pprint

# Local imports 
from util import *


@click.command()
@click.option("--symbol", type=str,
              help="If not provided, return tickers of all symbols. You can provide one or more symbols, "
                   "use comma to separate multiple symbols.")
@click.option("--config", type=str, default="config.json")
def run(symbol, config):

    ascdexCfg = load_config(get_config_or_default(config))['ascendex']

    host = ascdexCfg['https']

    url = f"{host}/{ROUTE_PREFIX}/ticker"
    params = dict(symbol=symbol)
    print(url)
    print(params)

    res = requests.get(url, params=params)
    pprint(parse_response(res))


if __name__ == "__main__":
    run()
