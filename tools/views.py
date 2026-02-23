from django.shortcuts import render
from django.http import FileResponse
from pypdf import PdfReader, PdfWriter
import io
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def merge_pdf(request):
    if request.method == "POST":
        files = request.FILES.getlist("pdf_files")

        # Validation: minimum 2 files
        if len(files) < 2:
            return render(request, "merge_pdf.html", {
                "error": "Please upload at least 2 PDF files."
            })

        writer = PdfWriter()

        try:
            for pdf_file in files:

                # File type validation
                if not pdf_file.name.lower().endswith(".pdf"):
                    return render(request, "merge_pdf.html", {
                        "error": "Only PDF files are allowed."
                    })

                reader = PdfReader(pdf_file)

                # Add all pages
                for page in reader.pages:
                    writer.add_page(page)

            # Memory file create
            output = io.BytesIO()
            writer.write(output)
            output.seek(0)

            return FileResponse(
                output,
                as_attachment=True,
                filename="merged.pdf"
            )

        except Exception as e:
            return render(request, "merge_pdf.html", {
                "error": "Invalid or corrupted PDF file detected."
            })

    return render(request, "merge_pdf.html")



from PIL import Image
from django.shortcuts import render
from django.http import FileResponse
import io


def compress_image(request):
    if request.method == "POST":
        image_file = request.FILES.get("image")
        target_kb = request.POST.get("target_size", "100")

        if not image_file:
            return render(request, "compress_image.html", {
                "error": "Please upload an image."
            })

        try:
            target_kb = int(target_kb)
            target_bytes = target_kb * 1024

            img = Image.open(image_file)

            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            quality = 90
            output = io.BytesIO()

            # Reduce quality until file size <= target
            while quality > 10:
                output.seek(0)
                output.truncate()

                img.save(output, format="JPEG", quality=quality, optimize=True)

                if output.tell() <= target_bytes:
                    break

                quality -= 5

            output.seek(0)

            return FileResponse(
                output,
                as_attachment=True,
                filename=f"compressed_{target_kb}kb.jpg"
            )

        except Exception:
            return render(request, "compress_image.html", {
                "error": "Invalid image file."
            })

    return render(request, "compress_image.html")




from PIL import Image
from django.shortcuts import render
from django.http import FileResponse
import io


def jpg_to_pdf(request):
    if request.method == "POST":
        images = request.FILES.getlist("images")

        if not images:
            return render(request, "jpg_to_pdf.html", {
                "error": "Please upload at least one image."
            })

        image_list = []

        try:
            for img_file in images:

                if not img_file.name.lower().endswith((".jpg", ".jpeg", ".png")):
                    return render(request, "jpg_to_pdf.html", {
                        "error": "Only JPG, JPEG, PNG files allowed."
                    })

                img = Image.open(img_file)

                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                image_list.append(img)

            output = io.BytesIO()

            # First image save with append_images
            image_list[0].save(
                output,
                format="PDF",
                save_all=True,
                append_images=image_list[1:]
            )

            output.seek(0)

            return FileResponse(
                output,
                as_attachment=True,
                filename="converted.pdf"
            )

        except Exception:
            return render(request, "jpg_to_pdf.html", {
                "error": "Invalid image file."
            })

    return render(request, "jpg_to_pdf.html")


import subprocess
import os
from django.shortcuts import render
from django.http import FileResponse
from django.conf import settings


def compress_pdf(request):
    if request.method == "POST":
        pdf_file = request.FILES.get("pdf")

        if not pdf_file:
            return render(request, "compress_pdf.html", {
                "error": "Please upload a PDF file."
            })

        try:
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

            input_path = os.path.join(settings.MEDIA_ROOT, "input.pdf")
            output_path = os.path.join(settings.MEDIA_ROOT, "compressed.pdf")

            # Save uploaded file
            with open(input_path, "wb") as f:
                for chunk in pdf_file.chunks():
                    f.write(chunk)

            gs_path = r"C:\Program Files\gs\gs10.06.0\bin\gswin64c.exe"

            command = [
                gs_path,
                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.4",
                "-dPDFSETTINGS=/ebook",
                "-dNOPAUSE",
                "-dBATCH",
                "-sOutputFile=" + output_path,
                input_path,
            ]

            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode != 0:
                print("Ghostscript Error:", result.stderr)
                return render(request, "compress_pdf.html", {
                    "error": "Ghostscript compression failed."
                })

            return FileResponse(
                open(output_path, "rb"),
                as_attachment=True,
                filename="compressed.pdf"
            )

        except Exception as e:
            print("Exception:", str(e))
            return render(request, "compress_pdf.html", {
                "error": "Compression failed."
            })

    return render(request, "compress_pdf.html")


