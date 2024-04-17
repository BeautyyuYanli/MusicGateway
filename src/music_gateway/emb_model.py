from typing import List

import laion_clap
import numpy as np


class CLAPEmbModel:
    model: laion_clap.CLAP_Module

    def __init__(self):
        self.model = laion_clap.CLAP_Module(enable_fusion=False, amodel="HTSAT-base")
        self.model.load_ckpt("weights/music_audioset_epoch_15_esc_90.14.pt")

    def emb_audios(self, files_path: List[str]) -> List[np.ndarray]:
        return [x for x in self.model.get_audio_embedding_from_filelist(x=files_path)]

    def emb_texts(self, texts: List[str]) -> List[np.ndarray]:
        if len(texts) == 1:
            return [[x for x in self.model.get_text_embedding([texts[0], ""])][0]]
        return [x for x in self.model.get_text_embedding(texts)]


clap_emb_model = CLAPEmbModel()
__all__ = ["clap_emb_model"]
