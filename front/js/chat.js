// Получаем элементы DOM
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const newChatBtn = document.getElementById('newChatBtn');
const themeToggleBtn = document.getElementById('themeToggleBtn');

// Функция для генерации уникального ID
function generateChatId() {
    return 'chat_' + Math.random();
}

// Генерируем уникальный ID для чата
let chatId = generateChatId();

// Функция для добавления сообщения в чат
function addMessageToChat(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'avatar';
    
    const icon = document.createElement('i');
    icon.className = isUser ? 'fas fa-user' : 'fas fa-lightbulb';
    avatarDiv.appendChild(icon);
    
    const messageContentDiv = document.createElement('div');
    messageContentDiv.className = 'message-content';
    
    const senderDiv = document.createElement('div');
    senderDiv.className = 'message-sender';
    senderDiv.textContent = isUser ? 'Вы' : 'ИИ Ассистент';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    textDiv.textContent = content;
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageContentDiv.appendChild(senderDiv);
    messageContentDiv.appendChild(textDiv);
    messageContentDiv.appendChild(timeDiv);
    
    messageDiv.appendChild(isUser ? avatarDiv : messageContentDiv);
    messageDiv.appendChild(isUser ? messageContentDiv : avatarDiv);
    
    chatMessages.appendChild(messageDiv);
    
    // Прокручиваем чат вниз
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Функция для отправки сообщения на сервер
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;
    
    // Добавляем сообщение пользователя в чат
    addMessageToChat(message, true);
    
    // Очищаем поле ввода
    userInput.value = '';
    userInput.style.height = 'auto';
    
    // Отправляем сообщение на сервер
    try {
        const response = await fetch(`/chat/${chatId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question: message })
        });
        
        if (response.ok) {
            const data = await response.json();
            // Добавление ответа ИИ в чат
            addMessageToChat(data.response);
        } else {
            addMessageToChat('Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте еще раз.');
        }
    } catch (error) {
        console.error('Error:', error);
        addMessageToChat('Произошла ошибка при подключении к серверу.');
    }
}

// Функция для автоматической подстройки высоты textarea
function adjustTextareaHeight() {
    userInput.style.height = 'auto';
    userInput.style.height = (userInput.scrollHeight > 150 ? 150 : userInput.scrollHeight) + 'px';
}

// Обработчик события для кнопки отправки
sendBtn.addEventListener('click', sendMessage);

// Обработчик события для отправки по Ctrl+Enter
userInput.addEventListener('keydown' , (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
    // Автоматическая подстройка высоты
    setTimeout(adjustTextareaHeight, 0);
});

// Обработчик события для кнопки новой темы
newChatBtn.addEventListener('click', () => {
    // Генерируем новый ID для чата
    chatId = generateChatId();
    
    // Очищаем историю сообщений
    chatMessages.innerHTML = `
        <div class="message ai-message">
            <div class="avatar">
                <i class="fas fa-lightbulb"></i>
            </div>
            <div class="message-content">
                <div class="message-sender">ИИ Ассистент</div>
                <div class="message-text">Привет! Я ваш ИИ ассистент. Чем могу помочь вам сегодня?</div>
            </div>
        </div>
    `;
});

// Обработчик события для переключения темы
themeToggleBtn.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    
    // Обновляем текст и иконку кнопки
    const icon = themeToggleBtn.querySelector('i');
    const span = themeToggleBtn.querySelector('span');
    
    if (document.body.classList.contains('dark-mode')) {
        icon.className = 'fas fa-sun';
        span.textContent = 'Светлая тема';
    } else {
        icon.className = 'fas fa-moon';
        span.textContent = 'Темная тема';
    }
});

// Начальная настройка высоты textarea
adjustTextareaHeight();