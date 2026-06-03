FROM python:3.14-slim

ARG DEV_DEPS=false

ENV TZ=Europe/Berlin \
    UV_PROJECT_ENVIRONMENT=/usr/local \
    UV_CACHE_DIR=/tmp/uv_cache \
    # Don't use hardlinks in Docker (more reliable across filesystems)
    UV_LINK_MODE=copy \
    # Pre-compile to .pyc for faster container startup
    UV_COMPILE_BYTECODE=1 \
    # Suppress the progress bar for cleaner Docker logs
    UV_NO_PROGRESS=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    locales \
    libeccodes-dev \
    && sed -i -e 's/# de_DE.UTF-8 UTF-8/de_DE.UTF-8 UTF-8/' /etc/locale.gen \
    && dpkg-reconfigure --frontend=noninteractive locales \
    && update-locale \
    && apt-get autoremove -y \
    && apt-get autoclean -y \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements to cache in layer
WORKDIR /usr/src/app


# Install dependencies
COPY pyproject.toml uv.lock* README.md ./

RUN echo "DEV_DEPS value is: ${DEV_DEPS}" && \
    # Install dependencies based on DEV_DEPS argument
    if [ "${DEV_DEPS}" = "true" ]; then \
      uv sync --frozen --no-install-project; \
    else \
      uv sync --frozen --no-install-project --no-dev; \
    fi

# Install package
# only copy the package
COPY . ./
RUN uv sync --frozen

