from music_gateway.spec import MusicInfo, MusicInfoLegacy
from music_gateway.builder.index_music import get_basic_info, check_youtube

START_POINT = "9bf3ac69-2100-4eac-95a9-cbe906ed3c2a"
started = False

cnt = 0
with open("data/mbids_done.jsonl", "r") as f:
    while line := f.readline():
        cnt += 1
        music = MusicInfoLegacy.model_validate_json(line)
        if started == False:
            if music.mbid == START_POINT:
                started = True
            continue
        basic_info = get_basic_info(music.mbid)
        ytb_url = check_youtube(music.url)
        if ytb_url is None:
            print(f"{cnt}. Error get ytb url for {music.mbid}")
            continue
        print(f"{cnt}. Done {music.mbid}")
        new_music = MusicInfo(
            mbid=music.mbid,
            name=basic_info.name,
            url=music.url,
            ytb_url=ytb_url,
            wiki=music.wiki,
            emb=music.emb,
            emotions=music.emotions,
            tags=music.tags,
            artiest_mbid=music.artiest_mbid,
            album_mbid=music.album_mbid,
        )
        with open("data/mbids_done_new.jsonl", "a") as f1:
            f1.write(new_music.model_dump_json())
            f1.write("\n")
