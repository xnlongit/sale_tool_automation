#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ER Sports Automation Tool - Python Package

Công cụ tự động đăng nhập và mua hàng từ website er-sports.com với giao diện đồ họa.

Tác giả: AI Assistant
Phiên bản: 1.0.0
Ngày tạo: 2024
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"
__email__ = "ai@example.com"
__description__ = "ER Sports Automation Tool with GUI"

# Import các class chính
from .src.main import ERSportsAutomationGUI, BrowserAutomation

# Export các class chính
__all__ = [
    'ERSportsAutomationGUI',
    'BrowserAutomation',
    '__version__',
    '__author__',
    '__email__',
    '__description__'
]
