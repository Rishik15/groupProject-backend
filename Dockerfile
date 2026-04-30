FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY . .

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD gunicorn --worker-class eventlet --workers 1 --bind 0.0.0.0:${PORT:-8000} --log-level info --access-logfile - --error-logfile - app.main:app