#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for ER Sports Automation Tool

Cài đặt package Python cho ER Sports Automation Tool.
"""

from setuptools import setup, find_packages
import os

# Đọc README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "ER Sports Automation Tool with GUI"

# Đọc requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return [
        'selenium>=4.15.0',
        'webdriver-manager>=4.0.0'
    ]

setup(
    name="er-sports-automation",
    version="1.0.0",
    author="AI Assistant",
    author_email="ai@example.com",
    description="ER Sports Automation Tool with GUI",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/er-sports-automation",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Software Development :: Testing",
        "Topic :: Office/Business",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.800',
        ],
        'docs': [
            'sphinx>=4.0',
            'sphinx-rtd-theme>=1.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'er-sports-automation=er_sports_automation.src.main:main',
        ],
    },
    include_package_data=True,
    package_data={
        'er_sports_automation': [
            'config/*.json',
            'data/*.json',
            'docs/*.md',
        ],
    },
    keywords=[
        'automation',
        'selenium',
        'web-scraping',
        'gui',
        'tkinter',
        'er-sports',
        'e-commerce',
        'browser-automation'
    ],
    project_urls={
        'Bug Reports': 'https://github.com/your-username/er-sports-automation/issues',
        'Source': 'https://github.com/your-username/er-sports-automation',
        'Documentation': 'https://er-sports-automation.readthedocs.io/',
    },
)
