from time import sleep
from music_gateway.builder.index_music import get_music_info

START_POINT = "ab892614-7199-4cb0-bd11-72a2ad4c72e0"
with open("data/mbids.txt", "r") as f:
    mbids = [line.strip() for line in f.readlines()]

start_idx = mbids.index(START_POINT)
mbids = mbids[start_idx + 1 :]


for idx, mbid in enumerate(mbids):
    try:
        music = get_music_info(mbid)
    except Exception as e:
        print(f"Error get_music_info for {idx}. {mbid}: {e}")
        continue

    try:
        with open("data/mbids_done.jsonl", "a") as f:
            f.write(music.model_dump_json())
            f.write("\n")
    except Exception as e:
        print(f"Error persist_info for {idx}. {mbid}: {e}")
        continue

    print(f"Done {idx}. {mbid}")
    print(f"Progress: {idx}/{len(mbids)}, {idx/len(mbids)*100:.2f}%")
    print("Sleeping 5 seconds...")
    sleep(5)

print(f"Done all {len(mbids)} mbids.")
