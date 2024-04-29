import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
from music_gateway.retriever.default import search_by_direct_text, search_by_audio
from music_gateway.builder.youtube import bytes_from_youtube
from dotenv import load_dotenv
from music_gateway.spec import MusicInfo
from music_gateway.emotions import emotions
from typing import Dict, Optional, List
from agent_path.llm import LLM
from agent_path.utils import get_json_object
from pydantic import BaseModel, Field
from llama_index.llms.openai import OpenAI
import tempfile

load_dotenv()


@st.cache_resource()
def read_info():
    cnt = 0
    musics: Dict[str, MusicInfo] = {}
    with open("data/mbids_done_13899.jsonl", "r") as f:
        while line := f.readline():
            cnt += 1
            music = MusicInfo.model_validate_json(line)
            musics[music.mbid] = music
    return cnt, musics


cnt, musics = read_info()
st.info(f"当前数据库收录音乐: {cnt}")


@st.cache_resource
def get_llm():
    return LLM(client=OpenAI("gpt-4"))


llm = get_llm()


def display(mbid: str, context: str = ""):
    music = musics.get(mbid)
    cols = st.columns([1, 1])
    with cols[0]:
        st.write(f"Title: [{music.name}]({music.ytb_url})")
        st.caption(f"MBID: {mbid}")
    with cols[1]:

        def download_audio(ytb_url: str, mbid: str):
            data, mime = bytes_from_youtube(ytb_url)
            st.session_state[f"audio_{mbid}"] = [data, mime]

        if not st.session_state.get(f"audio_{mbid}"):
            st.button(
                "Download",
                key=f"download_{mbid}{context}",
                on_click=download_audio,
                args=(music.ytb_url, mbid),
            )
        if st.session_state.get(f"audio_{mbid}"):
            data, mime = st.session_state[f"audio_{mbid}"]
            st.audio(data, format=mime)


def search_on_ontology(text: str):
    return search_by_direct_text(text)


def search_on_audio(audio: UploadedFile):
    music_byte = audio.read()
    with tempfile.NamedTemporaryFile() as f:
        f.write(music_byte)
        f.seek(0)
        return search_by_audio(f.name)


# Audio Upload

audio = st.file_uploader("音频上传")

# Text Input
tabs = st.tabs(["LLM 检索", "本体论检索"])

