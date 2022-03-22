# praktikum_new_diplom
Foodgram - Продуктовый помощник.
Сервис позволяет публиковать рецепты, подписываться на публикации других пользователей,
добавлять понравившиеся рецепты в список "Избранное", а перед походом в магазин - скачивать
сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/DevCatRain/foodgram-project-react.git
```

```
cd foodgram
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
. venv/bin/activate
```

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

На удаленном сервере установить Docker и docker-compose:
```
sudo apt install docker.io
sudo apt install docker-compose
```
Скопировать файлы docker-compose.yaml и nginx/default.conf из проекта на ваш сервер в home/<ваш_username>/docker-compose.yaml и home/<ваш_username>/nginx/default.conf

При пуше в GitHub приложение сначала проходит тесты, при условии пуша в ветку master обновляется образ на Docker Hub и автоматически деплоится на сервер (при успешном workflow). Затем нужно подключиться к удаленному серверу и применить миграции:
```
sudo docker-compose exec backend python3 manage.py migrate --noinput
```

создать суперпользователя:
```
sudo docker-compose exec backend python3 manage.py createsuperuser
```

загрузить ингредиенты в базу данных:
```
sudo docker-compose exec backend python3 manage.py load_data
```

Логин суперюзера: admin
Пароль суперюзера: admin

Логин: test@test.ru
Пароль: test123test
