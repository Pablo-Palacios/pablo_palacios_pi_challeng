from langchain_text_splitters import RecursiveCharacterTextSplitter

from PyPDF2 import PdfReader
# Lectura y extraccion de contenido de pdf hacia un objeto en python

import chromadb

chroma_client = chromadb.Client()

collection = chroma_client.create_collection(name="db_historias_api")

reader = PdfReader('Guia-de-Criptomonedas.pdf')

#print(len(reader.pages))

text_=""
for x in range(len(reader.pages)):
    page = reader.pages[x]
    text_ += page.extract_text()


text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
chuncks = text_splitter.split_text(text_)


