FROM python:latest

WORKDIR /app

COPY . /app/

RUN pip install poetry

RUN poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-root

CMD [ "poetry","run","uvicorn","02_product.main:app","--host","0.0.0.0","--port","8091","--reload" ]