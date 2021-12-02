from abc import ABCMeta
import asyncio
import collections
import sys
import json
import logging
import numpy as np
import time
from urllib.parse import urlparse
import uuid

from autobahn.asyncio.websocket import WebSocketClientFactory
from autobahn.asyncio.websocket import WebSocketClientProtocol

# Local imports 
from util import *


#logger = log.get_logger()

GROUP_ID = 1
API_KEY = "BclE7dBGbS1AP3VnOuq6s8fJH0fWbH7r"
SECRET = "fAZcQRUMxj3eX3DreIjFcPiJ9UR3ZTdgIw8mxddvtcDxLoXvdbXJuFQYadUUsF7q"

SANDBOX_URL = f"wss://ascendex-test.io:443/{GROUP_ID}/{ROUTE_PREFIX}/stream"

Channels = ['order', 'trades', 'ref-px', 'bar', 'summary', 'depth', 'bbo']

OrderInfo = collections.namedtuple('Order', ['symbol', 'px', 'qty', 'order_type', 'order_side', 'post_only'])


def get_message_topic(message):
    if 'm' in message:
        return message['m']
    elif 'message' in message:
        return message['message']
    else:
        return None


class ClientProtocol(WebSocketClientProtocol):

    def __call__(self, *args, **kwargs):
        return self

    def setName(self, name):
        self.name = name

    def onConnect(self, response):
        print(response)

    def onOpen(self):
        self.factory.on_open()

    def onClose(self, wasClean, code, reason):
        self.factory.on_close(wasClean, code, reason)

    def onMessage(self, payload, isBinary):
        try:
            msg = json.loads(payload.decode('utf8'))
            topic = get_message_topic(msg)
            if topic == 'error':
                self.factory.on_error(msg['m'], msg.get('reason', ''))
            elif topic in ['pong', 'sub', 'connected', 'unsub', 'auth']:
                logging.debug(msg)
            else:
                self.factory.on_message(msg)
        except :
            logging.error("Unexpected error:", sys.exc_info())
            logging.error("ignore message {}".format(payload))


