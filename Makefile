.PHONY: help build up down logs clean test lint format install dev prod

# Переменные
COMPOSE_FILE = docker-compose.yml
APP_NAME = subscription-flow

# Цвета для вывода
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Показать справку по командам
	@echo "$(GREEN)SubscriptionFlow - Умный менеджер подписок$(NC)"
	@echo ""
	@echo "$(YELLOW)Доступные команды:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Собрать Docker образы
	@echo "$(GREEN)Сборка Docker образов...$(NC)"
	docker-compose -f $(COMPOSE_FILE) build

up: ## Запустить приложение
	@echo "$(GREEN)Запуск приложения...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d

down: ## Остановить приложение
	@echo "$(YELLOW)Остановка приложения...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down

logs: ## Показать логи
	@echo "$(GREEN)Логи приложения:$(NC)"
	docker-compose -f $(COMPOSE_FILE) logs -f

clean: ## Очистить все контейнеры и образы
	@echo "$(RED)Очистка Docker ресурсов...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down -v --rmi all
	docker system prune -f

install: ## Установить зависимости локально
	@echo "$(GREEN)Установка Python зависимостей...$(NC)"
	pip install -r requirements.txt

dev: ## Запустить в режиме разработки
	@echo "$(GREEN)Запуск в режиме разработки...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up --build -d
	@echo "$(GREEN)Приложение доступно по адресу: http://localhost:8000$(NC)"

prod: ## Запустить в продакшн режиме
	@echo "$(GREEN)Запуск в продакшн режиме...$(NC)"
	docker-compose -f $(COMPOSE_FILE) -f docker-compose.prod.yml up -d

test: ## Запустить тесты
	@echo "$(GREEN)Запуск тестов...$(NC)"
	python -m pytest tests/ -v

lint: ## Проверить код линтером
	@echo "$(GREEN)Проверка кода...$(NC)"
	flake8 app/ --max-line-length=88 --extend-ignore=E203,W503
	black --check app/

format: ## Форматировать код
	@echo "$(GREEN)Форматирование кода...$(NC)"
	black app/
	isort app/

db-migrate: ## Запустить миграции базы данных
	@echo "$(GREEN)Запуск миграций...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec app alembic upgrade head

db-reset: ## Сбросить базу данных
	@echo "$(RED)Сброс базы данных...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down -v
	docker-compose -f $(COMPOSE_FILE) up -d postgres redis
	sleep 5
	docker-compose -f $(COMPOSE_FILE) exec app alembic upgrade head

shell: ## Открыть shell в контейнере приложения
	@echo "$(GREEN)Открытие shell в контейнере...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec app bash

status: ## Показать статус сервисов
	@echo "$(GREEN)Статус сервисов:$(NC)"
	docker-compose -f $(COMPOSE_FILE) ps

restart: ## Перезапустить приложение
	@echo "$(YELLOW)Перезапуск приложения...$(NC)"
	docker-compose -f $(COMPOSE_FILE) restart

backup: ## Создать резервную копию базы данных
	@echo "$(GREEN)Создание резервной копии...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec postgres pg_dump -U postgres subscriptions_db > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore: ## Восстановить базу данных из резервной копии
	@echo "$(GREEN)Восстановление базы данных...$(NC)"
	@read -p "Введите имя файла резервной копии: " backup_file; \
	docker-compose -f $(COMPOSE_FILE) exec -T postgres psql -U postgres subscriptions_db < $$backup_file

nginx-reload: ## Перезагрузить конфигурацию Nginx
	@echo "$(GREEN)Перезагрузка Nginx...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec nginx nginx -s reload

monitor: ## Мониторинг ресурсов
	@echo "$(GREEN)Мониторинг ресурсов:$(NC)"
	docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

setup: ## Первоначальная настройка проекта
	@echo "$(GREEN)Первоначальная настройка проекта...$(NC)"
	@if [ ! -f .env ]; then \
		cp env.example .env; \
		echo "$(YELLOW)Создан файл .env из env.example$(NC)"; \
		echo "$(YELLOW)Отредактируйте .env файл перед запуском$(NC)"; \
	fi
	@echo "$(GREEN)Настройка завершена!$(NC)"
	@echo "$(GREEN)Запустите 'make dev' для запуска приложения$(NC)" 