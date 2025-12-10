FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

ENV PORT=8000

CMD gunicorn --bind "0.0.0.0:${PORT}" --workers 4 "app:create_app()"