from typing import Literal

import streamlit as st
from dotenv import load_dotenv
from google.api_core.exceptions import InternalServerError, ResourceExhausted
from google.generativeai.types.generation_types import StopCandidateException
from llama_index.core.base.llms.types import ChatMessage
from llama_index.llms.gemini import Gemini
from streamlit.runtime.scriptrunner import get_script_run_ctx

load_dotenv()

llm = Gemini(temperature=0.1)


def st_logger(level: Literal["ERROR", "INFO", "WARNING"], message: str):
    icons = {"ERROR": "🚨", "INFO": "📢", "WARNING": "⚠️"}
    st.toast(message, icon=icons.get(level, "📢"))


cli_logger = st_logger if get_script_run_ctx() is not None else print


def llm_write(prompt: str, retry: int = 5) -> str:
    while retry > 0:
        try:
            res = llm.chat([ChatMessage(content=prompt)])
            return res.message.content
        except (InternalServerError, ResourceExhausted, StopCandidateException):
            retry -= 1
            cli_logger("WARNING", "Failed to call Google Gemini API, retrying...")
