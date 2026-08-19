FROM python:3.13-alpine3.23
LABEL maintainer="sardor.tozhiev@gmail.com"

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN adduser \
    --disabled-password \
    --no-create-home \
    my_user

USER my_user
