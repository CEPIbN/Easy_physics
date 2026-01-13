# Импорт необходимых библиотек
import hashlib
import os
import shutil
from typing import List, Generator
from langchain_community.document_loaders import PyPDFLoader  # Убрали TextLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import MarkdownTextSplitter
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings

# Путь до директории ChromaDB
CHROMA_PATH = "./db_metadata"
DATA_PATH = "./docs"
global_unique_hashes = set()


def walk_through_pdf_files(path: str) -> Generator[str, None, None]:
    """Проходимся по PDF файлам в каталоге и указываем путь до этих файлов"""
    for (dir_path, _, filenames) in os.walk(path):
        for filename in filenames:
            if filename.lower().endswith('.pdf'):  # Проверяем расширение .pdf
                yield os.path.join(dir_path, filename)


def load_documents() -> List[Document]:
    """
    Загружаем PDF документы из каталога docs
    :return:
    Список объектов документа
    """
    documents = []

    # Загрузка только PDF файлов
    pdf_files = []
    for (dir_path, _, filenames) in os.walk(DATA_PATH):
        for filename in filenames:
            if filename.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(dir_path, filename))

    for pdf_file in pdf_files:
        try:
            loader = PyPDFLoader(pdf_file)
            documents.extend(loader.load())
            print(f"Загружен PDF: {pdf_file}")
        except Exception as e:
            print(f"Ошибка при загрузке {pdf_file}: {e}")

    print(f"Всего загружено {len(documents)} страниц из PDF файлов")
    return documents


def hash_text(text: str) -> str:
    """Генерирует хэш-значение для текста, используя SHA-256"""
    hash_object = hashlib.sha256(text.encode())
    return hash_object.hexdigest()


def split_text(documents: List[Document]) -> List[Document]:
    """
    Разделяет текстовое содержимое документов на более мелкие фрагменты
    :param documents: Список объектов документа, содержащих текстовое содержимое для разделения.
    :return: Список объектов документа, представляющих разделенные текстовые фрагменты (chunks).
    """
    # Разделение текста с данными параметрами
    text_splitter = MarkdownTextSplitter(
        chunk_size=500,  # Размер каждого фрагмента в символах
        chunk_overlap=100,
        length_function=len,  # Функция для вычисления длины текста
    )
    # Разделение документов на более мелкие фрагменты функцией text_splitter
    chunks = text_splitter.split_documents(documents)
    print(f"Документы {len(documents)} разделены на {len(chunks)} частей.")

    # Убираем дубликаты
    unique_chunks = []
    for chunk in chunks:
        chunk_hash = hash_text(chunk.page_content)
        if chunk_hash not in global_unique_hashes:
            unique_chunks.append(chunk)
            global_unique_hashes.add(chunk_hash)

    # Вывод содержимого страницы и метаданных для фрагментов
    print(f"Количество уникальных фрагментов {len(unique_chunks)}.")
    return unique_chunks


def save_to_chroma(chunks: List[Document]) -> None:
    """
    Сохранение заданных объектов документа в Chroma DB.
    :param chunks: Список объектов документов, представляющих фрагменты текста для сохранения.
    :return: None
    """
    # Удаление существующего каталога БД, если он существует
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Создание новой БД на основе документов, используя Ollama embeddings
    db = Chroma.from_documents(
        documents=chunks,
        embedding=OllamaEmbeddings(model="mxbai-embed-large"),
        persist_directory=CHROMA_PATH
    )

    # Запись данных в БД
    print(f"Сохранено {len(chunks)} фрагментов в директории {CHROMA_PATH}")


def generate_data_store() -> None:
    """Создание векторной БД в Chroma из документов"""
    documents = load_documents()  # Загрузка документов из источника
    if documents:  # Проверяем, что документы загрузились
        chunks = split_text(documents)  # Разделение документов на фрагменты
        save_to_chroma(chunks)  # Сохранение обработанных данных в хранилище
    else:
        print("Не найдено PDF файлов для обработки")


if __name__ == "__main__":
    generate_data_store()