class Client(WebSocketClientFactory):
    def __init__(self, loop, feed_url=SANDBOX_URL,
                 auth=False, key='', secret='', passphrase='',
                 auto_connect=True, auto_reconnect=True,
                 name='WebSocket Client'):
        self.loop = loop
        self.connected = asyncio.Event()
        self.disconnected = asyncio.Event()
        self.disconnected.set()
        self.closing = False

        self.feed_url = feed_url

        self.subscribers = {}

        if auth and not (key and secret and passphrase):
            raise ValueError('auth requires key, secret, and passphrase')

        self.auth = auth
        self.key = key
        self.secret = secret
        self.passsphrase = passphrase

        self.auto_connect = auto_connect
        self.auto_reconnect = auto_reconnect
        self.name = name

        super().__init__(self.feed_url)

        if self.auto_connect:
            self.add_as_task_to_loop()

    def utc_timestamp(self):
        tm = time.time()
        return int(tm * 1e3)

    def authenticate(self):
        max_try = 0
        while not self.connected.is_set():
            time.sleep(1)
            max_try += 1
            if max_try > 10:
                break

        if self.connected.is_set():
            ts = self.utc_timestamp()
            sig = make_auth_headers(ts, "stream", self.key, self.secret)['x-auth-signature']
            msg = json.dumps(dict(op="auth", id=self.get_uuid()[:6], t=ts, key=self.key, sig=sig)).encode('utf8')
            logging.info(f">>> {msg}")
            self.protocol.sendMessage(msg)
        else:
            logging.error("websocket isn't active")

    def _get_subscribe_message(self, channel, symbols, unsubscribe=False, timestamp=None):
        msg_type = 'unsub' if unsubscribe else 'sub'
        msg = {
            'op': msg_type,
            'ch': '{}:{}'.format(channel, symbols)
        }
        logging.debug(msg)
        return json.dumps(msg).encode('utf8')

    def _send_subscribe(self, symbol, channel, unsubscrible=False):

        if self.connected.is_set():
            msg = self._get_subscribe_message(channel, symbol, unsubscribe=unsubscrible)
            print(msg)
            self.protocol.sendMessage(msg)

    def subscribe(self, topic_id, channel):
        """ subscribe a symbol/account to channel """
        self._send_subscribe(topic_id, channel)

    def unsubscribe(self, topic_id, channel):
        """ unsubscribe a symbol/account from channel """
        self._send_subscribe(topic_id, channel, True)

    def ping_pong(self):
        """ ping pong to keep connection live """
        if self.connected.is_set():
            msg = json.dumps({'op': 'ping'}).encode('utf8')
            logging.debug(msg)
            self.protocol.sendMessage(msg)

    def add_as_task_to_loop(self):
        """
        creates a coroutine for making a connection to the WebSocket server and adds it as a task to the asyncio loop.
        """
        self.protocol = ClientProtocol()
        self.protocol.setName(self.name)
        url = urlparse(self.url)
        self.coro = self.loop.create_connection(self, url.hostname, url.port,
                                                ssl=(url.scheme == 'wss'))
        self.loop.create_task(self.coro)

    def on_open(self):
        """
        callback fired on initial WebSocket opening handshake completion.
        """
        self.connected.set()
        self.disconnected.clear()
        self.closing = False

    def on_close(self, wasClean, code, reason):
        self.connected.clear()
        self.disconnected.set()
        self.closing = True
        logging.info(reason)

    def on_error(self, message, reason):
        logging.error(f'{message}: {reason}')

    def on_message(self, message):
        """
        callback fired when a complete WebSocket message was received.
        You usually need to override this method to consume the data.

        :param dict message: message dictionary.
        """
        logging.debug(message)
        topic = get_message_topic(message)

        if 'symbol' in message:
            topic_id = message['symbol']
        elif 'accountId' in message:
            topic_id = message['accountId']
        else:
            logging.error(f"unhandled message ${message}")
            return
        if 'data' in message:
            data = message['data']
        elif 'info' in message:
            data = message['info']
        elif topic in ['bar', 'summary']:
            data = message
        else:
            logging.error(f"no data info: ${message}")
            return

        self.publish_data(topic, topic_id, data)

    def publish_data(self, channel, id, data):
        subscribers = self.subscribers.setdefault(channel, dict()).setdefault(id, set())
        for subscriber in subscribers:
            subscriber.update(channel, id, data)

    def get_products(self):
        """ get exchange supported product list
        TODO: fake now. Refer to query_pub_products.py
        """
        return ['BTC/USDT', 'ETH/USDT', 'ETC/USDT', 'PAX/USDT', 'EOS/USDT', 'XRP/USDT', 'ETH/BTC']

    def get_channels(self):
        """ get all supported sub/unsub channels """
        return Channels

    def bar_snapshot(self):
        """ take bar snapshot """
        pass

    def depth_snapshot(self, symbol):
        """ take depth snapshot """
        req = {
            'op': 'req',
            'action': 'depth-snapshot',
            'args': {
                'symbol': '{}'.format(symbol)
            }
        }

        logging.info('depth snapshot: {}'.format(req))
        self.protocol.sendMessage(json.dumps(req).encode('utf8'))

    def trade_snapshot(self, symbol):
        """ take trade snapshot """
        req = {
            'op': 'req',
            'action': 'trade-snapshot',
            'args': {
                'symbol': '{}'.format(symbol),
                'level': 12
            }
        }

        logging.info('trade snapshot: {}'.format(req))
        self.protocol.sendMessage(json.dumps(req).encode('utf8'))

    def place_new_order(self, symbol, px, qty, order_type, order_side, post_only=False, resp_inst='ACK'):
        """
        Place a new order via websocket

        :param symbol: product symbol
        :param px: order price
        :param qty: order size
        :param order_type: limit or market
        :param order_side: buy or sell
        :param post_only: if postonly
        :param resp_inst: 'ACK', 'ACCEPT', or 'DONE'
        :return: user generated coid for this order
        """
        order_msg = {
            'op': 'req',
            'action': 'place-Order',
            'args': {
                'time': self.utc_timestamp(),
                'coid': self.get_uuid(),
                'symbol': symbol,
                'orderPrice': str(px),
                'orderQty': str(qty),
                'orderType': order_type,
                'side': order_side,
                'postOnly': post_only,
                'respInst': resp_inst
            }
        }
        logging.info('Place new order: {}'.format(order_msg))
        self.protocol.sendMessage(json.dumps(order_msg).encode('utf8'))
        return order_msg['args']['coid']

    def cancel_order(self, coid, symbol):
        """
        Cancel an existing order via websocket

        :param coid: server returned order id
        :param symbol: cancel target symbol
        :return:
        """
        cancel_msg = {
            'op': 'req',
            'action': 'cancel-Order',
            'args': {
                'time': self.utc_timestamp(),
                'coid': self.get_uuid(),
                'origCoid': coid,
                'symbol': symbol,
            }
        }
        logging.info('To cancel order: {}'.format(cancel_msg))
        self.protocol.sendMessage(json.dumps(cancel_msg).encode('utf8'))
        return cancel_msg['coid']

    def cancel_all_orders(self, symbol=None):
        """
        Cancel all open orders.

        :param symbol: optional
        :return:
        """
        cancel_msg = {
            'op': 'req',
            'action': 'cancel-All',
            'args': {
                'time': self.utc_timestamp(),
                'symbol': symbol
            }
        }

        logging.info("Cancel all order")
        self.protocol.sendMessage(json.dumps(cancel_msg).encode('utf8'))

    def gen_order(self):
        """ generate some random order """
        symbol = np.random.choice(list(self.get_products()))
        px = round(100 * (1 + (np.random.uniform() - 0.5) * 0.02), 6)
        qty = round(max(1000./px, 0.01), 6)
        order_type = np.random.choice(['market', 'limit'])
        order_side = np.random.choice(['buy', 'sell'])
        post_only = [True, False][np.random.choice([0, 1])]
        return OrderInfo(symbol, px, qty, order_type, order_side, post_only)

    def get_uuid(self):
        return uuid.uuid4().hex

    def subscribe_subs(self, subscriber, channel, id):
        """
        subscribe
        :param subscriber: subscriber object
        :param channel:  subscribe channel: order, trades, and so on
        :param id: symbol or account id, depending on channel
        :return:
        """
        channel_data = self.subscribers.setdefault(channel, dict())
        subscribers = channel_data.setdefault(id, set())
        subscribers.add(subscriber)
        self.subscribe(id, channel)


