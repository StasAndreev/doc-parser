from ocrpostprocessor import OCRPostProcessor
from suryaimageprocessor import SuryaImageProcessor
from applicationinfo import ApplicationInfo
from PIL import Image
import os
from config import ApplicationConfig
from status import Status
import logging
from tqdm import tqdm
from functools import partialmethod
import hashlib
import regex as re
import time
import progressbar

tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)
OUTPUT_TEXT_FILE = 'result.md'

if not os.path.exists('log'):
    os.makedirs('log')
current_time = time.strftime("%d.%m.%y %H.%M.%S")
logging.basicConfig(level=logging.DEBUG, filename=f"log\\log {current_time}.txt", filemode='w',
                    format='%(levelname)s: %(message)s')

class Application:
    def __init__(self):
        self.config = None
        self.input_directory = None
        self.is_formulas_parsed = None
        self.status_file_path = None
        self.langs = None
        self.output_text_folder = None
        self.output_image_folder = None

        self.application_info = None

        self.last_processed_page = None

        self.processor = None
        self.postprocessor = None

        self.status = None

        self.initialized = False

    def run(self):
        if not self.initialized:
            self.__initialize()

        md5_checksum = self.__calculate_checksum()
        checksum_match = self.application_info.get_checksum() == md5_checksum
        self.application_info.set_checksum(md5_checksum)

        # Read starting page info
        starting_page = 0
        if checksum_match:
            try:
                starting_page = self.application_info.get_last_page() + 1
                logging.info('Checksum match. Starting reading from page ' + str(starting_page + 1))
            except FileNotFoundError:
                pass
            except ValueError:
                logging.error('Page file has invalid value')
                raise ValueError
        else:
            self.application_info.set_last_page(-1)
            logging.info('Starting reading from page 0')


        png_images = [f for f in os.listdir(self.input_directory) if f.endswith(f'.png')]
        if starting_page == len(png_images):
            logging.info('All pages have already been processed')
        else:
            if starting_page == 0:
                self.__clean_up()
            self.__process_pages(png_images, starting_page)
            logging.info('All pages have been successfully processed')

        self.status.set_status(2)
        self.application_info.set_repeated_fatal_error(0)

    def set_status(self, status):
        if self.status is not None:
            self.status.set_status(status)

    def __initialize(self):
        if self.initialized:
            return

        self.config = ApplicationConfig()
        self.input_directory = self.config.get_input_folder_path()
        self.is_formulas_parsed = self.config.get_is_formulas_parsed()
        self.status_file_path = self.config.get_status_file_path()
        self.langs = self.config.get_langs()
        self.output_text_folder = self.config.get_text_output_folder_path()
        self.output_image_folder = self.config.get_image_output_folder_path()
        self.last_processed_page = -1

        self.processor = SuryaImageProcessor(self.langs, self.is_formulas_parsed)
        self.postprocessor = OCRPostProcessor(page_start_index=0, is_formulas_parsed=self.is_formulas_parsed)

        self.status = Status(self.status_file_path)
        if self.status.get_status() != 0:
            logging.error("Program is not ready to run (status is not 0)")
            raise Exception
        self.status.set_status(1)

        self.application_info = ApplicationInfo()

    def __calculate_checksum(self):
        # Calculate md5 hash
        md5 = hashlib.md5()
        for png_image in [f for f in os.listdir(self.input_directory) if f.endswith(f'.png')]:
            with open(f'{self.input_directory}/{png_image}', 'rb') as checksum_file:
                md5.update(checksum_file.read())
        return md5.hexdigest()

    def __process_pages(self, pages, starting_page):
        self.processor.load_models()

        print("\nProcessing pages")
        time.sleep(0.5)
        bar = progressbar.ProgressBar(max_value=len(pages))
        bar.update(0)

        for image_number, png_image in enumerate(pages):
            if image_number < starting_page:
                continue

            logging.debug(f'Processing page {image_number + 1}')
            image = Image.open(f'{self.input_directory}/{png_image}')
            page_items = self.processor.process(image)
            logging.debug(f'Page {image_number + 1} processed')
            text, images = self.postprocessor.process(page_items, image_number)
            logging.debug(f'Page {image_number + 1} post-processed')

            with open(f'{self.output_text_folder}/{OUTPUT_TEXT_FILE}', 'a', encoding='utf-8') as result_file:
                result_file.write(f'<page-start>{image_number + 1}</page-start>\n')
                result_file.write(text)
                result_file.write(f'<page-end>{image_number + 1}</page-end>\n')

            logging.debug(f'Page {image_number + 1} text saved')

            for image_name, image in images:
                image.save(f'{self.output_image_folder}/{image_name}', optimize=True, quality=80)

            logging.debug(f'Page {image_number + 1} images saved')

            self.application_info.set_last_page(image_number)
            bar.update(image_number + 1)
            logging.info(f'Page {image_number} processed')

    def __clean_up(self):
        for filename in [f for f in os.listdir(self.output_image_folder)
                         if re.match(r'page.*-image.*.\png', f)]:
            os.remove(f'{self.output_image_folder}/{filename}')
        with open(f'{self.output_text_folder}/{OUTPUT_TEXT_FILE}', 'w', encoding='utf-8'):
            pass

if __name__ == '__main__':
    try_run = False
    app = Application()
    app_info = ApplicationInfo()
    old_checksum = app_info.get_checksum()
    old_last_page = app_info.get_last_page()
    try:
        try_run = True
        app.run()
    except Exception as e:
        logging.fatal("Program execution interrupted")
        logging.error("Exception: " + str(e.with_traceback(None)))
        # Check fatal error
        if (old_last_page == app_info.get_last_page()
            and old_checksum == app_info.get_checksum()):
            if app_info.get_repeated_fatal_error() == 2:
                app.set_status(4)
            elif not try_run:
                app_info.set_repeated_fatal_error(0)
                app.set_status(3)
            else:
                error_value = app_info.get_repeated_fatal_error()
                app_info.set_repeated_fatal_error(error_value + 1)
                app.set_status(3)
        else:
            app_info.set_repeated_fatal_error(1)
            app.set_status(3)
        raise e
