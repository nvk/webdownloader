# Contributing to WebDownloader

Contributions are welcome. Please keep changes focused, include tests for
behavior changes, and avoid committing downloaded websites, generated images,
virtual environments, or build artifacts.

## Development Setup

```bash
git clone https://github.com/nvk/webdownloader.git
cd webdownloader
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

WebDownloader supports Python 3.9 and newer.

## Before Opening a Pull Request

Run the regression tests:

```bash
python -m unittest discover -v
```

Run syntax checks:

```bash
python -m py_compile webdownloader.py setup.py prepare_homebrew_release.py tests/test_webdownloader.py
bash -n create_homebrew_tap.sh update_tap.sh
```

For downloader changes, add or update tests in `tests/` using a local HTTP
fixture instead of depending on a live third-party site.

## Pull Request Guidelines

1. Keep the PR scoped to one behavior change or cleanup.
2. Update `README.md` when user-facing behavior changes.
3. Include a short description of the test coverage you ran.
4. Do not include downloaded site output, package archives, virtual
   environments, or local OS/editor files.

## Releases

Maintainers can prepare a release with:

```bash
python prepare_homebrew_release.py 1.0.3
```

Then create and push the tag:

```bash
git tag -a v1.0.3 -m "Release v1.0.3"
git push origin v1.0.3
```

After the GitHub release tarball exists, update the Homebrew formula SHA:

```bash
python prepare_homebrew_release.py 1.0.3 --calculate-sha
```

## Conduct

Be respectful, specific, and constructive in issues and pull requests.
