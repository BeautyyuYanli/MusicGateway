import streamlit as st
from music_gateway.retriever.default import search_by_direct_text, search_by_audio
from dotenv import load_dotenv
from music_gateway.spec import MusicInfo
from typing import Dict
import tempfile

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

audio = st.file_uploader("音频上传")
if audio:
    st.audio(audio)


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

    if audio is not None:
        music_byte = audio.read()
        with tempfile.NamedTemporaryFile() as f:
            f.write(music_byte)
            f.seek(0)
            audio_ans = search_by_audio(f.name)
    else:
        audio_ans = []

    def dis(mbid: str):
        musics: Dict[str, MusicInfo] = {}
        with open("data/mbids_done_13899.jsonl", "r") as f:
            while line := f.readline():
                music = MusicInfo.model_validate_json(line)
                musics[music.mbid] = music

        music = musics.get(mbid)
        st.write(f"Title: [{music.name}]({music.ytb_url}) MBID: {mbid} ")

    tabs = st.tabs(["Text", "Audio"])
    with tabs[0]:
        st.write("文本检索结果")
        for mbid in search_by_direct_text(text):
            dis(mbid)
    with tabs[1]:
        st.write("音频检索结果")
        for mbid in audio_ans:
            dis(mbid)
