# Standard libraries
import io
import logging

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

nlp = spacy.load(LANGUAGE)


class OCRProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_extension = file_path.rsplit('.', 1)[1].lower()

    def process_file(self):
        self.validate_file()
        return self.process_pdf_file() if self.file_extension == 'pdf' else self.process_image_file()

    def validate_file(self):
        if not self.file_path:
            self.log_and_raise_error("File URL not provided.")
        if not self.is_allowed_file():
            self.log_and_raise_error("Invalid file type.")

    def is_allowed_file(self):
        return '.' in self.file_path and self.file_path.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

    def process_image_file(self):
        with open(self.file_path, 'rb') as image_file:
            image = Image.open(image_file)
        return self.ocr_image(image), {}

    def ocr_all_images(self, images):
        return [self.ocr_image(image) for image in images]

    def ocr_image(self, image):
        image_np = self.preprocess_image(image)
        text = pytesseract.image_to_string(image_np, config=TESSERACT_CONFIG, lang='pol+eng')
        return self.clean_text(text)

    def preprocess_image(self, image):
        image_np = np.array(image)
        gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, BLUR_SIZE, BLUR_VALUE)
        thresh = cv2.adaptiveThreshold(blur, 255, THRESH_METHOD, THRESH_TYPE, THRESH_BLOCK_SIZE, THRESH_CONSTANT)
        cleaned_image_np = self.remove_lines(thresh)
        return Image.fromarray(cleaned_image_np)

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
        doc = nlp(text)
        cleaned_text = ''.join(
            token.lemma_ + ' ' if token.pos_ not in ['PUNCT', 'X', 'SYM'] and not token.is_stop else token.text_with_ws
            for token in doc)
        return re.sub(r'\s+', ' ', cleaned_text).strip()  # Normalize whitespace

    @staticmethod
    def final_cleaning(text):
        text = re.sub(r'(?<=[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ])\n(?=[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ])', ' ', text)
        text = re.sub(r'(.)\1{2,}', r'\1\1', text)  # Reduce excessively repeated characters
        text = re.sub(r'\n', ' ', text)
        text = text.replace("$", " dolar ").replace("€", " euro ")
        text = re.sub(r'Page \d+ of \d+|Strona \d+ z \d+', '', text)
        return text.strip()  # Trim leading and trailing whitespace
