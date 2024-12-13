from fastapi import APIRouter,HTTPException
from models.model import NewDocument,Embeddigns,document_list,convertir_embeddings,chat_ask,chat_search,co,Chatbot
from models.config import collection
from langchain_text_splitters import RecursiveCharacterTextSplitter


router = APIRouter()

@router.post("/upload")
def add_document(new_docu: NewDocument):
    if new_docu.title == '' or new_docu.content == '':
        raise HTTPException(status_code=403,detail="Los campos no pueden estar vacios")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
    chuncks = text_splitter.split_text(new_docu.content)
    
    docu = NewDocument(title=new_docu.title, content=chuncks[0])
    document_list[new_docu.id] = docu
    #print(document_list)
    return {"message":"Document upload success", "document_id":new_docu.id}

@router.post("/generate_embeddings")
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

            
    
@router.post("/ask")
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