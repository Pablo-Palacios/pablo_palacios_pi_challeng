import requests

url = "https://api.coingecko.com/api/v3/simple/price"

param = {
    "ids":"Ripple",
    "vs_currencies": "usd"
}

response = requests.get(url, params=param)

if response.status_code == 200:
    data = response.json()
    print(data)  # Imprime los precios actuales
else:
    print("Error:", response.status_code)