"""
Dashboard package for the Health & Wellness Information Pipeline.
Provides layout and callback modules consumed by app.py.
"""
from .layout import create_layout
from .callbacks import register_callbacks

__all__ = ["create_layout", "register_callbacks"]