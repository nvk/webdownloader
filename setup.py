# Copyright (c) 2025 nvk
# Licensed under the MIT License

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="webdownloader",
    version="1.1.0",
    author="nvk",
    description="A command-line tool to download websites for offline use with multiple output options",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nvk/webdownloader",
    py_modules=["webdownloader"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.34.2",
        "beautifulsoup4>=4.14.3",
    ],
    extras_require={
        "markdown": [
            "html2text>=2025.4.15",
        ],
        "proxy": [
            "requests[socks]>=2.34.2",
        ],
    },
    project_urls={
        "Source": "https://github.com/nvk/webdownloader",
        "Issues": "https://github.com/nvk/webdownloader/issues",
    },
    entry_points={
        "console_scripts": [
            "webdownloader=webdownloader:main",
        ],
    },
)
