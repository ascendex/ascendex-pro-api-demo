import click
import requests
from pprint import pprint

# Local imports
from util import *


@click.command()
@click.option("--account", type=click.Choice(['cash', 'margin', 'futures']), default="cash",
              help="cash, margin or futures")
@click.option("--date", default=None, help="if date YYYY-mm-dd is not None, get snapshot")
@click.option("--start_offset", default=None, help="if start_offset is not None, get history from start_offset")
@click.option("--config", type=str, default="config_prod15.json", help="path to the config file")
@click.option("--verbose/--no-verbose", default=True)
def run(account, date, start_offset, config, verbose):

    btmx_cfg = load_config(get_config_or_default(config))['bitmax']

    host = btmx_cfg['https']
    apikey = btmx_cfg['apikey']
    secret = btmx_cfg['secret']

    ts = utc_timestamp()

    ## get balannce snapshot
    if date is not None:
        headers = make_auth_headers(ts, "balance/snapshot", apikey, secret)
        url = f"{host}/api/pro/v1/data/balance/snapshot"
        params = dict(account=account, date=date)

        if verbose:
            print(f"Using url: {url}")
            print(f"params: {params}")

        res = requests.get(url, headers=headers, params=params)
        json = parse_response(res)
        print(json)
        last_offset = json['meta']['sn']
        pprint(json)
        print(last_offset)
    elif start_offset is not None:
        next_offset = start_offset
        ## query delta by
        headers = make_auth_headers(ts, "balance/history", apikey, secret)
        url = f"{host}/api/pro/v1/data/balance/history"
        params = dict(account=account, startOffset=next_offset)

        if verbose:
            print(f"Using url: {url}")
            print(f"params: {params}")

        res = requests.get(url, headers=headers, params=params)
        pprint(parse_response(res))


if __name__ == "__main__":
    run()
