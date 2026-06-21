FROM python:3.12-slim

ENV POETRY_VERSION=1.8.3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installation de Google Chrome de manière sécurisée (sans apt-key)
RUN apt-get update && apt-get install -y \
    wget \
    --no-install-recommends && \
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb --no-install-recommends && \
    rm google-chrome-stable_current_amd64.deb && \
    rm -rf /var/lib/apt/lists/*

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app

# On ne copie QUE le pyproject.toml pour forcer Render à recréer les bons liens
COPY pyproject.toml /app/

# Installation des dépendances (sans les paquets de développement)
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi --only main

COPY . /app

ENTRYPOINT ["poetry", "run", "python", "main.py"]
