FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy the rest of the code
COPY . .

CMD ["uv", "run", "init_db.py"]

# Run the app
CMD ["uv", "run", "flask", "run", "--host=0.0.0.0"]