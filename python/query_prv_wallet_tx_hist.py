import os
import click
import requests
from pprint import pprint

# Local imports
from util import *


@click.command()
@click.option("--config", type=str, default=None, help="path to the config file")
@click.option("--asset", type=str)
@click.option("--page", type=int)
@click.option("--page-size", type=int)
@click.option("--txType", type=click.Choice(["deposit", "withdrawal"]), default=None,
              help="transaction type, deposit/withdrawal/both, default is both")
@click.option('--verbose/--no-verbose', default=False)
def run(config, asset, page, page_size, txtype, verbose):
    cfg = load_config(get_config_or_default(config))['ascendex']

    host = cfg['https']
    apikey = cfg['apikey']
    secret = cfg['secret']

    url = f"{host}/api/pro/v1/wallet/transactions"
    params = dict(
        asset=asset,
        page=page,
        pageSize=page_size,
        txType=txtype,
    )

    ts = utc_timestamp()
    headers = make_auth_headers(ts, "wallet/transactions", apikey, secret)

    if verbose:
        print(f"url = {url}")
        print(f"params = {params}")

    res = requests.get(url, headers=headers, params=params)
    pprint(parse_response(res))


if __name__ == "__main__":
    run()
