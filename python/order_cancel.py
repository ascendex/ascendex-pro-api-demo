import os 
import click
import requests
from pprint import pprint

# Local imports 
from util import *


def cancel_order(order, apikey, secret, base_url, method="order"):
    url = "{}/{}".format(base_url, method)
    ts = utc_timestamp()
    headers = make_auth_headers(ts, method, apikey, secret)
    return requests.delete(url, headers=headers, json=order)


def cancel_batch_order(orders, apikey, secret, base_url, method="order/batch"):
    url = "{}/{}".format(base_url, method)
    ts = utc_timestamp()
    batch_order = {"orders": orders}
    headers = make_auth_headers(ts, method, apikey, secret)
    return requests.delete(url, headers=headers, json=batch_order)


def test_cancel_batch_order(api_key, secret, base_url):
    ts = utc_timestamp()
    order1 = dict(
        id=uuid32(),
        orderId="16e61d5ff43s8bXHbAwwoqDo9d817339",
        time=ts,
        symbol="BTC/USDT",
    )

    order2 = dict(
        coid=uuid32(),
        origCoid="16e61adeee5a8bXHbAwwoqDo100e364e",
        time=ts,
        symbol='ETH/USDT',
    )

    res = cancel_batch_order([order1, order2], api_key, secret, base_url)
    pprint(parse_response(res))


@click.command()
@click.option("--account", type=click.Choice(['cash', 'margin']), default="cash")
@click.option("--order_id", type=str, default="a16ef5d5de48U9490877774NG1IhX3jK", help="order id (provided by server when placing order) to cancel")
@click.option("--symbol", type=str, default='BTC/USDT')
@click.option("--resp_inst", type=click.Choice(['ACK', 'ACCEPT', 'DONE']), default="ACCEPT")
@click.option("--config", type=str, default="config.json", help="path to the config file")
def run(account, order_id, symbol, resp_inst, config):

    ascdex_cfg = load_config(get_config_or_default(config))['ascendex']

    host = ascdex_cfg['https']
    group = ascdex_cfg['group']
    apikey = ascdex_cfg['apikey']
    secret = ascdex_cfg['secret']

    base_url = f"{host}/{group}/{ROUTE_PREFIX}/{account}"

    ts = utc_timestamp()
    order = dict(
        id=uuid32(),
        orderId=order_id,
        time=ts,
        symbol=symbol.replace("-", "/"),
        respInst=resp_inst,
    )

    print("Cancel order {}".format(order))
    res = cancel_order(order, apikey=apikey, secret=secret, base_url=base_url, method="order")
    pprint(parse_response(res))


if __name__ == "__main__":
    run()
