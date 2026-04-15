# llm-p

Репозиторий проекта "Защищённый API для работы с большой языковой моделью", Курс «Принципы разработки на языке
Python», группа M25-555.

Целью данной работы является разработка серверного приложения на FastAPI, предоставляющего защищённый API для
взаимодействия с большой языковой моделью (LLM) через сервис OpenRouter.

В рамках задания реализованы:

- аутентификация пользователей;
- авторизацию пользователей с использованием JWT;
- хранение данных в базе SQLite;
- разделение ответственности между слоями приложения (API, бизнес-логика, доступ к данным).

## Подготовка окружения

Клонируйте репозиторий:

```shell
git clone https://github.com/AlekseiAgarkov/llm-p.git
cd llm-p
```

Установите [uv](https://docs.astral.sh/uv/):

```shell
pip install uv
```

Создайте виртуальное окружение:

```shell
uv venv
```

Активируйте виртуальное окружение:

MacOS/Linux:

```shell
source .venv/bin/activate
```

Windows:

```shell 
 
.venv\Scripts\activate.bat
```

Установите зависимости:

```shell
uv pip install -r <(uv pip compile pyproject.toml)
```

## Создание конфигурации `.env`

Скопируйте конфигурационный файл `.env`

```shell
cp .env.example .env
```

Зарегистрируйтесь на OpenRouter и получите API ключ

Добавьте свой ключ в переменную `OPENROUTER_API_KEY` в файле `.env`.

По умолчанию для OpenRouter указана модель `openrouter/free`, но Вы можете изменить её на другую в переменной
`OPENROUTER_MODEL`.

## Запуск проекта

Для запуска проекта активируйте окружение `.venv` и вызовите команду:

```shell
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger UI с OpenAPI документацией будет доcтупен по адресу http://127.0.0.1:8000/docs.

## Скриншоты

### /health

![01_health_get.png](docs%2Fimg%2F01_health_get.png)

### Регистрация пользователя

![02_register_OK.png](docs%2Fimg%2F02_register_OK.png)

![03_register_user_already_exists.png](docs%2Fimg%2F03_register_user_already_exists.png)

![04_register_password_too_long.png](docs%2Fimg%2F04_register_password_too_long.png)

### Логин и получение JWT

![05_login_OK.png](docs%2Fimg%2F05_login_OK.png)

![06_login_wrong_password.png](docs%2Fimg%2F06_login_wrong_password.png)

![07_login_non_existent_user.png](docs%2Fimg%2F07_login_non_existent_user.png)

### Авторизация через Swagger

![08_swagger_auth_OK.png](docs%2Fimg%2F08_swagger_auth_OK.png)

### Вызов auth/me

![09_auth_me_not_authenticated.png](docs%2Fimg%2F09_auth_me_not_authenticated.png)

![10_auth_me_OK.png](docs%2Fimg%2F10_auth_me_OK.png)

### Вызов POST /chat

![11_chat_msg_01.png](docs%2Fimg%2F11_chat_msg_01.png)

![12_chat_msg_02.png](docs%2Fimg%2F12_chat_msg_02.png)

![13_chat_msg_03.png](docs%2Fimg%2F13_chat_msg_03.png)

### Получение истории через GET /chat/history

![14_chat_history.png](docs%2Fimg%2F14_chat_history.png)

### Удаление истории через DELETE /chat/history

![15_chat_delete.png](docs%2Fimg%2F15_chat_delete.png)

![16_chat_delete_checked.png](docs%2Fimg%2F16_chat_delete_checked.png)