class Subscriber(metaclass=ABCMeta):
    """
    A simple data consumer
    """
    def __init__(self, client):
        self.client = client

    def update(self, channel, id, data):
        pass

    def subscribe(self, channel, id):
        pass


class Strategy(Subscriber):
    """
    A simple data driving simulator
    """
    def __init__(self, client):
        super().__init__(client)
        self.data_cache = {}
        self.last_trade_px = {}
        self.avg_px = {}
        self.last_bbo = {}

    def update(self, channel, id, data):
        self.process(channel, id, data)

    def subscribe(self, channel, id):
        self.client.subscribe_subs(self, channel, id)

    def process(self, channel, id, data):
        {
            'order': self.process_order,
            'bbo': self.process_bbo,
            'trades': self.process_trades,
            'summary': self.process_summary,
            'bar': self.process_bar
        }.setdefault(channel, self.process_dummy)(id, data)

    def process_trades(self, id, data):
        pass

    def process_bbo(self, id, data):
        bbo_med = (float(data['bid'][0]) + float(data['ask'][0]))/2
        avg_px = self.avg_px.setdefault(id, 0)
        if avg_px > 0 and (bbo_med - avg_px) / avg_px > 0.1:
            px = bbo_med
            qty = max(100/px, 0.123)
            self.place_new_order(id, px, qty, 'limit', 'buy')
        elif avg_px < 0 and (bbo_med - avg_px) / avg_px < -0.1:
            px = bbo_med
            qty = max(100 / px, 0.123)
            self.place_new_order(id, px, qty, 'limit', 'sell')
        elif np.random.uniform() > 0.8:
            px = bbo_med
            qty = max(100 / px, 0.123)
            order_type = np.random.choice(['market', 'limit'])
            order_side = np.random.choice(['buy', 'sell'])
            post_only = [True, False][np.random.choice([0, 1])]
            resp_inst = "DONE" if order_type == 'market' else "ACK"
            self.place_new_order(id, px, qty, order_type, order_side, post_only, resp_inst)

    def process_order(self, id, data):
        """ consuming order data """
        print(f"order update: {id} => {data}")

    def process_summary(self, id, data):
        """ consuming summary data """
        print("summary {} => {}".format(id, data))

    def process_bar(self, id, data):
        """ consuming bar data """
        if data['intervalName'] == '1d':
            px_fields = ['openPrice', 'closePrice', 'highPrice', 'lowPrice']
            self.avg_px[data['symbol']] = (
                sum(float(data[px_field]) for px_field in px_fields) / 4
            )

    def process_dummy(self, id, data):
        """ just drop data """
        logging.debug(f"Skip processing data {id} => {data}")

    def place_new_order(self, symbol, px, qty, order_type, order_side, post_only=False, resp_inst='ACK'):
        logging.info(f"Place new order for {symbol}")
        self.client.place_new_order(symbol, px, qty, order_type, order_side, post_only, resp_inst)


def run_simulation(url=SANDBOX_URL, api_key=API_KEY, secret=SECRET):
    logging.info("run " + str(id))
    loop = asyncio.get_event_loop()
    ws = Client(loop, feed_url=url, key=api_key, secret=secret, name="instance" + str(id))

    strategy = Strategy(ws)

    async def ping():
        # ping to keep live
        while True:
            await asyncio.sleep(50)
            ws.ping_pong()

    loop.create_task(ping())

    async def to_run():
        await asyncio.sleep(1)
        ws.authenticate()

        # subscribe to order update
        ws.subscribe("cash", ["order"])

        # subscribe to all kinds of data channel
        for symbol in ['BTC/USDT', 'ETH/USDT', 'EOS/USDT', 'XRP/USDT', 'ETH/BTC', 'LTC/BTC', 'BNB/BTC',
                       'EOS/ETH', 'XRP/ETH']:
            strategy.subscribe("summary", symbol)
            strategy.subscribe("trades", symbol)
            strategy.subscribe("bbo", symbol)
            strategy.subscribe("bar", symbol)

    loop.create_task(to_run())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(ws.close())
        loop.close()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    run_simulation()
