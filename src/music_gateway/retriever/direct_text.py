import os
from typing import List

from dotenv import load_dotenv
from llama_index.core.vector_stores import VectorStoreQuery
from llama_index.vector_stores.milvus import MilvusVectorStore
from pymilvus.exceptions import MilvusException

from music_gateway.emb_model import clap_emb_model

load_dotenv()

milvus = MilvusVectorStore(
    uri=os.getenv("MILVUS_URI"),
    token=os.getenv("MILVUS_TOKEN"),
    collection_name=os.getenv("PROJECT_NAME") + "_clap",
    dim=512,
)


def search_by_direct_text(text: str, top_k=3) -> List[str]:
    emb = clap_emb_model.emb_texts([text])[0]
    while True:
        try:
            res = milvus.query(
                VectorStoreQuery(
                    query_embedding=emb.tolist(),
                    similarity_top_k=top_k,
                )
            )
            break
        except MilvusException as e:
            continue

    return res.ids or []


if __name__ == "__main__":
    print(search_by_direct_text("It is a happy song."))
