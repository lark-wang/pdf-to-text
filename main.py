from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import pytesseract
import numpy as np
import cv2
from pdf2image import convert_from_bytes
from fastapi.middleware.cors import CORSMiddleware
import io

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    contents = await file.read()
    pages = convert_from_bytes(contents, dpi=200)

    text_str = ""

    for page in pages:

        curr_page = np.array(page)
        rotated = cv2.rotate(curr_page, cv2.ROTATE_90_CLOCKWISE)
        
        h, w, _ = rotated.shape
        mid_x = w // 2
        width = 300  

        left_page  = rotated[:, :mid_x + width]
        right_page = rotated[:, mid_x + width:]

        text_left  = pytesseract.image_to_string(left_page, lang="eng")
        text_right = pytesseract.image_to_string(right_page, lang="eng")

        text_str += text_left + "\n" + text_right + "\n"
        
    print("=== OCR OUTPUT START ===")
    print(repr(text_str))  
    print("=== OCR OUTPUT END ===")

    return JSONResponse({"text": text_str})
