class PageItem:

    def __init__(self, bbox, position, label, is_text):
        self.bbox = bbox
        self.position = position
        self.label = label
        self.is_text = is_text
        self.text = None
        self.image = None