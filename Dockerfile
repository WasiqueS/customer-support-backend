FROM python:3.8-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy only pyproject.toml and poetry.lock for caching
COPY pyproject.toml poetry.lock* /app/

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy rest of your code
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
