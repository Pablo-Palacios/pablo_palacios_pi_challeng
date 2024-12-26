from dotenv import load_dotenv
import os
import tweepy
import tweepy.client

load_dotenv()

api_key = os.getenv("TWITTER_API_KEY")
api_secret = os.getenv("TWITTER_KEY_SECRET")
bearer_token= os.getenv("TWITTER_BEARER_TOKEN")


def tweets_account(username):
    client = tweepy.Client(bearer_token=bearer_token)

    # Obtener el ID del usuario
    user = client.get_user(username=username)
    user_id = user.data.id

    # Obtener los tweets aplicando filtros
    tweets = client.get_users_tweets(
        id=user_id, 
        max_results=10, 
        tweet_fields=["id", "text"], 
        exclude=["replies"]
    )

    # Filtrar manualmente los tweets según los criterios
    for tweet in tweets.data:
        if "-is:retweet" not in tweet.text and "-has:media" not in tweet.text:
            print(f"{tweet.id}: {tweet.text}")


def tweets_especific():
    client = tweepy.Client(bearer_token=bearer_token)

    query = f"#XRP OR Ripple lang:en -is:retweet -has:media"

    tweets = client.search_recent_tweets(query=query, max_results=10) 

    for tweet in tweets.data:
        print(f"{tweet.id}: {tweet.text}")


# print(tweets_account(username="SergioCanales"))
# print(tweets_account(username="pablogoofy_27"))
# print(tweets_account(username="DrJStrategy"))


import requests


# Endpoint de búsqueda reciente de Twitter
url = "https://api.twitter.com/2/tweets/search/recent"

# Función para obtener tweets de una cuenta específica
def get_tweets_from_account(username, max_results=10):
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }
    params = {
        "query": f"from:{username}",  # Filtrar tweets del usuario específico
        "max_results": max_results,
        "tweet.fields": "created_at,text"
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        tweets = response.json()
        for tweet in tweets.get("data", []):
            print(f"{tweet['created_at']}: {tweet['text']}")


#print(get_tweets_from_account(username="pablogoofy_27"))
#print(get_tweets_from_account(username="SergioCanales"))
#print(get_tweets_from_account(username="DrJStrategy"))