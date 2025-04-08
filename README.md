# WinDI Chat — Мини-мессенджер на FastAPI + WebSocket

Мессенджер с авторизацией, обменом сообщениями в реальном времени через WebSocket, поддержкой групповых чатов и системой прочтения сообщений.  
Проект выполнен с использованием **FastAPI**, **async SQLAlchemy**, **PostgreSQL**, **JWT**, **Docker**, **WebSocket**.

---

## 🚀 Быстрый запуск (через Docker)

```bash
git clone https://github.com/<your-username>/windi-chat.git
cd windi-chat
docker-compose up --build
FastAPI Docs: http://localhost:8000/docs
```
Сервер будет доступен по адресу: http://localhost:8000

Структура проекта
```
windi-chat/
├── app/
│   ├── main.py                  # Точка входа FastAPI
│   ├── models.py                # SQLAlchemy-модели (User, Message, Chat, Group)
│   ├── schemas.py               # Pydantic-схемы
│   ├── database.py              # Подключение к БД
│   ├── config.py                # Конфиг (SECRET, DB URL)
│   ├── services/                # Бизнес-логика (чаты, сообщения)
│   ├── routers/                 # Эндпоинты API (auth, message, websocket)
│   └── dependencies.py          # get_db, get_current_user
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
└── README.md
```
### Аутентификация
```
JWT токен при логине

Защищённые эндпоинты с Authorization: Bearer <access_token>
```
### Эндпоинты API


```
POST	/auth/register	Регистрация пользователя
POST	/auth/login	Авторизация, возвращает JWT
GET	/auth/me	Получение текущего пользователя
```


### Messages
Метод	Endpoint	Описание
POST	/messages	Отправка сообщения
POST	/messages/{message_id}/read	Отметка сообщения как прочитанного, уведомление отправителю
GET	/messages/history/{chat_id}	Получить историю сообщений по чату (limit, offset)
```
# WebSocket
ws://localhost:8000/ws/chat?user_id=<id>
```
Отправка сообщения:
{
  "chat_id": 1,
  "text": "Привет!",
  "client_message_id": "unique-<timestamp>"
}

`Ответ от сервера (всем участникам чата):`
```
{
  "id": 42,
  "chat_id": 1,
  "sender_id": 2,
  "text": "Привет!",
  "timestamp": "2025-04-08T12:00:00Z",
  "is_read": false,
  "client_message_id": "unique-1744111111111"
}

Уведомление о прочтении:

{
  "type": "read_receipt",
  "message_id": 42,
  "chat_id": 1,
  "reader_id": 3,
  "is_read": true
}
```

 # (Логика приложения) #
WebSocket-соединения отслеживаются через active_connections, где user_id → множество соединений.

Отправка сообщения → сохраняется в PostgreSQL, рассылается всем участникам чата по WebSocket.

Прочтение сообщения (/messages/{id}/read) → обновляет статус is_read = true, сервер уведомляет отправителя.

Предотвращение дубликатов — через UniqueConstraint(chat_id, client_message_id).

# Примеры


### Регистрация


```
 curl -X POST http://localhost:8000/auth/register \
 -H "Content-Type: application/json" \
 -d '{"name": "test", "email": "m@example.com", "password": "123"}'
```
### Авторизация 

```
curl -X POST http://localhost:8000/auth/login \
 -H "Content-Type: application/x-www-form-urlencoded" \
 -d "username=m@example.com&password=123"
```

```
curl http://localhost:8000/auth/me \
 -H "Authorization: Bearer <access_token>"
```
###### Подключение к ДБ через psql вставьте ссылку на свою бд и скрипт будет работать
# Реализовано:
 FastAPI, asyncio, SQLAlchemy async

 WebSocket чат в реальном времени

 JWT авторизация

 PostgreSQL и Docker Compose

 Уникальные client_message_id

 Групповые чаты (many-to-many)

 Прочтение сообщений + уведомление

 Swagger-документация
