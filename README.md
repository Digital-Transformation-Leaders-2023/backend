## backend

### Project setup
```
docker-compose build

docker-compose up
```

### Запуск с дебагом
```
docker-compose up -d database

pip install -r requirements.txt

uvicorn app.main:app --host 0.0.0.0 --port 8001
```