FROM python:3.7-alpine as base

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install --upgrade pip

RUN apk add build-base

COPY . .

RUN pip3 install -e .

ENV FLASK_APP=flaskr
ENV FLASK_ENV=development

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_HOST=ebook-app_psql-db_1
ENV POSTGRES_PORT=5432


FROM base AS build-test

ENV POSTGRES_DB=ebook_db_test

RUN pip3 install pytest 

CMD [ "python3", "-m" , "pytest"]


FROM base AS build-run

ENV POSTGRES_DB=ebook_db

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
