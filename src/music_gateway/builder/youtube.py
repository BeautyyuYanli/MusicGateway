import tempfile
from pathlib import Path

import numpy as np
from pytube import YouTube

from music_gateway.emb_model import clap_emb_model


def vector_from_youtube(url: str) -> np.ndarray:
    s = YouTube(url=url).streams.filter(type="audio").order_by("abr").desc().first()
    if s is not None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            s.download(
                output_path=tmp_dir,
                filename="tmp.audio",
                max_retries=5,
            )
            file_path = Path(tmp_dir) / "tmp.audio"
            vec = clap_emb_model.emb_audios([str(file_path)])[0]
        return vec
    else:
        raise ValueError("No audio stream found")


if __name__ == "__main__":
    v1 = vector_from_youtube("https://www.youtube.com/watch?v=jHjUHKdoaqI")
    v2 = clap_emb_model.emb_audios(["tests/data/FocalorsSacrifice.webm"])[0]
    similarity = np.linalg.norm(v1 - v2)
    print(similarity)
