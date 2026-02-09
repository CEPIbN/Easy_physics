// Получаем элементы DOM
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const newChatBtn = document.getElementById('newChatBtn');
const themeToggleBtn = document.getElementById('themeToggleBtn');

// Функция для генерации уникального ID
function generateChatId() {
    return 'chat_' + Math.random().toString(36).substr(2, 9);
}

// Генерируем уникальный ID для чата
let chatId = generateChatId();

// Константы для расчета строк
const LINE_HEIGHT = 24; // Примерная высота одной строки в пикселях (зависит от font-size и line-height)
const MAX_VISIBLE_LINES = 3; // Максимальное количество строк без скроллбара

// Функция для подсчета строк в textarea
function countTextareaLines(textarea) {
    const text = textarea.value;
    const lines = text.split('\n').length;
    return lines;
}

// Функция для управления скроллбаром
function manageScrollbar() {
    const lines = countTextareaLines(userInput);

    if (lines >= MAX_VISIBLE_LINES) {
        // Добавляем класс для показа скроллбара
        userInput.classList.add('show-scrollbar');
    } else {
        // Убираем класс для скрытия скроллбара
        userInput.classList.remove('show-scrollbar');
    }
}

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

    // Проверяем, что сообщение не пустое
    if (!message) {
        // Можно добавить визуальную индикацию, что поле пустое
        userInput.style.borderColor = '#ff6b6b';
        setTimeout(() => {
            userInput.style.borderColor = '';
        }, 1000);
        return;
    }

    // Добавляем сообщение пользователя в чат
    addMessageToChat(message, true);

    // Очищаем поле ввода
    userInput.value = '';
    userInput.style.height = 'auto';

    // Убираем скроллбар после отправки
    userInput.classList.remove('show-scrollbar');

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
    const newHeight = Math.min(userInput.scrollHeight, 150);
    userInput.style.height = newHeight + 'px';

    // Управляем скроллбаром
    manageScrollbar();
}

// Обработчик события для кнопки отправки
sendBtn.addEventListener('click', sendMessage);

// Обработчик события для textarea - правильная обработка Enter
userInput.addEventListener('keydown', (e) => {
    // Если нажат Enter без Shift
    if (e.key === 'Enter' && !e.shiftKey) {
        // Предотвращаем стандартное поведение (перенос строки)
        e.preventDefault();

        // Отправляем сообщение
        sendMessage();
    }

    // Если нажат Shift+Enter - разрешаем стандартное поведение (перенос строки)
    // и после этого подстраиваем высоту и проверяем скроллбар
    if (e.key === 'Enter' && e.shiftKey) {
        // Разрешаем перенос строки
        // После добавления новой строки подстраиваем высоту
        setTimeout(() => {
            adjustTextareaHeight();
            manageScrollbar(); // Проверяем, нужно ли показывать скроллбар
        }, 0);
    }
});

// Обработчик для подстройки высоты и скроллбара при любом вводе
userInput.addEventListener('input', () => {
    adjustTextareaHeight();
    manageScrollbar();
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

        // Сохраняем в localStorage
        localStorage.setItem('darkMode', 'true');
    } else {
        icon.className = 'fas fa-moon';
        span.textContent = 'Темная тема';

        // Сохраняем в localStorage
        localStorage.setItem('darkMode', 'false');
    }
});

// Проверяем сохраненную тему при загрузке
document.addEventListener('DOMContentLoaded', () => {
    const savedDarkMode = localStorage.getItem('darkMode');

    if (savedDarkMode === 'true') {
        document.body.classList.add('dark-mode');
        const icon = themeToggleBtn.querySelector('i');
        const span = themeToggleBtn.querySelector('span');
        icon.className = 'fas fa-sun';
        span.textContent = 'Светлая тема';
    }

    // Инициализируем высоту textarea
    adjustTextareaHeight();
});