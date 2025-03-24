#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="arcee-cli",
    version="1.0.0",
    description="Interface de linha de comando para o Arcee AI",
    author="Diego Fornalha",
    author_email="diegofornalha@gmail.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.15.0",
        "colorama>=0.4.4",
        "rich>=10.0.0",
        "prompt-toolkit>=3.0.20",
        "pytest>=7.0.0",
    ],
    entry_points={
        "console_scripts": [
            "arcee=arcee_cli.presentation.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="arcee, cli, api, ai, chat",
    python_requires=">=3.7",
    include_package_data=True,
    zip_safe=False,
) 