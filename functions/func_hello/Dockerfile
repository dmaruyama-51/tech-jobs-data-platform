FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

COPY functions/func_hello/main.py ./

# Cloud Functions用の環境変数を設定
ENV FUNCTION_TARGET=hello_world
ENV FUNCTION_SOURCE=main.py

# Cloud Functions Frameworkを起動
CMD ["python", "-m", "functions_framework", "--target", "hello_world"]