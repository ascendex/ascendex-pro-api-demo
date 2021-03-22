import os
import click
import requests
from pprint import pprint

# Local imports 
from util import *


@click.command()
@click.option("--asset", type=str, default=None,
              help='optional, if none, return all assets with non-empty balance. You can specify an asset (e.g. "BTC")')
@click.option("--account", type=click.Choice(['cash', 'margin']), default="cash", help="cash (default) or margin")
@click.option("--show-all/--no-show-all", default=False, help="show all balances, including empty balances")
@click.option("--config", type=str, default="config.json", help="path to the config file")
@click.option("--verbose/--no-verbose", default=False)
def run(asset, account, show_all, config, verbose):

    ascdex_cfg = load_config(get_config_or_default(config))['ascendex']

    host = ascdex_cfg['https']
    group = ascdex_cfg['group']
    apikey = ascdex_cfg['apikey']
    secret = ascdex_cfg['secret']

    ts = utc_timestamp()
    headers = make_auth_headers(ts, "balance", apikey, secret)
    url = f"{host}/{group}/{ROUTE_PREFIX}/{account}/balance"
    params = dict(asset=asset, showAll=show_all)

    if verbose:
        print(f"Using url: {url}")
        print(f"params: {params}")

    res = requests.get(url, headers=headers, params=params)
    pprint(parse_response(res))


if __name__ == "__main__":
    run()
