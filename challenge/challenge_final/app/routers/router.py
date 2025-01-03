import json
from fastapi import APIRouter,HTTPException,UploadFile,File,Form
from models.model import NewDocument,Embeddigns,document_list,convertir_embeddigns,chat_ask,chat_search,co,Chatbot,faker,chat_cripto,chat_asistente_data,chat_asistente_personal
from models.config import collection
from langchain_text_splitters import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
import redis

router = APIRouter()

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


@router.post("/upload")
async def add_document(new_docu: NewDocument):
    if new_docu.title == '' or new_docu.content == '':
        raise HTTPException(status_code=403,detail="Los campos no pueden estar vacios")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
    chuncks = text_splitter.split_text(new_docu.content)
    
    docu = NewDocument(title=new_docu.title, content=chuncks[0])
    document_list[new_docu.id] = docu
    #print(document_list)
    return {"message":"Document upload success", "document_id":new_docu.id}


@router.post("/upload_pdf")
async def add_document(title: str = Form(...), file: UploadFile = File(...)):
    
    if not title or not file:
        raise HTTPException(status_code=403, detail="Los campos no pueden estar vacíos")

     
    reader = PdfReader(file.file)

    text_ = ""
    for page in reader.pages:
        text_ += page.extract_text()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=0)
    chuncks = text_splitter.split_text(text_)
    id = faker.random_number(digits=3)
    docu = {"id":id,"title":title,"content":chuncks[0]}
    
    redis_client.set(f"document:{id}", json.dumps(docu))
    #document_list[docu.id] = docu

    return {"message": "PDF uploaded successfully", "title": title, "document_id":id}



@router.post("/generate_embeddings")
async def generate_embeddings(embeddings_docu: Embeddigns):
    document_id = embeddings_docu.document_id
    key_redis = f"document:{document_id}"
    doc_data= redis_client.get(key_redis)
    document = json.loads(doc_data)
   
    
    if document is None:
        raise HTTPException(status_code=404, detail="Document id no encontrado")
    else:
        texto = document["content"]
        embeddings = convertir_embeddigns(texto)

        collection.add(
            documents=texto,
            ids=str(document_id),
            embeddings=embeddings)
                    
        return {"message":f"Create and add embeddings for document {document_id}", "title_document":document["title"]}

@router.post("/generate_embeddings_all")
async def generate_embeddings_all():
   
    cursor = 0
    keys_to_process = []

    while True:
        cursor, keys = redis_client.scan(cursor=cursor, match="document:*", count=100)
        keys_to_process.extend(keys)
        if cursor == 0:
            break

    if not keys_to_process:
        raise HTTPException(status_code=404, detail="No hay documentos en Redis.")

    processed_documents = 0
    for key in keys_to_process:
        doc_data = redis_client.get(key)
        if doc_data:
            document = json.loads(doc_data)
            document_id = key.split(":")[1]  
            texto = document.get("content", "")

            if not texto:
                continue

            embeddings = convertir_embeddigns(texto)
            #print(embeddings)

            collection.add(
                documents=texto,
                ids=str(document_id),
                embeddings=embeddings
            )

            processed_documents += 1

    return {
        "message": f"Se generaron embeddings para {processed_documents} documentos.",
        "total_documents": processed_documents
    }
    
@router.post("/ask")
async def ask_llm(question: Chatbot):
    if question.question == '':
        raise HTTPException(status_code=403,detail="Los campos no pueden estar vacios")
    ask_ = question.question
    
    chat = chat_cripto(ask_)
    if chat == 'No tengo conocimientos sobre ese tema.':
        raise HTTPException(status_code=404, detail=chat)
    else:
        return {"answer":chat}


@router.post("/search")
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

    if chat == 'No tengo conocimientos sobre ese tema.':
        raise HTTPException(status_code=404, detail=chat)
    else:
        return {"result":[chat]}



@router.post("/add_data_user")
async def data_user(data: Chatbot):
    if data.question == '':
        raise HTTPException(status_code=403,detail="Los campos no pueden estar vacios")
    else:
        chat = chat_asistente_data(data.question)
        if chat == "Faltan los siguientes campos obligatorios" in str(chat):
            raise HTTPException(status_code=404, detail=chat)
        else:
            return {"answer":chat}


@router.post("/assist_personal")
async def assist_personal(data: Chatbot):
    if data.question == '':
        raise HTTPException(status_code=403,detail="Los campos no pueden estar vacios")
    else:
        chat = chat_asistente_personal(data.question)
        if chat == "Faltan los siguientes campos obligatorios" in str(chat):
            raise HTTPException(status_code=404, detail=chat)
        else:
            return {"answer":chat}
        
@router.post("/traiding_bot")
async def trading_bot(data: Chatbot):
    pass