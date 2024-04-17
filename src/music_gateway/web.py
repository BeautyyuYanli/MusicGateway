import streamlit as st
from music_gateway.retriever.direct_text import search_by_direct_text
from dotenv import load_dotenv
from music_gateway.spec import MusicInfo
from typing import Dict

load_dotenv()

st.info(
    """Demo 展示
- 已经建立了基于 CLAP embedding 的朴素检索，适合使用本体论的描述进行检索(样例下述)
- 已经搭建了向量数据库的检索存储，正在随数据爬取而同步更新
- 已构建 音乐、专辑、艺术家 的 schema
"""
)
cnt = 0
with open("data/mbids_done_13899.jsonl", "r") as f:
    while line := f.readline():
        cnt += 1
st.info(f"当前数据量: {cnt}")

with st.form("default_form"):
    st.write(
        """Examples:
- This is a happy drum.
- This is a relaxing saxophone.
- This is a celebratory song."""
    )
    text = st.text_area("Input your query", placeholder="This is a happy drum.")
    btn = st.form_submit_button("Submit")


if btn:
    st.title("Results")
    for mbid in search_by_direct_text(text):
        musics: Dict[str, MusicInfo] = {}
        with open("data/mbids_done_13899.jsonl", "r") as f:
            while line := f.readline():
                music = MusicInfo.model_validate_json(line)
                musics[music.mbid] = music

        music = musics.get(mbid)
        st.write(f"[{music.name}]({music.ytb_url})")
        # st.write(music.model_dump(exclude=["emb"]))
