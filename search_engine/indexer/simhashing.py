from hashlib import md5
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
