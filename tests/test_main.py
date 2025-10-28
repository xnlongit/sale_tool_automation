#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test cases for ER Sports Automation Tool

Unit tests và integration tests cho các component chính.
"""

import unittest
import sys
import os

# Thêm src vào path để import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import BrowserAutomation, ERSportsAutomationGUI


class TestBrowserAutomation(unittest.TestCase):
    """
    Test cases cho BrowserAutomation class
    """
    
    def setUp(self):
        """
        Setup test environment
        """
        self.browser = BrowserAutomation(headless=True)
    
    def tearDown(self):
        """
        Cleanup after test
        """
        if self.browser.driver:
            self.browser.close()
    
    def test_browser_initialization(self):
        """
        Test browser initialization
        """
        self.assertIsNone(self.browser.driver)
        self.assertFalse(self.browser.is_logged_in)
        self.assertTrue(self.browser.headless)
    
    def test_setup_driver(self):
        """
        Test driver setup (requires Chrome)
        """
        # Chỉ test nếu Chrome có sẵn
        try:
            result = self.browser.setup_driver()
            if result:
                self.assertIsNotNone(self.browser.driver)
                self.browser.close()
        except Exception as e:
            self.skipTest(f"Chrome not available: {e}")


class TestERSportsAutomationGUI(unittest.TestCase):
    """
    Test cases cho ERSportsAutomationGUI class
    """
    
    def setUp(self):
        """
        Setup test environment
        """
        # Không khởi tạo GUI trong test để tránh tkinter issues
        pass
    
    def test_import_modules(self):
        """
        Test import các modules chính
        """
        try:
            import tkinter as tk
            import selenium
            import webdriver_manager
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Required modules not available: {e}")


class TestConfiguration(unittest.TestCase):
    """
    Test cases cho configuration files
    """
    
    def test_config_files_exist(self):
        """
        Test các file cấu hình tồn tại
        """
        config_files = [
            'config/accounts_sample.json',
            'config/products_sample.json',
            'config/config_sample.json'
        ]
        
        for file_path in config_files:
            with self.subTest(file=file_path):
                self.assertTrue(os.path.exists(file_path), f"Config file {file_path} not found")
    
    def test_json_format(self):
        """
        Test format JSON của các file cấu hình
        """
        import json
        
        config_files = [
            'config/accounts_sample.json',
            'config/products_sample.json',
            'config/config_sample.json'
        ]
        
        for file_path in config_files:
            with self.subTest(file=file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    self.fail(f"Invalid JSON in {file_path}: {e}")


class TestPackageStructure(unittest.TestCase):
    """
    Test cases cho package structure
    """
    
    def test_package_files_exist(self):
        """
        Test các file package tồn tại
        """
        package_files = [
            '__init__.py',
            'setup.py',
            'requirements.txt',
            'README.md',
            'LICENSE',
            'CHANGELOG.md',
            'MANIFEST.in',
            '.gitignore'
        ]
        
        for file_path in package_files:
            with self.subTest(file=file_path):
                self.assertTrue(os.path.exists(file_path), f"Package file {file_path} not found")
    
    def test_directory_structure(self):
        """
        Test cấu trúc thư mục
        """
        directories = [
            'src',
            'tests',
            'docs',
            'data',
            'logs',
            'config'
        ]
        
        for dir_path in directories:
            with self.subTest(directory=dir_path):
                self.assertTrue(os.path.isdir(dir_path), f"Directory {dir_path} not found")


if __name__ == '__main__':
    # Chạy tests
    unittest.main(verbosity=2)
