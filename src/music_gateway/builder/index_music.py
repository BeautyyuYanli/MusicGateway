import os
from typing import List, Optional

from bs4 import BeautifulSoup
from pydantic import BaseModel

from music_gateway.builder.youtube import vector_from_youtube
from music_gateway.emotions import get_emotion_by_emb
from music_gateway.builder.utils import API_BASE, http_get
from music_gateway.spec import MusicInfo

from time import sleep


def check_youtube(lastfm_url: str) -> Optional[str]:
    html = http_get(lastfm_url).text
    soup = BeautifulSoup(html, "html.parser")
    item = soup.select_one("#track-page-video-playlink")
    if item is None:
        return None
    return item.attrs["href"]


class MusicInfoOutput(BaseModel):
    class TopTags(BaseModel):
        class Tag(BaseModel):
            name: str

        tag: List[Tag]

    class Wiki(BaseModel):
        content: str

    class Artist(BaseModel):
        mbid: str

    class Album(BaseModel):
        mbid: str

    mbid: str
    name: str
    url: str
    toptags: Optional[TopTags] = None
    wiki: Optional[Wiki] = None
    artist: Artist
    album: Album


class FullOutput(BaseModel):
    track: MusicInfoOutput


def get_basic_info(mbid: str) -> MusicInfoOutput:
    res = http_get(
        url=API_BASE,
        params={
            "method": "track.getInfo",
            "mbid": mbid,
            "api_key": os.getenv("LASTFM_API_KEY"),
            "format": "json",
        },
    )
    return FullOutput.model_validate_json(res.content).track


def add_music_detail(mbid: str, music: MusicInfoOutput) -> MusicInfo:
    youtube_url = check_youtube(music.url)
    if youtube_url is None:
        raise ValueError("No youtube link found")
    vec = vector_from_youtube(youtube_url)
    return MusicInfo(
        mbid=mbid,
        name=music.name,
        url=music.url,
        ytb_url=youtube_url,
        emb=vec.tolist(),
        emotions=get_emotion_by_emb(vec),
        tags=[tag.name for tag in music.toptags.tag] if music.toptags else [],
        wiki=music.wiki.content if music.wiki else "",
        artiest_mbid=music.artist.mbid,
        album_mbid=music.album.mbid,
    )


def get_music_info(mbid: str) -> MusicInfo:
    music = get_basic_info(mbid)
    music_info = add_music_detail(mbid, music)
    return music_info


if __name__ == "__main__":
    info = get_music_info("32ca187e-ee25-4f18-b7d0-3b6713f24635")
    print(info.model_dump_json(indent=2, exclude=["emb"]))
    print(len(info.emb))
