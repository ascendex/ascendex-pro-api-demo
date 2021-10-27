import os
import click
import requests
from pprint import pprint

# Local imports 
from util import *


@click.command()
@click.option("--feecat", type=click.Choice(["spot", "futures"]), default="generic", help="generic (default) or futures")
@click.option("--info/--products", default=False)
@click.option("--config", type=str, default="config.json", help="path to the config file")
@click.option("--verbose/--no-verbose", default=False)
def run(feecat, info, config, verbose):

    ascdex_cfg = load_config(get_config_or_default(config))['ascendex']

    host = ascdex_cfg['https']
    group = ascdex_cfg['group']
    apikey = ascdex_cfg['apikey']
    secret = ascdex_cfg['secret']

    ts = utc_timestamp()
    headers = make_auth_headers(ts, "fee", apikey, secret)
    url = f"{host}/{group}/{ROUTE_PREFIX}/{feecat}/fee"
    if info:
        url += "/info"

    if verbose:
        print(f"Using url: {url}")
        #print(f"params: {params}")

    res = requests.get(url, headers=headers, params=[])
    pprint(parse_response(res))


if __name__ == "__main__":
    run()
