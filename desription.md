# Тестовые задания

Задания необходимо выполнить изолированно от действующего проекте. 

# Задание 1: Напоминания

Цель: Создание механизма напоминаний с использованием языковой модели.

Флоу: Пользователь может написать в ТГ боту сообщение в стиле

- Напомни мне сегодня в 6 вечера купить продукты - создаётся запись о напоминании в бд, на 6 вечера сегодняшнего дня
- напомни мне завтра заехать в магазин - создаётся запись в бд о напоминании в тоже время следующего дня
- напомни через пару дней вернуться к этой задаче - создаётся запись о напоминании через 2 дня в тоже время

Подход:

Сообщение П триггерит вызов функции в openai (tools_call в completions api) которая вызывается если напоминание нужно и вернет период для создания напоминания. В бд рождается запись. Бот отвечает что напомнит и тд, если все успешно.
Celery триггерит напоминание когда подойдёт срок, бот присылает сообщение с reply_to на исходное(с просьбой о напоминании) в стиле "Привет, ты просил напомнить что..."

Стек: Django, Celery, Telegram Bot Api, OpenAI Api

# Задание 2: Опрос

Цель: Собрать информацию о П которую можно использовать.

Флоу: П активирует бота, запускается механизм опроса и бот задаёт первый вопрос, после каждого ответа присылается следующий вопрос. Может быть два типа вопросов

1. Сообщение с ответами в кнопке в сообщении
2. Сообщение с ответом в сообщении от П

В завершении бот благодарит о прохождении опроса

Админская часть: Когда П активирует бота создаётся тред в форуме-админке с инфой о юзере, сообщения от бота и пользователя форвардятся туда в процессе прохождения опроса.

Подход: В бд хранится список опросов и список вопросов привызанных к опросу, старт бота происходит с указанием id запускаемого опроса, ответы юзера тоже сохраняются в бд: id чата и сообщения для пересылки

Стек: Django, Telegram Bot Api