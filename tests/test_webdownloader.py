import contextlib
import functools
import http.server
import io
import os
import socketserver
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

from prepare_homebrew_release import update_formula
from webdownloader import (
    check_vpn_preflight,
    convert_to_relative_url,
    create_http_session,
    download_website,
    format_vpn_preflight_summary,
    is_non_english_page,
    is_valid_url,
    local_path_for_url,
    output_path_for_url,
    require_html2text,
    validate_proxy_url,
)


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


class WorkingDirectory:
    def __init__(self, path):
        self.path = path
        self.previous = None

    def __enter__(self):
        self.previous = os.getcwd()
        os.chdir(self.path)

    def __exit__(self, exc_type, exc, tb):
        os.chdir(self.previous)


class FakeResponse:
    def __init__(self, status_code=200, data=None, text=''):
        self.status_code = status_code
        self._data = data
        self.text = text

    def json(self):
        if self._data is None:
            raise ValueError("No JSON")
        return self._data


class WebDownloaderTests(unittest.TestCase):
    def test_local_paths_are_normalized_inside_output(self):
        self.assertEqual(
            local_path_for_url('https://example.com/../../outside.html'),
            'outside.html',
        )
        self.assertEqual(
            local_path_for_url('https://example.com/%2e%2e/secret.txt'),
            'secret.txt',
        )
        self.assertEqual(
            local_path_for_url('https://example.com/docs/'),
            'docs/index.html',
        )

        with tempfile.TemporaryDirectory() as output_dir:
            _, output_path = output_path_for_url(
                'https://example.com/../../outside.html',
                output_dir,
            )
            Path(output_path).resolve().relative_to(Path(output_dir).resolve())

    def test_relative_url_conversion_preserves_fragments(self):
        self.assertEqual(
            convert_to_relative_url(
                'docs/index.html',
                'https://example.com/about/team.html#people',
                'https://example.com',
                '/tmp/site',
            ),
            '../about/team.html#people',
        )
        self.assertEqual(
            convert_to_relative_url(
                'index.html',
                'https://external.example/page.html#intro',
                'https://example.com',
                '/tmp/site',
            ),
            'https://external.example/page.html#intro',
        )

    def test_url_validation_rejects_non_http_links(self):
        self.assertFalse(is_valid_url('javascript:void(0)', 'https://example.com'))
        self.assertFalse(is_valid_url('mailto:test@example.com', 'https://example.com'))
        self.assertTrue(is_valid_url('https://example.com/docs', 'https://example.com'))

    def test_create_http_session_sets_process_proxy(self):
        session = create_http_session('socks5h://127.0.0.1:1080')

        self.assertEqual(session.proxies['http'], 'socks5h://127.0.0.1:1080')
        self.assertEqual(session.proxies['https'], 'socks5h://127.0.0.1:1080')

    def test_proxy_validation_rejects_unsupported_scheme(self):
        with self.assertRaisesRegex(RuntimeError, 'Unsupported proxy scheme'):
            validate_proxy_url('ftp://127.0.0.1:1080')

    def test_socks_proxy_validation_error_is_actionable(self):
        real_import = __import__

        def fake_import(name, *args, **kwargs):
            if name == 'socks':
                raise ImportError("No module named socks")
            return real_import(name, *args, **kwargs)

        with mock.patch('builtins.__import__', side_effect=fake_import):
            with self.assertRaisesRegex(RuntimeError, 'SOCKS proxy support requires PySocks'):
                validate_proxy_url('socks5h://127.0.0.1:1080')

    def test_markdown_dependency_error_is_actionable(self):
        real_import = __import__

        def fake_import(name, *args, **kwargs):
            if name == 'html2text':
                raise ImportError("No module named html2text")
            return real_import(name, *args, **kwargs)

        with mock.patch('builtins.__import__', side_effect=fake_import):
            with self.assertRaisesRegex(RuntimeError, 'Markdown export requires html2text'):
                require_html2text()

    def test_mullvad_preflight_accepts_reported_exit_ip(self):
        response = FakeResponse(data={
            'ip': '198.51.100.10',
            'mullvad_exit_ip': True,
            'mullvad_exit_ip_hostname': 'us-test-wg-001',
            'city': 'New York',
            'country': 'United States',
        })

        with mock.patch('webdownloader.requests.get', return_value=response) as get:
            data = check_vpn_preflight(mullvad_check=True, timeout=3)

        get.assert_called_once_with('https://am.i.mullvad.net/json', timeout=3)
        self.assertEqual(data['ip'], '198.51.100.10')
        self.assertIn('us-test-wg-001', format_vpn_preflight_summary(data))

    def test_mullvad_preflight_rejects_non_mullvad_exit_ip(self):
        response = FakeResponse(data={
            'ip': '198.51.100.20',
            'mullvad_exit_ip': False,
        })

        with mock.patch('webdownloader.requests.get', return_value=response):
            with self.assertRaisesRegex(RuntimeError, 'not reported as a Mullvad exit IP'):
                check_vpn_preflight(mullvad_check=True)

    def test_generic_vpn_preflight_can_require_exit_ip(self):
        response = FakeResponse(data={'ip': '203.0.113.42'})

        with mock.patch('webdownloader.requests.get', return_value=response):
            data = check_vpn_preflight(expected_exit_ip='203.0.113.42')

        self.assertEqual(data['ip'], '203.0.113.42')

    def test_generic_vpn_preflight_rejects_unexpected_exit_ip(self):
        response = FakeResponse(text='203.0.113.99')

        with mock.patch('webdownloader.requests.get', return_value=response):
            with self.assertRaisesRegex(RuntimeError, 'expected 203.0.113.42'):
                check_vpn_preflight(expected_exit_ip='203.0.113.42')

    def test_english_only_detection_allows_english_and_non_language_segments(self):
        self.assertFalse(is_non_english_page('https://example.com/en/docs'))
        self.assertFalse(is_non_english_page('https://example.com/go/docs'))
        self.assertFalse(is_non_english_page('https://example.com/us/listings'))
        self.assertTrue(is_non_english_page('https://example.com/fr/docs'))
        self.assertTrue(is_non_english_page('https://example.com/es-mx/listings'))
        self.assertFalse(is_non_english_page(
            'https://example.com/docs',
            '<html lang="en-US"><body>English</body></html>',
        ))
        self.assertTrue(is_non_english_page(
            'https://example.com/docs',
            '<html lang="fr"><body>Français</body></html>',
        ))

    def test_page_only_download_saves_resources(self):
        with tempfile.TemporaryDirectory(prefix='wd-site.') as site_dir:
            with tempfile.TemporaryDirectory(prefix='wd-output.') as output_dir:
                site = Path(site_dir)
                site.joinpath('index.html').write_text(
                    '<!doctype html><html><head>'
                    '<link rel="stylesheet" href="/style.css">'
                    '<script src="/app.js"></script>'
                    '</head><body>'
                    '<img src="/pic.png">'
                    '<a href="/other.html#section">other</a>'
                    '<a href="#local">local</a>'
                    '</body></html>',
                    encoding='utf-8',
                )
                site.joinpath('style.css').write_text('body { color: red; }', encoding='utf-8')
                site.joinpath('app.js').write_text('console.log("ok");', encoding='utf-8')
                site.joinpath('pic.png').write_bytes(b'fake png')

                handler = functools.partial(QuietHandler, directory=site_dir)
                with socketserver.TCPServer(('127.0.0.1', 0), handler) as httpd:
                    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
                    thread.start()
                    url = f'http://127.0.0.1:{httpd.server_address[1]}/'
                    try:
                        with contextlib.redirect_stdout(io.StringIO()):
                            download_website(url, output_dir=output_dir, delay=0, page_only=True)
                    finally:
                        httpd.shutdown()
                        thread.join(timeout=2)

                root = Path(output_dir)
                self.assertTrue(root.joinpath('index.html').is_file())
                self.assertEqual(root.joinpath('style.css').read_text(encoding='utf-8'), 'body { color: red; }')
                self.assertEqual(root.joinpath('app.js').read_text(encoding='utf-8'), 'console.log("ok");')
                self.assertEqual(root.joinpath('pic.png').read_bytes(), b'fake png')

                html = root.joinpath('index.html').read_text(encoding='utf-8')
                self.assertIn('href="style.css"', html)
                self.assertIn('src="app.js"', html)
                self.assertIn('src="pic.png"', html)
                self.assertIn('href="other.html#section"', html)
                self.assertIn('href="#local"', html)


class HomebrewReleaseTests(unittest.TestCase):
    def test_update_formula_replaces_only_release_sha(self):
        original_formula = '''class Webdownloader < Formula
  url "https://github.com/nvk/webdownloader/archive/refs/tags/v1.0.2.tar.gz"
  sha256 "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

  resource "requests" do
    url "https://files.pythonhosted.org/packages/requests.tar.gz"
    sha256 "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
  end
end
'''

        with tempfile.TemporaryDirectory() as temp_dir:
            formula_path = Path(temp_dir, 'webdownloader.rb')
            formula_path.write_text(original_formula, encoding='utf-8')

            with WorkingDirectory(temp_dir):
                with contextlib.redirect_stdout(io.StringIO()):
                    update_formula(
                        '1.2.3',
                        'cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc',
                    )

            updated_formula = formula_path.read_text(encoding='utf-8')
            self.assertIn('v1.2.3.tar.gz', updated_formula)
            self.assertIn('sha256 "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"', updated_formula)
            self.assertIn('sha256 "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"', updated_formula)
            self.assertNotIn('sha256 "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"', updated_formula)


if __name__ == '__main__':
    unittest.main()
