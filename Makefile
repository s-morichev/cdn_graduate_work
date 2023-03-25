include .env

auth-init:
	docker compose exec auth flask db upgrade
	docker compose exec auth flask insert-roles
	docker compose exec auth flask createsuperuser --email ${AUTH_SUPERUSER_LOGIN} --password ${AUTH_SUPERUSER_PASSWORD}

dev-run:
	docker compose up --build -d
	sleep 5  # ждем запуск постгрес для применения миграций
	$(MAKE) auth-init
	docker compose exec auth python fake_data.py

format:
	black .
	isort .

lint:
	black --check .
	isort --check-only .
	flake8 .
