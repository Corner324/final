# Система управления и контроля бизнеса

## Архитектура

- Микросервисная архитектура (Python 3.12 + FastAPI + Pydantic v2)
- Каждый сервис — отдельное приложение со своей базой данных (PostgreSQL 15)
- Взаимодействие:
  - **REST** — синхронные запросы между сервисами
  - **Event-Bus (RabbitMQ)** — публикация/подписка доменных событий
- Монорепозиторий (mono-repo) — единый `docker-compose.yml`, но каждый сервис можно запускать автономно
- CI / CD — GitHub Actions → Docker Hub / GHCR (шаблон workflow в `/docker/ci.yml`)

### Диаграмма взаимодействия сервисов

```mermaid
flowchart TD
    subgraph RabbitMQ
        MQ["user.events<br/>other topics"]
    end

    Auth[[auth]] -- "HTTP /users<br/>publish user.events" --> MQ
    MQ -- "fanout" --> Team[[team]]

    Meetings[[meetings]] -- "HTTP /calendar/availability" --> Calendar[[calendar]]
    Calendar -- "team events" --> Meetings

    Org[org_structure] -. uses .-> Team
    Tasks[[tasks]] -- REST --> Team
    Motivation[[motivation]] -- REST --> Team

    Admin[admin-panel] -- REST --> Auth & Team & Tasks
```

> В диаграмме показаны только ключевые взаимодействия; дополнительные вызовы (например, авторизация через `auth` с JWT-токеном) опущены для краткости.

## Микросервисы и их ответственность

| Сервис            | Порт | Сущности / Задачи                                                                                                    |
| ----------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **auth**          | `8001` | Пользователи, аутентификация, токены JWT, события `user.events`                           |
| **team**          | `8002` | Команды/компании, участники, роли, синхронизация пользователей через MQ |
| **org_structure** | `8003` | Дерева подразделений и ролей, связь с `team`                                                      |
| **tasks**         | `8004` | Задачи, статусы, комментарии                                                                               |
| **motivation**    | `8005` | Оценки, метрики, статистика мотивации                                                              |
| **meetings**      | `8006` | Встречи, участники, проверка занятости через `calendar`                                    |
| **calendar**      | `8007` | Календарные события (личные/командные), проверка интервалов                     |
| **admin_panel**   | `8010` | SQLAdmin UI для чтения/редактирования данных                                                          |

## Быстрый старт

1. Склонируйте репозиторий и установите Docker ≥ 24.0.
2. Создайте файл `.env` в корне и задайте необходимые переменные (см. ниже).
3. Запустите всю систему:

```bash
docker compose up --build -d
```

4. Swagger UI каждого сервиса будет доступен по `http://localhost:<PORT>/docs`.

### Только один сервис

```bash
cd services/auth
docker compose up --build
```

## Переменные окружения (общие)

| Имя                | По умолчанию          | Описание                       |
| --------------------- | -------------------------------- | -------------------------------------- |
| `POSTGRES_DB`       | `service_db`                   | Имя БД                            |
| `POSTGRES_USER`     | `user`                         | Пользователь БД          |
| `POSTGRES_PASSWORD` | `password`                     | Пароль                           |
| `RABBIT_URL`        | `amqp://guest:guest@rabbitmq/` | DSN RabbitMQ                           |
| `SECRET_KEY`        | —                               | Секрет для подписи JWT |

Полный список переменных расположен в `.env` файлов каждого сервиса.

## Запуск миграций

Перед первым запуском каждого сервиса выполняется:

```bash
poetry run alembic upgrade head  # внутри контейнера
```

## Доменные события

| Топик          | Producer | Consumer | Payload              |
| ------------------- | -------- | -------- | -------------------- |
| `user.events`     | auth     | team     | `{event, payload}` |
| `meeting.created` | meetings | calendar | data of meeting      |

## Тестирование

* Юнит-тесты лежат в `services/<name>/tests/`.
* Запуск:

```bash
pytest -q
```
