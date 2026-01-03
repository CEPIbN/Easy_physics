# Langchain dependencies
import hashlib
import os
import shutil
from pathlib import Path
from typing import List, Generator

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import MarkdownTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

# Path to the directory to save Chroma database
CHROMA_PATH = "./db_metadata_v5"
DATA_PATH = "./docs"
global_unique_hashes = set()


def walk_through_files(path: str, file_extension: str = '.txt') -> Generator[str, None, None]:
    """Walk through files in directory and yield file paths."""
    for (dir_path, _, filenames) in os.walk(path):
        for filename in filenames:
            if filename.endswith(file_extension):
                yield os.path.join(dir_path, filename)


def load_documents() -> List[Document]:
    """
    Load documents from the specified directory
    Returns:
    List of Document objects
    """
    documents = []
    for f_name in walk_through_files(DATA_PATH):
        # Явно преобразуем в строку, если нужно
        document_loader = TextLoader(str(f_name), encoding="utf-8")
        documents.extend(document_loader.load())

    return documents


def hash_text(text: str) -> str:
    """Generate a hash value for the text using SHA-256."""
    hash_object = hashlib.sha256(text.encode())
    return hash_object.hexdigest()


def split_text(documents: List[Document]) -> List[Document]:
    """
    Split the text content of the given list of Document objects into smaller chunks.

    Args:
    documents (List[Document]): List of Document objects containing text content to split.

    Returns:
    List[Document]: List of Document objects representing the split text chunks.
    """
    # Initialize text splitter with specified parameters
    text_splitter = MarkdownTextSplitter(
        chunk_size=500,  # Size of each chunk in characters
        chunk_overlap=100,  # Overlap between consecutive chunks
        length_function=len,  # Function to compute the length of the text
    )

    # Split documents into smaller chunks using text splitter
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    # Deduplication mechanism
    unique_chunks = []
    for chunk in chunks:
        chunk_hash = hash_text(chunk.page_content)
        if chunk_hash not in global_unique_hashes:
            unique_chunks.append(chunk)
            global_unique_hashes.add(chunk_hash)

    # Print example of page content and metadata for a chunk
    print(f"Unique chunks equals {len(unique_chunks)}.")
    # print(unique_chunks[:-5])

    return unique_chunks  # Return the list of split text chunks


def save_to_chroma(chunks: List[Document]) -> None:
    """
    Save the given list of Document objects to a Chroma database.

    Args:
    chunks (List[Document]): List of Document objects representing text chunks to save.

    Returns:
    None
    """
    # Clear out the existing database directory if it exists
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Create a new Chroma database from the documents using Ollama embeddings
    db = Chroma.from_documents(
        documents=chunks,
        embedding=OllamaEmbeddings(model="mxbai-embed-large"),
        persist_directory=CHROMA_PATH
    )

    # Persist the database to disk
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")


def generate_data_store() -> None:
    """Generate vector database in chroma from documents."""
    documents = load_documents()  # Load documents from a source
    chunks = split_text(documents)  # Split documents into manageable chunks
    save_to_chroma(chunks)  # Save the processed data to a data store


if __name__ == "__main__":
    generate_data_store()