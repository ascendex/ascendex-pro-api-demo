# This demo shows how to keep the most recent orderbook snapshot. 
# It keeps the entire orderbook in memory, and prints the current
# best bid/ask data every 5 seconds. 
#
# Please use Python 3.6 or higher
#
# This demo uses websocket_client for symplicity reasons:
# 
# * reference: https://pypi.org/project/websocket_client/
# * installation: pip install websocket_client
#
# You also need to install Sorted Container to construct the OrderBook
#
# * reference: http://www.grantjenks.com/docs/sortedcontainers/
# * installation: pip install sortedcontainers


import os
import click
import json
import websocket

try:
    import thread
except ImportError:
    import _thread as thread
from time import sleep
from sortedcontainers import SortedDict
from decimal import Decimal
from functools import partial

# Local imports 
from util import *



class OrderBook(object):
    def __init__(self):
        self.bids = SortedDict()
        self.asks = SortedDict()


def send(ws, msg):
    o = json.dumps(msg)
    print(f'> {o}')
    ws.send(o)


def print_progress(ws):
    print(f"bid levels = ${len(ws.orderbook.bids)}, ask levels = ${len(ws.orderbook.asks)}")


def update_orderbook(book, updates):
    for p, z in updates:
        px, sz = Decimal(p), Decimal(z)
        if sz > Decimal(0):
            book[px] = sz
        elif px in book and sz == Decimal(0):
            del book[px]
        else:
            print(f"unable to process update [{p}, {z}]")


def send_pong(ws):
    sub = dict(op="pong")
    send(ws, sub)


def sub_depth(ws):
    sub = dict(op="sub", ch=f"depth:{ws.symbol}")
    send(ws, sub)


def req_depth_snapshot(ws):
    req = dict(op="req", action='depth-snapshot', args=dict(symbol=ws.symbol))
    send(ws, req)


def on_message(ws, message):
    obj = json.loads(message)
    m = obj['m']
    if m == 'depth-snapshot':
        # Construct a new orderbook using the snapshot data
        bids = obj['data']['bids']
        asks = obj['data']['asks']
        print(f"received depth-snapshot with {len(bids)} bids and {len(asks)} asks")
        ws.orderbook.bids = SortedDict({Decimal(p): Decimal(z) for p, z in bids})
        ws.orderbook.asks = SortedDict({Decimal(p): Decimal(z) for p, z in asks})
    elif m == 'depth':
        # Update the orderbook using depth messages
        update_orderbook(ws.orderbook.bids, obj['data']['bids'])
        update_orderbook(ws.orderbook.asks, obj['data']['asks'])
        ws.msg_counter = ws.msg_counter + 1
    elif m == "ping":
        send_pong(ws)
    else:
        print(f"ignore message {m}")


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws, duration, prefix):
    def run(*args):
        sub_depth(ws)  # always subscribe to depth first
        sleep(1)

        req_depth_snapshot(ws)

        for _ in range(duration):
            sleep(1)
            bids = ws.orderbook.bids
            asks = ws.orderbook.asks
            best_bid = bids.peekitem(index=-1) if len(bids) > 0 else "NA"
            best_ask = asks.peekitem(index=0) if len(asks) > 0 else "NA"

            print(f"{prefix}Processed {ws.msg_counter:3d} depth updates:: " +
                  f"#bids {len(bids):<3d}, #asks {len(asks):<3d}, " +
                  f"best bid {best_bid}, best ask {best_ask}")
            ws.msg_counter = 0

        ws.close()
        print("thread terminating...")

    thread.start_new_thread(run, ())


@click.command()
@click.option("--symbol", type=str, default="BTC/USDT")
@click.option("--duration", type=int, default=1000, help="how long should the program run (in seconds)")
@click.option("--tag", type=str, default="", help="a tag to be printed for each message too boost readability")
@click.option("--config", type=str, default="config.json")
def run(symbol, duration, tag, config):
    if config is None:
        config = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.json")
        print(f"Config file is not specified, use {config}")
    ascdexCfg = load_config(config)['ascendex']

    wss = ascdexCfg['wss']
    grp = ascdexCfg['group']

    url = f"{wss}/{grp}/{ROUTE_PREFIX}/stream"
    print(f"connecting to {url}, symbol {symbol}")

    prefix = f"[{tag}] " if tag != "" else ""

    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    # hack the object for simplicity
    ws.symbol = symbol
    ws.msg_counter = 0
    ws.orderbook = OrderBook()

    ws.on_open = partial(on_open, duration=duration, prefix=prefix)
    ws.run_forever()


if __name__ == "__main__":
    run()
