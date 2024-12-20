import requests
from bs4 import BeautifulSoup


URL = "https://www.coindesk.com"


def get_info_crypto():
    try:
        response_url = requests.get(URL)

        if response_url.status_code == 200:
            soup = BeautifulSoup(response_url.content, "html.parser")

            new_titles = soup.find_all("div", class_="card-title")

            for i,item in enumerate(new_titles[:5], start=1):
                title = item.get_text(strip=True)
                print(f"{i}. {title}")
        else:
            print(f"Code: {response_url.status_code}")
    except Exception as e:
        print(f"error: {e}")
            

def get_crypto_news():
    try:
        # Realizamos la solicitud HTTP para obtener el HTML
        response = requests.get(URL)
        
        # Verificamos si la solicitud fue exitosa
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            print(soup.prettify()) 
            
            # Extraer las noticias usando las clases o etiquetas HTML (depende del sitio)
            news_items = soup.find_all("h3", class_="heading")  # Clase específica para títulos
            
            # Mostrar los títulos de noticias
            print("Últimas noticias sobre criptomonedas:")
            for i, item in enumerate(news_items[:5], start=1):  # Mostramos las 5 primeras noticias
                title = item.get_text(strip=True)
                print(f"{i}. {title}")
        else:
            print(f"Error {response.status_code}: No se pudo acceder a la página")
    
    except Exception as e:
        print(f"Hubo un error: {e}")



print(get_crypto_news())


 # Imprime el HTML completo
