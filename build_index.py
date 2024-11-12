import os
from indexer import index_page
from indexer.utils import save_index_json

def build_partial_index(domain_path: str, partials_dir):
    partial_index = {}
    for page in os.scandir(domain_path):
        if page.is_file():
            file_path = f"{domain_path}/{page.name}"
            index_page(partial_index,file_path)
    save_index_json(partials_dir, domain_path.split("/")[-1], partial_index)

def build_index(src_path: str="CORPUS", partials_dir: str="PARTIAL_INDEXES"):
    os.mkdir(partials_dir)
    for domain in os.scandir(src_path):
        if not domain.is_dir(): 
            continue
        domain_path = f"{src_path}/{domain.name}"
        build_partial_index(domain_path, partials_dir)
    #TODO: construct full index from partial indexes

if __name__ == "__main__":
    build_index()
