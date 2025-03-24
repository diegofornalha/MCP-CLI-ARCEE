#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="veyrax-cli",
    version="0.1.0",
    description="Interface de linha de comando para a API do VeyraX",
    author="Diego Fornalha",
    author_email="diegofornalha@gmail.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.15.0",
        "colorama>=0.4.4",
        "rich>=10.0.0",
        "prompt-toolkit>=3.0.20",
    ],
    entry_points={
        "console_scripts": [
            "veyrax=veyrax_cli.veyrax_cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="veyrax, cli, api, arcee, llm",
    python_requires=">=3.7",
    include_package_data=True,
    zip_safe=False,
) 