import yaml
import logging


APPLICATION_INFO_PATH = 'application_info.yml'


class ApplicationInfo:
    def __init__(self):
        self.application_info = None

        try:
            with open(APPLICATION_INFO_PATH, "r", encoding="utf-8") as file:
                self.application_info = yaml.safe_load(file)
        except FileNotFoundError:
            logging.error("Config file not found")
            raise FileNotFoundError
        except yaml.YAMLError as exc:
            logging.error("Config file format is invalid")
            logging.error(f"YAML parser exception: {exc}")
            raise yaml.YAMLError

    def get_checksum(self):
        if self.application_info is None:
            return None

        return self.__get_field('Checksum')

    def get_last_page(self):
        if self.application_info is None:
            return None

        return self.__get_field('LastPage')

    def get_repeated_fatal_error(self):
        if self.application_info is None:
            return None

        return self.__get_field('RepeatedFatalError')

    def set_checksum(self, checksum):
        self.__set_field('Checksum', checksum)

    def set_last_page(self, last_page):
        self.__set_field('LastPage', last_page)

    def set_repeated_fatal_error(self, repeated_fatal_error):
        self.__set_field('RepeatedFatalError', repeated_fatal_error)

    def __get_field(self, field_name):
        if self.application_info is None:
            raise yaml.YAMLError

        field = self.application_info.get(field_name)
        if field is None:
            logging.error(f'{field_name} not found in application info file')
            raise yaml.YAMLError

        return field

    def __set_field(self, field_name, field_value):
        if self.application_info is None:
            raise yaml.YAMLError

        try:
            self.application_info[field_name] = field_value
            yaml.dump(self.application_info, open(APPLICATION_INFO_PATH, 'w'))
        except FileNotFoundError:
            logging.error(f"Application info file '{APPLICATION_INFO_PATH}' not found")
            raise FileNotFoundError
