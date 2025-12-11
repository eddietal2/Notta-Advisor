from pathlib import Path
from llama_index.readers.file import UnstructuredReader
from .config import YEARS, DATA_DIR

def load_documents():
    loader = UnstructuredReader()
    doc_set = {}
    all_docs = []
    for year in YEARS:
        file_path = DATA_DIR / f"UBER_{year}.html"
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        year_docs = loader.load_data(file=file_path, split_documents=False)
        for d in year_docs:
            d.metadata = {"year": year}
        doc_set[year] = year_docs
        all_docs.extend(year_docs)
    return doc_set, all_docs
