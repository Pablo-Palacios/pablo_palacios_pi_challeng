from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from typing import List
import os
import json
import chromadb
import cohere
from dotenv import load_dotenv
import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter
from faker import Faker
from typing import Optional




load_dotenv() 

api_key = os.getenv("COHERE_API_KEY")
co = cohere.ClientV2()
chroma_client = chromadb.Client()


collection = chroma_client.create_collection(name="db_historias_api")
app = FastAPI()
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


def query_vector(pregunta_embeddings):
    response = collection.query(
        query_embeddings=pregunta_embeddings,
        n_results=1
    )

    return response["documents"][0][0]




@app.post("/upload")
def add_document(new_docu: NewDocument):
    if new_docu.title == '' or new_docu.content == '':
        raise HTTPException(status_code=403,detail="Los campos no pueden estar vacios")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
    chuncks = text_splitter.split_text(new_docu.content)
    
    docu = NewDocument(title=new_docu.title, content=chuncks[0])
    document_list[new_docu.id] = docu
    #print(document_list)
    return {"message":"Document upload success", "document_id":new_docu.id}

@app.post("/generate_embeddings")
def generate_embeddings(embeddings_docu: Embeddigns):
    document_id = embeddings_docu.document_id
    document = document_list.get(document_id, None)
                
    if document is None:
        raise HTTPException(status_code=404, detail="Document id no encontrado")
    else:
        texto = document.content
        embeddings = convertir_embeddings(texto)

        collection.add(
            documents=texto,
            ids=str(document_id),
            embeddings=embeddings)
                    
        return {"message":f"Create and add embeddings for document {document_id}"}

            
    
@app.post("/ask")
def ask_llm(question: Chatbot):
    if question.question == '':
        raise HTTPException(status_code=403,detail="Los campos no pueden estar vacios")
    ask_ = question.question
    response = co.embed(
                    texts=[ask_],
                    model="embed-multilingual-v3.0",
                    input_type="search_document",
                    embedding_types=["float"]
                )

    question_embeddings = response.embeddings.float_
    
    response = collection.query(
        query_embeddings=question_embeddings,
        n_results=1
    )

    context = response["documents"][0][0]
    
    chat = chat_ask(context, question)
    if chat == 'No tengo conocimientos sobre ese tema':
        raise HTTPException(status_code=404, detail=chat)
    else:
        return {"answer":chat}


@app.post("/search")
def search_llm(question: Chatbot):
    if question.question == '':
        raise HTTPException(status_code=403,detail="Los campos no pueden estar vacios")
    search = question.question
    response = co.embed(
                    texts=[search],
                    model="embed-multilingual-v3.0",
                    input_type="search_document",
                    embedding_types=["float"]
                )
    search_embeddings = response.embeddings.float_
    response = collection.query(
        query_embeddings=search_embeddings,
        n_results=1
    )

    context = response["documents"][0][0]

    chat = chat_search(context,question)

    if chat == 'No tengo conocimientos sobre ese tema':
        raise HTTPException(status_code=404, detail=chat)
    else:
        return {"result":[chat]}