
### Запуск

docker compose up -d --build sync-service minio-0 createbuckets


### Тесты

Тестирование на хосте

Переименовать в ./cdn/sync_service .env.test.example в .env.test
- `make run-test-db` запустить контейнер с тестовой базой данных
- `make test-sync`
- `make stop-test-db` удалить контейнер с тестовой базой данных

