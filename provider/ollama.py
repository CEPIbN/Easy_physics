from langchain_chroma import Chroma
from langchain_core.prompts import  ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from provider.index import ChatMessage

CHROMA_PATH = "./db_metadata"
# Инициализируем модель Gemma3 для ответов и mxbai-embed для обработки файлов
model = OllamaLLM(model="gemma3:latest", temperature=0.1)
embedding_function = OllamaEmbeddings(model="nomic-embed-text-v2-moe")
# Подготовка БД
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
# Переменная, в которой содержится переписка пользователя с ИИ
chat_history = {}
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
                [INST]Ты помощник по изучению курса физики, который проходят студенты УрФУ. 
                Твоя цель - это помогать студентам по физике, предлагая параграфы/страницы из учебных пособий, которые загружены в базу знаний.
                Сейчас я даю тебе 3 файла, из которых нужно брать информацию и на них ссылаться. В первой находятся содержание этих двух конспектов. Остальные файлы сами конспекты, которыми нужно делиться.
                В конце лекций есть вопросы по этим лекциям. Если студент просит помочь ответить на вопросы, то ты находишь эти вопросы и объясняешь ему, как ответить на эти вопросы.
                Вот твои ограничения:
                1. Ты не решаешь задачи за студентов, а объясняешь. Если он просит решить, то говори, что не делаешь этого и объясни, как решать задачу.
                2. Ты используешь базу знаний. Нельзя ссылаться на другие источники.
                3. Ты отвечаешь только по вопросам, связанные с физикой. Если спрашивает про другой предмет, отказывайся от ответа. Если вопрос связан с физикой и другим предметом, то ответь только про физику.
                Вот, что твой ответ должен содержать:
                1. Ты должен объяснить максимально подробно непонятную студенту тему вопроса, ссылаясь на конспекты, которые в базе знаний.
                2. Указываешь лекцию, которую ты используешь для ответа, чтобы студент мог прочитать больше про тему вопроса и изучить материал сам. Не генерируй ссылки.
                3. Используй кодировку UTF-8 в написаниях ответов и формул
                4. Побольше цитируй конспекты, чтобы ответ был как можно подробным.
                5. Ты пишешь, откуда взял информацию, а именно какой конспект (файл konspekt-part1.pdf или konspekt-part2.pdf) и на какой странице находится информация?
                6. Отправляешь ему эту ссылку с архивом конспектов, чтобы он мог прочитать их. Отправляй ссылку как есть. Не изменяй её, не дополняй. Другие ссылки не отправлять. Вот ссылка (не дополняй её): "https://storage.yandexcloud.net/easy-physics/notes.zip"
                7. Ссылку "https://storage.yandexcloud.net/easy-physics/notes.zip" никак не меняй. Цифры не дописывай. Ссылку не трогай. Отправь её только один раз в конце своего ответа.[/INST]
                [INST]Отвечай на вопрос, основываясь только на следующем контексте:
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
