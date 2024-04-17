from music_gateway.spec import ArtistInfo
from music_gateway.spec import MusicInfo
from music_gateway.builder.utils import http_get, API_BASE
from music_gateway.builder.index_artist import get_artist_info

existed = set()
cnt = 0
with open("data/mbids_done_13899.jsonl", "r") as f0:
    while line := f0.readline():
        music = MusicInfo.model_validate_json(line)
        if music.artiest_mbid in existed:
            continue
        try:
            artist = get_artist_info(music.artiest_mbid)
        except:
            continue
        cnt += 1
        existed.add(music.artiest_mbid)
        with open("data/artists_13899.jsonl", "a") as f1:
            f1.write(artist.model_dump_json())
            f1.write("\n")
print(cnt)
