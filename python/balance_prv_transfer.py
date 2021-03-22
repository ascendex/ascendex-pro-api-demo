import os
import click
import requests
import numpy as np
from pprint import pprint

# Local imports
from util import *


@click.command()
@click.option("--asset", type=str, default="USDT", help="asset to be transferred")
@click.option("--amount", type=float, default=11, help="amount to be transferred, will be rounded to 4th decimal places")
@click.option("--from_ac", type=str, default="cash", help="account to be transferred from")
@click.option("--to_ac", type=str, default="margin", help="account to be transferred to")
@click.option("--config", type=str, default="config.json", help="path to the config file")
def run(asset, amount, from_ac, to_ac, config):
    if config is None:
        config = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.json")
        print(f"Config file is not specified, use {config}")
    ascdex_cfg = load_config(config)['ascendex']

    host = ascdex_cfg['https']
    group = ascdex_cfg['group']
    apikey = ascdex_cfg['apikey']
    secret = ascdex_cfg['secret']

    amount = "%.4f" % np.round(np.float_(amount), 4)

    json = dict(
        fromAccount = from_ac,
        toAccount = to_ac,
        asset = asset,
        amount = amount,
    )
    pprint(json)

    ts = utc_timestamp()
    headers = make_auth_headers(ts, "transfer", apikey, secret)
    url = f"{host}/{group}/api/pro/transfer"

    print(f"url = {url}")

    res = requests.post(url, headers=headers, json=json)
    pprint(parse_response(res))


if __name__ == "__main__":
    run()
