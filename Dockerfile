FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY app/requirements.txt /app/app/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /app/app/requirements.txt

COPY . /app

RUN mkdir -p /app/data/tenants

EXPOSE 8888

CMD ["python", "app/main.py"]
