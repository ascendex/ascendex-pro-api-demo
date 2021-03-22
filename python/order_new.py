import os
import click
import requests
from pprint import pprint

# Local imports 
from util import *


@click.command()
@click.option("--account", type=click.Choice(['cash', 'margin']), default="cash")
@click.option("--symbol", type=str, default='BTC/USDT')
@click.option("--price", type=str, default='7000.0')
@click.option("--qty", type=str, default='0.00082')
@click.option("--order-type", type=str, default="limit")
@click.option("--side", type=click.Choice(['buy', 'sell']), default='buy')
@click.option("--resp-inst", type=click.Choice(['ACK', 'ACCEPT', 'DONE']), default="ACCEPT")
@click.option("--time-in-force", type=click.Choice(['GTC', 'IOC', 'IOO', 'FOK']), default="GTC")
@click.option("--config", type=str, default="config.json", help="path to the config file")
def run(account, symbol, price, qty, order_type, side, resp_inst, time_in_force, config):

    ascdex_cfg = load_config(get_config_or_default(config))['ascendex']

    host = ascdex_cfg['https']
    group = ascdex_cfg['group']
    apikey = ascdex_cfg['apikey']
    secret = ascdex_cfg['secret']

    url = f"{host}/{group}/api/pro/v1/{account}/order"

    ts = utc_timestamp()

    order = dict(
        id=uuid32(),
        time=ts,
        symbol=symbol.replace("-", "/"),
        orderPrice=str(price),
        orderQty=str(qty),
        orderType=order_type,
        side=side.lower(),
        timeInForce=time_in_force,
        respInst=resp_inst,
    )

    print("Place order {} through {}".format(order, url))

    headers = make_auth_headers(ts, "order", apikey, secret)
    res = requests.post(url, headers=headers, json=order)
    pprint(parse_response(res))


if __name__ == "__main__":
    run()
