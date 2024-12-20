import chromadb
import redis
from faker import Faker
import json
from pydantic import BaseModel
from typing import Optional


chroma_client = chromadb.Client()

collection = chroma_client.create_collection(name="db_vectoral_test1")

faker = Faker()

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


class User(BaseModel):
    nombre: Optional[str]
    edad: int
    ingreso_fijo: int
    ahorro: int

    
def query_vector(pregunta_embeddings):
    response = collection.query(
        query_embeddings=pregunta_embeddings,
        n_results=4
    )

    return response["documents"][0][0]




def add_data_user(nombre,edad,ingreso_fijo,ahorro):
    id_user= faker.random_number(digits=3)
    user_data = {"nombre":nombre, 
                 "edad":edad, 
                  "ingreso_fijo":ingreso_fijo,
                  "ahorro":ahorro
                  }
    user= User(nombre=nombre, edad=edad,ingreso_fijo=ingreso_fijo,ahorro=ahorro)
    redis_client.set(f"user_data:{user.nombre}", json.dumps(user_data))
    return {"message":"User data add success"}


def get_data_user(nombre):
    key_redis = f"user_data:{nombre}"
    doc_data= redis_client.get(key_redis)
    user = json.loads(doc_data)

    return user


def guardar_chat_ask(role="",content=""):
    chat = {"role":role, "content":content}
    redis_client.rpush(f"chat_assistan:ask", json.dumps(chat))

def guardar_chat_personal(role="",content=""):
    chat = {"role":role, "content":content}
    redis_client.rpush(f"chat_assistan:personal", json.dumps(chat))