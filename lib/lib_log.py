#
# lib_log.py
# version: 1.0, 2026-06-22, robert.jiranek@gmail.com
#
import sys
import logging

class LogFile ():
    def __init__(self):
        self.log_directory = "./log"
        self.log_file_name = ""
        self.log_file = ""

    def logfile_init(self, file_name: str, format: str="%(asctime)s %(levelname)s: %(message)s"):

        self.log_file_name = file_name
        self.log_file = f"{self.log_directory}/{self.log_file_name}.log"
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format=format
        )
        self.logging = logging.getLogger()

    def critical(self, message: str = ""):
        self.logging.critical(message)

    def error(self, message: str = ""):
        self.logging.error(message)

    def warning(self, message: str = ""):
        self.logging.warning(message)

    def info(self, message: str = ""):
        self.logging.info(message)

    def debug(self, message: str = ""):
        self.logging.debug(message)
