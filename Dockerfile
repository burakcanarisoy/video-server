FROM python:3.11-slim

# FFmpeg yükleniyor
RUN apt-get update && apt-get install -y ffmpeg

# Çalışma dizini
WORKDIR /app

# Gereksinim dosyası kopyalanıyor ve yükleniyor
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Tüm dosyaları kopyala
COPY . .

# Uygulama başlat
CMD ["python", "app.py"]
