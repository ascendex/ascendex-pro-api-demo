import os
import click
import requests
from pprint import pprint

# Local imports 
from util import *



@click.command()
@click.option("--account", type=click.Choice(['cash', 'margin']), default="cash", help="account category")
@click.option("--order-id", type=str, default=None)
@click.option("--config", type=str, default="config.json", help="path to the config file")
@click.option("--verbose/--no-verbose", default=False)
def run(account, order_id, config, verbose):

    ascdex_cfg = load_config(get_config_or_default(config))['ascendex']

    host = ascdex_cfg['https']
    group = ascdex_cfg['group']
    apikey = ascdex_cfg['apikey']
    secret = ascdex_cfg['secret']

    ts = utc_timestamp()
    headers = make_auth_headers(ts, "order/status", apikey, secret)
    url = f"{host}/{group}/api/pro/v1/{account}/order/status"
    params = dict(orderId = order_id)

    if verbose:
        print(f"Using url: {url}")
        print(f"params: {params}")

    res = requests.get(url, headers=headers, params=params)
    pprint(parse_response(res))


if __name__ == "__main__":
    run()
