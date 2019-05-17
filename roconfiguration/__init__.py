import os
import yaml
import json
import configparser
from collections import abc


__all__ = ['Configuration', 'ConfigurationError']


class ConfigurationError(Exception):
    """An exception risen for invalid configuration."""


def apply_key_value(obj, key, value):
    key = key.strip('_:')  # remove special characters from both ends
    for token in (':', '__'):
        if token in key:
            parts = key.split(token)

            sub_property = obj
            last_part = parts[-1]
            for part in parts[:-1]:

                if isinstance(sub_property, abc.MutableSequence):
                    try:
                        index = int(part)
                    except ValueError:
                        raise ValueError(f'{part} was supposed to be a numeric index in {key}')

                    sub_property = sub_property[index]
                    continue

                try:
                    sub_property = sub_property[part]
                except KeyError:
                    sub_property[part] = {}
                    sub_property = sub_property[part]
                else:
                    if not isinstance(sub_property, abc.Mapping) and not isinstance(sub_property, abc.MutableSequence):
                        raise ConfigurationError(f'The key `{key}` cannot be used because it overrides another '
                                                 f'variable with shorter key! ({part}, {sub_property})')

            if isinstance(sub_property, abc.MutableSequence):
                try:
                    index = int(last_part)
                except ValueError:
                    raise ValueError(f'{last_part} was supposed to be a numeric index in {key}')

                sub_property[index] = value
            else:
                try:
                    sub_property[last_part] = value
                except TypeError as te:
                    raise TypeError(f'invalid assignment {key} -> {value}; {str(te)}')

            return obj

    obj[key] = value
    return obj


def _develop_configparser_values(parser):
    values = {}
    for section_name in parser.sections():
        section_values = {}
        for k, v in parser[section_name].items():
            section_values[k] = _develop_configparser_values(v) if isinstance(v, abc.Mapping) else v
        values[section_name] = section_values
    return values


class Configuration:
    """
    Provides methods to handle configuration objects.
    A read-only façade for navigating configuration objects using attribute notation.

    Thanks to Fluent Python, book by Luciano Ramalho; this class is inspired by his example of JSON structure explorer.
    """

    __slots__ = ('__data',)

    def __new__(cls, arg=None):
        if not arg:
            return super().__new__(cls)
        if isinstance(arg, abc.Mapping):
            return super().__new__(cls)
        if isinstance(arg, abc.MutableSequence):
            return [cls(item) for item in arg]
        return arg

    def __init__(self, mapping=None):
        self.__data = {}
        if mapping:
            self.add_map(mapping)

    def __contains__(self, item):
        return item in self.__data

    def __getitem__(self, name):
        return self.__getattr__(name)

    def __getattr__(self, name):
        if name in self.__data:
            value = self.__data.get(name)
            if isinstance(value, abc.Mapping) or isinstance(value, abc.MutableSequence):
                return Configuration(value)
            return value
        raise KeyError(name)

    @property
    def values(self):
        """
        Returns a copy of the dictionary of current settings.
        """
        return self.__data.copy()

    def add_value(self, name, value):
        """
        Adds a configuration value by name. The name can contain
        paths to nested objects and list indices.

        :param name: name of property to set
        :param value: the value to set
        """
        apply_key_value(self.__data, name, value)

    def add_map(self, value):
        """
        Merges a mapping object such as a dictionary,
        inside this configuration,

        :param value: instance of mapping object
        """
        for key, value in value.items():
            self.__data[key] = value

    def add_environmental_variables(self, prefix=None):
        """
        Reads environmental variables inside this configuration object,
        optionally filtered by prefix.

        :param prefix: optional prefix, to filter read environmental variables.
        """
        for k, v in os.environ.items():
            lk = k.lower()
            if prefix and not lk.startswith(prefix):
                continue
            apply_key_value(self.__data, lk, v)

    def add_ini(self, ini_settings):
        """
        Reads settings from given ini configuration code.
        
        :param ini_settings: source ini code 
        """
        parser = configparser.ConfigParser()
        parser.read_string(ini_settings)
        self.add_map(_develop_configparser_values(parser))

    def _handle_missing_configuration_file(self, file_path):
        raise FileNotFoundError(f'missing configuration file: {file_path}')

    def add_ini_file(self, file_path, optional=False):
        """
        Reads and parse an ini file, merging its values into an instance of Configuration.

        :param file_path: path to an ini file
        :param optional: whether the ini file is optional.
        """
        if not os.path.exists(file_path):
            if optional:
                return
            self._handle_missing_configuration_file(file_path)
        parser = configparser.ConfigParser()
        parser.read(file_path)
        self.add_map(_develop_configparser_values(parser))

    def add_json_file(self, file_path, optional=False):
        """
        Reads and parse an json file, merging its values into an instance of Configuration.

        :param file_path: path to an json file
        :param optional: whether the json file is optional.
        """
        if not os.path.exists(file_path):
            if optional:
                return
            self._handle_missing_configuration_file(file_path)

        with open(file_path, 'rt', encoding='utf-8') as f:
            self.add_map(json.load(f))

    def add_yaml_file(self, file_path, optional=False, safe_load=True):
        """
        Reads and parse an yaml file, merging its values into an instance of Configuration.

        :param file_path: path to an yaml file
        :param optional: whether the yaml file is optional.
        :param safe_load: whether to use safe load
        """
        if not os.path.exists(file_path):
            if optional:
                return
            self._handle_missing_configuration_file(file_path)

        with open(file_path, 'rt', encoding='utf-8') as f:

            if safe_load:
                data = yaml.safe_load(f)
            else:
                data = yaml.full_load(f)

            self.add_map(data)
