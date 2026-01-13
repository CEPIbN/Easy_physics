from langchain_chroma import Chroma
from langchain_core.prompts import  ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from provider.index import ChatMessage

CHROMA_PATH = "./db_metadata"
# Инициализируем модель Gemma3 для ответов и mxbai-embed для обработки файлов
model = OllamaLLM(model="gemma3:latest", temperature=0.1)
embedding_function = OllamaEmbeddings(model="mxbai-embed-large:latest")
# Подготовка БД
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
# Переменная, в которой содержится переписка пользователя с ИИ
chat_history = {}
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
                [INST]Ты — ассистент-библиограф по учебным пособиям по физике. Твоя задача — по запросу студента рекомендовать конкретные разделы из предоставленной базы знаний.
ПРАВИЛА:
1. ОТВЕЧАЙ ТОЛЬКО НА РУССКОМ ЯЗЫКЕ.
2. Используй информацию из предоставленного контекста.
4. Не придумывай ответ. Не решай задачи. Не объясняй теорию.
5. Формат ответа: четкий нумерованный список. Для каждого пункта укажи: **Название учебного пособия**, **Глава/Раздел**, **Название параграфа**, **номера страниц**. Объяснений не требуется.[/INST]
                [INST]Ответьте на вопрос, основываясь только на следующем контексте:
                {context}[/INST]
            """
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}")
    ]
)

document_chain = create_stuff_documents_chain(llm=model, prompt=prompt_template)


def query_rag(message: ChatMessage, session_id: str = "") -> str:
    """
    RAG-запрос к БД Chroma.
    :param message: Сообщение в чате - текст для запроса к системе RAG
    :param session_id: Идентификатор сеанса str
    :return: str
    """
    if session_id not in chat_history:
        chat_history[session_id] = []

    # Генерирует ответ на основе промпта
    response_text = document_chain.invoke({"context": db.similarity_search(message.question, k=3),
                                          "question": message.question,
                                          "chat_history": chat_history[session_id]})
    chat_history[session_id].append(HumanMessage(content=message.question))
    chat_history[session_id].append(AIMessage(content=response_text))
    return response_text
