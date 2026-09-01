# -*- coding: utf-8 -*-


def classFactory(iface):
    from .gbfs_now import gbfs_now

    return gbfs_now(iface)
