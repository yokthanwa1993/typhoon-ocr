# Typhoon OCR API Server

API Server สำหรับ OCR เอกสารและรูปภาพจาก URL โดยใช้ Typhoon OCR จาก OpenTyphoon.ai

## 📋 คุณสมบัติ

- ✅ **OCR จาก URL** - รองรับการ OCR ไฟล์จาก URL โดยตรง
- ✅ **ผลลัพธ์ทันที** - ส่งผลลัพธ์ JSON กลับมาทันที (Synchronous)
- ✅ **รองรับภาษาไทย** - อ่านภาษาไทยได้ดีมาก
- ✅ **รองรับหลายรูปแบบ** - PNG, JPEG, PDF, TIFF, BMP
- ✅ **การจัดการข้อผิดพลาด** - แสดงข้อผิดพลาดที่ชัดเจน
- ✅ **ข้อมูลครบถ้วน** - เวลา, ขนาดไฟล์, ประเภทไฟล์
- ✅ **Docker Ready** - พร้อม deploy บน CapRover

## 🚀 การติดตั้ง

### 1. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### 2. ตั้งค่า API Key
แก้ไขไฟล์ `config.env`:
```env
TYPHOON_OCR_API_KEY=your_api_key_here
HOST=0.0.0.0
PORT=8001
LOG_LEVEL=INFO
```

### 3. รัน Server
```bash
python3 api_server.py
```

Server จะรันที่ `http://localhost:8001`

## 🐳 การ Deploy บน CapRover

### 1. เตรียมไฟล์
ไฟล์ที่จำเป็นสำหรับ CapRover:
- `Dockerfile` - สำหรับ build Docker image
- `captain-definition` - กำหนดค่า CapRover
- `.dockerignore` - ไฟล์ที่ไม่ต้องการใน Docker image

### 2. Push ไป GitHub
```bash
# สร้าง repository ใหม่บน GitHub
git init
git add .
git commit -m "Initial commit: Typhoon OCR API"
git branch -M main
git remote add origin https://github.com/your-username/typhoon-ocr-api.git
git push -u origin main
```

### 3. Deploy บน CapRover
1. เข้าไปที่ CapRover dashboard
2. กด "One-Click Apps" หรือ "New App"
3. เลือก "Deploy from GitHub"
4. ใส่ GitHub repository URL
5. ตั้งค่า Environment Variables:
   ```
   TYPHOON_OCR_API_KEY=your_api_key_here
   ```
6. กด "Deploy"

### 4. ตรวจสอบการ Deploy
```bash
# ทดสอบ API
curl "https://your-app.caprover.com/api/v1/?url=https://iili.io/FNrnLOJ.png"
```

## 📖 API Endpoints

### 1. หน้าแรก
```
GET /
```

### 2. OCR จาก URL (URL Parameter) - **แนะนำ**
```
GET /api/v1/?url=YOUR_URL
```

**Parameters:**
- `url` (required): URL ของไฟล์ที่ต้องการ OCR
- `task_type` (optional): "default" หรือ "structure" (default: "default")
- `page_num` (optional): หมายเลขหน้า (สำหรับ PDF) (default: 1)

### 3. OCR จาก URL (JSON Body)
```
POST /api/v1/ocr/url/sync
```

**Request Body:**
```json
{
    "url": "https://example.com/document.pdf",
    "task_type": "default",
    "page_num": 1
}
```

### 4. ตรวจสอบสถานะ Server
```
GET /health
```

### 5. รูปแบบไฟล์ที่รองรับ
```
GET /api/v1/ocr/supported-formats
```

## 🎯 การใช้งาน

### ตัวอย่างที่ 1: รูปภาพภาษาไทย
```bash
curl "http://localhost:8001/api/v1/?url=https://iili.io/FNrnLOJ.png"
```

**ผลลัพธ์:**
```json
{
  "success": true,
  "text": "เลิกได้เลยนะ\nเอารถไปจอดไว้ตลาด\nจอดไว้ที่โลตัส\nแล้วแอบไปกับกิ๊ก",
  "error": null,
  "processing_time": 1.76,
  "file_size": 66501,
  "file_type": "Image"
}
```

### ตัวอย่างที่ 2: รูปภาพภาษาอังกฤษ
```bash
curl "http://localhost:8001/api/v1/?url=https://httpbin.org/image/png"
```

**ผลลัพธ์:**
```json
{
  "success": true,
  "text": "pig",
  "error": null,
  "processing_time": 2.68,
  "file_size": 8090,
  "file_type": "Image"
}
```

### ตัวอย่างที่ 3: PDF
```bash
curl "http://localhost:8001/api/v1/?url=https://example.com/document.pdf&page_num=1"
```

### ตัวอย่างที่ 4: ระบุ task_type
```bash
curl "http://localhost:8001/api/v1/?url=https://example.com/image.jpg&task_type=structure"
```

## 🛠️ สคริปต์ช่วยเหลือ

### 1. ดึงเฉพาะข้อความ
```bash
python3 extract_ocr_text.py "https://iili.io/FNrnLOJ.png"
```

**ผลลัพธ์:**
```
🔍 กำลัง OCR: https://iili.io/FNrnLOJ.png
📄 ข้อความที่ได้: เลิกได้เลยนะ
เอารถไปจอดไว้ตลาด
จอดไว้ที่โลตัส
แล้วแอบไปกับกิ๊ก
```

### 2. ดึงผลลัพธ์เป็น JSON
```bash
python3 extract_ocr_json.py "https://iili.io/FNrnLOJ.png"
```

