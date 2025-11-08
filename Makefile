.PHONY: help build up down logs clean restart recreate test load-test-data clear-test-data load-test-snapshots clear-test-snapshots

# Переменные
COMPOSE_FILE = ci-cd/docker-compose.yml
DOCKERFILE = ci-cd/Dockerfile

help: ## Показать справку по доступным командам
	@echo "Доступные команды:"
	@echo ""
	@echo "Docker окружение:"
	@echo "  make build            - Собрать Docker образы"
	@echo "  make up               - Запустить контейнеры"
	@echo "  make down             - Остановить контейнеры"
	@echo "  make logs             - Показать логи контейнеров"
	@echo "  make clean            - Остановить и удалить контейнеры, сети и volumes"
	@echo "  make restart          - Перезапустить контейнеры"
	@echo "  make recreate         - Пересоздать контейнеры (применить изменения .env)"
	@echo "  make test             - Запустить тесты в контейнере"
	@echo ""
	@echo "Управление данными:"
	@echo "  make load-test-data                - Загрузить тестовые данные в БД"
	@echo "  make clear-test-data               - Удалить тестовые данные из БД"
	@echo "  make load-test-snapshots           - Загрузить тестовые фотографии (случайные + из test_photos/)"
	@echo "  make load-test-snapshots-from-dir  - Загрузить только фотографии из test_photos/"
	@echo "  make load-full-test                - Загрузить все тестовые данные и фотографии (удобная команда)"
	@echo "  make clear-test-snapshots          - Удалить тестовые фотографии"

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

# Команды для управления данными
load-test-data: ## Загрузить тестовые данные в БД
	docker-compose -f $(COMPOSE_FILE) exec app python scripts/load_test_data.py

clear-test-data: ## Удалить тестовые данные из БД
	docker-compose -f $(COMPOSE_FILE) exec app python scripts/load_test_data.py --clear

load-test-snapshots: ## Загрузить тестовые фотографии (случайные + из test_photos/)
	docker-compose -f $(COMPOSE_FILE) exec app python scripts/load_test_snapshots.py

load-test-snapshots-from-dir: ## Загрузить только фотографии из test_photos/
	docker-compose -f $(COMPOSE_FILE) exec app python scripts/load_test_snapshots.py --only-dir

clear-test-snapshots: ## Удалить тестовые фотографии
	docker-compose -f $(COMPOSE_FILE) exec app python scripts/load_test_snapshots.py --clear

load-full-test: ## Загрузить полный набор тестовых данных (данные + снимки)
	docker-compose -f $(COMPOSE_FILE) exec app python scripts/load_test_data.py
	docker-compose -f $(COMPOSE_FILE) exec app python scripts/load_test_snapshots.py --only-dir
