#!/usr/bin/env python3
"""
Typhoon OCR API Server
รองรับการ OCR จาก URL และส่งผลลัพธ์ JSON กลับมาทันที
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
import requests
import tempfile
import os
import logging
import base64
from dotenv import load_dotenv
from typing import Optional
from typhoon_ocr import ocr_document

# โหลด environment variables
load_dotenv('config.env')

# ตั้งค่า logging
logging.basicConfig(level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Typhoon OCR API",
    description="API สำหรับ OCR เอกสารและรูปภาพจาก URL",
    version="1.0.0"
)

class OCRRequest(BaseModel):
    url: Optional[HttpUrl] = None
    base64Image: Optional[str] = None
    task_type: Optional[str] = "default"
    page_num: Optional[int] = 1

class OCRResponse(BaseModel):
    success: bool
    text: Optional[str] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None

def download_file_from_url(url: str) -> tuple[str, int]:
    """ดาวน์โหลดไฟล์จาก URL และบันทึกเป็นไฟล์ชั่วคราว"""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # สร้างไฟล์ชั่วคราว
        file_extension = get_file_extension_from_url(url)
        temp_file = tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=file_extension
        )
        
        file_size = 0
        # เขียนไฟล์
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
            file_size += len(chunk)
        
        temp_file.close()
        logger.info(f"ดาวน์โหลดไฟล์สำเร็จ: {temp_file.name} (ขนาด: {file_size} bytes)")
        return temp_file.name, file_size
        
    except Exception as e:
        logger.error(f"เกิดข้อผิดพลาดในการดาวน์โหลด: {e}")
        raise HTTPException(status_code=400, detail=f"ไม่สามารถดาวน์โหลดไฟล์ได้: {str(e)}")

def save_base64_to_file(base64_data: str, file_extension: str = ".jpg") -> tuple[str, int]:
    """แปลง base64 เป็นไฟล์และบันทึกเป็นไฟล์ชั่วคราว"""
    try:
        # ลบ data URL prefix ถ้ามี
        if base64_data.startswith('data:'):
            base64_data = base64_data.split(',')[1]
        
        # แปลง base64 เป็น bytes
        image_data = base64.b64decode(base64_data)
        
        # สร้างไฟล์ชั่วคราว
        temp_file = tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=file_extension
        )
        
        # เขียนไฟล์
        temp_file.write(image_data)
        temp_file.close()
        
        file_size = len(image_data)
        logger.info(f"แปลง base64 สำเร็จ: {temp_file.name} (ขนาด: {file_size} bytes)")
        return temp_file.name, file_size
        
    except Exception as e:
        logger.error(f"เกิดข้อผิดพลาดในการแปลง base64: {e}")
        raise HTTPException(status_code=400, detail=f"ไม่สามารถแปลง base64 ได้: {str(e)}")

def get_file_extension_from_url(url: str) -> str:
    """ดึงนามสกุลไฟล์จาก URL"""
    # รองรับไฟล์ที่ใช้บ่อย
    supported_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp']
    
    # หานามสกุลจาก URL
    for ext in supported_extensions:
        if url.lower().endswith(ext):
            return ext
    
    # ถ้าไม่มีนามสกุล ให้เดาว่าเป็นรูปภาพ
    return '.jpg'

def get_file_type_from_extension(extension: str) -> str:
    """แปลงนามสกุลไฟล์เป็นประเภทไฟล์"""
    extension = extension.lower()
    if extension in ['.pdf']:
        return 'PDF'
    elif extension in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
        return 'Image'
    else:
        return 'Unknown'

def process_ocr_sync(url: str = None, base64_data: str = None, task_type: str = "default", page_num: int = 1):
    """ประมวลผล OCR แบบ synchronous"""
    import time
    start_time = time.time()
    
    try:
        # ตรวจสอบ task_type
        if task_type not in ["default", "structure"]:
            raise HTTPException(status_code=400, detail="task_type ต้องเป็น 'default' หรือ 'structure'")
        
        # ตรวจสอบ page_num
        if page_num < 1:
            raise HTTPException(status_code=400, detail="page_num ต้องมากกว่า 0")
        
        # ตรวจสอบว่ามี URL หรือ base64
        if not url and not base64_data:
            raise HTTPException(status_code=400, detail="ต้องระบุ URL หรือ base64Image")
        
        if url and base64_data:
            raise HTTPException(status_code=400, detail="ระบุได้แค่ URL หรือ base64Image อย่างใดอย่างหนึ่ง")
        
        temp_file_path = None
        file_size = None
        file_type = None
        
        try:
            if url:
                logger.info(f"เริ่มประมวลผล OCR จาก URL: {url}")
                # ดาวน์โหลดไฟล์
                temp_file_path, file_size = download_file_from_url(url)
                file_extension = get_file_extension_from_url(url)
                file_type = get_file_type_from_extension(file_extension)
            else:
                logger.info("เริ่มประมวลผล OCR จาก base64")
                # แปลง base64 เป็นไฟล์
                temp_file_path, file_size = save_base64_to_file(base64_data)
                file_type = "Image"
            
            # ประมวลผล OCR
            result = ocr_document(
                pdf_or_image_path=temp_file_path,
                task_type=task_type,
                page_num=page_num
            )
            
            processing_time = time.time() - start_time
            
            logger.info(f"OCR เสร็จสิ้น: {processing_time:.2f} วินาที")
            
            return {
                "success": True,
                "text": result,
                "error": None,
                "processing_time": round(processing_time, 2),
                "file_size": file_size,
                "file_type": file_type
            }
            
        finally:
            # ลบไฟล์ชั่วคราว
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                logger.info(f"ลบไฟล์ชั่วคราว: {temp_file_path}")
                
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"เกิดข้อผิดพลาด: {e}")
        return {
            "success": False,
            "text": None,
            "error": str(e),
            "processing_time": round(processing_time, 2),
            "file_size": None,
            "file_type": None
        }

@app.get("/")
async def root():
    """หน้าแรก"""
    return {
        "message": "Typhoon OCR API Server",
        "version": "1.0.0",
        "endpoints": {
            "GET /api/v1/": "OCR จาก URL (URL parameter)",
            "POST /api/v1/ocr/url/sync": "OCR จาก URL หรือ base64 (JSON body)",
            "GET /health": "ตรวจสอบสถานะ server",
            "GET /api/v1/ocr/supported-formats": "รูปแบบไฟล์ที่รองรับ"
        }
    }

@app.get("/api/v1/")
async def ocr_from_url_get(
    url: str = Query(..., description="URL ของไฟล์ที่ต้องการ OCR"),
    task_type: str = Query("default", description="ประเภทการประมวลผล: default หรือ structure"),
    page_num: int = Query(1, description="หมายเลขหน้า (สำหรับ PDF)")
):
    """OCR จาก URL และส่งผลลัพธ์กลับมาทันที (URL parameter)"""
    result = process_ocr_sync(url=url, task_type=task_type, page_num=page_num)
    
    # ส่งกลับเฉพาะ text หรือ error
    if result["success"]:
        return {"text": result["text"]}
    else:
        return {"error": result["error"]}

@app.post("/api/v1/ocr/url/sync", response_model=OCRResponse)
async def ocr_from_url_sync(request: OCRRequest):
    """OCR จาก URL หรือ base64 และส่งผลลัพธ์กลับมาทันที (JSON body)"""
    if request.url:
        result = process_ocr_sync(url=str(request.url), task_type=request.task_type, page_num=request.page_num)
    elif request.base64Image:
        result = process_ocr_sync(base64_data=request.base64Image, task_type=request.task_type, page_num=request.page_num)
    else:
        raise HTTPException(status_code=400, detail="ต้องระบุ URL หรือ base64Image")
    
    return OCRResponse(**result)

@app.get("/health")
async def health_check():
    """ตรวจสอบสถานะ server"""
    return {
        "status": "healthy",
        "api_key_configured": bool(os.getenv('TYPHOON_OCR_API_KEY')),
        "mode": "synchronous"
    }

@app.get("/api/v1/ocr/supported-formats")
async def get_supported_formats():
    """แสดงรูปแบบไฟล์ที่รองรับ"""
    return {
        "supported_formats": {
            "images": [".jpg", ".jpeg", ".png", ".tiff", ".bmp"],
            "documents": [".pdf"],
            "task_types": ["default", "structure"]
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    # ตรวจสอบ API Key
    api_key = os.getenv('TYPHOON_OCR_API_KEY')
    if not api_key:
        print("⚠️  ไม่พบ TYPHOON_OCR_API_KEY กรุณาตั้งค่า environment variable")
        print("ตัวอย่าง: TYPHOON_OCR_API_KEY=your_api_key_here")
        exit(1)
    
    # ใช้ port จาก environment variable หรือ default
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '8001'))
    
    print("🚀 เริ่มต้น Typhoon OCR API Server...")
    print(f"📖 API Documentation: http://localhost:{port}/docs")
    print(f"🔍 Health Check: http://localhost:{port}/health")
    print("⚡ โหมด: ส่งผลลัพธ์ทันที")
    print("🌐 URL Parameter: GET /api/v1/?url=your-url")
    
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=False  # ปิด reload สำหรับ production
    ) 