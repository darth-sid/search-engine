from hashlib import md5
import time
import numpy as np

def hamming_distance(simhash1: int, simhash2: int) -> int:
    return (simhash1 ^ simhash2).bit_count()

def simhash(features: list[str]) -> int:
    sums = np.zeros(128, dtype=int)
    for feature in features:
        feature_hash = md5(feature.encode()).digest()
        bits = np.unpackbits(np.frombuffer(feature_hash, dtype=np.uint8))
        bits = bits.astype(int)
        bits[bits==0] = -1
        sums += bits
    sums[sums < 0] = 0
    sums[sums > 0] = 1
    return int.from_bytes(np.packbits(sums))

def shingle(features: list[str], k: int=1) -> list[str]:
    return [' '.join(features[i:i+k]) for i in range(len(features)-k+1)]

def tokenize(string: str) -> list[str]:
    return string.split()

if __name__ == "__main__":
    strings = []
    strings.append("Hello, I am a bird and I can fly")
    strings.append("Hello, I am a cat and I can jump")
    strings.append("Hello, I am a fly and I can bird")
    strings.append("Hello, I am a bird and I cna fly")
    strings.append("Hello, I can fly and I am a bird")
    tokenss = [tokenize(string) for string in strings]
    shingless = [shingle(tokens,2) for tokens in tokenss]
    hashes = [simhash(shingles) for shingles in shingless]

    i = 0
    for j in range(1,len(hashes)):
        print(strings[i],strings[j])
        print(shingless[i],shingless[j])
        print(hamming_distance(hashes[i],hashes[j]))
