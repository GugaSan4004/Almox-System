import os
import io

from pdf2image import convert_from_path

class init:
    def __init__(self, path):
        os.environ["PATH"] += os.pathsep + r"C:\poppler\Library\bin"
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path + r"\api-key\rock-tower-480410-d2-446c98045165.json"

        from google.cloud import vision_v1

        self.vision = vision_v1
        

    def load_image(self, img_path):
        if img_path.lower().endswith(".pdf"):
            pages = convert_from_path(img_path, dpi=200)
            temp_img = img_path.replace(".pdf", "_page1.jpg")
            pages[0].save(temp_img, "JPEG")
            return temp_img
        
        return img_path

    def extractText(self, path):
        
        path = self.load_image(path)
        client = self.vision.ImageAnnotatorClient()

        with io.open(path, "rb") as img_file:
            content = img_file.read()

        image = self.vision.Image(content=content)

        image_context = self.vision.ImageContext(
            language_hints=["mul-Latn-t-i0-handwrit"]
        )
        response = client.document_text_detection( # type: ignore
            image=image, image_context=image_context
        )

        text = response.full_text_annotation.text

        return text.replace("»", "").replace("«", "").replace("(", "").replace(")", "")