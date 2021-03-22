import os
import click
import requests
from pprint import pprint

# Local imports 
from util import *


def get_hist_orders(base_url, apikey, secret, symbol, start_time, end_time, order_type, side,
                    method="order/hist/current"):
    ts = utc_timestamp()
    url = "{}/{}".format(base_url, method)
    headers = make_auth_headers(ts, method, apikey, secret)
    params = {"symbol": symbol, "startTime": start_time, "endTime": end_time, "orderType": order_type, "side": side}
    return requests.get(url, headers=headers, params=params)


def get_open_orders(base_url, apikey, secret, symbol, method="order/open"):
    ts = utc_timestamp()
    url = "{}/{}".format(base_url, method)
    headers = make_auth_headers(ts, method, apikey, secret)
    params = {"symbol": symbol}
    return requests.get(url, headers=headers, params=params)


def get_order_status(base_url, apikey, secret, order_id, method="order/status"):
    url = "{}/{}".format(base_url, method, order_id)
    print(url)
    ts = utc_timestamp()
    headers = make_auth_headers(ts, method, apikey, secret)
    return requests.get(url, headers=headers, params={"orderId": order_id})


@click.command()
@click.option("--account", type=click.Choice(['cash', 'margin']), default="cash")
@click.option("--symbol", type=str, default='BTC/USDT')
@click.option("--start_time", type=int, default=0)
@click.option("--end_time", type=int, default=utc_timestamp())
@click.option("--order_type", type=str, default=None)  # "market" or "limit"
@click.option("--side", type=click.Choice(['buy', 'sell']), default=None)
@click.option("--order_id", type=str, default=None)
@click.option("--config", type=str, default="config_local.json", help="path to the config file")
def run(account, symbol, start_time, end_time, order_type, side, config, order_id):

    ascdex_cfg = load_config(get_config_or_default(config))['ascendex']

    host = ascdex_cfg['https']
    group = ascdex_cfg['group']
    apikey = ascdex_cfg['apikey']
    secret = ascdex_cfg['secret']

    base_url = f"{host}/{group}/{ROUTE_PREFIX}/{account}"

    print("Get history orders")
    res = get_hist_orders(base_url, apikey, secret, symbol, start_time, end_time, order_type=order_type, side=side)
    pprint(parse_response(res))

    print("\n ****** \n")
    print("Get open orders")
    res = get_open_orders(base_url, apikey, secret, None)
    pprint(parse_response(res))

    if order_id is not None:
        print("\n ****** \n")
        print(f"Query status for order {order_id}")
        res = get_order_status(base_url, apikey, secret, order_id)
        pprint(parse_response(res))


if __name__ == "__main__":
    run()
