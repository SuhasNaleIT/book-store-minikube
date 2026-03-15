FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

# No apt-get needed — psycopg2-binary is pre-compiled 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 8000

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "--forwarded-allow-ips=*",  "run:app"]
