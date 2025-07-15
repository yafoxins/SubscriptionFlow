# Nginx Configuration

Эта папка содержит конфигурацию Nginx для проекта SubscriptionFlow.

## Структура

```
nginx/
├── nginx.conf          # Основная конфигурация Nginx
├── ssl/                # SSL сертификаты (для продакшена)
└── README.md           # Этот файл
```

## Конфигурация

### Основные особенности:

- **Reverse Proxy** для FastAPI приложения
- **Gzip сжатие** для оптимизации
- **Кэширование статических файлов**
- **CORS настройки** для API
- **SSL/TLS поддержка** (для продакшена)
- **Безопасность** с дополнительными заголовками

### Порты:

- **80** - HTTP
- **443** - HTTPS (SSL)

### Домены:

По умолчанию настроено для:
- `localhost`
- `subscription-flow.local`

Для продакшена измените `server_name` в `nginx.conf`.

## SSL Сертификаты

Для продакшена поместите ваши SSL сертификаты в папку `ssl/`:

- `cert.pem` - SSL сертификат
- `key.pem` - приватный ключ

Затем раскомментируйте строки в `nginx.conf`:

```nginx
ssl_certificate /etc/nginx/ssl/cert.pem;
ssl_certificate_key /etc/nginx/ssl/key.pem;
```

## Перезагрузка конфигурации

```bash
# Через Makefile
make nginx-reload

# Или напрямую
docker-compose exec nginx nginx -s reload
```

## Логи

Логи Nginx доступны в контейнере:
- `/var/log/nginx/access.log`
- `/var/log/nginx/error.log`

Для просмотра логов:
```bash
docker-compose logs nginx
``` 