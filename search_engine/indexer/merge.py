from utils import create_empty_dir, copy, walk
from utils.io import read_bin, read_bin_chunk, write_bin
from utils.structs import Posting, TermData
from typing import NamedTuple
import heapq
from math import log


def merge_partials(partials_path: str, path: str) -> None:
    """merges partial index from partials path into a single index and lookup table at given path"""
    create_empty_dir(path)
    copy(f"{partials_path}/ids.bin", f"{path}/ids.bin")
    with open(f"{path}/ids.bin", "rb") as file:
        N = len(read_bin(file))  # total number of indexed docs

    partials = []
    for file_path in walk(partials_path, file_ext="bin"):
        if file_path.endswith("ids.bin"):
            continue
        else:
            partial = PartialIndexReadBuffer(file_path)
            partials.append(partial)
    partials = MultiPartialReader(partials)

    offsets = {}
    with open(f"{path}/index.bin", "wb") as index:
        pos = 0
        while partials:
            term, _, postings = partials.pop()
            while partials and partials.peek().term == term:
                entry = partials.pop()
                postings.extend(entry.postings)

            df = len(postings)
            idf = log(N / df)
            data = TermData(postings=postings, idf=idf)
            size = write_bin(index, data, pos=pos)
            frag = term[:2]
            if frag not in offsets:
                offsets[frag] = {}
            offsets[frag][term] = (pos, size)
            pos += size

    offsets_offsets = {}
    with open(f"{path}/offsets.bin", "ab") as file:
        pos = 0
        for frag in offsets:
            size = write_bin(file, offsets[frag])
            offsets_offsets[frag] = (pos, size)
            pos += size

    with open(f"{path}/offsets0.bin", "wb") as file:
        write_bin(file, offsets_offsets)


class PartialIndexReadBuffer:
    """read wrapper for partial index bin files"""

    def __init__(self, path: str, part_id: int | None = None):
        self.id = (
            int(path.split("_")[-1].rstrip(".bin")) if part_id is None else part_id
        )
        self._file = open(path, "rb")
        self._pos = 0
        self._EOF = self._file.seek(0, 2)

    def close(self) -> None:
        """close file"""
        self._file.close()

    def read_next(self) -> tuple[str, list[Posting]] | None:
        """read next chunk from bin file"""
        if self._pos >= self._EOF:
            self.close()
            return None
        val, size = read_bin_chunk(
            self._file, pos=self._pos, format=tuple[str, list[Posting]]
        )
        self._pos += size
        return val


class MultiPartialReader:
    """reads terms and their data from multiple open partial indexes"""

    class Entry(NamedTuple):
        term: str
        src_id: int
        postings: list[Posting]  # dict of tag : posting list

    def __init__(self, partials: list[PartialIndexReadBuffer]):
        self._heap = []
        self._partials = partials
        for partial in partials:
            if (tup := partial.read_next()) is None:
                continue
            term, postings = tup
            heapq.heappush(
                self._heap,
                MultiPartialReader.Entry(
                    term=term, src_id=partial.id, postings=postings
                ),
            )

    def __len__(self):
        return len(self._heap)

    def pop(self) -> Entry:
        """pop term and its data from heap and try to repopulate with a
        term-data pair from same partial index"""
        entry = heapq.heappop(self._heap)
        if (tup := self._partials[entry.src_id].read_next()) is not None:
            term, postings = tup
            heapq.heappush(
                self._heap,
                MultiPartialReader.Entry(
                    term=term, src_id=entry.src_id, postings=postings
                ),
            )
        return entry

    def peek(self) -> Entry:
        """see next term-data pair to be popped"""
        return self._heap[0]
