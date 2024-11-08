import re
import cv2
import pytesseract
import spacy
import configparser


class ReceiptProcessingAI:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('ConfigFile.properties')
        pytesseract.pytesseract.tesseract_cmd = config['Path']['OCR_reader']
        
    def extract_main_term(self, text, nlp):
        doc = nlp(text)
        main_tokens = [token.text for token in doc if token.pos_ in {"NOUN", "PROPN"}]
        return " ".join(main_tokens) if main_tokens else text


    def filter_edible_products(self, product_list, threshold=0.3):
        nlp = spacy.load("en_core_web_md")
        edible_products = []

        # Referințe pentru a identifica produse alimentare și non-alimentare
        # Referințe extinse pentru produsele alimentare
        food_references = [
            nlp("food"), nlp("meal"), nlp("fruit"), nlp("vegetable"), nlp("meat"),
            nlp("dairy"), nlp("snack"), nlp("beverage"), nlp("drink"), nlp("produce"),
            nlp("grocery"), nlp("seafood"), nlp("protein"), nlp("grain"), nlp("ingredient"),
            nlp("sauce"), nlp("condiment"), nlp("bread"), nlp("milk"), nlp("cheese"),
            nlp("cereal"), nlp("nutrition"), nlp("organic"), nlp("frozen food"), nlp("pantry")
        ]

        # Referințe extinse pentru produsele non-alimentare
        non_food_references = [
            nlp("cleaning"), nlp("hygiene"), nlp("detergent"), nlp("soap"), nlp("cosmetic"),
            nlp("skincare"), nlp("cleanser"), nlp("sanitizer"), nlp("disinfectant"),
            nlp("bleach"), nlp("laundry"), nlp("fabric softener"), nlp("surface cleaner"),
            nlp("shampoo"), nlp("conditioner"), nlp("deodorant"), nlp("lotion"), nlp("fragrance"),
            nlp("perfume"), nlp("toothpaste"), nlp("tissue"), nlp("paper towels"),
            nlp("hand wash"), nlp("wipes"), nlp("facial cleanser"), nlp("household cleaner")
        ]

        for product in product_list:
            main_term = self.extract_main_term(product, nlp)
            main_doc = nlp(main_term)

            # Calculăm similaritatea medie cu referințele alimentare
            food_similarity_scores = [food_token.similarity(main_doc) for food_token in food_references]
            average_food_similarity = sum(food_similarity_scores) / len(food_similarity_scores)

            # Calculăm similaritatea medie cu referințele de non-alimentare
            non_food_similarity_scores = [non_food_token.similarity(main_doc) for non_food_token in non_food_references]
            average_non_food_similarity = sum(non_food_similarity_scores) / len(non_food_similarity_scores)

            # Verificăm dacă similaritatea cu alimentul este mai mare decât cea cu non-alimentul
            if average_food_similarity >= threshold and average_food_similarity > average_non_food_similarity:
                edible_products.append(product)

        return edible_products




    def process_receipt(self, image_path):
        """
        Process a receipt image to extract product names, ensuring no duplicates.
        :param image_path: path to the receipt image
        :return: list of unique food items found
        """
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ocr_text = pytesseract.image_to_string(gray, config="--psm 6")

        item_pattern = r'\b([a-zA-Z]+(?: [a-zA-Z]+)*(?:/[a-zA-Z]+)*(?: [a-zA-Z]+)*)\b'
        item_names = re.findall(item_pattern, ocr_text)

        seen_items = set()
        unique_food_items = []
        for item in item_names:
            item = item.strip()
            if (item and
                    item not in seen_items and
                    len(item) > 1):
                unique_food_items.append(item)
                seen_items.add(item)

        return self.filter_edible_products(unique_food_items)
