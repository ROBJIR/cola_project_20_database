#
# lib_config_file.lib
# version: 1.0, 2026-06-22, robert.jiranek@gmail.com
#
import sys
from configparser import ConfigParser

class ConfigurationFile ():
    def __init__(self):
        self.configuration_directory = "./cfg"
        self.configuration_file_name = ""
        self.configuration_file = ""

    def parameter_get(self, file_name: str, section: str, key:str):
        self.configuration_file_name = file_name
        self.configuration_file = f"{self.configuration_directory}/{self.configuration_file_name}.cfg"
        configfile = ConfigParser()

        if not configfile.read(self.configuration_file):
            raise FileNotFoundError(f"ERROR: configuration file '{self.configuration_file}' not found")
        else:
            configfile.read(self.configuration_file)

            if not configfile.has_section(section):
                print (f"ERROR: in file {self.configuration_file} not found section '{section}' for key '{key}'!")
                #self.error_message(modul="get_database_cfg", errorno=61,
                #                   err=f"in file {self.configuration_file} not found section {section}!")
            else:
                if not configfile.has_option(section, key):
                    configuration_parameter = ""
                else:
                    configuration_parameter = configfile[section][key]

                # if the parameter value is enclosed in " or '
                if configuration_parameter.startswith('"') and configuration_parameter.endswith('"'):
                    configuration_parameter = configuration_parameter[1:-1]

                if configuration_parameter.startswith("'") and configuration_parameter.endswith("'"):
                    configuration_parameter = configuration_parameter[1:-1]

        return configuration_parameter