FROM python:3.10

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /usr/src/app/app

CMD ["uvicorn", "app.main:app", "--host", "", "--port", "8001"]
