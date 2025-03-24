#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI do Arcee AI
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="arcee-cli",
    version="1.0.0",
    author="Arcee AI",
    author_email="support@arcee.ai",
    description="CLI para interagir com a API do Arcee AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/diegofornalha/MCP-CLI-ARCEE",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.15.0",
        "colorama>=0.4.4",
        "rich>=10.0.0",
        "prompt-toolkit>=3.0.20",
        "pytest>=7.0.0",
        "typer>=0.9.0",
        "openai>=1.12.0",
    ],
    entry_points={
        "console_scripts": [
            "arcee=arcee_cli.__main__:app",
        ],
    },
)
