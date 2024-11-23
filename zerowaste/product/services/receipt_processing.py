import re
import cv2
import pytesseract
import spacy
import configparser
from concurrent.futures import ThreadPoolExecutor

# Încarcă modelul Spacy o singură dată global
nlp = spacy.load("en_core_web_md")

class ReceiptProcessingAI:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('ConfigFile.properties')
        pytesseract.pytesseract.tesseract_cmd = config['Path']['OCR_reader']
        self.executor = ThreadPoolExecutor()

    def extract_main_term(self, text):
        doc = nlp(text)
        main_tokens = [token.text for token in doc if token.pos_ in {"NOUN", "PROPN"}]
        return " ".join(main_tokens) if main_tokens else text
    
    def safe_similarity(self, token, doc):
        # Returnează 0 dacă vectorul token-ului este gol
        if token.vector_norm == 0 or doc.vector_norm == 0:
            return 0.0
        return token.similarity(doc)


    def filter_edible_products(self, product_list, threshold=0.3):
        edible_products = []

        food_references = [nlp("food"), nlp("meal"), nlp("fruit"), nlp("vegetable"), nlp("meat"),
                        nlp("dairy"), nlp("snack"), nlp("beverage"), nlp("drink"), nlp("produce"),
                        nlp("grocery"), nlp("seafood"), nlp("protein"), nlp("grain"), nlp("ingredient"),
                        nlp("sauce"), nlp("condiment"), nlp("bread"), nlp("milk"), nlp("cheese"),
                        nlp("cereal"), nlp("nutrition"), nlp("organic"), nlp("frozen food"), nlp("pantry")]

        non_food_references = [nlp("cleaning"), nlp("hygiene"), nlp("detergent"), nlp("soap"), nlp("cosmetic"),
                            nlp("skincare"), nlp("cleanser"), nlp("sanitizer"), nlp("disinfectant"),
                            nlp("bleach"), nlp("laundry"), nlp("fabric softener"), nlp("surface cleaner"),
                            nlp("shampoo"), nlp("conditioner"), nlp("deodorant"), nlp("lotion"), nlp("fragrance"),
                            nlp("perfume"), nlp("toothpaste"), nlp("tissue"), nlp("paper towels"),
                            nlp("hand wash"), nlp("wipes"), nlp("facial cleanser"), nlp("household cleaner")]

        for product in product_list:
            main_term = self.extract_main_term(product)
            main_doc = nlp(main_term)

            food_similarity_scores = [self.safe_similarity(food_token, main_doc) for food_token in food_references]
            average_food_similarity = sum(food_similarity_scores) / len(food_similarity_scores)

            non_food_similarity_scores = [self.safe_similarity(non_food_token, main_doc) for non_food_token in non_food_references]
            average_non_food_similarity = sum(non_food_similarity_scores) / len(non_food_similarity_scores)

            if average_food_similarity >= threshold and average_food_similarity > average_non_food_similarity:
                edible_products.append(product)

        return edible_products


    def process_receipt(self, image):
        # Preprocesarea imaginii primite ca parametru
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Extrage textul folosind pytesseract
        ocr_text = pytesseract.image_to_string(gray, config="--psm 6")
        
        # Extrage produsele din textul OCR
        item_pattern = r'\b([a-zA-Z]+(?: [a-zA-Z]+)*(?:/[a-zA-Z]+)*(?: [a-zA-Z]+)*)\b'
        item_names = re.findall(item_pattern, ocr_text)

        seen_items = set()
        unique_food_items = []
        for item in item_names:
            item = item.strip()
            if item and item not in seen_items and len(item) > 1:
                unique_food_items.append(item)
                seen_items.add(item)

        # Filtrează produsele comestibile
        rez = self.filter_edible_products(unique_food_items)
        return rez
