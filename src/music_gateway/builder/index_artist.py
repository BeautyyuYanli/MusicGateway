import os
from typing import Optional

from pydantic import BaseModel

from music_gateway.builder.utils import API_BASE, http_get
from music_gateway.spec import ArtistInfo


class ArtistInfoOutput(BaseModel):
    class Bio(BaseModel):
        content: str

    name: str
    bio: Optional[Bio] = None


class FullOutput(BaseModel):
    artist: ArtistInfoOutput


def get_artist_info(mbid: str) -> ArtistInfo:
    res = http_get(
        url=API_BASE,
        params={
            "method": "artist.getInfo",
            "mbid": mbid,
            "api_key": os.getenv("LASTFM_API_KEY"),
            "format": "json",
        },
    )
    output = FullOutput.model_validate_json(res.content).artist
    return ArtistInfo(
        name=output.name,
        mbid=mbid,
        bio_content=output.bio.content if output.bio else "",
    )


if __name__ == "__main__":
    artist = get_artist_info("bfcc6d75-a6a5-4bc6-8282-47aec8531818")
    print(artist)
