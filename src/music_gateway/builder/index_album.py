import os
from typing import List, Optional

from pydantic import BaseModel, Field

from music_gateway.builder.utils import API_BASE, http_get
from music_gateway.spec import AlbumInfo


class AlbumInfoOutput(BaseModel):
    class Wiki(BaseModel):
        content: str

    class Image(BaseModel):
        text: str = Field(alias="#text")

    name: str
    wiki: Optional[Wiki] = None
    image: Optional[List[Image]] = None


class FullOutput(BaseModel):
    album: AlbumInfoOutput


def get_album_info(mbid: str) -> AlbumInfo:
    res = http_get(
        url=API_BASE,
        params={
            "method": "album.getinfo",
            "mbid": mbid,
            "api_key": os.getenv("LASTFM_API_KEY"),
            "format": "json",
        },
    )
    output = FullOutput.model_validate_json(res.content).album
    return AlbumInfo(
        name=output.name,
        mbid=mbid,
        wiki_content=output.wiki.content if output.wiki else "",
        image_url=output.image[-1].text if output.image else None,
    )


if __name__ == "__main__":
    album = get_album_info("03c91c40-49a6-44a7-90e7-a700edf97a62")
    print(album)
