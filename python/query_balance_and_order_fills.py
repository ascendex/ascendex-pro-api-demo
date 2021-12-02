import click
import requests
from pprint import pprint

# Local imports
from util import *


@click.command()
@click.option("--account", type=click.Choice(['cash', 'margin', 'futures']), default="cash",
              help="cash, margin or futures")
@click.option("--date", default=None, help="if date YYYY-mm-dd is not None, get snapshot")
@click.option("--start_sn", default=sys.maxsize, help="if start_sn is not None, get history from start_sn")
@click.option("--config", type=str, default="conf.json", help="path to the config file")
@click.option("--verbose/--no-verbose", default=True)
def run(account, date, start_sn, config, verbose):

    btmx_cfg = load_config(get_config_or_default(config))['bitmax']

    host = btmx_cfg['https']
    apikey = btmx_cfg['apikey']
    secret = btmx_cfg['secret']

    ts = utc_timestamp()

    ## get balannce snapshot
    if date is not None:
        auth_method = f"data/v1/{account}/balance/snapshot"
        headers = make_auth_headers(ts, auth_method, apikey, secret)
        url = f"{host}/api/pro/data/v1/{account}/balance/snapshot"
        params = dict(date=date)

        if verbose:
            print(f"Using url: {url}")
            print(f"params: {params}")

        res = requests.get(url, headers=headers, params=params)
        json = parse_response(res)
        print(json)
        last_offset = json['meta']['sn']
        pprint(json)
        print(last_offset)
        # next with last_offset + 1 as 'start_sn' ('sn' in api request param) to call balance/history
        # ......
    elif start_sn is not None:
        next_sn = start_sn
        ## query delta by

        auth_method = f"data/v1/{account}/balance/history"
        headers = make_auth_headers(ts, auth_method, apikey, secret)
        url = f"{host}/api/pro/data/v1/{account}/balance/history"
        params = dict(sn=next_sn, limit=10)

        if verbose:
            print(f"Using url: {url}")
            print(f"params: {params}")

        res = requests.get(url, headers=headers, params=params)
        pprint(parse_response(res))


if __name__ == "__main__":
    run()
