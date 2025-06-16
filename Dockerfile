FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean

WORKDIR /app/src

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9500

CMD ["python", "app/src/main.py"]
