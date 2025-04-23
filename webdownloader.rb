# Copyright (c) 2025 nvk
# Licensed under the MIT License

class Webdownloader < Formula
  include Language::Python::Virtualenv

  desc "Command-line tool to download websites for offline use with multiple output options"
  homepage "https://github.com/nvk/webdownloader"
  url "https://github.com/nvk/webdownloader/archive/refs/tags/v1.0.2.tar.gz"
  sha256 "b913e17694995905313659435308e63773f2f93d57caab9d62ca5a6a510e47ec"
  license "MIT"

  depends_on "python@3.9"

  resource "beautifulsoup4" do
    url "https://files.pythonhosted.org/packages/af/0b/44c39cf3b18a9280950ad63a579ce395dda4c32193ee9da7ff0aed547094/beautifulsoup4-4.12.2.tar.gz"
    sha256 "b913e17694995905313659435308e63773f2f93d57caab9d62ca5a6a510e47ec"
  end

  resource "html2text" do
    url "https://files.pythonhosted.org/packages/6c/f9/033a17d8ea8181aee41f20c74c3b20f1ccbefbbc3f7cd24e3692de99fb25/html2text-2020.1.16.tar.gz"
    sha256 "b913e17694995905313659435308e63773f2f93d57caab9d62ca5a6a510e47ec"
  end

  resource "requests" do
    url "https://files.pythonhosted.org/packages/9d/ee/391076f5937f0a8cdf5e53b701ffc91753e87b07d66bae4a09aa671897bf/requests-2.28.2.tar.gz"
    sha256 "b913e17694995905313659435308e63773f2f93d57caab9d62ca5a6a510e47ec"
  end

  resource "urllib3" do
    url "https://files.pythonhosted.org/packages/c5/52/fe421fb7364aa738b3506a2d99e4f3a56e079c0a798e9f4fa5e14c60922f/urllib3-1.26.14.tar.gz"
    sha256 "b913e17694995905313659435308e63773f2f93d57caab9d62ca5a6a510e47ec"
  end

  resource "certifi" do
    url "https://files.pythonhosted.org/packages/37/f7/2b1b0ec44fdc30a3d31dfebe52226be9ddc40cd6c0f34ffc8923ba423b69/certifi-2022.12.7.tar.gz"
    sha256 "b913e17694995905313659435308e63773f2f93d57caab9d62ca5a6a510e47ec"
  end

  resource "charset-normalizer" do
    url "https://files.pythonhosted.org/packages/96/d7/1675d9089a1f4677df5eb29c3f8b064aa1e70c1251a0a8a127803158942d/charset-normalizer-3.0.1.tar.gz"
    sha256 "b913e17694995905313659435308e63773f2f93d57caab9d62ca5a6a510e47ec"
  end

  resource "idna" do
    url "https://files.pythonhosted.org/packages/8b/e1/43beb3d38dba6cb420cefa297822eac205a277ab43e5ba5d5c46faf96438/idna-3.4.tar.gz"
    sha256 "b913e17694995905313659435308e63773f2f93d57caab9d62ca5a6a510e47ec"
  end

  resource "soupsieve" do
    url "https://files.pythonhosted.org/packages/f3/03/bac179d539362319b4779a00764e95f7542f4920084163db6b0fd4742d38/soupsieve-2.3.2.post1.tar.gz"
    sha256 "b913e17694995905313659435308e63773f2f93d57caab9d62ca5a6a510e47ec"
  end

  # Include only the essential dependencies
  # Requests has its own dependencies (certifi, charset-normalizer, idna, urllib3)
  # BeautifulSoup4 depends on soupsieve

  def install
    virtualenv_install_with_resources
  end

  test do
    system bin/"webdownloader", "--help"
  end
end 