run-storage:
	docker compose -f docker-compose.local.yml up -d --build

run-redis:
	docker run -d --name some-redis -p 6379:6379 redis:7.0.10-alpine

run-api:
	sh -c "cd src && uvicorn main:app --reload"

run-worker:
	sh -c "cd src && celery -A workers.worker.celery worker --loglevel=info"

run-flower:
	celery --broker=redis://localhost:6379/0 flower

run-service:
	docker compose -f docker-compose.service.yml up -d --build
