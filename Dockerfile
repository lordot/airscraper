FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt .

RUN python3 -m pip install -r ./requirements.txt --no-cache-dir

EXPOSE 8000

COPY . .

CMD ["python3", "main.py"]
