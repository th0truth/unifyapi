FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1

WORKDIR /app/

ENV PATH="/app/.venv/bin:$PATH"

RUN pip install --no-cache-dir poetry

COPY ./pyproject.toml /app/

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

COPY src/ /app/     
COPY .env /app/

ENV PYTHONPATH="/app/app/"

EXPOSE 10000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000", "--reload"]