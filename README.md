# 📊 SubscriptionFlow - Умный менеджер подписок

<div align="center">

![SubscriptionFlow](https://img.shields.io/badge/SubscriptionFlow-📊%20Умный%20менеджер%20подписок-blue?style=for-the-badge&logo=fastapi)

**Современная веб-платформа для управления подписками с аналитикой, уведомлениями и умными категориями**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?style=flat-square&logo=postgresql)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7--alpine-red?style=flat-square)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue?style=flat-square&logo=docker)](https://www.docker.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-3.0-purple?style=flat-square&logo=tailwind-css)](https://tailwindcss.com/)

[🚀 Демо](https://sub.yafoxin.ru) • [📖 Документация](#) • [🐛 Баги](https://github.com/yafoxins/SubscriptionFlow/issues) • [💡 Предложения](https://github.com/yafoxins/SubscriptionFlow/issues)

</div>

---

## 🖼️ Скриншоты

<div align="center">

### 🏠 Главная страница
![Главная страница](images/home.png)

<details>
<summary>📊 Другие скриншоты</summary>

### 📊 Дашборд
![Дашборд](images/dashboard.png)

### 📈 Аналитика
![Аналитика](images/static.png)

### ⚙️ Настройки
![Настройки](images/set.png)

### 📋 Подписки
![Подписки](images/sub.png)

### 👨‍💼 Админ панель
![Админ панель](images/admin.png)

</details>

</div>

---

## ✨ Возможности

### 🔐 Безопасность и аутентификация
- **JWT токены** для безопасной аутентификации
- **Хеширование паролей** с bcrypt
- **Защита от SQL инъекций** через SQLAlchemy
- **Валидация данных** через Pydantic

### 📊 Аналитика и статистика
- **Детальная аналитика** расходов по категориям
- **Прогнозирование** будущих расходов
- **Тренды и инсайты** для оптимизации
- **Экспорт данных** в JSON и CSV форматах

### 🧠 Умные функции
- **Автоматическое определение категорий** по названию сервиса
- **Российские сервисы** в базе данных категорий
- **Умные уведомления** о предстоящих платежах
- **Интеграция с календарями** (Google Calendar, Outlook)

### 🎨 Современный интерфейс
- **Адаптивный дизайн** для всех устройств
- **Темная/светлая тема** (в разработке)
- **Интуитивный интерфейс** с Tailwind CSS
- **Анимации и переходы** для лучшего UX

### 🔔 Уведомления и напоминания
- **Автоматические уведомления** о платежах
- **Настраиваемые напоминания**
- **История уведомлений**
- **Статус прочтения**

---

## 🛠 Технологический стек

| Компонент | Технология | Версия |
|-----------|------------|--------|
| **Backend** | FastAPI | 0.104.1 |
| **Язык** | Python | 3.11+ |
| **База данных** | PostgreSQL | 15 |
| **Кэш** | Redis | 7-alpine |
| **Frontend** | HTML + Tailwind CSS + JavaScript | - |
| **Аутентификация** | JWT | - |
| **Контейнеризация** | Docker + Docker Compose | - |
| **Reverse Proxy** | Nginx | Alpine |

---

## 🚀 Быстрый старт

### Вариант 1: Makefile (Рекомендуется)

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/yafoxins/subscription-flow.git
cd subscription-flow

# 2. Первоначальная настройка
make setup

# 3. Запуск в режиме разработки
make dev

# 4. Откройте в браузере
open http://localhost:8000
```

### Вариант 2: Docker Compose

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/yafoxins/subscription-flow.git
cd subscription-flow

# 2. Запустите с Docker Compose
docker-compose up --build -d

# 3. Откройте в браузере
open http://localhost:8000
```

### Вариант 3: Локальная разработка

```bash
# 1. Установите зависимости
pip install -r requirements.txt

# 2. Настройте переменные окружения
cp env.example .env
# Отредактируйте .env файл

# 3. Запустите PostgreSQL и Redis
docker-compose up postgres redis -d

# 4. Запустите приложение
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🛠 Makefile Команды

Проект включает удобный Makefile для быстрой разработки:

```bash
# Основные команды
make help          # Показать справку по командам
make setup         # Первоначальная настройка проекта
make dev           # Запуск в режиме разработки
make prod          # Запуск в продакшн режиме
make build         # Собрать Docker образы
make up            # Запустить приложение
make down          # Остановить приложение
make logs          # Показать логи
make clean         # Очистить все контейнеры и образы

# Разработка
make install       # Установить зависимости локально
make test          # Запустить тесты
make lint          # Проверить код линтером
make format        # Форматировать код
make shell         # Открыть shell в контейнере

# База данных
make db-migrate    # Запустить миграции
make db-reset      # Сбросить базу данных
make backup        # Создать резервную копию БД
make restore       # Восстановить БД из резервной копии

# Мониторинг
make status        # Показать статус сервисов
make restart       # Перезапустить приложение
make monitor       # Мониторинг ресурсов
make nginx-reload  # Перезагрузить Nginx
```

---

## 🏗 Архитектура проекта

### 📊 Общая архитектура

```mermaid
flowchart LR
    FE[Frontend<br/>HTML/Tailwind/JS]
    NG[Nginx<br/>Reverse Proxy]
    API[FastAPI<br/>Backend API]
    BL[Business Logic<br/>Services]
    DB[(PostgreSQL<br/>Database)]
    RD[(Redis<br/>Cache)]
    
    FE <--> NG
    NG <--> API
    API <--> BL
    BL <--> DB
    BL <--> RD
    API <--> RD
```

### 🔄 Поток данных

```
User Request → Nginx → FastAPI → Business Logic → Database
     ↑                                                      ↓
Response ← Templates ← JSON API ← Services ← SQLAlchemy ← PostgreSQL
```

### 🏛 Слои архитектуры

#### 1. **Frontend Layer** 🎨
- **HTML Templates** - Серверный рендеринг
- **Tailwind CSS** - Современные стили
- **JavaScript** - Интерактивность
- **Chart.js** - Визуализация данных

#### 2. **API Gateway Layer** 🌐
- **Nginx** - Reverse proxy и балансировка
- **SSL/TLS** - Безопасное соединение
- **CORS** - Кросс-доменные запросы
- **Gzip** - Сжатие данных

#### 3. **Application Layer** ⚡
- **FastAPI** - Высокопроизводительный веб-фреймворк
- **JWT Authentication** - Безопасная аутентификация
- **Pydantic** - Валидация данных
- **Dependency Injection** - Чистая архитектура

#### 4. **Business Logic Layer** 🧠
- **Services** - Бизнес-логика
- **Analytics Engine** - Аналитика и прогнозы
- **Smart Categories** - ИИ для категоризации
- **Notification System** - Система уведомлений

#### 5. **Data Layer** 💾
- **PostgreSQL** - Основная база данных
- **Redis** - Кэширование и сессии
- **SQLAlchemy** - ORM для работы с БД
- **Alembic** - Миграции базы данных

---

## 📁 Структура проекта

```
subscription-flow/
├── 📁 app/                          # Основное приложение
│   ├── 📁 core/                     # Конфигурация и безопасность
│   │   ├── config.py               # Настройки приложения
│   │   └── security.py             # JWT аутентификация
│   ├── 📁 models/                   # Модели данных
│   │   ├── user.py                 # Модель пользователя
│   │   └── subscription.py         # Модели подписок
│   ├── 📁 routers/                  # API маршруты
│   │   ├── auth.py                 # Аутентификация
│   │   ├── subscriptions.py        # Управление подписками
│   │   ├── dashboard.py            # Дашборд
│   │   └── analytics.py            # Аналитика
│   ├── 📁 services/                 # Бизнес-логика
│   │   └── smart_categories.py     # Умные категории
│   └── main.py                     # Точка входа
├── 📁 templates/                    # HTML шаблоны
│   ├── base.html                   # Базовый шаблон
│   ├── dashboard.html              # Дашборд
│   ├── analytics.html              # Аналитика
│   └── ...
├── 📁 static/                       # Статические файлы
│   ├── 📁 css/                     # Стили
│   └── 📁 js/                      # JavaScript
├── 📁 nginx/                        # Nginx конфигурация
│   └── nginx.conf                  # Reverse proxy
├── 🐳 docker-compose.yml           # Docker Compose
├── 🐳 Dockerfile                   # Docker образ
├── 📋 requirements.txt              # Python зависимости
└── 📖 README.md                    # Документация
```

---

## 🔧 Конфигурация

### Переменные окружения

Создайте файл `.env` в корне проекта:

```env
# База данных
DATABASE_URL=postgresql://postgres:postgres123@postgres:5432/subscriptions_db

# Redis
REDIS_URL=redis://redis:6379

# Безопасность
SECRET_KEY=your-super-secret-key-change-in-production
DEBUG=true

# Дополнительные настройки
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

### Docker Compose

Проект включает полную конфигурацию Docker Compose с:
- **FastAPI приложение** на порту 8000
- **PostgreSQL** база данных
- **Redis** для кэширования
- **Nginx** reverse proxy на порту 80

---

## 📚 API Документация

### Аутентификация
```http
POST /api/auth/register    # Регистрация пользователя
POST /api/auth/login       # Вход в систему
```

### Подписки
```http
GET    /api/subscriptions/           # Получить все подписки
POST   /api/subscriptions/           # Создать подписку
GET    /api/subscriptions/{id}       # Получить подписку
PUT    /api/subscriptions/{id}       # Обновить подписку
DELETE /api/subscriptions/{id}       # Удалить подписку
```

### Аналитика
```http
GET /api/analytics/summary           # Общая аналитика
GET /api/analytics/export/json       # Экспорт JSON
GET /api/analytics/export/csv        # Экспорт CSV
```

### Дашборд
```http
GET /api/dashboard/stats             # Статистика дашборда
GET /api/dashboard/notifications     # Уведомления
```

---

## 🎯 Основные функции

### 💳 Управление подписками
- ✅ Добавление новых подписок
- ✅ Редактирование существующих
- ✅ Удаление подписок
- ✅ Автоматическая категоризация
- ✅ Отслеживание статуса

### 📊 Аналитика расходов
- 📈 Графики расходов по месяцам
- 🥧 Распределение по категориям
- 🔮 Прогнозирование будущих расходов
- 📊 Детальная статистика

### 🔔 Уведомления
- ⏰ Напоминания о платежах
- 📅 Интеграция с календарями
- 📱 Push уведомления (в разработке)
- 📧 Email уведомления (в разработке)

### 🧠 Умные категории
- 🤖 Автоматическое определение категории
- 🇷🇺 Поддержка российских сервисов
- 🎯 Точная классификация
- 📝 Возможность ручной настройки

---

## 🔒 Безопасность

- **JWT токены** для безопасной аутентификации
- **Хеширование паролей** с bcrypt
- **Защита от SQL инъекций** через SQLAlchemy
- **Валидация данных** через Pydantic
- **CORS настройки** для безопасности
- **Rate limiting** (в разработке)

---

## 🐳 Развертывание

### Docker Compose (Продакшн)

```bash
# Создайте .env файл с продакшн настройками
cp .env.example .env.prod

# Запустите в продакшн режиме
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Nginx Reverse Proxy

Проект включает готовую конфигурацию Nginx для:
- **SSL/TLS** терминации
- **Gzip сжатия**
- **Кэширования статических файлов**
- **Load balancing** (при необходимости)

---

## 🤝 Вклад в проект

Мы приветствуем вклад в развитие проекта! 

### Как внести вклад:

1. **Fork** репозиторий
2. Создайте **feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit** изменения (`git commit -m 'Add amazing feature'`)
4. **Push** в branch (`git push origin feature/amazing-feature`)
5. Откройте **Pull Request**

### Стандарты кода:

- Следуйте **PEP 8** для Python кода
- Используйте **типизацию** (type hints)
- Пишите **документацию** для новых функций
- Добавляйте **тесты** для новой функциональности

---

## 📄 Лицензия

Этот проект распространяется под лицензией **MIT**. См. файл `LICENSE` для подробностей.

---

## 👨‍💻 Автор

**Aleksandr Timkov** - [GitHub](https://github.com/yafoxins)

### 📞 Контакты

- **Telegram**: [@yafoxin](https://t.me/yafoxin)
- **GitHub**: [yafoxins](https://github.com/yafoxins)
- **Email**: yafoxins@gmail.com

## 💰 Поддержка проекта / Support the Project

<div align="center">

### 🇷🇺 Поддержать разработку

Если вам нравится проект, вы можете поддержать его развитие:

| 💎 Криптовалюта | 🏦 Адрес |
|-----------------|----------|
| **USDT (TRC20)** | `TPyfMGvU482U9i4mqVzvBbFmWniHDpQhhN` |
| **USDT (TON)** | `UQDwQyau0M1dPOAM1BB8_VgMMc--O2gO0ixSlWSG2PN_lKTx` |
| **Bitcoin (BTC)** | `1HFpMPEdxdNQBagkzBkJQpWDvf5dLDNmy4` |
| **TON** | `UQDwQyau0M1dPOAM1BB8_VgMMc--O2gO0ixSlWSG2PN_lKTx` |

### 🇺🇸 Support the project

If you like the project, you can support its development:

| 💎 Cryptocurrency | 🏦 Address |
|-------------------|------------|
| **USDT (TRC20)** | `TPyfMGvU482U9i4mqVzvBbFmWniHDpQhhN` |
| **USDT (TON)** | `UQDwQyau0M1dPOAM1BB8_VgMMc--O2gO0ixSlWSG2PN_lKTx` |
| **Bitcoin (BTC)** | `1HFpMPEdxdNQBagkzBkJQpWDvf5dLDNmy4` |
| **TON** | `UQDwQyau0M1dPOAM1BB8_VgMMc--O2gO0ixSlWSG2PN_lKTx` |

</div>

**Ваша поддержка помогает развивать проект! 🚀**

---

<div align="center">

**⭐ Если проект вам понравился, поставьте звездочку! ⭐**

[![GitHub stars](https://img.shields.io/github/stars/yafoxins/SubscriptionFlow?style=social)](https://github.com/yafoxins/SubscriptionFlow)
[![GitHub forks](https://img.shields.io/github/forks/yafoxins/SubscriptionFlow?style=social)](https://github.com/yafoxins/SubscriptionFlow)
[![GitHub issues](https://img.shields.io/github/issues/yafoxins/SubscriptionFlow)](https://github.com/yafoxins/SubscriptionFlow/issues)

</div> 