**ผลลัพธ์:**
```json
{
  "text": "เลิกได้เลยนะ\nเอารถไปจอดไว้ตลาด\nจอดไว้ที่โลตัส\nแล้วแอบไปกับกิ๊ก"
}
```

## 📊 รูปแบบไฟล์ที่รองรับ

### รูปภาพ
- `.jpg`, `.jpeg`
- `.png`
- `.tiff`
- `.bmp`

### เอกสาร
- `.pdf`

### ประเภทการประมวลผล
- `default`: ประมวลผลแบบปกติ
- `structure`: ประมวลผลแบบมีโครงสร้าง

## 🔧 การตั้งค่า

### Environment Variables (config.env)
```env
# Typhoon OCR API Configuration
TYPHOON_OCR_API_KEY=your_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8001

# Logging Configuration
LOG_LEVEL=INFO
```

### Environment Variables สำหรับ CapRover
```env
TYPHOON_OCR_API_KEY=your_api_key_here
```

## 📖 API Documentation

เปิดเบราว์เซอร์ไปที่: **http://localhost:8001/docs**

## 🧪 การทดสอบ

### 1. ทดสอบ Health Check
```bash
curl http://localhost:8001/health
```

### 2. ทดสอบรูปแบบไฟล์ที่รองรับ
```bash
curl http://localhost:8001/api/v1/ocr/supported-formats
```

### 3. ทดสอบ OCR
```bash
# รูปภาพภาษาไทย
curl "http://localhost:8001/api/v1/?url=https://iili.io/FNrnLOJ.png"

# รูปภาพภาษาอังกฤษ
curl "http://localhost:8001/api/v1/?url=https://httpbin.org/image/png"
```

## ⚠️ การแก้ไขปัญหา

### 1. ไม่พบ API Key
```bash
# ตรวจสอบไฟล์ config.env
cat config.env

# ตั้งค่า API Key
echo "TYPHOON_OCR_API_KEY=your_api_key_here" >> config.env
```

### 2. Port ถูกใช้งาน
แก้ไขไฟล์ `config.env`:
```env
PORT=8002
```

### 3. ไม่สามารถดาวน์โหลดไฟล์
- ตรวจสอบ URL และการเชื่อมต่ออินเทอร์เน็ต
- ตรวจสอบว่าไฟล์มีอยู่จริง
- ตรวจสอบสิทธิ์การเข้าถึงไฟล์

### 4. ข้อผิดพลาดในการ OCR
- ตรวจสอบ API Key
- ตรวจสอบเครดิตของ Typhoon OCR
- ตรวจสอบรูปแบบไฟล์ที่รองรับ

### 5. ปัญหา CapRover
- ตรวจสอบ Environment Variables ใน CapRover
- ตรวจสอบ Logs ของ application
- ตรวจสอบ Network settings

## 📁 โครงสร้างไฟล์

```
typhoon-ocr/
├── api_server.py          # FastAPI server
├── config.env             # Configuration file (local)
├── requirements.txt       # Dependencies
├── Dockerfile            # Docker configuration
├── captain-definition    # CapRover configuration
├── .dockerignore         # Docker ignore file
├── .gitignore           # Git ignore file
├── extract_ocr_text.py   # Script สำหรับดึงข้อความ
├── extract_ocr_json.py   # Script สำหรับดึง JSON
└── README.md             # คู่มือการใช้งาน
```

## 🎯 ตัวอย่างการใช้งานจริง

### 1. ใช้งานผ่าน cURL
```bash
curl "http://localhost:8001/api/v1/?url=https://your-domain.com/image.jpg"
```

### 2. ใช้งานผ่าน Python
```python
import requests

response = requests.get(
    "http://localhost:8001/api/v1/",
    params={
        "url": "https://your-domain.com/document.pdf",
        "task_type": "default",
        "page_num": 1
    }
)

result = response.json()
if result["success"]:
    print(result["text"])
else:
    print(f"Error: {result['error']}")
```

### 3. ใช้งานผ่าน JavaScript
```javascript
fetch('http://localhost:8001/api/v1/?url=https://your-domain.com/image.jpg')
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log(data.text);
    } else {
      console.error(data.error);
    }
  });
```

### 4. ใช้งานบน CapRover
```bash
curl "https://your-app.caprover.com/api/v1/?url=https://iili.io/FNrnLOJ.png"
```

## 📈 ประสิทธิภาพ

- **ความเร็ว**: ประมวลผล 1-5 วินาทีต่อไฟล์
- **ความแม่นยำ**: อ่านภาษาไทยได้ดีมาก
- **ความเสถียร**: รองรับไฟล์ขนาดใหญ่
- **การจัดการข้อผิดพลาด**: แสดงข้อผิดพลาดที่ชัดเจน

## 🔒 ความปลอดภัย

- API Key เก็บในไฟล์ `config.env` (ไม่ควร commit ขึ้น git)
- ไฟล์ชั่วคราวถูกลบหลังประมวลผลเสร็จ
- มีการ timeout สำหรับการดาวน์โหลดไฟล์
- รองรับ HTTPS URLs

## 📞 การสนับสนุน

หากมีปัญหาในการใช้งาน สามารถตรวจสอบ:
1. Log ของ server
2. Health check endpoint
3. API documentation
4. ตัวอย่างการใช้งานใน README

---

**พัฒนาโดยใช้ Typhoon OCR จาก OpenTyphoon.ai** 