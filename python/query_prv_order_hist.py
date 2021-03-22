
import click
import requests
from pprint import pprint

# Local imports
from util import *

def get_hist_orders(base_url, apikey, secret, category, symbol, start_time, end_time, order_type, side,
                    method="order/hist"):
    ts = utc_timestamp()
    url = "{}/{}".format(base_url, method)
    print(url)
    headers = make_auth_headers(ts, method, apikey, secret)
    params = {"category": category, "startTime": start_time, "endTime": end_time, "orderType": order_type, "side": side}
    return requests.get(url, headers=headers, params=params)

def get_hist_save_orders(base_url, apikey, secret, category, symbol, start_time, end_time, order_type, side,
                    method="order/histSave"):
    ts = utc_timestamp()
    url = "{}/{}".format(base_url, method)
    print(url)
    headers = make_auth_headers(ts, method, apikey, secret)
    params = {"symbol": symbol, "category": category, "startTime": start_time, "endTime": end_time, "orderType": order_type, "side": side}
    return requests.get(url, headers=headers, params=params)

def get_hist_upload(base_url, apikey, secret, symbol, method="order/histUpload"):
    ts = utc_timestamp()
    url = "{}/{}".format(base_url, method)
    print(url)
    headers = make_auth_headers(ts, method, apikey, secret)
    params = {"symbol": symbol, "category": "MARGIN"}
    return requests.get(url, headers=headers, params=params)

@click.command()
@click.option("--account", type=click.Choice(['cash', 'margin', 'futures']), default=None)
@click.option("--symbol", type=str, default=None)
@click.option("--start_time", type=int, default=0)
@click.option("--end_time", type=int, default=utc_timestamp())
@click.option("--order_type", type=str, default=None)  # "market" or "limit"
@click.option("--side", type=click.Choice(['buy', 'sell']), default=None)
@click.option("--config", type=str, default="config.json", help="path to the config file")
def run(account, symbol, start_time, end_time, order_type, side, config):

    ascdex_cfg = load_config(get_config_or_default(config))['ascendex']

    host = ascdex_cfg['https']
    group = ascdex_cfg['group']
    apikey = ascdex_cfg['apikey']
    secret = ascdex_cfg['secret']

    base_url = f"{host}/{group}/{ROUTE_PREFIX}"

    print("Get history orders")
    res = get_hist_orders(base_url, apikey, secret, account, symbol, start_time, end_time, order_type=order_type, side=side)
    pprint(parse_response(res))

    # print("Get history save orders")
    # res = get_hist_save_orders(base_url, apikey, secret, account, symbol, start_time, end_time, order_type=order_type, side=side)
    # pprint(parse_response(res))
    #
    # print("Get history upload ")
    # res = get_hist_upload(base_url, apikey, secret, symbol)
    # pprint(parse_response(res))

if __name__ == "__main__":
    run()
