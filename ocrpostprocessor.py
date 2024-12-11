class OCRPostProcessor:
    def __init__(self, page_start_index, is_formulas_parsed):
        self.is_formulas_parsed = is_formulas_parsed

    def process(self, page_items, page_number):
        result_text = ""
        result_images = []
        for item in page_items:
            if item.label == 'Section-header':
                result_text += '<h>' + item.text + '</h>' + '\n'
            elif item.is_text and item.label != 'Formula':
                result_text += '<p>' + item.text + '</p>' + '\n'
            elif item.label == 'Formula' and self.is_formulas_parsed == 1:
                result_text += '<formula>' + item.text + '</formula>' + '\n'
            elif item.label != 'Formula' or self.is_formulas_parsed != 0:
                image_name = f'page{page_number}-image{len(result_images)}.png'
                result_text += '<image>' + image_name + '</image>' + '\n'
                result_images.append([image_name, item.image])
        return result_text, result_images
