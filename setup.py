# Copyright (c) 2025 nvk
# Licensed under the MIT License

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="webdownloader",
    version="1.0.2",
    author="nvk",
    author_email="",
    description="A command-line tool to download websites for offline use with multiple output options",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nvk/webdownloader",
    py_modules=["webdownloader"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.2",
        "html2text>=2024.2.26",
    ],
    entry_points={
        "console_scripts": [
            "webdownloader=webdownloader:main",
        ],
    },
) 