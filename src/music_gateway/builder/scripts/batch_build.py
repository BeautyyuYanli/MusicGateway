ORIGIN_PATH = "data/lastfm-dataset-1K/userid-timestamp-artid-artname-traid-traname.tsv"
mbids = set()

with open(ORIGIN_PATH, "r") as f:
    cnt = 0
    while True:
        cnt += 1
        line = f.readline().strip()
        if line == "":
            break
        row = line.split("\t")
        if row[4].strip():
            mbids.add(row[4].strip())

print(cnt)
print(len(mbids))
with open("data/mbids.txt", "w") as f:
    f.write("\n".join(mbids))
