from music_gateway.spec import MusicInfo, AlbumInfo, ArtistInfo

with open("data/mbids_done_13899.jsonl", "r") as f:
    cnt = 0
    while line := f.readline():
        cnt += 1
        music = MusicInfo.model_validate_json(line)
    print(f"Total: {cnt} musics")

with open("data/album_13899.jsonl", "r") as f:
    cnt = 0
    while line := f.readline():
        cnt += 1
        album = AlbumInfo.model_validate_json(line)
    print(f"Total: {cnt} albums")

with open("data/artists_13899.jsonl", "r") as f:
    cnt = 0
    while line := f.readline():
        cnt += 1
        artist = ArtistInfo.model_validate_json(line)
    print(f"Total: {cnt} artists")
