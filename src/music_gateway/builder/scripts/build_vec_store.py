from llama_index.core.schema import TextNode
from llama_index.vector_stores.milvus import MilvusVectorStore
from music_gateway.spec import MusicInfo
import os
from dotenv import load_dotenv

load_dotenv()
milvus = MilvusVectorStore(
    uri=os.getenv("MILVUS_URI"),
    token=os.getenv("MILVUS_TOKEN"),
    collection_name=os.getenv("PROJECT_NAME") + "_clap",
    dim=512,
)
cnt = 0
with open("data/mbids_done_13899.jsonl", "r") as f:
    while line := f.readline():
        cnt += 1
        if cnt % 1000 == 0:
            print(f"Processing {cnt}...")
        music = MusicInfo.model_validate_json(line)
        milvus.add(
            [
                TextNode(
                    id_=music.mbid,
                    embedding=music.emb,
                )
            ]
        )
