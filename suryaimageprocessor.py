from surya.ocr import run_ocr
from surya.detection import batch_text_detection
from surya.layout import batch_layout_detection
from surya.ordering import batch_ordering
from surya.model.detection.model import load_model as load_det_model, load_processor as load_det_processor
from surya.model.recognition.model import load_model as load_rec_model
from surya.model.recognition.processor import load_processor as load_rec_processor
from surya.model.ordering.model import load_model as load_ord_model
from surya.model.ordering.processor import load_processor as load_ord_processor
from texify.inference import batch_inference
from texify.model.model import load_model as load_texify_model
from texify.model.processor import load_processor as load_texify_processor
from surya.settings import settings
from pageitem import PageItem
import time
import logging
import progressbar
import pytesseract


class SuryaImageProcessor:
    def __init__(self, langs, is_formulas_parsed):
        self.is_model_loaded = False
        self.layout_model = None
        self.layout_processor = None
        self.det_model = None
        self.det_processor = None
        self.rec_model = None
        self.rec_processor = None
        self.ord_model = None
        self.ord_processor = None
        self.texify_model = None
        self.texify_processor = None

        self.langs = langs
        self.is_formulas_parsed = is_formulas_parsed

    def process(self, image):
        if not self.is_model_loaded:
            raise Exception('Models not loaded')

        batch_text_result = batch_text_detection([image], self.det_model, self.det_processor)
        logging.debug("Text detection done")
        batch_layout_result = batch_layout_detection([image], self.layout_model, self.layout_processor, batch_text_result)
        logging.debug("Layout detection done")
        batch_layout_bboxes = [item.bbox for item in batch_layout_result[0].bboxes]
        batch_ordering_result = batch_ordering([image], [batch_layout_bboxes], self.ord_model, self.ord_processor)
        logging.debug("Ordering done")
        page_items = self.__merge_results(batch_layout_result[0].bboxes, batch_ordering_result[0].bboxes)
        page_items = sorted(page_items, key=lambda item: item.position)
        logging.debug("Merging and sorting done")

        for item in page_items:
            if not item.is_text:
                if item.label != 'Formula' or self.is_formulas_parsed == 2:
                    item.image = image.crop(item.bbox)
                elif item.label == 'Formula' and self.is_formulas_parsed == 1:
                    formula_result = batch_inference([image.crop(item.bbox)],
                                                     self.texify_model, self.texify_processor)
                    item.text = formula_result[0]
                    item.is_text = True
            else:
                # ocr_result = run_ocr([image.crop(item.bbox)], [self.langs],
                #                      self.det_model, self.det_processor,
                #                      self.rec_model, self.rec_processor)
                # item.text = self.__get_text(ocr_result)
                item.text = pytesseract.image_to_string(image.crop(item.bbox),
                                                         config="--psm 6", lang='+'.join(self.langs))

        logging.debug("OCR done")

        return page_items

    def load_models(self):
        if self.is_model_loaded:
            return

        start_time = time.time()

        print("Loading models")
        time.sleep(0.5)
        bar = progressbar.ProgressBar(max_value=5)
        bar.update(0)

        self.layout_model = load_det_model(checkpoint=settings.LAYOUT_MODEL_CHECKPOINT)
        self.layout_processor = load_det_processor(checkpoint=settings.LAYOUT_MODEL_CHECKPOINT)
        bar.update(1)

        self.det_model = load_det_model()
        self.det_processor = load_det_processor()
        bar.update(2)

        self.rec_model = load_rec_model()
        self.rec_processor = load_rec_processor()
        bar.update(3)

        self.ord_model = load_ord_model()
        self.ord_processor = load_ord_processor()
        bar.update(4)

        self.texify_model = load_texify_model()
        self.texify_processor = load_texify_processor()
        bar.update(5)

        self.is_model_loaded = True
        logging.info('Model loading time: {:.2f} sec'.format(time.time() - start_time))

    @staticmethod
    def __merge_results(layout_result, ordering_result):
        ordering_dict = {tuple(item.bbox): item.position for item in ordering_result}
        page_items = []
        for item in layout_result:
            position = ordering_dict[tuple(item.bbox)]
            is_text = item.label not in ("Picture", "Table", "Formula", "Figure")
            page_items.append(PageItem(item.bbox, position, item.label, is_text))
        return page_items

    @staticmethod
    def __get_text(ocr_result):
        text = ""
        for item in ocr_result[0].text_lines:
            text += item.text + '\n'
        return text
