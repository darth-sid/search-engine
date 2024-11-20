import pickle, os
with open("INDEX/ids.bin", "rb") as file:
    print("Number of indexed documents:", len(pickle.load(file)))
with open("INDEX/offsets.bin", "rb") as file:
    print("Number of unique tokens", len(pickle.load(file)))
total_size = os.path.getsize("INDEX/ids.bin") + os.path.getsize("INDEX/offsets.bin") + os.path.getsize("INDEX/index.bin")
print("Total size:",total_size)

with open("INDEX/offsets.bin", "rb") as file:
    pos,size = pickle.load(file)['research']
with open("INDEX/index.bin", "rb") as file:
    file.seek(pos)
    postings = pickle.loads(file.read(size))
    print(postings)
    print(len(postings))


