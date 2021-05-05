import os
import click
import requests
from pprint import pprint

# Local imports
from util import *


@click.command()
@click.option("--config", type=str, default=None, help="path to the config file")
@click.option("--asset", default='BTC', type=str)
@click.option("--blockchain", type=str)
def run(config, asset, blockchain):
    cfg = load_config(get_config_or_default(config))['ascendex']

    host = cfg['https']
    apikey = cfg['apikey']
    secret = cfg['secret']

    url = f"{host}/api/pro/v1/wallet/deposit/address"
    params = dict(
        asset=asset,
        blockchain=blockchain
    )

    ts = utc_timestamp()
    headers = make_auth_headers(ts, "wallet/deposit/address", apikey, secret)

    res = requests.get(url, headers=headers, params=params)
    pprint(parse_response(res))


if __name__ == "__main__":
    run()
