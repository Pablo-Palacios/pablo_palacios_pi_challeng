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
    order = client.order_market_buy(symbol=symbol, quantity=float(quantity))
    symbol_ = order["symbol"]
    data_order = order["fills"][0]
    price = data_order["price"]
    commission = data_order["commission"]
    commissionAsset = data_order["commissionAsset"]

    mjs = f"Buy done success: Coint: {symbol_} - Price_coint: {price} - Commission: {commission} - CommissionAsset: {commissionAsset}"

    return mjs


def place_sell_order(symbol,quantity):
    order = client.order_market_sell(symbol=symbol,quantity=quantity)
    print(f"Sell order done: {order}")


def get_coints_active_account():
    cli = client.get_account()
    list_coint = []
    for x in cli['balances']:
        free = float(x["free"])
        locked = float(x["locked"])

        if free > 0 or locked > 0:
            list_coint.append({
                "asset": x["asset"],
                "free": free,
                "locked": locked
            })

    return list_coint

def get_transaction_coint(symbol):
    client_ = client.get_my_trades(symbol=symbol)
    trade = client_[-1]
    
    mjs = {
        "coint":trade["symbol"],
        "order_id":trade["orderId"],
        "quantity_order":trade["qty"],
        "price_coint":trade["price"],
        "confirm_order":trade["isBuyer"],
        "total_coint":trade["quoteQty"]
    }

    return mjs
    
    

def get_all_trade_coint(symbol):
    cli = client.get_all_orders(symbol=symbol)

    trade = cli[0]
    print(trade)
    #qty = trade["qty"]

    

#print(get_transaction_coint(xrp))