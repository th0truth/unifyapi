# UnifyAPI

**UnifyAPI**, also knows as **unify**, is an open-source system RESTful API that offers simplify tasks with course managment, assesment and related operations for educational institutions. It provides endpoints for handling users, groups, disciplines, courses, etc.

## Features

- High-performace Python web framework for building APIs with automatic OpenAPI & Swagger & ReDoc docs. 
- Fully async using `async def` path operation, enabling non-blocking oprations.
- Fast and robust data validation and serialization using `Pydantic` library. 
- NoSQL databases:
    - Integrated with `MongoDB` using an async `pymotor` (related on 4.13 version) for efficient data access.
    - Supports `Redis` caching using async `aioredis`. 
- Seamless containerzation using `Docker` / `Docker compose`.
- Test suite using `pytest` framework.
- Environment configuration.

# Requirements

- [Python +3.11](https://www.python.org/downloads/)
- [Docker](https://docs.docker.com/get-started/get-docker/)

# Installation

The current recommend way to install unifyapi is from source.

## From source
```bash
git clone https://github.com/th0truth/unifyapi.git
cd unifyapi

python -m venv venv
source venv/bin/activate

pip install poetry

poetry install
```

# Usage

```bash
docker compose up
```