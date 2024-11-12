type posting = tuple[float, str] # (tf-idf, path/url)
type inverted_index = dict[str,list[posting]] # {token: [posting, ...]}
