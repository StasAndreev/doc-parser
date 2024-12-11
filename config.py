import yaml
import logging

CONFIG_PATH = 'config.yml'

class ApplicationConfig:
    def __init__(self):
        self.config = None

        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as file:
                self.config = yaml.safe_load(file)
        except FileNotFoundError:
            logging.error("Config file not found")
            raise FileNotFoundError
        except yaml.YAMLError as exc:
            logging.error("Config file format is invalid")
            logging.error(f"YAML parser exception: {exc}")
            raise yaml.YAMLError

    def get_input_folder_path(self):
        if self.config is None:
            return None

        input_file = self.config.get('InputFolder')
        if input_file is None:
            logging.error('InputFolder not found in config file')
            raise yaml.YAMLError

        try:
            with open(input_file, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            logging.error(f"Input folder file '{input_file}' not found")
            raise FileNotFoundError

    def get_image_output_folder_path(self):
        return self.__get_field('ImageOutputFolder')

    def get_text_output_folder_path(self):
        return self.__get_field('TextOutputFolder')

    def get_status_file_path(self):
        return self.__get_field('StatusFile')

    def get_langs(self):
        if self.config is None:
            return None

        lang_file = self.config.get('LangFile')
        if lang_file is None:
            logging.error('LangFile not found in config file')
            raise yaml.YAMLError

        try:
            with open(lang_file, "r", encoding="utf-8") as file:
                return [lang.strip() for lang in file.read().split(',')]
        except FileNotFoundError:
            logging.error(f"Lang file '{lang_file}' not found")
            raise FileNotFoundError

    def get_is_formulas_parsed(self):
        if self.config is None:
            raise yaml.YAMLError

        formula_parse_file = self.config.get('IsFormulasParsedFile')
        if formula_parse_file is None:
            logging.error('IsFormulasParsedFile not found in config file')
            raise yaml.YAMLError

        try:
            with open(formula_parse_file, "r", encoding="utf-8") as file:
                return int(file.read())
        except FileNotFoundError:
            logging.error(f"IsFormulasParsedFile '{formula_parse_file}' not found")
            raise FileNotFoundError
        except ValueError:
            logging.error(f"IsFormulasParsedFile '{formula_parse_file}' has invalid value")
            raise ValueError

    def __get_field(self, field_name):
        if self.config is None:
            raise yaml.YAMLError

        field = self.config.get(field_name)
        if field is None:
            logging.error(f'{field_name} not found in config file')
            raise yaml.YAMLError

        return field