# -*- coding: utf-8 -*-

import json
import os

EN = "en"
JA = "ja"


def load_field_labels():
    path = os.path.join(os.path.dirname(__file__), "field_labels.json")
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


FIELD_LABELS = load_field_labels()


def label_language(use_japanese):
    return JA if use_japanese else EN


def field_label(group, field_key, language):
    labels = FIELD_LABELS.get(group, {}).get(field_key, {})
    return labels.get(language) or labels.get(EN) or field_key
