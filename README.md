## backend

### Project setup
```
docker-compose up -d

pip install -r requirements.txt

uvicorn app.main:app --host 0.0.0.0 --port 8001
```