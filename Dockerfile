FROM python:3.13.10-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /code

ENV PATH="/code/.venv/bin:$PATH"

COPY "pyproject.toml" "uv.lock" ".python-version" ./
RUN uv sync --locked

COPY . .

# Set entry point
ENTRYPOINT ["uv", "run", "python", "pipeline/ingest_xlsx_into_sql.py"]