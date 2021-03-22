# This demo uses autobahn.asyncio
# 
# https://autobahn.readthedocs.io/en/latest/reference/autobahn.asyncio.html

import os
import asyncio
import datetime
from urllib.parse import urlparse
import uuid

import click
from autobahn.asyncio.websocket import WebSocketClientFactory
from autobahn.asyncio.websocket import WebSocketClientProtocol

# Local imports 
from util import *


SUCCESS = 0


class ClientProtocol(WebSocketClientProtocol):

    def __call__(self, *args, **kwargs):
        return self

    def onOpen(self):
        self.factory.on_open()

    def onClose(self, wasClean, code, reason):
        self.factory.on_close(wasClean, code, reason)

    def onMessage(self, payload, isBinary):
        try:
            msg = json.loads(payload.decode('utf8'))
            if msg['m'] == 'error':
                self.factory.on_error(msg['m'], msg.get('reason', ''))
            elif msg['m'] == 'auth':
                if msg.get('code', -1) == SUCCESS:
                    self.factory.auth = True
            else:
                self.factory.on_message(msg)
            print("<<< received message {}".format(payload))
        except:
            print("<<< ignore message {}".format(payload))


class Client(WebSocketClientFactory):
    def __init__(self, loop, feed_url, key='', secret=''):
        self.name = "AscendEx-WebSocket"
        self.loop = loop
        self.connected = asyncio.Event()
        self.disconnected = asyncio.Event()
        self.disconnected.set()
        self.closing = False

        self.feed_url = feed_url

        if not (key and secret):
            raise ValueError('auth requires key, secret')

        self.auth = False
        self.key = key
        self.secret = secret

        super().__init__(self.feed_url)

        self.connect()

    def utc_timestamp(self):
        tm = datetime.datetime.utcnow().timestamp()
        return int(tm * 1e3)

    def authenticate(self):
        if self.connected.is_set():
            ts = self.utc_timestamp()
            msg = f"{ts}+stream"
            sig = sign(msg, self.secret)
            msg = json.dumps(dict(op="auth", id=self.get_uuid()[:6], t=ts, key=self.key, sig=sig)).encode('utf8')
            print(f">>> {msg}")
            self.protocol.sendMessage(msg)
        else:
            print("websocket isn't active")

    def connect(self):
        self.protocol = ClientProtocol()
        url = urlparse(self.url)
        self.coro = self.loop.create_connection(self, url.hostname, url.port, ssl=(url.scheme == 'wss'))
        self.loop.create_task(self.coro)

    def on_open(self):
        self.connected.set()
        self.disconnected.clear()
        self.closing = False

    def on_close(self, wasClean, code, reason):
        self.connected.clear()
        self.disconnected.set()
        self.closing = True
        print(reason)

    def on_message(self, message):
        print(f"<<< {message}")

    async def close(self):
        pass

    def get_uuid(self):
        return uuid.uuid4().hex


@click.command()
@click.option("--config", type=str, default=None)
def run(config):
    if config is None:
        config = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.json")
        print(f"Config file is not specified, use {config}")
    ascdexCfg = load_config(config)['ascendex']

    host = ascdexCfg['wss']
    group = ascdexCfg['group']
    apikey = ascdexCfg['apikey']
    secret = ascdexCfg['secret']

    url = f"{host}/{group}/{ROUTE_PREFIX}/stream"

    loop = asyncio.get_event_loop()

    ws = Client(loop, feed_url=url, key=apikey, secret=secret)

    async def actions():
        while not ws.connected.is_set():
            await asyncio.sleep(1)
        ws.authenticate()

        await asyncio.sleep(5)
        if not ws.auth:
            print("Failed to authenticate the web-socket session, exit.")
            loop.stop()
        else:
            print("Authentication is successful.")

        # ** your code goes here **

        await asyncio.sleep(1)
        print("All done!")
        os._exit(0)

    loop.create_task(actions())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(ws.close())
        loop.close()


if __name__ == '__main__':
    run()
