from pydantic import BaseModel
from typing import Optional
from faker import Faker
import cohere
from dotenv import load_dotenv
import os


load_dotenv() 

api_key = os.getenv("COHERE_API_KEY")
co = cohere.ClientV2()

faker = Faker()


class NewDocument(BaseModel):
    id: Optional[int]= faker.random_number(digits=3) 
    title: str
    content: str

class Embeddigns(BaseModel):
    document_id: int

class Chatbot(BaseModel):
    question: str


document_list: dict[int, NewDocument] = {}


def chat_ask(contexto,consulta):
    
    model_ = "command-r-plus"
    prompt = co.chat(
        model=model_,
        messages=[{"role":"system","content":f"""Eres un asistente vitual. 
                   Te proporcionare un contexto para tengas un mejor panorama: {contexto}.
                   Tu tarea es asociar la pregunta del usuario y el contexto generado, elaborando una respuesta
                   de una oracion que responda la pregunta del usuario. Si la pregunta no tiene ninguna similitud al contexto, responde 'No tengo conocimientos sobre ese tema'"""},
                  {"role":"user", "content":f"{consulta}"}]
    )

    return prompt.message.content[0].text

# TENER EN CUENTA QUE EL CONTEXTO DEBE ESTAR EN EL ROLE USER Y EL SYSTEM NO SE DEBE MODIFICAR

def chat_search(contexto,consulta):
    
    model_ = "command-r-plus"
    prompt = co.chat(
        model=model_,
        messages=[{"role":"system","content":f"""Eres un asistente vitual. 
                   Te proporcionare un contexto para tengas un mejor panorama: {contexto}.
                   Tu tarea es asociar la pregunta del usuario, el contexto generado y buscar en la lista {document_list} el titulo y su id.
                   La respuesta debe ser el titulo, el document_id del documento y la primera frase en el content_snippet con el formato de diccionario como esta en la lista con sus keys y su contenido.
                   Si la pregunta no tiene ninguna similitud al contexto, responde 'No tengo conocimientos sobre ese tema'"""},
                  {"role":"user", "content":f"{consulta}"}]
    )

    return prompt.message.content[0].text

def convertir_embeddings(texto):
    response = co.embed(
                    texts=[texto],
                    model="embed-multilingual-v3.0",
                    input_type="search_document",
                    embedding_types=["float"]
                )

    return response.embeddings.float_