from music_gateway.spec import AlbumInfo
from music_gateway.spec import MusicInfo
from music_gateway.builder.index_album import get_album_info

existed = set()
cnt = 0
with open("data/mbids_done_13899.jsonl", "r") as f0:
    while line := f0.readline():
        music = MusicInfo.model_validate_json(line)
        if music.album_mbid in existed:
            continue
        try:
            album = get_album_info(music.album_mbid)
        except:
            continue
        cnt += 1
        existed.add(music.album_mbid)
        with open("data/album_13899.jsonl", "a") as f1:
            f1.write(album.model_dump_json())
            f1.write("\n")
print(cnt)
