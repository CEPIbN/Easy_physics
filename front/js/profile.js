// Скрипт для переключения темной/светлой темы

document.addEventListener('DOMContentLoaded', function() {
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const themeIcon = themeToggleBtn.querySelector('i');
    const themeText = themeToggleBtn.querySelector('span');

    // Проверяем, есть ли сохраненная тема в localStorage
    const savedTheme = localStorage.getItem('theme');

    // Проверяем системные настройки
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    // Устанавливаем начальную тему
    if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
        enableDarkTheme();
    } else {
        enableLightTheme();
    }

    // Обработчик клика по кнопке переключения темы
    themeToggleBtn.addEventListener('click', function() {
        if (document.body.classList.contains('dark-theme')) {
            enableLightTheme();
        } else {
            enableDarkTheme();
        }
    });

    // Функция для включения темной темы
    function enableDarkTheme() {
        document.body.classList.add('dark-theme');
        document.body.classList.remove('light-theme');
        themeIcon.className = 'fas fa-sun';
        themeText.textContent = 'Светлая тема';
        localStorage.setItem('theme', 'dark');
    }

    // Функция для включения светлой темы
    function enableLightTheme() {
        document.body.classList.add('light-theme');
        document.body.classList.remove('dark-theme');
        themeIcon.className = 'fas fa-moon';
        themeText.textContent = 'Темная тема';
        localStorage.setItem('theme', 'light');
    }

    // Слушаем изменения системных настроек темы
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
        if (!localStorage.getItem('theme')) {
            if (e.matches) {
                enableDarkTheme();
            } else {
                enableLightTheme();
            }
        }
    });
});