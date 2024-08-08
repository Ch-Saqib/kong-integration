FROM python:latest

WORKDIR /app

COPY . /app/

RUN pip install poetry

RUN poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-root

CMD [ "poetry","run","uvicorn","01_service.main:app","--port","8001","--reload" ]