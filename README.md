# Телеграм бот "Тайный Санта" 🎅
Сервис предназначен для проведения предновогодней игры "Тайный Санта". С помощью бота можно создать игру, получить ссылку для приглашения участников и провести жеребьевку. Каждому участнику в пределах игры будет назначен человек, которому он должен приготовить подарок. При создании игры существует возможность ограничить ценовой диапазон подарков. 
При регистрации участник может указать свои пожелания для подарка.
Жеребьевка проводится автоматически либо принудительно через админ-интерфейс с рассылкой уведомлений участникам.

# Установка

Все рекомендации даются при установке в `/opt`. При установке в другую директорию необходимо внести изменения в файлы сервисов.

Клонируйте репозиторий:

```shell-script
git clone git@github.com:MrSabin/secret-santa.git
```
Скопируйте или переименуйте файл env_example в корне репозитория и заполните своими данными:

```shell-script
cd /opt/secret-santa
mv env_example .env
```

* SECRET_KEY - секретный ключ Django
* DEBUG - отладочный режим, ставим False
* ALLOWED_HOSTS - вписываем домен либо IP сервера, на который деплоим
* REDIS_HOST - адрес сервера Redis, по умолчанию 127.0.0.1
* REDIS_PORT - порт Redis, по умолчанию 6379
* EMAIL_HOST - почтовый хост для рассылки уведомлений
* EMAIL_HOST_USER - логин почты
* EMAIL_HOST_PASSWORD - пароль почты
* TG_BOT_API - токен API бота телеграм

Создаем виртуальное окружение

```shell-script
python -m venv .venv
```

Устанавливаем зависимости

```shell-script
pip install -r requirements.txt
```

Копируем сервисы (либо под root, либо sudo)

```shell-script
cp admin-panel.service.example /etc/systemd/system/admin-panel.service
cp bot.service.example /etc/systemd/system/bot.service
cp celery.service.example /etc/systemd/system/celery.service
```

Устанавливаем Redis

```shell-script
sudo apt install redis
```

## Запуск

Собираем статику м накатываем миграции

```shell-script
python manage.py migrate
python manage.py collectstatic
```

Перезагружаем демон systemd

```shell-script
sudo systemd daemon-reload
```

Устанавливаем сервисы

```shell-script
sudo systemd enable admin-panel.service
sudo systemd enable bot.service
sudo systemd enable celery.service
```

Запускаем сервисы

```shell-script
sudo systemctl start admin-panel.service
sudo systemctl start bot.service
sudo systemctl start celery.service
```
