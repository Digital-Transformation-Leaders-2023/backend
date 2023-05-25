## backend

### Project setup
```
docker-compose up mongo postgres-db -d

pip install -r requirements.txt

uvicorn app.main:app --host 0.0.0.0 --port 8001
```

 ### Как накатывать миграции 
по дефолту накатываются на localhost, но, если в env указать prod, то будут в прод, автомигратор после мерджа позже настрою, если нужен будет
```
alembic revision --autogenerate -m "create test table"

alembic upgrade head
```