import pytesseract
from PIL import Image
from django.shortcuts import render
import numpy as np
import cv2

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def image_to_text(request):
    extracted_text = ""

    if request.method == "POST":
        image_file = request.FILES.get("image")
        language = request.POST.get("language", "eng")

        if not image_file:
            return render(request, "image_to_text.html", {
                "error": "Please upload an image."
            })

        try:
            img = Image.open(image_file)

            # Convert PIL to OpenCV
            img_np = np.array(img)

            # Convert to grayscale
            gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

            # Apply adaptive threshold (BETTER than simple threshold)
            thresh = cv2.adaptiveThreshold(
                gray,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )

            # Optional: Remove noise
            kernel = np.ones((1, 1), np.uint8)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

            # Use better OCR config
            custom_config = r'--oem 3 --psm 6'

            extracted_text = pytesseract.image_to_string(
                thresh,
                lang=language,
                config=custom_config
            )

        except Exception as e:
            print("OCR Error:", str(e))
            return render(request, "image_to_text.html", {
                "error": "OCR processing failed."
            })

    return render(request, "image_to_text.html", {
        "text": extracted_text
    })
    
    
from django.shortcuts import render
from django.http import FileResponse
from rembg import remove
from PIL import Image
import io


def background_remover(request):
    original_url = None
    processed_url = None

    if request.method == "POST":
        image_file = request.FILES.get("image")

        input_image = Image.open(image_file)
        output_image = remove(input_image)

        original_url = image_file
        buffer = io.BytesIO()
        output_image.save(buffer, format="PNG")
        buffer.seek(0)

        return FileResponse(buffer, as_attachment=True, filename="bg_removed.png")

    return render(request, "background_remover.html", {
        "original": original_url,
        "processed": processed_url
    })
    
from django.shortcuts import render


from django.shortcuts import render


def home(request):
    pdf_tools = [
        {"name": "Merge PDF", "url": "/merge-pdf/"},
        {"name": "Compress PDF", "url": "/compress-pdf/"},
        {"name": "Split PDF", "url": "/split-pdf/"},
        {"name": "Protect PDF", "url": "/protect-pdf/"},
        {"name": "Unlock PDF", "url": "/unlock-pdf/"},
        {"name": "PDF to Word", "url": "/pdf-to-word/"},
        {"name": "JPG to PDF", "url": "/jpg-to-pdf/"},
        {"name": "Add Text to PDF", "url": "/add-text-pdf/"},
    ]

    image_tools = [
        {"name": "Image Compressor", "url": "/compress-image/"},
        {"name": "Resize Image", "url": "/resize-image/"},
        {"name": "Background Remover", "url": "/background-remover/"},
    ]

    ai_tools = [
        {"name": "Image to Text (OCR)", "url": "/image-to-text/"},
    ]

    return render(request, "home.html", {
        "pdf_tools": pdf_tools,
        "image_tools": image_tools,
        "ai_tools": ai_tools
    })
    
from pypdf import PdfReader, PdfWriter
from django.shortcuts import render
from django.http import FileResponse
import io


def split_pdf(request):
    if request.method == "POST":
        pdf_file = request.FILES.get("pdf")
        page_range = request.POST.get("page_range")

        if not pdf_file or not page_range:
            return render(request, "split_pdf.html", {
                "error": "Please upload PDF and enter page range."
            })

        try:
            reader = PdfReader(pdf_file)
            writer = PdfWriter()

            # Example input: 1-3 or 5
            if "-" in page_range:
                start, end = page_range.split("-")
                start = int(start) - 1
                end = int(end)

                for i in range(start, end):
                    writer.add_page(reader.pages[i])
            else:
                page = int(page_range) - 1
                writer.add_page(reader.pages[page])

            output = io.BytesIO()
            writer.write(output)
            output.seek(0)

            return FileResponse(
                output,
                as_attachment=True,
                filename="split.pdf"
            )

        except Exception as e:
            print("Split Error:", str(e))
            return render(request, "split_pdf.html", {
                "error": "Invalid page range or PDF file."
            })

    return render(request, "split_pdf.html")


