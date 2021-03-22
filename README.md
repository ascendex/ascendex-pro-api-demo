# AscendEx Pro API Demo 

Before running demo scripts, please make sure you create a new file `config.json` and put in your API key and secret. You can use `config.json_template` as a template. 

Please refer to signature_demo for api signature.

## Command line Tools

- **Place New Order**
```
python3 python/order_new.py --symbol BTC/USDT --price 50000 --qty 0.0001 --order-type limit --side buy
```
- **Query All Open Orders**
```
python3 python/query_prv_open_orders.py --symbol BTC/USDT
```

- **Cancel All Open Orders**
```
python3 python/order_cancel_all.py --symbol BTC/USDT
```