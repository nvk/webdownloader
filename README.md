# WebDownloader

WebDownloader is a small command-line tool for saving same-domain web pages for
offline reading. It can write a local HTML copy with rewritten links, export
pages to a single Markdown file, or download only one page plus its direct
resources.

## Features

- Crawls same-domain HTML pages from a starting URL.
- Saves direct page resources such as linked stylesheets, scripts, and image
  `src` files.
- Rewrites internal HTML, stylesheet, script, and image links to local relative
  paths.
- Supports a page-only mode for saving one page and its direct resources.
- Supports an optional Markdown export mode with downloaded Markdown image
  references.
- Can skip pages marked as non-English by URL language segment or HTML language
  metadata.
- Includes a realtor.com/REA gallery helper for extracting higher-quality
  gallery image URLs.

## Installation

### pip

```bash
pip install git+https://github.com/nvk/webdownloader.git
```

After installation, run:

```bash
webdownloader --help
```

To use `--markdown`, install the optional Markdown dependency:

```bash
pip install "webdownloader[markdown] @ git+https://github.com/nvk/webdownloader.git"
```

To use SOCKS proxy URLs such as `socks5h://127.0.0.1:1080`, install the proxy
extra:

```bash
pip install "webdownloader[proxy] @ git+https://github.com/nvk/webdownloader.git"
```

### Homebrew

```bash
brew install nvk/tap/webdownloader
```

### From source

```bash
git clone https://github.com/nvk/webdownloader.git
cd webdownloader
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The source `requirements.txt` includes the optional Markdown dependency for
development and full local testing.

Run from source with:

```bash
python webdownloader.py --help
```

## Usage

```bash
webdownloader -d URL [options]
```

When running from a source checkout, use `python webdownloader.py` instead of
`webdownloader`.

### Options

- `-d, --download URL`: URL to download.
- `-o, --output DIR`: Output directory. Defaults to the domain name.
- `--delay SECONDS`: Delay between requests. Defaults to `0.5`.
- `--english-only`: Skip pages that appear to be non-English.
- `--markdown`: Export crawled HTML pages to one Markdown file. Requires the
  optional Markdown dependency.
- `-p, --page-only`: Download only the starting page and its direct resources.
- `-g, --gallery-mode`: Extract and download supported gallery images.
- `-c, --country-code CODE`: Country code for gallery image URL generation.
  Defaults to `cr`.
- `--mullvad-check`: Verify traffic exits through Mullvad before downloading.
- `--require-exit-ip IP`: Require this public VPN exit IP before downloading.
- `--vpn-check-url URL`: URL used for VPN preflight checks. Defaults to
  Mullvad's public connection-check JSON endpoint.
- `--vpn-check-timeout SECONDS`: Timeout for VPN preflight checks. Defaults to
  `10`.
- `--proxy URL`: Route this downloader process through an HTTP or SOCKS proxy.
  Use `socks5h://` for SOCKS5 with DNS resolution through the proxy.

### Examples

Download a same-domain site:

```bash
webdownloader -d example.com
```

Download a single page plus direct resources:

```bash
webdownloader -d example.com/page -p -o saved-page
```

Export pages as Markdown:

```bash
webdownloader -d example.com --markdown -o example-markdown
```

Skip pages marked as non-English:

```bash
webdownloader -d example.com --english-only
```

Download supported gallery images:

```bash
webdownloader -d "https://www.realtor.com/international/cr/example-property" -p -g
```

## VPN Preflight Checks

WebDownloader uses normal operating-system networking. If a WireGuard VPN is
connected and routing your traffic, downloads should use that route without any
special downloader configuration.

For safer runs, enable a preflight check before crawling:

```bash
webdownloader -d example.com --mullvad-check
```

For any WireGuard VPN provider, check the public exit IP you expect:

```bash
webdownloader -d example.com --require-exit-ip 203.0.113.42
```

To route only WebDownloader through a VPN path, run a local proxy backed by that
VPN and point WebDownloader at it:

```bash
webdownloader -d example.com --proxy socks5h://127.0.0.1:1080 --mullvad-check
```

`--proxy` affects only this process. Your browser and other apps keep using
their normal route unless you configure them separately.

The default VPN check URL is `https://am.i.mullvad.net/json`. Mullvad documents
that this endpoint continues to serve API responses for connection checks. You
can override it with `--vpn-check-url` if you use another endpoint that returns
JSON with an `ip` field or plain-text IP output.

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -v
```

Syntax-check the scripts with:

```bash
python -m py_compile webdownloader.py setup.py prepare_homebrew_release.py tests/test_webdownloader.py
bash -n create_homebrew_tap.sh update_tap.sh
```

## Release Helpers

`prepare_homebrew_release.py` updates `setup.py` and the local Homebrew formula for a
new version:

```bash
python prepare_homebrew_release.py 1.0.3
```

After creating and pushing a matching GitHub tag, calculate the release tarball
SHA and update the local formula with:

```bash
python prepare_homebrew_release.py 1.0.3 --calculate-sha
```

## Limitations

- WebDownloader does not execute JavaScript, so client-rendered content may not
  appear in the saved output.
- It downloads direct HTML references only. Assets referenced from CSS
  `url(...)`, `srcset`, service workers, or runtime JavaScript are not fully
  discovered yet.
- Markdown export focuses on readable content, not pixel-perfect layout.
- Markdown export uses the optional `html2text` package, which has its own
  license terms.
- VPN checks verify routing before the crawl starts; they do not connect,
  disconnect, or manage WireGuard tunnels.
- Mullvad's app does not support inverse split tunneling, so routing only this
  app through Mullvad requires an external per-app route such as a local
  WireGuard-backed proxy.
- The tool does not enforce `robots.txt`; you are responsible for respecting
  each site's terms, access policies, and rate limits.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
