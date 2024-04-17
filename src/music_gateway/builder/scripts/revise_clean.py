from music_gateway.spec import MusicInfo

musics = set()
cnt = 0
final_mbid = None
with open("data/mbids_done.jsonl", "r") as f:
    while line := f.readline() or cnt == 0:
        cnt += 1
        music = MusicInfo.model_validate_json(line)
        if music.mbid in musics:
            continue
        musics.add(music.mbid)
        final_mbid = music.mbid
        with open("data/mbids_done_new.jsonl", "a") as f1:
            f1.write(music.model_dump_json())
            f1.write("\n")
# json_str = ""
# stacks = []
# for char in things:
#     if char == "{":
#         stacks.append(True)
#     elif char == "}":
#         stacks.pop()
#     json_str += char
#     if len(stacks) == 0:
#         with open("data/mbids_done_new_clean.jsonl", "a") as f1:
#             f1.write(json_str)
#             f1.write("\n")
#         json_str = ""
#         cnt += 1

print(cnt)
print(len(musics))
print(final_mbid)
