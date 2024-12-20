import requests


def get_top_10_coins():
    api_cohere = "https://api.binance.com"
    endpoint = "/api/v3/ticker/24hr"
    response = requests.get(api_cohere + endpoint)
    
    if response.status_code == 200:
        tickers = response.json()
        
        volume_per_coin = {}

        for ticker in tickers:
            
            symbol = ticker["symbol"]
            base_asset = symbol[:-3]  
            quote_asset = symbol[-3:]  
            
            if quote_asset in ["BTC", "USDT", "ETH"]:  
                volume = float(ticker["quoteVolume"])  
                
                if base_asset in volume_per_coin:
                    volume_per_coin[base_asset] += volume
                else:
                    volume_per_coin[base_asset] = volume
        
        sorted_coins = sorted(volume_per_coin.items(), key=lambda x: x[1], reverse=True)
        
        top_10_coins = sorted_coins[:10]
        
        result = []
        for coin, volume in top_10_coins:
            result.append(f"Moneda: {coin}, Volumen Total: {volume}")

        return "\n".join(result)
        
        #return top_10_coins
    else:
        print("Error al obtener los datos:", response.status_code)
        return None
    

#print(get_top_10_coins())

def especifict_coint_valor(criptomoneda, moneda): 

    url = "https://api.coingecko.com/api/v3/simple/price"

    param = {
        "ids":f"{criptomoneda}",
        "vs_currencies": f"{moneda}"
    }

    response = requests.get(url, params=param)

    if response.status_code == 200:
        data = response.json()
        return data
        #print(data)  # Imprime los precios actuales
    else:
        return ("Error:", response.status_code)