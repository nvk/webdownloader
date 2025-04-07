# Copyright (c) 2025 nvk
# Licensed under the MIT License

class Webdownloader < Formula
  include Language::Python::Virtualenv

  desc "Command-line tool to download websites for offline use with multiple output options"
  homepage "https://github.com/nvk/webdownloader"
  url "https://github.com/nvk/webdownloader/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "REPLACE_WITH_ACTUAL_SHA256_AFTER_RELEASE"
  license "MIT"

  depends_on "python@3.9"

  resource "beautifulsoup4" do
    url "https://files.pythonhosted.org/packages/d8/12/23125e8f01f827e4a297f3372f15ef6a6c946ef9fc82982e7d2238d5364c/beautifulsoup4-4.12.2.tar.gz"
    sha256 "0969a8d1a97900ac880f641d39fe79cdf23e3a37db4d0aa7328005b62efdadf8"
  end

  resource "certifi" do
    url "https://files.pythonhosted.org/packages/71/da/e94e26401b62acd6d91df2b52954aceb7f561743aa5ccc32152886c76c96/certifi-2025.1.31.tar.gz"
    sha256 "0969a8d1a97900ac880f641d39fe79cdf23e3a37db4d0aa7328005b62efdadf8"
  end

  resource "charset-normalizer" do
    url "https://files.pythonhosted.org/packages/63/09/c1bc53dab74b1816a00d8d030de5bf98f724c52c1635e07681d312f20be8/charset-normalizer-3.3.2.tar.gz"
    sha256 "0969a8d1a97900ac880f641d39fe79cdf23e3a37db4d0aa7328005b62efdadf8"
  end

  resource "html2text" do
    url "https://files.pythonhosted.org/packages/ab/8a/7c343a58c9a47a13fbbc1460ef839ceb7ebd5e377ba45157f0866113faa8/html2text-2024.2.26.tar.gz"
    sha256 "0969a8d1a97900ac880f641d39fe79cdf23e3a37db4d0aa7328005b62efdadf8"
  end

  resource "idna" do
    url "https://files.pythonhosted.org/packages/bf/3f/ea4b9117521a1e9c50344b909be7886dd00a519552724809bb1f486986c2/idna-3.6.tar.gz"
    sha256 "0969a8d1a97900ac880f641d39fe79cdf23e3a37db4d0aa7328005b62efdadf8"
  end

  resource "requests" do
    url "https://files.pythonhosted.org/packages/9d/be/10918a2eac4ae9f02f6cfe6414b7a155ccd8f7f9d4380d62fd5b955065c3/requests-2.31.0.tar.gz"
    sha256 "0969a8d1a97900ac880f641d39fe79cdf23e3a37db4d0aa7328005b62efdadf8"
  end

  resource "soupsieve" do
    url "https://files.pythonhosted.org/packages/ce/21/952a240de1c196c7e3fbcd4e559681f0419b1280c617db21157a0390717b/soupsieve-2.5.tar.gz"
    sha256 "0969a8d1a97900ac880f641d39fe79cdf23e3a37db4d0aa7328005b62efdadf8"
  end

  resource "urllib3" do
    url "https://files.pythonhosted.org/packages/7a/50/7fd50a27caa0961c1526c7c260ddb5238b2103bb1aa312bc9bed400afe67/urllib3-2.2.1.tar.gz"
    sha256 "0969a8d1a97900ac880f641d39fe79cdf23e3a37db4d0aa7328005b62efdadf8"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system bin/"webdownloader", "--help"
  end
end 