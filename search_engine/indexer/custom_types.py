from typing import Iterable

type posting = tuple[float, int] # (tf-idf, path/url)
type inverted_index = dict[str,Iterable[posting]] # {token: [posting, ...]}
