### Сервис загрузки файлов из одного хранилища Minio в другое
API - FastAPI + Celery. В качестве очереди для Celery - Redis. 
Отдельно поднимается контейнер с Flower - Dashboard для Сelery

### Endpoints
* /ping - отвечает "pong"
* POST /v1/tasks/upload - загружает файл из `source` в `destination`  
-IN:`{"file": "P1010043.JPG", "source": "localhost:9000", "destination": "localhost:19000"}`  
-OUT:`{"task_id": "82cdb1f0-1b1a-4da8-acde-83f08dffb703"}`    
* POST /v1/tasks/delete - удаляет файл из `storage`  
-IN:`{"file": "1.MP4", "storage": "minio1:9000" }`  
-OUT:`{"task_id": "82cdb1f0-1b1a-4da8-acde-83f08dffb703"}`
* GET /v1/tasks/status/{task_id} - возвращает статус задачи по ее `task_id`  
  -OUT:  
 `{
 "task_id": "82cdb1f0-1b1a-4da8-acde-83f08dffb703",
  "task_status": "SUCCESS",
  "task_result": "{'name': 'P1010043.JPG', 'etag': 'af45e05f6ccf09f776e038d4a70a34c9', 'size': 2981355}"
}`

### Запуск
`make run-storage` - запускает два контейнера minio на портах 9000/1 и 19000/1 (логин `root` пароль `123456qwe`)
* minio_1: http://localhost:9000
* minio_2: http://localhost:19001  

`.env.s3ls.example` переименовать в `.env.s3ls` - используется для запуска сервиса в докере  
`make run-service` - запускает 4 контейнера, составляющие сервис загрузки  
* Dashboard доступен на http://localhost:5555
* API http://localhost:8000/docs
