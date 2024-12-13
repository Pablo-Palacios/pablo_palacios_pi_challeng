import chromadb

chroma_client = chromadb.Client()

collection = chroma_client.create_collection(name="db_historias_api")


def query_vector(pregunta_embeddings):
    response = collection.query(
        query_embeddings=pregunta_embeddings,
        n_results=1
    )

    return response["documents"][0][0]


