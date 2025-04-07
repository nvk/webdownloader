# Contributing to WebDownloader

Thank you for considering contributing to WebDownloader! This document provides guidelines for contributing to the project.

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests if available
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/webdownloader.git
cd webdownloader

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
```

## Code Style

Please follow the PEP 8 style guide for Python code.

## Pull Request Process

1. Update the README.md with details of changes if applicable
2. The PR should work on Python 3.6 and above
3. The PR will be merged once approved by a project maintainer

## Releasing

For maintainers, to create a new release:

1. Update version in setup.py
2. Create a new tag: `git tag -a v1.x.x -m "Release v1.x.x"`
3. Push the tag: `git push origin v1.x.x`
4. Create a new release on GitHub
5. Update the Homebrew formula

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. 