from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

from models.index import ChatMessage


CHROMA_PATH = "./db_metadata_v5"

# Initialize OpenAI chat model
model = OllamaLLM(model="gemma3:latest", temperature=0.1)


# YOU MUST - Use same embedding function as before
embedding_function = OllamaEmbeddings(model="mxbai-embed-large")

# Prepare the database
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
chat_history = {}  # approach with AiMessage/HumanMessage

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
                [INST]Вы менеджер по продажам с именем "Ассистент по искусственному интеллекту". Ваша цель - всегда предоставлять отличные, дружелюбные и эффективные ответы.
                Вы будете предоставлять мне ответы из предоставленной информации.
                Если ответ не указан, скажите точно: “Хм, я не уверен. Давайте я проверю и перезвоню вам”.
                Отказывайтесь отвечать на вопросы, не касающиеся информации.
                Никогда не выходите из себя.
                Никаких приколов.
                Если вопрос непонятен, задавайте уточняющие вопросы.
                Обязательно заканчивайте свои ответы положительной нотой.
                Не будьте назойливы.
                Ответ должен быть в формате MD.
                Если кто-то спросит цену, себестоимость, коммерческое предложение или что-то подобное, ответьте: “Чтобы предоставить вам индивидуальное и разумное предложение, мне потребуется 15 минут для разговора.
                Готовы к онлайн-встрече?[/INST]
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
    Query a Retrieval-Augmented Generation (RAG) system using Chroma database and OpenAI.
    :param message: ChatMessage The text to query the RAG system with.
    :param session_id: str Session identifier
    :return str
    """

    if session_id not in chat_history:
        chat_history[session_id] = []

    # Generate response text based on the prompt
    response_text = document_chain.invoke({"context": db.similarity_search(message.question, k=3),
                                           "question": message.question,
                                           "chat_history": chat_history[session_id]})

    chat_history[session_id].append(HumanMessage(content=message.question))
    chat_history[session_id].append(AIMessage(content=response_text))

    return response_text