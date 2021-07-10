#!/usr/bin/env python3
# setup.py

from setuptools import setup, find_packages


setup(
    name="aray",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib",
        "jupyter",
        "ipython",
        "ipdb",
        "black",
        "autopep8",
        "mypy",
        "pytest",
    ],
)
