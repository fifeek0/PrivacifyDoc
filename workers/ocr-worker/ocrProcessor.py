# Standard libraries
import io
import logging
from typing import List, Dict, Any, Tuple

import cv2
import numpy as np

# External libraries
from fastapi import HTTPException
from PIL import Image, UnidentifiedImageError
from pdf2image import convert_from_bytes
import re
import PyPDF2
import pytesseract
import spacy

TESSERACT_CONFIG = r'--oem 3 --psm 6'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
LANGUAGE = "pl_core_news_sm"
DPI = 300
BLUR_SIZE = (5, 5)
BLUR_VALUE = 0
THRESH_METHOD = cv2.ADAPTIVE_THRESH_GAUSSIAN_C
THRESH_TYPE = cv2.THRESH_BINARY
THRESH_BLOCK_SIZE = 11
THRESH_CONSTANT = 2
H_KERNEL_SIZE = (25, 1)
V_KERNEL_SIZE = (1, 25)
KERNEL_ITERATIONS = 2

try:
    nlp = spacy.load(LANGUAGE)
except OSError:
    logging.warning(f"Could not load spaCy model {LANGUAGE}. Using basic text processing.")
    nlp = None


class OCRProcessor:
    def __init__(self, file_path: str = None, file_bytes: bytes = None):
        self.file_path = file_path
        self.file_bytes = file_bytes

        if file_path:
            self.file_extension = file_path.rsplit('.', 1)[1].lower()
        elif file_bytes:
            self.file_extension = self._detect_file_type(file_bytes)
        else:
            raise ValueError("Either file_path or file_bytes must be provided")

    def _detect_file_type(self, file_bytes: bytes) -> str:
        if file_bytes.startswith(b'%PDF'):
            return 'pdf'
        elif file_bytes.startswith(b'\xff\xd8\xff'):
            return 'jpg'
        elif file_bytes.startswith(b'\x89PNG'):
            return 'png'
        else:
            return 'unknown'

    def process_file(self) -> Tuple[List[str], Dict[str, Any]]:
        self.validate_file()

        if self.file_extension == 'pdf':
            return self.process_pdf_file()
        else:
            return self.process_image_file()

    def process_from_bytes(self, file_bytes: bytes, content_type: str) -> Dict[str, Any]:
        try:
            self.file_bytes = file_bytes

            if content_type.startswith('image/'):
                return self._process_image_from_bytes(file_bytes)
            elif content_type == 'application/pdf':
                return self._process_pdf_from_bytes(file_bytes)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported content type: {content_type}")

        except Exception as e:
            logging.error(f"Error processing file from bytes: {str(e)}")
            raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

    def _process_image_from_bytes(self, file_bytes: bytes) -> Dict[str, Any]:
        try:
            image = Image.open(io.BytesIO(file_bytes))
            extracted_text = self.ocr_image(image)

            return {
                "success": True,
                "text": extracted_text,
                "pages": 1,
                "metadata": {
                    "format": image.format,
                    "size": image.size,
                    "mode": image.mode
                }
            }
        except Exception as e:
            logging.error(f"Error processing image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")

    def _process_pdf_from_bytes(self, file_bytes: bytes) -> Dict[str, Any]:
        try:
            metadata = self._extract_pdf_metadata(file_bytes)
            images = convert_from_bytes(file_bytes, dpi=DPI)
            texts = []

            for i, image in enumerate(images):
                logging.info(f"Processing PDF page {i + 1}/{len(images)}")
                page_text = self.ocr_image(image)
                texts.append(page_text)

            return {
                "success": True,
                "text": "\n\n--- Page Break ---\n\n".join(texts),
                "pages": len(texts),
                "page_texts": texts,
                "metadata": metadata
            }
        except Exception as e:
            logging.error(f"Error processing PDF: {str(e)}")
            raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")

    def _extract_pdf_metadata(self, file_bytes: bytes) -> Dict[str, Any]:
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            metadata = {}

            if pdf_reader.metadata:
                metadata = {
                    "title": pdf_reader.metadata.get("/Title", ""),
                    "author": pdf_reader.metadata.get("/Author", ""),
                    "subject": pdf_reader.metadata.get("/Subject", ""),
                    "creator": pdf_reader.metadata.get("/Creator", ""),
                    "producer": pdf_reader.metadata.get("/Producer", ""),
                    "creation_date": str(pdf_reader.metadata.get("/CreationDate", "")),
                    "modification_date": str(pdf_reader.metadata.get("/ModDate", ""))
                }

            metadata["page_count"] = len(pdf_reader.pages)
            return metadata
        except Exception as e:
            logging.warning(f"Could not extract PDF metadata: {str(e)}")
            return {}

    def validate_file(self):
        if self.file_path and not self.file_path:
            self.log_and_raise_error("File URL not provided.")
        if not self.is_allowed_file():
            self.log_and_raise_error("Invalid file type.")

    def is_allowed_file(self):
        return self.file_extension and self.file_extension.lower() in ALLOWED_EXTENSIONS

    def log_and_raise_error(self, message):
        logging.error(message)
        raise HTTPException(status_code=400, detail=message)

    def process_pdf_file(self):
        metadata, images = {}, []
        with open(self.file_path, 'rb') as pdf_file:
            reader = self.read_pdf_metadata(pdf_file)
            metadata = reader.metadata if reader else {}
            images = self.get_images_from_pdf(pdf_file)
        return self.ocr_all_images(images), metadata

    def read_pdf_metadata(self, pdf_file):
        try:
            return PyPDF2.PdfReader(pdf_file)
        except Exception as e:
            logging.error(f"Error reading PDF metadata: {str(e)}")
            return None

    def get_images_from_pdf(self, pdf_file):
        try:
            pdf_file.seek(0)
            pdf_bytes = pdf_file.read()
            return convert_from_bytes(pdf_bytes, dpi=DPI)
        except Exception as e:
            logging.error(f"Error converting PDF to images: {str(e)}")
            return []

    def process_image_file(self):
        with open(self.file_path, 'rb') as image_file:
            image = Image.open(image_file)
        return self.ocr_image(image), {}

    def ocr_all_images(self, images):
        return [self.ocr_image(image) for image in images]

    def ocr_image(self, image):
        try:
            image_np = self.preprocess_image(image)
            text = pytesseract.image_to_string(
                image_np,
                config=TESSERACT_CONFIG,
                lang='pol+eng'
            )
            return self.clean_text(text)
        except Exception as e:
            logging.error(f"OCR processing failed: {str(e)}")
            return ""

    def preprocess_image(self, image):
        try:
            image_np = np.array(image)

            if len(image_np.shape) == 3 and image_np.shape[2] == 4:
                image_np = cv2.cvtColor(image_np, cv2.COLOR_RGBA2RGB)
            elif len(image_np.shape) == 3 and image_np.shape[2] == 3:
                image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

            gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, BLUR_SIZE, BLUR_VALUE)
            thresh = cv2.adaptiveThreshold(
                blur, 255, THRESH_METHOD, THRESH_TYPE,
                THRESH_BLOCK_SIZE, THRESH_CONSTANT
            )
            cleaned_image_np = self.remove_lines(thresh)
            return Image.fromarray(cleaned_image_np)
        except Exception as e:
            logging.warning(f"Image preprocessing failed, using original: {str(e)}")
            return image

    def remove_lines(self, image):
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, H_KERNEL_SIZE)
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, V_KERNEL_SIZE)
        detected_lines_h = cv2.morphologyEx(image, cv2.MORPH_OPEN, horizontal_kernel, iterations=KERNEL_ITERATIONS)
        detected_lines_v = cv2.morphologyEx(image, cv2.MORPH_OPEN, vertical_kernel, iterations=KERNEL_ITERATIONS)
        contours = cv2.findContours(detected_lines_h, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0] \
                   + cv2.findContours(detected_lines_v, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        for contour in contours:
            cv2.drawContours(image, [contour], -1, (255, 255, 255), 5)
        return image

    def clean_text(self, text):
        return self.final_cleaning(self.spacy_cleaning(text))

    @staticmethod
    def spacy_cleaning(text):
        if nlp:
            doc = nlp(text)
            cleaned_text = ''.join(
                token.lemma_ + ' ' if token.pos_ not in ['PUNCT', 'X', 'SYM'] and not token.is_stop else token.text_with_ws
                for token in doc)
            return re.sub(r'\s+', ' ', cleaned_text).strip()
        return text

    @staticmethod
    def final_cleaning(text):
        text = re.sub(r'(?<=[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ])\n(?=[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ])', ' ', text)
        text = re.sub(r'(.)\1{2,}', r'\1\1', text)
        text = re.sub(r'\n', ' ', text)
        text = text.replace("$", " dolar ").replace("€", " euro ")
        text = re.sub(r'Page \d+ of \d+|Strona \d+ z \d+', '', text)
        return text.strip()
