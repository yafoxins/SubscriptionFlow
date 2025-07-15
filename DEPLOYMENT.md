# 🚀 Развертывание SubscriptionFlow

Подробное руководство по развертыванию проекта SubscriptionFlow в различных средах.

## 📋 Предварительные требования

### Для локальной разработки:
- Docker и Docker Compose
- Git
- Make (опционально)

### Для продакшена:
- Docker и Docker Compose
- SSL сертификаты
- Домен (опционально)

## 🔧 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-username/subscription-flow.git
cd subscription-flow
```

### 2. Настройка переменных окружения

```bash
# Скопируйте пример конфигурации
cp env.example .env

# Отредактируйте .env файл
nano .env
```

### 3. Запуск приложения

```bash
# Используя Makefile (рекомендуется)
make setup
make dev

# Или напрямую с Docker Compose
docker-compose up --build -d
```

### 4. Проверка работы

Откройте браузер и перейдите по адресу:
- **HTTP**: http://localhost:8000
- **HTTPS**: https://localhost (если настроен SSL)

## 🐳 Docker Compose

### Структура сервисов:

```yaml
services:
  app:           # FastAPI приложение (порт 8000)
  postgres:      # База данных PostgreSQL (порт 5432)
  redis:         # Кэш Redis (порт 6379)
  nginx:         # Reverse proxy (порт 80/443)
```

### Полезные команды:

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Очистка
docker-compose down -v --rmi all
```

## 🔒 Продакшн развертывание

### 1. Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Настройка SSL

```bash
# Создание SSL сертификатов (Let's Encrypt)
sudo apt install certbot

# Получение сертификата
sudo certbot certonly --standalone -d your-domain.com

# Копирование сертификатов
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
```

### 3. Настройка домена

Отредактируйте `nginx/nginx.conf`:

```nginx
server_name your-domain.com www.your-domain.com;
```

### 4. Продакшн переменные

Создайте `.env.prod`:

```env
DATABASE_URL=postgresql://postgres:strong-password@postgres:5432/subscriptions_db
REDIS_URL=redis://redis:6379
SECRET_KEY=your-super-secret-production-key
DEBUG=false
LOG_LEVEL=WARNING
```

### 5. Запуск в продакшне

```bash
# Создание продакшн конфигурации
cp docker-compose.yml docker-compose.prod.yml

# Запуск
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📊 Мониторинг

### Логи приложения:

```bash
# Все логи
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f app
docker-compose logs -f nginx
docker-compose logs -f postgres
```

### Мониторинг ресурсов:

```bash
# Статистика контейнеров
docker stats

# Через Makefile
make monitor
```

### Health Check:

```bash
# Проверка здоровья приложения
curl http://localhost/health

# Статус сервисов
make status
```

## 🔧 Обслуживание

### Резервное копирование:

```bash
# Создание резервной копии БД
make backup

# Восстановление
make restore
```

### Обновление приложения:

```bash
# Остановка
docker-compose down

# Обновление кода
git pull origin main

# Пересборка и запуск
docker-compose up --build -d
```

### Миграции базы данных:

```bash
# Запуск миграций
make db-migrate

# Сброс БД (осторожно!)
make db-reset
```

## 🛠 Устранение неполадок

### Проблемы с подключением к БД:

```bash
# Проверка статуса PostgreSQL
docker-compose exec postgres pg_isready

# Подключение к БД
docker-compose exec postgres psql -U postgres -d subscriptions_db
```

### Проблемы с Redis:

```bash
# Проверка Redis
docker-compose exec redis redis-cli ping

# Очистка кэша
docker-compose exec redis redis-cli FLUSHALL
```

### Проблемы с Nginx:

```bash
# Проверка конфигурации
docker-compose exec nginx nginx -t

# Перезагрузка
make nginx-reload
```

### Проблемы с приложением:

```bash
# Логи приложения
docker-compose logs app

# Shell в контейнере
make shell

# Перезапуск
docker-compose restart app
```

## 🔐 Безопасность

### Рекомендации для продакшена:

1. **Измените все пароли по умолчанию**
2. **Используйте сильные SECRET_KEY**
3. **Настройте SSL/TLS**
4. **Ограничьте доступ к портам**
5. **Регулярно обновляйте зависимости**
6. **Настройте firewall**

### Firewall (UFW):

```bash
# Установка UFW
sudo apt install ufw

# Настройка правил
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 📈 Масштабирование

### Горизонтальное масштабирование:

```bash
# Увеличение количества экземпляров приложения
docker-compose up -d --scale app=3
```

### Load Balancer:

Для продакшена рекомендуется использовать внешний load balancer (например, HAProxy или Cloud Load Balancer).

## 🔄 Автоматизация

### CI/CD с GitHub Actions:

Создайте `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        uses: appleboy/ssh-action@v0.1.4
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.KEY }}
          script: |
            cd /path/to/subscription-flow
            git pull origin main
            docker-compose down
            docker-compose up --build -d
```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи: `docker-compose logs`
2. Изучите документацию в README.md
3. Создайте issue в GitHub
4. Обратитесь к автору проекта

---

**Удачного развертывания! 🚀** 