import os
from dotenv import load_dotenv
from datetime import datetime
from binance.client import Client
import requests
import time
import hmac
import hashlib


load_dotenv()

xrp = 'XRPUSDT'

api_key = os.getenv('TEST_BINANCE_KEY')
secret_key = os.getenv('TEST_BINANCE_SECRET')

client = Client(api_key,secret_key,testnet=True)

def data_account_client():
    return client.get_account()

def data_account_xrp():
    cli = client.get_account()
    for x in cli['balances']:
        xrp_ = x['asset']
        if xrp_ == 'XRP':
            return x
        

def get_current_price(symbol):
    ticket = client.get_symbol_ticker(symbol = symbol)
    return float(ticket['price'])


def place_buy_order(symbol,quantity):
    order = client.order_market_buy(symbol=symbol, quantity=quantity)
    print(f"Buy order done: {order}")


def place_sell_order(symbol,quantity):
    order = client.order_market_sell(symbol=symbol,quantity=quantity)
    print(f"Sell order done: {order}")


#print(get_current_price('XRPUSDT'))
#print(place_buy_order(xrp,quantity=10))

#print(place_sell_order(xrp,quantity=10))

#print(data_account_client())
#print(data_account_xrp())