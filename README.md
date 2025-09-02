# Фудграм

Социальная сеть для публикации кулинарных рецептов.
На данный момент доступна по адресу:
https://practicumyandexxx.zapto.org/


## Основные возможности

- 📝 Публикация и редактирование рецептов
- ❤️ Добавление рецептов в избранное
- 👥 Подписка на авторов
- 🛒 Создание списка покупок
- 🏷️ Фильтрация рецептов по тегам

## 🚀 Развертывание проекта
- Создайте файл .env в корневой директории проекта и заполните следующие переменные:
 POSTGRES_DB=foodgram
 POSTGRES_USER=foodgram_user
 POSTGRES_PASSWORD=foodgram_password
 DB_NAME=foodgram
 DB_HOST=db
 DB_PORT=5432
 SECRET_KEY=<ваш ключ django из settings.py>
 ALLOWED_HOSTS=localhost,127.0.0.1,<ваши доменные имена>
 DEBUG=False
 DB=postgresql
 CSRF_TRUSTED_ORIGINS=<ваши доменные имена и ip через запятую>

- скопируйте файл .env и docker-compose.yml на ваш хост с помощью утилиты scp
- не забудьте дать права на доступ к папке и файлам вашему текущему пользователю
- перейдите в созданную вами папку проекта
- выполните команду sudo docker compose up -d
- дождитесь загрузки docker и выполните последовательно:
    sudo docker compose exec backend python manage.py migrate
    sudo docker compose exec backend python manage.py collectstatic
    sudo docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
- для наполнения бд ингредиентами выполните
    sudo docker compose exec backend python manage.py fill_db

## Спецификация API доступна:
- локально:
    http://localhost/api/docs/
- после развертывания на вашем ресурсе
    <ваш домен>api/docs/

## Технологии
- Python
- Django
- PostgreSQL
- JavaScript (SPA-функциональность)
- HTML/CSS

## Автор
https://github.com/mernser/