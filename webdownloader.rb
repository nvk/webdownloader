# Copyright (c) 2025 nvk
# Licensed under the MIT License

class Webdownloader < Formula
  include Language::Python::Virtualenv

  desc "Command-line tool to download websites for offline use with multiple output options"
  homepage "https://github.com/nvk/webdownloader"
  url "https://github.com/nvk/webdownloader/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "0969a8d1a97900ac880f641d39fe79cdf23e3a37db4d0aa7328005b62efdadf8"
  license "MIT"

  depends_on "python@3.9"

  resource "beautifulsoup4" do
    url "https://files.pythonhosted.org/packages/d8/12/23125e8f01f827e4a297f3372f15ef6a6c946ef9fc82982e7d2238d5364c/beautifulsoup4-4.12.2.tar.gz"
    sha256 "492bbc69dca35d12daac71c4db1bfff0c876c00ef4a2ffacce226d4638eb72da"
  end

  resource "certifi" do
    url "https://files.pythonhosted.org/packages/71/da/e94e26401b62acd6d91df2b52954aceb7f561743aa5ccc32152886c76c96/certifi-2025.1.31.tar.gz"
    sha256 "2412806c7f26097242850281948cf18164e880f3e880fcc2289c56a8274c0031"
  end

  resource "charset-normalizer" do
    url "https://files.pythonhosted.org/packages/63/09/c1bc53dab74b1816a00d8d030de5bf98f724c52c1635e07681d312f20be8/charset-normalizer-3.3.2.tar.gz"
    sha256 "f30c3cb33b24454a82faecaf01b19c18562b1e89558fb6c56de4d9118a032fd5"
  end

  resource "html2text" do
    url "https://files.pythonhosted.org/packages/ab/8a/7c343a58c9a47a13fbbc1460ef839ceb7ebd5e377ba45157f0866113faa8/html2text-2024.2.26.tar.gz"
    sha256 "a9a7731eeead6d4ee9d4b6d8cfba2b0f3fb3212a6f4880c323e2671e9d26484b"
  end

  resource "idna" do
    url "https://files.pythonhosted.org/packages/bf/3f/ea4b9117521a1e9c50344b909be7886dd00a519552724809bb1f486986c2/idna-3.6.tar.gz"
    sha256 "9ecdbbd083b06798ae1e86adcbfe8ab1479cf864e4ee30fe4e46a003d12491ca"
  end

  resource "requests" do
    url "https://files.pythonhosted.org/packages/9d/be/10918a2eac4ae9f02f6cfe6414b7a155ccd8f7f9d4380d62fd5b955065c3/requests-2.31.0.tar.gz"
    sha256 "942c5a758f98d790eaed1a29cb6eefc7ffb0d1cf7af05c3d2791656dbd6ad1e1"
  end

  resource "soupsieve" do
    url "https://files.pythonhosted.org/packages/ce/21/952a240de1c196c7e3fbcd4e559681f0419b1280c617db21157a0390717b/soupsieve-2.5.tar.gz"
    sha256 "5663d5a7b3bfaeee0bc4372e7fc48f9cff4940b3eec54a6451cc5299f1097690"
  end

  resource "urllib3" do
    url "https://files.pythonhosted.org/packages/7a/50/7fd50a27caa0961c1526c7c260ddb5238b2103bb1aa312bc9bed400afe67/urllib3-2.2.1.tar.gz"
    sha256 "d0570876c61ab9e520d776c38acbbb5b05a776d3f9ff98a5c8fd5162a444cf19"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system bin/"webdownloader", "--help"
  end
end 