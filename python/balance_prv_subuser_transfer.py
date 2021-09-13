import os
import click
import requests
import numpy as np
from pprint import pprint

# Local imports
from util import *

@click.command()
@click.option("--asset", type=str, default="USDT", help="asset to be transferred")
@click.option("--amount", type=float, default=11,
              help="amount to be transferred")
@click.option("--user_from", type=str, default="cash", help="user to transfer from")
@click.option("--user_to", type=str, default="cash", help="user to transfer to")
@click.option("--ac_from", type=str, default="cash", help="account to transfer from")
@click.option("--ac_to", type=str, default="cash", help="account to transfer to")
@click.option("--ack_mode", type=str, default="ack", help="ack/accept mode")
@click.option("--config", type=str, default="config.json", help="path to the config file")
def run(asset, amount, user_from, user_to, ac_from, ac_to, ack_mode,config):
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
        userFrom=user_from,
        userTo=user_to,
        acFrom=ac_from,
        acTo=ac_to,
        asset=asset,
        amount=amount,
	mode=ack_mode,
    )
    pprint(json)

    ts = utc_timestamp()
    headers = make_auth_headers(ts, "subuser-transfer", apikey, secret)
    url = f"{host}/{group}/{ROUTE_PREFIX_V2}/subuser/subuser-transfer"

    print(f"url = {url}")

    res = requests.post(url, headers=headers, json=json)
    pprint(parse_response(res))


if __name__ == "__main__":
    run()
