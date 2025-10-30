# syntax=docker/dockerfile:1.7

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore

WORKDIR /app

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential cmake \
      libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 libgomp1 \
      fonts-dejavu-core && \
    rm -rf /var/lib/apt/lists/*


COPY requirements/ ./requirements/

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements/linux_reqs.txt

COPY src ./src
COPY alembic ./alembic
COPY alembic.ini .

RUN useradd -m app && chown -R app:app /app
USER app

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
