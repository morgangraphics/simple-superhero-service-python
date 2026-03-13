# ARG before FROM parameterises the base image tag; override with --build-arg PYTHON=3.13
ARG PYTHON=3.12

FROM python:${PYTHON}-slim
LABEL maintainer="MORGANGRAPHICS,INC"

ARG PORT=8000

# Install curl (HEALTHCHECK) and dumb-init (PID 1 / signal forwarding).
# Clean up apt cache so it is not stored in the layer.
RUN apt-get update -y \
  && apt-get upgrade -y \
  && apt-get install -y --no-install-recommends curl dumb-init \
  && rm -rf /var/lib/apt/lists/*

# Install uv for fast, reproducible dependency installation.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# The official python image ships with a non-root user we create explicitly.
RUN groupadd --gid 1000 appuser && useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

USER appuser

ENV PORT=${PORT}
# Keep Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Tell uv to install into the system Python inside the container
ENV UV_SYSTEM_PYTHON=1

WORKDIR /home/appuser/service

# Copy dependency manifests first so the install layer is only invalidated
# when dependencies change, not on every source file change.
COPY --chown=appuser:appuser pyproject.toml uv.lock* ./

RUN uv sync --no-dev --frozen

# NOTE: sssp-cert.pem and sssp-key.pem are excluded via .dockerignore and must
# be mounted at runtime, e.g.:
#   docker run -v /path/to/certs:/home/appuser/service ...
COPY --chown=appuser:appuser . .

EXPOSE ${PORT}

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -fsk https://localhost:${PORT}/healthcheck || exit 1

# https://github.com/Yelp/dumb-init#usage
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["python", "main.py"]
