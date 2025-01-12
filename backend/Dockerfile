#1#
FROM python:3.13 AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

RUN --mount=type=bind,source=requirements.txt,target=/app/requirements.txt \
  pip wheel --no-cache-dir --no-deps -r /app/requirements.txt --wheel-dir /app/wheels

#2#
FROM python:3.13-slim

COPY --from=builder /app/wheels /wheels

RUN apt-get update \
    && apt-get install -y --no-install-recommends libxml2 libmariadb3 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install --no-cache --no-cache-dir /wheels/*

WORKDIR /app
COPY . .
CMD ["bash", "-c", "gunicorn main.wsgi:application --workers 4 --threads 2 -b :${BACKEND_PORT}"]
