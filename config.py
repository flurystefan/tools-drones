# -*- coding: utf-8 -*-
"""
Module to load configuration files
"""

import json
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
    return merge_dict(*jsons)
