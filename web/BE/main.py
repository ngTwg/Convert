import io
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import json
import os
import tempfile
import zipfile
import pandas as pd
import qrcode
import difflib
import random
import string
import base64
from PIL import Image
from pillow_heif import register_heif_opener
register_heif_opener()

app = FastAPI(title="MultiConvert Pro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/process")
async def process_task(
    tool: str = Form(...),
    files: List[UploadFile] = File(...),
    ranges: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    watermark: Optional[str] = Form(None),
    target_format: Optional[str] = Form(None)
):
    if not files:
        raise HTTPException(status_code=400, detail="Không có file nào được gửi lên.")

    try:
        # Xử lý tính năng Home: Chuyển đổi Đa năng (Universal)
        if tool == "convert_general":
            # Trong môi trường thực, gọi engine convert sang định dạng target_format
            contents = await files[0].read()
            output_io = io.BytesIO(contents)
            output_io.seek(0)
            
            ext = f".{target_format}" if target_format else ".converted"
            new_filename = files[0].filename.split('.')[0] + ext
            
            return StreamingResponse(
                output_io, 
                media_type="application/octet-stream", 
                headers={"Content-Disposition": f'attachment; filename="universal_{new_filename}"'}
            )
            
        elif tool == "merge":
            merger = PyPDF2.PdfMerger()
            for file in files:
                contents = await file.read()
                merger.append(io.BytesIO(contents))
            
            output_io = io.BytesIO()
            merger.write(output_io)
            merger.close()
            output_io.seek(0)
            
            return StreamingResponse(
                output_io, 
                media_type="application/pdf", 
                headers={"Content-Disposition": f'attachment; filename="merged_document.pdf"'}
            )
            
        elif tool == "protect":
            if not password:
                raise HTTPException(status_code=400, detail="Chưa cung cấp mật khẩu bảo vệ.")
            
            contents = await files[0].read()
            reader = PyPDF2.PdfReader(io.BytesIO(contents))
            writer = PyPDF2.PdfWriter()
            
            for page in reader.pages:
                writer.add_page(page)
                
            writer.encrypt(password)
            
            output_io = io.BytesIO()
            writer.write(output_io)
            output_io.seek(0)
            
            return StreamingResponse(
                output_io, 
                media_type="application/pdf", 
                headers={"Content-Disposition": f'attachment; filename="protected_{files[0].filename}"'}
            )
            
        elif tool in ["split", "extract"]:
            if not ranges:
                raise HTTPException(status_code=400, detail="Chưa cung cấp khoảng trang (vd: 1-5).")
            contents = await files[0].read()
            reader = PyPDF2.PdfReader(io.BytesIO(contents))
            writer = PyPDF2.PdfWriter()
            
            try:
                start, end = map(int, ranges.split('-'))
                start -= 1 # 0-indexed
            except:
                raise HTTPException(status_code=400, detail="Định dạng ranges không hợp lệ. Hãy dùng định dạng start-end (vd: 1-3).")
            
            for i in range(len(reader.pages)):
                if start <= i < end:
                    writer.add_page(reader.pages[i])
                    
            output_io = io.BytesIO()
            writer.write(output_io)
            output_io.seek(0)
            
            action_name = "extracted" if tool == "extract" else "splitted"
            return StreamingResponse(
                output_io, 
                media_type="application/pdf", 
                headers={"Content-Disposition": f'attachment; filename="{action_name}_{files[0].filename}"'}
            )

        elif tool == "remove_pages":
            if not ranges:
                raise HTTPException(status_code=400, detail="Chưa cung cấp khoảng trang (vd: 1-5).")
            contents = await files[0].read()
            reader = PyPDF2.PdfReader(io.BytesIO(contents))
            writer = PyPDF2.PdfWriter()
            
            try:
                start, end = map(int, ranges.split('-'))
                start -= 1 # 0-indexed
            except:
                raise HTTPException(status_code=400, detail="Định dạng ranges không hợp lệ. Hãy dùng định dạng start-end (vd: 1-3).")
            
            for i in range(len(reader.pages)):
                if not (start <= i < end):
                    writer.add_page(reader.pages[i])
                    
            output_io = io.BytesIO()
            writer.write(output_io)
            output_io.seek(0)
            
            return StreamingResponse(
                output_io, 
                media_type="application/pdf", 
                headers={"Content-Disposition": f'attachment; filename="removed_pages_{files[0].filename}"'}
            )

        elif tool == "unlock":
            if not password:
                raise HTTPException(status_code=400, detail="Chưa cung cấp mật khẩu để mở khóa.")
            contents = await files[0].read()
            reader = PyPDF2.PdfReader(io.BytesIO(contents))
            
            if reader.is_encrypted:
                reader.decrypt(password)
                
            writer = PyPDF2.PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
                
            output_io = io.BytesIO()
            writer.write(output_io)
            output_io.seek(0)
            
            return StreamingResponse(
                output_io, 
                media_type="application/pdf", 
                headers={"Content-Disposition": f'attachment; filename="unlocked_{files[0].filename}"'}
            )

        elif tool == "rotate":
            contents = await files[0].read()
            reader = PyPDF2.PdfReader(io.BytesIO(contents))
            writer = PyPDF2.PdfWriter()
            
            for page in reader.pages:
                page.rotate(90)
                writer.add_page(page)
                
            output_io = io.BytesIO()
            writer.write(output_io)
            output_io.seek(0)
            
            return StreamingResponse(
                output_io, 
                media_type="application/pdf", 
                headers={"Content-Disposition": f'attachment; filename="rotated_{files[0].filename}"'}
            )

        elif tool == "img_to_pdf":
            try:
                from PIL import Image
                images = []
                for file in files:
                    contents = await file.read()
                    img = Image.open(io.BytesIO(contents)).convert("RGB")
                    images.append(img)
                
                output_io = io.BytesIO()
                if len(images) > 0:
                    images[0].save(output_io, format="PDF", save_all=True, append_images=images[1:])
                output_io.seek(0)
                
                return StreamingResponse(
                    output_io, 
                    media_type="application/pdf", 
                    headers={"Content-Disposition": f'attachment; filename="images_converted.pdf"'}
                )
            except ImportError:
                raise HTTPException(status_code=500, detail="Thư viện Pillow chưa được cài đặt trên Backend.")

        elif tool == "pdf_to_img":
            import fitz
            import zipfile
            contents = await files[0].read()
            doc = fitz.open("pdf", contents)
            
            zip_io = io.BytesIO()
            with zipfile.ZipFile(zip_io, "w") as zip_file:
                for i in range(len(doc)):
                    page = doc.load_page(i)
                    pix = page.get_pixmap(dpi=150)
                    img_bytes = pix.tobytes("jpeg")
                    zip_file.writestr(f"page_{i+1}.jpg", img_bytes)
            
            zip_io.seek(0)
            return StreamingResponse(
                zip_io,
                media_type="application/zip",
                headers={"Content-Disposition": f'attachment; filename="images_{files[0].filename}.zip"'}
            )

        elif tool == "pdf_to_word":
            from pdf2docx import Converter
            import tempfile
            import os
            
            contents = await files[0].read()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                tmp_pdf.write(contents)
                pdf_path = tmp_pdf.name
                
            docx_path = pdf_path.replace(".pdf", ".docx")
            try:
                cv = Converter(pdf_path)
                cv.convert(docx_path, start=0, end=None)
                cv.close()
                
                with open(docx_path, "rb") as f:
                    docx_bytes = f.read()
                
                output_io = io.BytesIO(docx_bytes)
                output_io.seek(0)
                
                return StreamingResponse(
                    output_io,
                    media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    headers={"Content-Disposition": f'attachment; filename="{files[0].filename.split(".")[0]}.docx"'}
                )
            finally:
                if os.path.exists(pdf_path): os.remove(pdf_path)
                if os.path.exists(docx_path): os.remove(docx_path)

        elif tool == "watermark":
            if not watermark:
                raise HTTPException(status_code=400, detail="Chưa cung cấp nội dung watermark.")
            
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.colors import Color
            import PyPDF2
            
            packet = io.BytesIO()
            c = canvas.Canvas(packet, pagesize=A4)
            c.setFont("Helvetica-Bold", 60)
            c.setFillColor(Color(0.5, 0.5, 0.5, alpha=0.3))
            c.saveState()
            c.translate(A4[0] / 2, A4[1] / 2)
            c.rotate(45)
            c.drawCentredString(0, 0, watermark)
            c.restoreState()
            c.save()
            packet.seek(0)
            
            watermark_pdf = PyPDF2.PdfReader(packet)
            watermark_page = watermark_pdf.pages[0]
            
            contents = await files[0].read()
            reader = PyPDF2.PdfReader(io.BytesIO(contents))
            writer = PyPDF2.PdfWriter()
            
            for page in reader.pages:
                page.merge_page(watermark_page)
                writer.add_page(page)
                
            output_io = io.BytesIO()
            writer.write(output_io)
            output_io.seek(0)
            
            return StreamingResponse(
                output_io, 
                media_type="application/pdf", 
                headers={"Content-Disposition": f'attachment; filename="watermarked_{files[0].filename}"'}
            )

        elif tool == "compress":
            import fitz
            contents = await files[0].read()
            doc = fitz.open("pdf", contents)
            
            output_io = io.BytesIO()
            doc.save(output_io, deflate=True, garbage=4)
            output_io.seek(0)
            
            return StreamingResponse(
                output_io,
                media_type="application/pdf",
                headers={"Content-Disposition": f'attachment; filename="compressed_{files[0].filename}"'}
            )

        elif tool == "ai_summarize":
            # AI Placeholder: Extract text and return a summary of first 2000 chars
            contents = await files[0].read()
            reader = PyPDF2.PdfReader(io.BytesIO(contents))
            full_text = ""
            for page in reader.pages[:5]: # limit to 5 pages
                full_text += page.extract_text()
            
            summary = "SUMMARY (AI Placeholder):\n" + full_text[:1000] + "..."
            output_io = io.BytesIO(summary.encode('utf-8'))
            output_io.seek(0)
            return StreamingResponse(output_io, media_type="text/plain", headers={"Content-Disposition": f'attachment; filename="summary_{files[0].filename}.txt"'})

        elif tool == "img_remove_bg":
            from rembg import remove
            contents = await files[0].read()
            result = remove(contents)
            output_io = io.BytesIO(result)
            output_io.seek(0)
            return StreamingResponse(output_io, media_type="image/png", headers={"Content-Disposition": f'attachment; filename="no_bg_{files[0].filename.split(".")[0]}.png"'})

        elif tool == "heic_to_jpg":
            contents = await files[0].read()
            image = Image.open(io.BytesIO(contents))
            output_io = io.BytesIO()
            image.convert("RGB").save(output_io, format="JPEG")
            output_io.seek(0)
            return StreamingResponse(output_io, media_type="image/jpeg", headers={"Content-Disposition": f'attachment; filename="{files[0].filename.split(".")[0]}.jpg"'})

        elif tool == "qr_generator":
            data = watermark or "MultiConvert Pro" # reuse watermark param as data
            img = qrcode.make(data)
            output_io = io.BytesIO()
            img.save(output_io)
            output_io.seek(0)
            return StreamingResponse(output_io, media_type="image/png", headers={"Content-Disposition": 'attachment; filename="qrcode.png"'})

        elif tool == "video_to_mp3":
            from moviepy.editor import VideoFileClip
            contents = await files[0].read()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_vid:
                tmp_vid.write(contents)
                vid_path = tmp_vid.name
            
            audio_path = vid_path.replace(".mp4", ".mp3")
            try:
                clip = VideoFileClip(vid_path)
                clip.audio.write_audiofile(audio_path)
                clip.close()
                with open(audio_path, "rb") as f:
                    audio_bytes = f.read()
                output_io = io.BytesIO(audio_bytes)
                output_io.seek(0)
                return StreamingResponse(output_io, media_type="audio/mpeg", headers={"Content-Disposition": f'attachment; filename="{files[0].filename.split(".")[0]}.mp3"'})
            finally:
                if os.path.exists(vid_path): os.remove(vid_path)
                if os.path.exists(audio_path): os.remove(audio_path)

        elif tool == "dev_format":
            import jsbeautifier
            contents = await files[0].read()
            text = contents.decode('utf-8')
            res = jsbeautifier.beautify(text)
            output_io = io.BytesIO(res.encode('utf-8'))
            output_io.seek(0)
            return StreamingResponse(output_io, media_type="text/plain", headers={"Content-Disposition": f'attachment; filename="formatted_{files[0].filename}"'})

        elif tool == "json_to_csv":
            contents = await files[0].read()
            data = json.loads(contents)
            df = pd.json_normalize(data)
            output_io = io.BytesIO()
            df.to_csv(output_io, index=False)
            output_io.seek(0)
            return StreamingResponse(output_io, media_type="text/csv", headers={"Content-Disposition": f'attachment; filename="{files[0].filename.split(".")[0]}.csv"'})

        elif tool == "excel_merge":
            dfs = []
            for file in files:
                contents = await file.read()
                dfs.append(pd.read_excel(io.BytesIO(contents)))
            merged = pd.concat(dfs, ignore_index=True)
            output_io = io.BytesIO()
            merged.to_excel(output_io, index=False)
            output_io.seek(0)
            return StreamingResponse(output_io, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": 'attachment; filename="merged_sheets.xlsx"'})

        elif tool == "ai_translate":
            # AI Placeholder for Translation
            contents = await files[0].read()
            text = "AI TRANSLATION (Placeholder):\n" + "This feature would use a deep learning model to translate your content while preserving format."
            output_io = io.BytesIO(text.encode('utf-8'))
            output_io.seek(0)
            return StreamingResponse(output_io, media_type="text/plain", headers={"Content-Disposition": 'attachment; filename="translated_dummy.txt"'})

        elif tool == "img_compress":
            contents = await files[0].read()
            img = Image.open(io.BytesIO(contents))
            output_io = io.BytesIO()
            img.save(output_io, format="JPEG", quality=40, optimize=True)
            output_io.seek(0)
            return StreamingResponse(output_io, media_type="image/jpeg", headers={"Content-Disposition": f'attachment; filename="compressed_{files[0].filename}"'})

        elif tool == "video_compress":
            from moviepy.editor import VideoFileClip
            contents = await files[0].read()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                tmp.write(contents)
                p = tmp.name
            out = p.replace(".mp4", "_low.mp4")
            clip = VideoFileClip(p)
            clip.write_videofile(out, bitrate="500k")
            clip.close()
            with open(out, "rb") as f: data = f.read()
            os.remove(p); os.remove(out)
            return StreamingResponse(io.BytesIO(data), media_type="video/mp4", headers={"Content-Disposition": 'attachment; filename="compressed.mp4"'})

        elif tool == "dev_pass_gen":
            res = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=16))
            return StreamingResponse(io.BytesIO(res.encode()), media_type="text/plain", headers={"Content-Disposition": 'attachment; filename="password.txt"'})

        elif tool == "dev_base64":
            contents = await files[0].read()
            res = base64.b64encode(contents)
            return StreamingResponse(io.BytesIO(res), media_type="text/plain", headers={"Content-Disposition": 'attachment; filename="base64.txt"'})

        elif tool == "excel_dedupe":
            contents = await files[0].read()
            df = pd.read_excel(io.BytesIO(contents))
            df = df.drop_duplicates()
            output_io = io.BytesIO()
            df.to_excel(output_io, index=False)
            output_io.seek(0)
            return StreamingResponse(output_io, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": 'attachment; filename="deduplicated.xlsx"'})

        elif tool == "ai_tts":
            import edge_tts
            text = watermark or "Xin chào, đây là hệ thống MultiConvert Pro."
            communicate = edge_tts.Communicate(text, "vi-VN-NamMinhNeural")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                await communicate.save(tmp.name)
                with open(tmp.name, "rb") as f: data = f.read()
            os.remove(tmp.name)
            return StreamingResponse(io.BytesIO(data), media_type="audio/mpeg", headers={"Content-Disposition": 'attachment; filename="speech.mp3"'})

        # Final fallback for unhandled tools (returns original file)
        else:
            contents = await files[0].read()
            output_io = io.BytesIO(contents)
            output_io.seek(0)
            return StreamingResponse(output_io, media_type="application/octet-stream", headers={"Content-Disposition": f'attachment; filename="processed_{tool}_{files[0].filename}"'})
            
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
