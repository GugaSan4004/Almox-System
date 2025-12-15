import os
import io
from google.cloud import vision_v1
from pdf2image import convert_from_path
from datetime import datetime, timedelta, timezone

os.environ["PATH"] += os.pathsep + r"C:\poppler\Library\bin"

def load_image(img_path):
    if img_path.lower().endswith(".pdf"):
        pages = convert_from_path(img_path, dpi=200)
        temp_img = img_path.replace(".pdf", "_page1.jpg")
        pages[0].save(temp_img, "JPEG")
        return temp_img
    
    return img_path

def extractText(path):
    
    path = load_image(path)
    client = vision_v1.ImageAnnotatorClient()

    with io.open(path, "rb") as img_file:
        content = img_file.read()

    image = vision_v1.Image(content=content)

    image_context = vision_v1.ImageContext(
        language_hints=["mul-Latn-t-i0-handwrit"]
    )
    response = client.document_text_detection( # type: ignore
        image=image, image_context=image_context
    )

    text = response.full_text_annotation.text

    return text.replace("»", "").replace("«", "").replace("(", "").replace(")", "")