# -*- coding: utf-8 -*-
"""
Module to load configuration files
"""

import json
import logging
import os

_CONFIG_FOLDER = "config"
_DEFAULT_CONFIG = "config"


def merge_dict(*sources):
    """ Merge multiple dict into one

    A very basic dictionary merging algorithm
    (Similar to https://pypi.org/project/jsonmerge/)

    - New keys are added
    - Existing keys are handled as follows:
        - dict: merged calling merge_dict recursively
        - list: values are appended
        - others: existing value is replaced with new value
    """
    merged = {}
    for source in sources:
        for key, value_to_merge in source.items():
            if key in merged:
                original_value = merged[key]
                if type(original_value) is dict and type(value_to_merge) is dict:
                    merged[key] = merge_dict(original_value, value_to_merge)
                    continue
                elif type(original_value) is list and type(value_to_merge) is list:
                    original_value.extend(value_to_merge)
                    continue
            merged[key] = value_to_merge
    return merged


def get_config(*additional_configs):
    """ Returns the config dictionary for the given environment """
    configs = [_DEFAULT_CONFIG]
    for additional_config in additional_configs:
        configs.append(additional_config)
    config_files = [
        os.path.join(os.path.dirname(__file__), _CONFIG_FOLDER, "{}.json".format(config))
        for config in configs
    ]
    jsons = [
        json.load(open(file, "r", encoding='utf-8')) for file in config_files
        if os.path.exists(file)
    ]
    return ConfigDict(merge_dict(*jsons))


class ConfigDict:
    """ Custom dict implementation to allow resolving key from parent """
    def __init__(self, value_dict, parent=None):
        self.__parent = None
        if parent is not None:
            if type(parent) is not ConfigDict:
                raise TypeError("parent must be of type ConfigDict")
            self.__parent = parent
        for key, value in value_dict.items():
            if type(value) is dict:
                value_dict[key] = ConfigDict(value, self)
        self.__dict = value_dict

    def __repr__(self):
        return repr(self.__dict)

    def __getitem__(self, indices):
        """ Resolve key in internal dict or fallback to parent """
        if not isinstance(indices, str):
            raise ("Only string indicies are supported")
        if indices in self.__dict or self.__parent is None:
            return self.__dict[indices]
        logging.warning("Key '%s' not found in %s, falling back to parent", indices, self)
        return self.__parent[indices]

    def __contains__(self, key):
        return self.__dict.__contains__(key)
