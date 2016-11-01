"""
CozyWeboob main module
"""
from __future__ import absolute_import

from cozyweboob.WeboobProxy import WeboobProxy
from cozyweboob.__main__ import clean, main_fetch, main

__all__ = ["WeboobProxy", "clean", "main_fetch", "main"]
