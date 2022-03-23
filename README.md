![example workflow](https://github.com/DevCatRain/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

[foodgram](http:178.154.197.104/recipes)

# Дипломный проект
Foodgram - Продуктовый помощник.
Сервис позволяет публиковать рецепты, подписываться на публикации других пользователей,
добавлять понравившиеся рецепты в список "Избранное", а перед походом в магазин - скачивать
сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/DevCatRain/foodgram-project-react.git
```

### Инфраструктура
* Проект работает с СУБД PostgreSQL.

* Проект запущен на сервере в Яндекс.Облаке в трёх контейнерах: nginx, PostgreSQL и Django+Gunicorn. Заготовленный контейнер с фронтендом - используется для сборки файлов.

* Контейнер с проектом обновляется на Docker Hub.

* В nginx настроена раздача статики, запросы с фронтенда переадресуются в контейнер с Gunicorn. Джанго-админка работает напрямую через Gunicorn.

* Данные сохраняются в volumes.

* Создайте .env файл в директории проекта:

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

* В терминале выполните команды из директории infra:

- собираем и запускаем инфраструктуру
```
docker-compose up -d --build
``` 
- выполняем миграции
```
docker-compose exec backend python manage.py migrate --noinput
``` 
- собираем статику
```
docker-compose exec backend python manage.py collectstatic --no-input
``` 
- загружаем тестовые данные
```
docker-compose exec backend python manage.py loaddata dump.json
```

### Функциональность проекта:
* Все сервисы и страницы доступны для пользователей в соответствии с их правами
* Рецепты на всех страницах сортируются по дате публикации от новых к старым
* Работает фильтрация по тегам
* Пагинация включена на всех страницах
* База наполнена исходными данные: добавлены ингредиенты, теги, тестовые пользователи и рецепты

### Тестовые пользователи
```
Логин: admin (суперюзер)
Пароль: admin
```

```
Логин: test@test.ru
Пароль: test123test
```
```
Логин: foodgram@foodgram.ru
Пароль: food123food
```

### Оформление кода
Код соответствует PEP8

### Об авторе
CatRain - [DevCatRain](https://github.com/DevCatRain)
