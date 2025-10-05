FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY backend /app/backend

WORKDIR /app/backend/src

ENV PYTHONPATH=/app

EXPOSE 6700

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "6700"]