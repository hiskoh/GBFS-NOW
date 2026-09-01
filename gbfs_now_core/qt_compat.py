# -*- coding: utf-8 -*-


_ENUM_CLASSES = (
    "AlignmentFlag",
    "ArrowType",
    "AspectRatioMode",
    "CaseSensitivity",
    "CursorShape",
    "DockWidgetArea",
    "ItemDataRole",
    "ItemFlag",
    "MouseButton",
    "Orientation",
    "ScrollBarPolicy",
    "SortOrder",
    "TextFormat",
    "TransformationMode",
)


class CompatibleQt:
    def __init__(self, qt):
        self._qt = qt

    def __getattr__(self, name):
        value = getattr(self._qt, name, None)
        if value is not None:
            return value
        for class_name in _ENUM_CLASSES:
            enum_class = getattr(self._qt, class_name, None)
            value = getattr(enum_class, name, None)
            if value is not None:
                return value
        raise AttributeError(name)


def compatible_qt(qt):
    return CompatibleQt(qt)


def enum_value(qt, enum_class_name, value_name):
    enum_class = getattr(qt, enum_class_name, None)
    if enum_class is not None:
        value = getattr(enum_class, value_name, None)
        if value is not None:
            return value
    return getattr(qt, value_name)


def size_policy(policy, name):
    value = getattr(policy, name, None)
    if value is not None:
        return value
    return getattr(policy.Policy, name)


def class_enum(owner, name):
    value = getattr(owner, name, None)
    if value is not None:
        return value
    for member_name in dir(owner):
        member = getattr(owner, member_name)
        value = getattr(member, name, None)
        if value is not None:
            return value
    raise AttributeError(name)


def network_reply_no_error(reply_class):
    value = getattr(reply_class, "NoError", None)
    if value is not None:
        return value
    return getattr(getattr(reply_class, "NetworkError"), "NoError")


def qgis_message_level(qgis, name):
    value = getattr(qgis, name, None)
    if value is not None:
        return value
    return getattr(getattr(qgis, "MessageLevel"), name)


def log_message_level(qgis, warning=False):
    return qgis_message_level(qgis, "Warning" if warning else "Info")
