import os
import click
import requests
import numpy as np
from pprint import pprint

# Local imports
from util import *

@click.command()
@click.option("--asset", type=str, default=None, help="asset to query, optional")
@click.option("--user_id", type=str, default=None, help="user to query, optional")
@click.option("--start_time", type=int, default=None, help="start timestamp to query, optional")
@click.option("--end_time", type=int, default=None, help="end timestamp to query, optional")
@click.option("--page", type=int, default=1, help="page index")
@click.option("--page_size", type=int, default=10, help="number of record in one page")
@click.option("--config", type=str, default="config.json", help="path to the config file")
def run(asset, user_id, start_time, end_time, page, page_size, config):
    if config is None:
        config = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.json")
        print(f"Config file is not specified, use {config}")
    ascdex_cfg = load_config(config)['ascendex']

    host = ascdex_cfg['https']
    group = ascdex_cfg['group']
    apikey = ascdex_cfg['apikey']
    secret = ascdex_cfg['secret']

    json = dict(
        asset=asset,
        subUserId=user_id,
        startTime=start_time,
        endTime=end_time,
        page=page,
        pageSize=page_size
    )
    pprint(json)

    ts = utc_timestamp()
    headers = make_auth_headers(ts, "subuser-transfer-hist", apikey, secret)
    url = f"{host}/{group}/{ROUTE_PREFIX_V2}/subuser/subuser-transfer-hist"

    print(f"url = {url}")

    res = requests.post(url, headers=headers, json=json)
    pprint(parse_response(res))


if __name__ == "__main__":
    run()
