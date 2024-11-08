import re
import cv2
import pytesseract
import configparser


class ReceiptProcessingAI:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('ConfigFile.properties')
        pytesseract.pytesseract.tesseract_cmd = config['Path']['OCR_reader']

    def process_receipt(self, image_path):
        """
        Process a receipt image to extract product names, ensuring no duplicates.
        :param image_path: path to the receipt image
        :return: list of unique food items found
        """
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ocr_text = pytesseract.image_to_string(gray, config="--psm 6")

        exclude_patterns = r'\b(?:PCS x|KG x|kg|g|Lidl Plus discount|DISCOUNT)\b'

        non_food_keywords = [
            'napkins', 'layer', 'bag', 'toothpaste', 'detergent', 'shampoo', 'soap', 'foil', 'wrap',
            'plastic', 'bottle', 'paper', 'tissue', 'cloth', 'cleaner', 'bag', 'bin', 'pack', 'towel',
            'toilet', 'napkin', 'plates', 'cutlery', 'cups', 'str', 'strainer', 'lid', 'table'
        ]
        non_food_pattern = r'\b(?:' + '|'.join(non_food_keywords) + r')\b'

        item_pattern = r'\b([a-zA-Z]+(?: [a-zA-Z]+)*(?:/[a-zA-Z]+)*(?: [a-zA-Z]+)*)\b'
        item_names = re.findall(item_pattern, ocr_text)

        seen_items = set()
        unique_food_items = []
        for item in item_names:
            item = item.strip()
            if (item and
                    item not in seen_items and
                    not re.search(exclude_patterns, item, re.IGNORECASE) and
                    not re.search(non_food_pattern, item, re.IGNORECASE) and
                    len(item) > 1):
                unique_food_items.append(item)
                seen_items.add(item)

        return unique_food_items
