FROM python:3.8-slim-buster

WORKDIR /app/cache

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "-u", "caching_server.py"]
