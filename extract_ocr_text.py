#!/usr/bin/env python3
"""
สคริปต์สำหรับดึงเฉพาะข้อความ OCR จาก API
"""

import requests
import json
import sys
import os
from dotenv import load_dotenv

# โหลด environment variables
load_dotenv('config.env')

def extract_ocr_text(url, task_type="default", page_num=1):
    """ดึงข้อความ OCR จาก URL"""
    try:
        # ใช้ port จาก config.env หรือ default เป็น 8001
        port = os.getenv('PORT', '8001')
        
        payload = {
            "url": url,
            "task_type": task_type,
            "page_num": page_num
        }
        
        response = requests.post(
            f"http://localhost:{port}/api/v1/ocr/url/sync",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                return data["text"]
            else:
                return f"Error: {data['error']}"
        else:
            return f"HTTP Error: {response.status_code}"
            
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 extract_ocr_text.py <url> [task_type] [page_num]")
        print("Example: python3 extract_ocr_text.py https://example.com/image.jpg")
        sys.exit(1)
    
    url = sys.argv[1]
    task_type = sys.argv[2] if len(sys.argv) > 2 else "default"
    page_num = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    
    print(f"🔍 กำลัง OCR: {url}")
    result = extract_ocr_text(url, task_type, page_num)
    print(f"📄 ข้อความที่ได้: {result}")

if __name__ == "__main__":
    main() 