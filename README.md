# Unify

**Unify**, is an open-source system RESTful API that offers simplify tasks with course managment, assesment and related operations for educational institutions. It provides endpoints for handling users, groups, disciplines, courses, etc.

## **Features**

- High-performace Python web framework for building APIs with automatic OpenAPI & Swagger & ReDoc docs. 
- Fully async using async def path operation, enabling non-blocking oprations.
- Fast and robust data validation and serialization using Pydantic library. 
- Secure authentification using OAuth2.0 standard with username / password and access token (JWT).
- NoSQL databases:
    - Integrated with MongoDB using an async pymongo (related to 4.13 version) for efficient data access.
    - Supports Redis caching using async aioredis. 
- Seamless containerzation using Docker / Docker compose.
- Test suite using pytest framework.
- Environment configuration.


# **Installation**

The current recommend way to install unifyapi is from source.

## From source
```bash
git clone https://github.com/th0truth/unifyapi.git
cd unifyapi
```

## Requirements

- [Python +3.11](https://www.python.org/downloads/)
- [Docker](https://docs.docker.com/get-started/get-docker/)

# Configure

You must update configs in the `.env` files to customize your configuration. 

# **How to use**

```bash
bash scripts/build.sh

bash scripts/run.sh
```

or

```bash
python -m venv venv
source Scripts/venv/activate

pip install poetry

poetry install --no-root

docker compose up
```
