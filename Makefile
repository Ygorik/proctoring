.PHONY: help build up down logs clean restart recreate test

# Переменные
COMPOSE_FILE = ci-cd/docker-compose.yml
DOCKERFILE = ci-cd/Dockerfile

help: ## Показать справку по доступным командам
	@echo "Доступные команды:"
	@echo ""
	@echo "Docker окружение:"
	@echo "  make build       - Собрать Docker образы"
	@echo "  make up          - Запустить контейнеры"
	@echo "  make down        - Остановить контейнеры"
	@echo "  make logs        - Показать логи контейнеров"
	@echo "  make clean       - Остановить и удалить контейнеры, сети и volumes"
	@echo "  make restart     - Перезапустить контейнеры"
	@echo "  make recreate    - Пересоздать контейнеры (применить изменения .env)"
	@echo "  make test        - Запустить тесты в контейнере"

# Команды для Docker окружения
build: ## Собрать Docker образы
	docker-compose -f $(COMPOSE_FILE) build

up: ## Запустить контейнеры
	docker-compose -f $(COMPOSE_FILE) up -d

down: ## Остановить контейнеры
	docker-compose -f $(COMPOSE_FILE) down

logs: ## Показать логи контейнеров
	docker-compose -f $(COMPOSE_FILE) logs -f

clean: ## Остановить и удалить контейнеры, сети и volumes
	docker-compose -f $(COMPOSE_FILE) down -v --remove-orphans

restart: ## Перезапустить контейнеры
	docker-compose -f $(COMPOSE_FILE) restart

recreate: ## Пересоздать контейнеры (применить изменения .env)
	docker-compose -f $(COMPOSE_FILE) up -d --force-recreate

test: ## Запустить тесты в контейнере
	docker-compose -f $(COMPOSE_FILE) exec app pytest -v tests/
