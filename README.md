# Q&A API Project

## Описание
Это REST API приложение для управления системой вопросов и ответов. Пользователи могут создавать вопросы, добавлять ответы к ним, получать список вопросов и детальную информацию о каждом вопросе вместе с ответами, а также удалять вопросы и ответы.

## Основные возможности
- CRUD для вопросов (создание, получение, удаление)  
- CRUD для ответов на вопросы  
- Поддержка каскадного удаления: при удалении вопроса удаляются все связанные ответы  
- Валидация данных при создании вопросов и ответов  
- Swagger документация для всех эндпоинтов  

## Технологии
- Django + Django REST Framework  
- PostgreSQL  
- Docker и Docker Compose  
- Python logging  
- Swagger (drf_yasg)

## Установка и запуск

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/Suetosha/qa_django_project.git
```

### 2. Создайте .env файл
Пример содержимого .env:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=qa_project
DB_USER=postgres
DB_PASSWORD=123
DB_HOST=db
DB_PORT=5432
```

### 3. Запуск через Docker Compose
```bash
docker-compose up -d
```

### 4. Доступ к приложению
```
Swagger документация: http://localhost:8000/swagger/

Основной API: http://localhost:8000/api/
```

### Рекомендации

#### Перед первым запуском убедитесь, что порт 5432 свободен для PostgreSQL.

#### Для тестирования API используйте Swagger или Postman.