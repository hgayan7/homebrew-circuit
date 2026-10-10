class Circuit < Formula
  desc "Governed execution boundary for autonomous AI agents"
  homepage "https://github.com/hgayan7/circuit"
  version "0.3.0"
  license "MIT"

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/hgayan7/circuit/releases/download/v0.3.0/circuit_0.3.0_darwin_arm64.tar.gz"
      sha256 "be99d07509090fbe39fcd571d5eb2de0e5d141fc7472eb26e36972d89c1c4553"
    else
      url "https://github.com/hgayan7/circuit/releases/download/v0.3.0/circuit_0.3.0_darwin_amd64.tar.gz"
      sha256 "eba135169484c2738b50c89138161fb61191f5dbc32bb64166e0b696db310342"
    end
  end

  on_linux do
    if Hardware::CPU.arm? && Hardware::CPU.is_64_bit?
      url "https://github.com/hgayan7/circuit/releases/download/v0.3.0/circuit_0.3.0_linux_arm64.tar.gz"
      sha256 "5a8558583bf23ac124b84ebfaf20ca6246e5dfcb2f2a01b075267c99a18ad772"
    else
      url "https://github.com/hgayan7/circuit/releases/download/v0.3.0/circuit_0.3.0_linux_amd64.tar.gz"
      sha256 "a6334fe887f33d85ad709b59bae6a73ecdea585932a8ad2718a791910c8e7511"
    end
  end

  def install
    bin.install "circuit"
  end

  test do
    assert_equal "circuit v#{version}", shell_output("#{bin}/circuit version 2>&1").strip
  end
end
