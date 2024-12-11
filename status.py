import logging

class Status:
    def __init__(self, status_file_path):
        self.status_file_path = status_file_path

    def get_status(self):
        try:
            with open(self.status_file_path, "r") as file:
                return int(file.read())
        except FileNotFoundError:
            logging.ERROR(f"Status file '{self.status_file_path}' not found")
            raise FileNotFoundError
        except ValueError:
            logging.ERROR(f"Status file '{self.status_file_path}' has invalid value")
            raise ValueError

    def set_status(self, status):
        try:
            with open(self.status_file_path, "w") as file:
                file.write(str(status))
        except FileNotFoundError:
            logging.ERROR(f"Status file '{self.status_file_path}' not found")
            raise FileNotFoundError