FROM python:3.13

WORKDIR /app

RUN pip install --upgrade pip

RUN pip install poetry

COPY ./pyproject.toml /app/ 

# RUN poetry install --no-interaction --no-ansi
# RUN poetry config virtualenvs.create false \
    # && poetry install --no-interaction --no-ansi --no-root
# 
# COPY . /app/
# 
# RUN poetry install --no-interaction --no-ansi

CMD ["uvicorn", "app/main:app", "--host", "127.0.0.0", "--port", "8000", "--reload"]