import requests
from bs4 import BeautifulSoup
import json
import re

# URL de la página
url = "https://www.coindesk.com"

# Realizar la solicitud HTTP
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Buscar el script que contiene los datos JSON
script_tag = soup.find("script", string=re.compile(r"mostReadArticles"))

if script_tag:
    # Extraer el contenido del script
    script_content = script_tag.string
    
    # Buscar y extraer la parte del JSON dentro del script
    json_match = re.search(r"mostReadArticles\":(\[.*?\])", script_content)
    if json_match:
        articles_json = json_match.group(1)
        
        # Convertir el JSON a un diccionario Python
        articles = json.loads(articles_json)
        
        # Imprimir los artículos encontrados
        for article in articles:
            title = article.get("title")
            description = article.get("description")
            author = article.get("authorDetails", [{}])[0].get("byline", "N/A")
            image_url = article.get("__featuredImages", [{}])[0].get("source", {}).get("src")
            
            print(f"Title: {title}")
            print(f"Description: {description}")
            print(f"Author: {author}")
            print(f"Image URL: {image_url}")
            print("-" * 80)
else:
    print("No se encontró el script con los datos JSON.")
