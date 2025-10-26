from configparser import ConfigParser

from lockpy import singleton

@singleton
class ConfigReader:
    def __init__(self):
        self.config_reader = ConfigParser()
        self.config_reader.read("config.ini")

    def get_config(self, config_header: str, config_value: str)-> str:
        return self.config_reader[config_header][config_value]
