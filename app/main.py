from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from provider.index import ChatMessage
from provider.ollama import query_rag

# Инициализация приложения Fastapi
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтируем папку front
app.mount("/front", StaticFiles(directory="front"), name="front")

#Страница с чатом
@app.get("/")
async def read_root():
    return FileResponse("./front/html/chat.html")

# Страница профиля
@app.get("/profile")
async def read_profile():
    return FileResponse("./front/html/profile.html")

# Страница регистрации
@app.get("/register")
async def read_register():
    return FileResponse("./front/html/register.html")

#Страница входа
@app.get("/login")
async def read_login():
    return FileResponse("./front/html/login.html")

#Отправка сообщения
@app.post("/chat/{chat_id}")
async def ask(chat_id: str, message: ChatMessage):
    return {"response": query_rag(message, chat_id)}