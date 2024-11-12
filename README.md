# API для медицинских справочников
Для запуска проекта локально необходимо
- склонировать репозиторий:
```commandline
git clone git@github.com:LeoNefesch/terminology_med_service.git
```
*Ниже приводятся команды для Linux.

- Зайти в директорию, установить и активировать виртуальное окружение:
```
cd terminology_med_service
```

- Cоздать и активировать виртуальное окружение:
```
python3 -m venv venv
```

```
source v venv/bin/activate
```

- Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

- В головной директории создайте файл .env, где будут храниться secrets:
```
DEBUG=True  # False для продакшна
SECRET_KEY=сгенерируй, например, здесь: https://djecrety.ir/
ALLOWED_HOSTS=127.0.0.1,localhost
```
- Также, если в головной директории отстуствует файл `db.sqlite3`, его потребуется
создать.

- Находясь в головной директории (в папке с файлом manage.py), выполнить миграции:
```
python3 manage.py migrate
```

- Создать суперпользователя:
```commandline
python3 manage.py createsuperuser
```

- Запустить проект:
```
python3 manage.py runserver
```

- В браузере перейти по адресу `http://127.0.0.1:8000/admin` и заполнить БД
необходимыми данными.

- Для тестирования api перейдите в браузере по адресу `http://127.0.0.1:8000/docs`.
- Для скачивания и передачи схемы api на той же странице в браузере откройте
раздел `schema`, выберите формат `yaml` и интересующий язык (например, `ru`).
`Execute` - и файл со схемой api доступен для скачивания.


## Тесты и code-styling
### Запуск flake8 (из головной директории):
```commandline
flake8
```
### Запуск тестов (из головной директории):
```commandline
pytest med_refbook/tests.py
```