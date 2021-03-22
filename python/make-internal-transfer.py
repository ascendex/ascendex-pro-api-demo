import os
import click
import requests
from pprint import pprint

# Local imports 
from util import *


@click.command()
@click.option("--uid", type=str, required=True)
@click.option("--asset", type=str, required=True)
@click.option("--amount", type=str, required=True)
@click.option("--config", type=str, default="config_local.json", help="path to the config file")
@click.option("--verbose/--no-verbose", default=False)
def run(uid, asset, amount, config, verbose):

    ascdex_cfg = load_config(get_config_or_default(config))['ascendex']

    host = ascdex_cfg['https']
    apikey = ascdex_cfg['apikey']
    secret = ascdex_cfg['secret']

    url = f"{host}/api/pro/v1/wallet/withdraw/internal"
    body = dict(uid=uid, asset=asset, amount=amount)

    if verbose:
        print(f"url: {url}")

    ts = utc_timestamp()
    headers = make_auth_headers(ts, f"wallet/withdraw/internal+{uid}", apikey, secret)

    res = requests.post(url, headers=headers, json=body)
    pprint(parse_response(res))

    
if __name__ == "__main__":
    run()
