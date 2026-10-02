class Circuit < Formula
  desc "The Governance & Safety Proxy for AI Agents and MCP Tooling"
  homepage "https://circuitproxy.com"
  version "0.1.0"
  license "MIT"

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/hgayan7/circuit/releases/download/v0.1.0/circuit_0.1.0_darwin_arm64.tar.gz"
      sha256 "1ed4ed3fc0a46167d1fe52bde10f5a8e2ba7dfd0941bf4d6b1a1b478da9bad15"
    else
      url "https://github.com/hgayan7/circuit/releases/download/v0.1.0/circuit_0.1.0_darwin_amd64.tar.gz"
      sha256 "7fadbcd34d53f8ef6b82fbed490eb55cd84ad7925480037420e49c165ce6bdd3"
    end
  end

  on_linux do
    if Hardware::CPU.arm? && Hardware::CPU.is_64_bit?
      url "https://github.com/hgayan7/circuit/releases/download/v0.1.0/circuit_0.1.0_linux_arm64.tar.gz"
      sha256 "b31ead694dcac684f5831832ebb680aeec48fb71bdfd3c7c2b65b36dc89ae3fb"
    else
      url "https://github.com/hgayan7/circuit/releases/download/v0.1.0/circuit_0.1.0_linux_amd64.tar.gz"
      sha256 "50608cb8b1825a236e81dd1fe86937df2ab11ee1386ca8e51c57c32b24597b14"
    end
  end

  def install
    bin.install "circuit"
  end

  test do
    system "#{bin}/circuit", "version"
  end
end
