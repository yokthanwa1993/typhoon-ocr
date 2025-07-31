FROM python:3.12-slim

# ตั้งค่า working directory
WORKDIR /app

# ติดตั้ง system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# คัดลอก requirements และติดตั้ง Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอก source code
COPY . .

# สร้างไฟล์ .env จาก environment variables
RUN echo "TYPHOON_OCR_API_KEY=${TYPHOON_OCR_API_KEY}" > config.env && \
    echo "HOST=0.0.0.0" >> config.env && \
    echo "PORT=8001" >> config.env && \
    echo "LOG_LEVEL=INFO" >> config.env

# เปิด port
EXPOSE 8001

# รัน application
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8001"] 