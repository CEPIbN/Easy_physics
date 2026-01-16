"""
Скрипт для просмотра чанков по номеру.
Используется после создания базы данных через основной скрипт
"""

import json
import os
import sys
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

# Конфигурация
CHROMA_PATH = "./db_metadata"
CHUNKS_SAVE_FILE = "./chunks_metadata.json"  # Файл для сохранения метаданных чанков


class ChunkViewer:
    def __init__(self, chroma_path: str = CHROMA_PATH):
        """
        Инициализация просмотрщика чанков
        :param chroma_path: Путь к базе данных Chroma
        """
        self.chroma_path = chroma_path
        self.db = None
        self.chunks_metadata = []

        # Проверяем существование базы данных
        if not os.path.exists(chroma_path):
            print(f"База данных не найдена по пути: {chroma_path}")
            sys.exit(1)

    def load_database(self):
        """Загрузка базы данных Chroma"""
        print("Загрузка базы данных")
        try:
            self.db = Chroma(
                persist_directory=self.chroma_path,
                embedding_function=OllamaEmbeddings(model="mxbai-embed-large")
            )
            print(f"База данных загружена из {self.chroma_path}")
        except Exception as e:
            print(f"Ошибка при загрузке базы данных: {e}")
            sys.exit(1)

    def extract_all_chunks(self):
        """Извлечение всех чанков из базы данных"""
        print("Извлечение чанков из базы данных...")

        try:
            # Получаем все документы из коллекции
            collection = self.db._collection
            results = collection.get(include=["metadatas", "documents"])

            documents = results["documents"]
            metadatas = results["metadatas"]
            ids = results["ids"]

            # Создаем список чанков с метаданными
            self.chunks_metadata = []
            for i, (doc_id, metadata, content) in enumerate(zip(ids, metadatas, documents)):
                chunk_info = {
                    "chunk_id": i + 1,  # Порядковый номер, начиная с 1
                    "db_id": doc_id,
                    "content": content,
                    "metadata": metadata,
                    "length": len(content),
                    "source_file": metadata.get("source_file", "Неизвестно"),
                    "page_number": metadata.get("page_number", metadata.get("page", 0)),
                }
                self.chunks_metadata.append(chunk_info)

            print(f"Извлечено {len(self.chunks_metadata)} чанков")

            # Сохраняем метаданные в файл для быстрого доступа
            self.save_chunks_metadata()

        except Exception as e:
            print(f"Ошибка при извлечении чанков: {e}")
            sys.exit(1)

    def save_chunks_metadata(self):
        """Сохранение метаданных чанков в файл"""
        try:
            # Подготавливаем данные для сохранения
            save_data = {
                "total_chunks": len(self.chunks_metadata),
                "chunks": []
            }

            for chunk in self.chunks_metadata[:100]:  # Сохраняем первые 100 чанков полностью
                save_data["chunks"].append({
                    "chunk_id": chunk["chunk_id"],
                    "length": chunk["length"],
                    "source_file": chunk["source_file"],
                    "page_number": chunk["page_number"],
                    "preview": chunk["content"][:200] + "..." if len(chunk["content"]) > 200 else chunk["content"]
                })

            # Сохраняем в файл
            with open(CHUNKS_SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)

            print(f"Метаданные чанков сохранены в {CHUNKS_SAVE_FILE}")

        except Exception as e:
            print(f"Не удалось сохранить метаданные: {e}")

    def display_chunk(self, chunk_number: int):
        """
        Отображение чанка по номеру
        :param chunk_number: Номер чанка (начиная с 1)
        """
        if not self.chunks_metadata:
            print("Чанки не загружены. Сначала вызовите extract_all_chunks().")
            return

        if chunk_number < 1 or chunk_number > len(self.chunks_metadata):
            print(f"Некорректный номер чанка. Доступные номера: 1-{len(self.chunks_metadata)}")
            return

        # Получаем чанк
        chunk = self.chunks_metadata[chunk_number - 1]

        # Форматированный вывод
        print(f"ЧАНК #{chunk_number}")
        print(f"\nОСНОВНАЯ ИНФОРМАЦИЯ:")
        print(f"   ID в базе данных: {chunk['db_id']}")
        print(f"   Длина: {chunk['length']} символов")
        print(f"   Файл источника: {chunk['source_file']}")
        print(f"   Номер страницы: {chunk['page_number']}")

        print(f"\n МЕТАДАННЫЕ:")
        for key, value in chunk['metadata'].items():
            print(f"   {key}: {value}")

        print(f"\n СОДЕРЖИМОЕ:")

        # Разбиваем на строки для лучшего отображения
        content = chunk['content']
        lines = content.split('\n')

        # Выводим по строкам с нумерацией
        for i, line in enumerate(lines):
            if line.strip():  # Пропускаем пустые строки
                print(f"{i + 1:3d} | {line}")
        # Статистика по чанку
        non_empty_lines = sum(1 for line in lines if line.strip())
        avg_line_length = sum(len(line) for line in lines) / max(1, len(lines))

        print(f"\n СТАТИСТИКА:")
        print(f"   Всего строк: {len(lines)}")
        print(f"   Непустых строк: {non_empty_lines}")
        print(f"   Средняя длина строки: {avg_line_length:.1f} символов")

        # Поиск формул
        formula_indicators = ['=', '∑', '∫', '∂', '∇', 'α', 'β', 'γ', '^', '_', '→', '∞', '≠', '≈', '≡', '≤', '≥', '×',
                              '÷', '√']
        formula_lines = []

        for i, line in enumerate(lines):
            if any(indicator in line for indicator in formula_indicators):
                formula_lines.append((i + 1, line))

        if formula_lines:
            print(f"\n НАЙДЕНЫ ФОРМУЛЫ/МАТЕМАТИЧЕСКИЕ СИМВОЛЫ:")
            for line_num, line in formula_lines[:5]:  # Показываем первые 5
                truncated_line = line[:100] + "..." if len(line) > 100 else line
                print(f"   Строка {line_num}: {truncated_line}")
            if len(formula_lines) > 5:
                print(f"   ... и еще {len(formula_lines) - 5} строк с формулами")

    def display_chunks_list(self, start: int = 1, count: int = 10):
        """
        Показать список чанков с кратким описанием
        :param start: Начальный номер
        :param count: Количество для показа
        """
        end = min(start + count - 1, len(self.chunks_metadata))

        print(f"\n СПИСОК ЧАНКОВ {start}-{end} (всего: {len(self.chunks_metadata)})")

        for i in range(start - 1, end):
            chunk = self.chunks_metadata[i]
            preview = chunk['content'][:100].replace('\n', ' ') + "..."

            print(f"#{chunk['chunk_id']:4d} | "
                  f"Стр: {chunk['length']:4d} | "
                  f"Файл: {chunk['source_file'][:20]:20s} | "
                  f"Стр: {chunk['page_number']:3d} | "
                  f"{preview}")
        print(f"Используйте 'view номер' для просмотра конкретного чанка")
        print(f"Используйте 'list начало количество' для показа другого диапазона")

    def search_in_chunks(self, search_term: str, max_results: int = 10):
        """
        Поиск текста в чанках
        :param search_term: Текст для поиска
        :param max_results: Максимальное количество результатов
        """
        results = []

        for chunk in self.chunks_metadata:
            if search_term.lower() in chunk['content'].lower():
                # Находим контекст вокруг найденного текста
                content_lower = chunk['content'].lower()
                search_idx = content_lower.find(search_term.lower())

                if search_idx != -1:
                    # Извлекаем контекст
                    start = max(0, search_idx - 50)
                    end = min(len(chunk['content']), search_idx + len(search_term) + 50)
                    context = chunk['content'][start:end]

                    # Заменяем переносы строк для компактности
                    context = context.replace('\n', ' ')

                    results.append({
                        'chunk_id': chunk['chunk_id'],
                        'context': context,
                        'position': search_idx
                    })

                if len(results) >= max_results:
                    break

        if results:
            print(f"\n РЕЗУЛЬТАТЫ ПОИСКА: '{search_term}'")

            for result in results:
                print(f"Чанк #{result['chunk_id']} (позиция: {result['position']}):")
                print(f"  ...{result['context']}...")
                print()

            print(f"Найдено: {len(results)} результатов (показано первых {len(results)})")
        else:
            print(f" По запросу '{search_term}' ничего не найдено")

    def interactive_mode(self):
        """Интерактивный режим для просмотра чанков"""
        print(" РЕЖИМ ПРОСМОТРА ЧАНКОВ")

        # Загружаем базу данных
        self.load_database()

        # Извлекаем все чанки
        self.extract_all_chunks()

        # Показываем первую страницу
        self.display_chunks_list(1, 10)

        # Основной цикл
        while True:
            try:
                command = input("\nВведите команду (номер, 'list', 'search', 'exit'): ").strip().lower()

                if command == 'exit' or command == 'quit' or command == 'q':
                    print(" Выход из программы")
                    break

                elif command.startswith('list'):
                    # Обработка команды list
                    parts = command.split()
                    if len(parts) == 1:
                        self.display_chunks_list(1, 10)
                    elif len(parts) == 2:
                        try:
                            start = int(parts[1])
                            self.display_chunks_list(start, 10)
                        except ValueError:
                            print(" Неверный формат. Используйте: list [начало] [количество]")
                    elif len(parts) == 3:
                        try:
                            start = int(parts[1])
                            count = int(parts[2])
                            self.display_chunks_list(start, count)
                        except ValueError:
                            print(" Неверный формат. Используйте: list [начало] [количество]")

                elif command.startswith('search'):
                    # Обработка команды поиска
                    parts = command.split(' ', 1)
                    if len(parts) == 2:
                        search_term = parts[1]
                        self.search_in_chunks(search_term, max_results=5)
                    else:
                        print(" Укажите поисковый запрос. Используйте: search текст")

                elif command.startswith('view'):
                    # Обработка команды view
                    parts = command.split()
                    if len(parts) == 2:
                        try:
                            chunk_number = int(parts[1])
                            self.display_chunk(chunk_number)
                        except ValueError:
                            print(" Неверный формат номера. Используйте: view номер")
                    else:
                        print(" Укажите номер чанка. Используйте: view номер")

                elif command.isdigit():
                    # Если введено просто число - показываем чанк
                    chunk_number = int(command)
                    self.display_chunk(chunk_number)

                else:
                    print("   Неизвестная команда. Доступные команды:")
                    print("   номер          - Показать чанк с указанным номером")
                    print("   list [н] [к]   - Показать список чанков (н - начало, к - количество)")
                    print("   search текст   - Поиск текста в чанках")
                    print("   view номер     - Показать чанк с указанным номером")
                    print("   exit/quit/q    - Выйти из программы")

            except KeyboardInterrupt:
                print("\n\n Выход из программы")
                break
            except Exception as e:
                print(f" Ошибка: {e}")


def main():
    """Основная функция"""
    # Проверяем существование базы данных
    if not os.path.exists(CHROMA_PATH):
        print(f" База данных не найдена по пути: {CHROMA_PATH}")
        sys.exit(1)

    # Создаем и запускаем просмотрщик
    viewer = ChunkViewer(CHROMA_PATH)
    viewer.interactive_mode()


if __name__ == "__main__":
    main()