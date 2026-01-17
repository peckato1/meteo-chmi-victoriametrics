FROM alpine:3.23

ENV UV_NO_DEV=1

RUN apk update && apk add uv

COPY main.py /app/main.py
COPY chmi/ /app/chmi/
COPY uv.lock /app/uv.lock
COPY pyproject.toml /app/pyproject.toml

WORKDIR /app
RUN uv sync

CMD ["uv", "run", "main.py"]
