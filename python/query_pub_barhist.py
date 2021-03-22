import os 
import click
import requests
from pprint import pprint

# Local imports 
from util import *


@click.command()
@click.option("--symbol", type=str, default="BTC/USDT")
@click.option("--interval", type=str, default="1")
@click.option("--frm", type=int)
@click.option("--to", type=int)
@click.option("--n", type=int, default=10)
@click.option("--config", type=str, default="config.json")
def run(symbol, interval, frm, to, n, config):
    if config is None:
        config = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.json")
        print(f"Config file is not specified, use {config}")
    ascdexCfg = load_config(config)['ascendex']

    host = ascdexCfg['https']
  
    url = f"{host}/{ROUTE_PREFIX}/barhist"
    params = {
        "symbol":   symbol,
        "interval": interval,
        "n":        n,
        "from":     frm,
        "to":       to,
    }

    print(url)
    res = requests.get(url, params = params)
    pprint(parse_response(res))


if __name__ == "__main__": 
    run()  
