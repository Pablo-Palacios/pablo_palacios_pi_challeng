import os
from dotenv import load_dotenv
from datetime import datetime
from binance.client import Client
import requests
import time
import hmac
import hashlib


load_dotenv()

api_key = os.getenv('TEST_BINANCE_KEY')
secret_key = os.getenv('TEST_BINANCE_SECRET')

client = Client(api_key,secret_key,testnet=True)

print(client.get_account())