# LLM Input
with tabs[0]:
    with st.container(border=False):
        if st.session_state.get("llm_submit"):
            st.session_state["llm_task"] = st.session_state["llm_submit_text"]

        if (dis_task := st.session_state.get("llm_task", None)) is not None:
            with st.chat_message(name="human"):
                if audio is not None:
                    st.write(f"输入音频:")
                    st.audio(audio)
                if dis_task:
                    st.write(f"查找任务: {dis_task}")

            with st.chat_message(name="ai"):
                st.write("分析检索目标...")
                if (
                    st.session_state.get("llm_submit")
                    and st.session_state["llm_submit_text"]
                ):
                    prompt = f"""
You are a useful AI assistant that can help me find music.
Here is the description of the music I want to find:
{st.session_state["llm_submit_text"]}

From the description, I want you to infer the following information if exist:
NAME: Name of the music
ARTIST: Artist of the music
ALBUM: Album of the music
ONTOLOGY: Ontology description of a music, like "This is a happy drum." "This is a relaxing saxophone." "This is a celebratory violin."
TAGS: Tags that can appear in the music, like "disco" "electronic" "70s" "pop"
EMOTIONS: Emotions that can be evoked by the music. These must be in some of {str(emotions)}

output format:
```json
{{
    "NAME": str,
    "ARTIST": str,
    "ALBUM": str,
    "ONTOLOGY": str,
    "TAGS": List[str],
    "EMOTIONS": List[str]
}}

If some of the information is missing in the description, or you can not infer the information, you can omit the field.
The output should always use English
"""

                    class AnswerModel(BaseModel):
                        NAME: Optional[str] = None
                        ARTIST: Optional[str] = None
                        ALBUM: Optional[str] = None
                        ONTOLOGY: Optional[str] = None
                        TAGS: Optional[List[str]] = Field(default_factory=list)
                        EMOTIONS: Optional[List[str]] = Field(default_factory=list)

                    while True:
                        try:
                            ans = llm.generate(prompt)
                            ans_model = AnswerModel.model_validate_json(
                                get_json_object(ans)
                            )
                        except Exception as e:
                            st.write(f"Error: {e}")
                            continue
                        break
                    st.session_state["llm_name"] = ans_model.NAME
                    st.session_state["llm_artist"] = ans_model.ARTIST
                    st.session_state["llm_album"] = ans_model.ALBUM
                    st.session_state["llm_onto"] = ans_model.ONTOLOGY
                    st.session_state["llm_tags"] = ans_model.TAGS
                    st.session_state["llm_emotions"] = ans_model.EMOTIONS

                if st.session_state.get("llm_name", None):
                    st.write(f"音乐名称: {st.session_state['llm_name']}")
                if st.session_state.get("llm_artist", None):
                    st.write(f"音乐家: {st.session_state['llm_artist']}")
                if st.session_state.get("llm_album", None):
                    st.write(f"专辑: {st.session_state['llm_album']}")
                if st.session_state.get("llm_onto", None):
                    st.write(f"本体论描述: {st.session_state['llm_onto']}")
                if st.session_state.get("llm_tags", None):
                    st.write(f"标签: {st.session_state['llm_tags']}")
                if st.session_state.get("llm_emotions", None):
                    st.write(f"情感: {st.session_state['llm_emotions']}")

            with st.chat_message(name="ai"):
                st.write("检索结果")
                full_ans: List[str] = []
                # Audio
                if st.session_state.get("llm_submit"):
                    st.session_state["llm_audio_res"] = (
                        search_on_audio(audio) if audio else []
                    )
                if st.session_state.get("llm_audio_res"):
                    with st.expander("音频检索结果"):
                        for mbid in st.session_state.get("llm_audio_res", []):
                            display(mbid, "llm_a_retri")
                            full_ans.append(mbid)
                # Onto
                if st.session_state.get("llm_submit"):
                    onto = st.session_state.get("llm_onto", None)
                    st.session_state["llm_onto_res"] = (
                        search_on_ontology(onto) if onto else []
                    )
                if st.session_state.get("llm_onto_res"):
                    with st.expander("文本检索结果"):
                        for mbid in st.session_state.get("llm_onto_res", []):
                            display(mbid, "llm_o_retri")
                            full_ans.append(mbid)
                # Full
                st.write("综合检索结果")
                full_ans.sort()
                for mbid in full_ans[:5]:
                    display(mbid, "llm_full_retri")

        with st.container(border=True):
            st.text_area("描述你要寻找的音乐", key="llm_submit_text")
            st.caption("留空仅使用音频查找")
            st.button("寻找", type="primary", key="llm_submit")

# Ontology Input
with tabs[1]:
    with st.container(border=False):
        st.markdown(
            """Examples:

    - This is a happy drum.
    - This is a relaxing saxophone.
    - This is a celebratory violin."""
        )
        text = st.text_area("Input your query", placeholder="This is a happy drum.")
        if st.button("Submit"):
            st.session_state["onto_audio_res"] = search_on_audio(audio) if audio else []
            st.session_state["onto_text_res"] = search_on_ontology(text) if text else []

        tabs = st.tabs(["文本检索结果", "音频检索结果"])
        with tabs[0]:
            for mbid in st.session_state.get("onto_text_res", []):
                display(mbid, "onto_text_retri")
        with tabs[1]:
            for mbid in st.session_state.get("onto_audio_res", []):
                display(mbid, "onto_audio_retri")
