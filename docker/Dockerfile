# Use the official image Python
FROM python:3.12-bullseye AS base

MAINTAINER Spashev Nurken

# Установите переменные среды
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONFAULTHANDLER 1
ENV PYTHONBUFFERED 1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV ROOT=/code
ENV TZ=Asia/Astana
ENV PATH="$ROOT/commands:$PATH"

# Add alpine mirrors
RUN set -eux; \
    apt-get update && apt-get install -y --no-install-recommends \
    apt-utils \
    libc-dev \
    gcc \
    gettext \
    screen \
    vim \
    build-essential \
    postgresql \
    postgresql-contrib \
    netcat-traditional \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR $ROOT

# Копирование кода
COPY app $ROOT

# Копирование команды
COPY docker/commands/ $ROOT/commands/
RUN chmod +x $ROOT/commands/*

# Обновление pip
RUN pip install --upgrade pip &&  pip install -r requirements.txt

EXPOSE 8000
EXPOSE 9000
