from typing import List, Optional
from pydantic import BaseModel


class ArtistInfo(BaseModel):
    name: str
    mbid: str
    bio_content: str


class AlbumInfo(BaseModel):
    name: str
    mbid: str
    wiki_content: str
    image_url: Optional[str] = None


class MusicInfoLegacy(BaseModel):
    mbid: str
    url: str
    wiki: str
    emb: List[float]
    emotions: List[str]
    tags: List[str]
    artiest_mbid: str
    album_mbid: str


class MusicInfo(BaseModel):
    mbid: str
    name: str
    url: str
    ytb_url: str
    wiki: str
    emb: List[float]
    emotions: List[str]
    tags: List[str]
    artiest_mbid: str
    album_mbid: str