from pypdf import PdfReader
from docx import Document
from django.http import FileResponse
import io


def pdf_to_word(request):
    if request.method == "POST":
        pdf_file = request.FILES.get("pdf")

        try:
            reader = PdfReader(pdf_file)
            document = Document()

            for page in reader.pages:
                text = page.extract_text()
                document.add_paragraph(text)

            output = io.BytesIO()
            document.save(output)
            output.seek(0)

            return FileResponse(
                output,
                as_attachment=True,
                filename="converted.docx"
            )

        except Exception:
            return render(request, "pdf_to_word.html", {
                "error": "Conversion failed."
            })

    return render(request, "pdf_to_word.html")

from PIL import Image
import io


def resize_image(request):
    if request.method == "POST":
        image_file = request.FILES.get("image")
        width = int(request.POST.get("width"))
        height = int(request.POST.get("height"))

        try:
            img = Image.open(image_file)
            resized = img.resize((width, height))

            buffer = io.BytesIO()
            resized.save(buffer, format="JPEG")
            buffer.seek(0)

            return FileResponse(
                buffer,
                as_attachment=True,
                filename="resized.jpg"
            )

        except Exception:
            return render(request, "resize_image.html", {
                "error": "Resize failed."
            })

    return render(request, "resize_image.html")

from pypdf import PdfReader, PdfWriter


def protect_pdf(request):
    if request.method == "POST":
        pdf_file = request.FILES.get("pdf")
        password = request.POST.get("password")

        try:
            reader = PdfReader(pdf_file)
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            writer.encrypt(password)

            output = io.BytesIO()
            writer.write(output)
            output.seek(0)

            return FileResponse(
                output,
                as_attachment=True,
                filename="protected.pdf"
            )

        except Exception:
            return render(request, "protect_pdf.html", {
                "error": "Protection failed."
            })

    return render(request, "protect_pdf.html")


from pypdf import PdfReader, PdfWriter
from django.shortcuts import render
from django.http import FileResponse
import io


def unlock_pdf(request):
    if request.method == "POST":
        pdf_file = request.FILES.get("pdf")
        password = request.POST.get("password")

        if not pdf_file or not password:
            return render(request, "unlock_pdf.html", {
                "error": "Please upload PDF and enter password."
            })

        try:
            reader = PdfReader(pdf_file)

            # Check if encrypted
            if reader.is_encrypted:
                reader.decrypt(password)
            else:
                return render(request, "unlock_pdf.html", {
                    "error": "PDF is not password protected."
                })

            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            output = io.BytesIO()
            writer.write(output)
            output.seek(0)

            return FileResponse(
                output,
                as_attachment=True,
                filename="unlocked.pdf"
            )

        except Exception as e:
            print("Unlock Error:", str(e))
            return render(request, "unlock_pdf.html", {
                "error": "Incorrect password or invalid PDF."
            })

    return render(request, "unlock_pdf.html")




from django.shortcuts import render
from django.http import FileResponse
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io


def add_text_pdf(request):
    if request.method == "POST":
        pdf_file = request.FILES.get("pdf")
        text = request.POST.get("text")
        page_number = int(request.POST.get("page")) - 1
        x = int(request.POST.get("x"))
        y = int(request.POST.get("y"))

        try:
            reader = PdfReader(pdf_file)
            writer = PdfWriter()

            for i, page in enumerate(reader.pages):
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=letter)

                if i == page_number:
                    can.drawString(x, y, text)

                can.save()
                packet.seek(0)

                overlay_pdf = PdfReader(packet)
                page.merge_page(overlay_pdf.pages[0])
                writer.add_page(page)

            output = io.BytesIO()
            writer.write(output)
            output.seek(0)

            return FileResponse(
                output,
                as_attachment=True,
                filename="text_added.pdf"
            )

        except Exception as e:
            print("Add Text Error:", str(e))
            return render(request, "add_text_pdf.html", {
                "error": "Something went wrong."
            })

    return render(request, "add_text_pdf.html")