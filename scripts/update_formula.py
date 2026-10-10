#!/usr/bin/env python3
"""Advance the tap only to the newest validated, published stable Circuit release."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

SOURCE = "hgayan7/circuit"
ROOT = Path(__file__).resolve().parents[1]


def gh_json(path):
    return json.loads(subprocess.check_output(["gh", "api", path], text=True))


def release_commit(tag):
    obj = gh_json(f"repos/{SOURCE}/git/ref/tags/{tag}")["object"]
    for _ in range(8):
        if obj["type"] == "commit":
            return obj["sha"]
        if obj["type"] != "tag":
            break
        obj = gh_json(f"repos/{SOURCE}/git/tags/{obj['sha']}")["object"]
    raise RuntimeError("release tag must resolve to a commit")


def validated_release(release):
    tag = release["tag_name"]
    if release["draft"] or release["prerelease"] or not re.fullmatch(r"v\d+\.\d+\.\d+", tag):
        raise RuntimeError("only published stable semantic-version releases are eligible")
    commit = release_commit(tag)
    for workflow, branch in (("ci.yml", "main"), ("release.yml", tag)):
        runs = gh_json(f"repos/{SOURCE}/actions/workflows/{workflow}/runs?head_sha={commit}&status=success&per_page=100")["workflow_runs"]
        if not any(run["head_sha"] == commit and run["head_branch"] == branch and run["status"] == "completed" and run["conclusion"] == "success" and run["event"] == "push" for run in runs):
            raise RuntimeError(f"{workflow} must have succeeded for exact release commit {commit}")
    return tag


def read_checksums(path):
    result = {}
    for line in path.read_text().splitlines():
        digest, name = line.split()
        name = name.lstrip("*")
        if name in result or not re.fullmatch(r"[a-fA-F0-9]{64}", digest):
            raise RuntimeError("invalid or duplicate checksum entry")
        result[name] = digest.lower()
    return result


def render_formula(version, hashes):
    def asset(os_name, arch):
        name = f"circuit_{version}_{os_name}_{arch}.tar.gz"
        return f'      url "https://github.com/{SOURCE}/releases/download/v{version}/{name}"\n      sha256 "{hashes[name]}"'
    return f'''class Circuit < Formula
  desc "Governed execution boundary for autonomous AI agents"
  homepage "https://github.com/{SOURCE}"
  version "{version}"
  license "MIT"

  on_macos do
    if Hardware::CPU.arm?
{asset("darwin", "arm64")}
    else
{asset("darwin", "amd64")}
    end
  end

  on_linux do
    if Hardware::CPU.arm? && Hardware::CPU.is_64_bit?
{asset("linux", "arm64")}
    else
{asset("linux", "amd64")}
    end
  end

  def install
    bin.install "circuit"
  end

  test do
    assert_equal "circuit v#{{version}}", shell_output("#{{bin}}/circuit version").strip
  end
end
'''


def main():
    release = gh_json(f"repos/{SOURCE}/releases/latest")
    tag = validated_release(release)
    version = tag[1:]
    formula = ROOT / "Formula/circuit.rb"
    old = re.search(r'^  version "(\d+\.\d+\.\d+)"$', formula.read_text(), re.M)
    if not old:
        raise RuntimeError("formula must have an explicit stable version")
    if tuple(map(int, version.split("."))) < tuple(map(int, old[1].split("."))):
        raise RuntimeError("refusing to downgrade the formula")
    names = [f"circuit_{version}_{os_name}_{arch}.tar.gz" for os_name in ("darwin", "linux") for arch in ("arm64", "amd64")]
    if not set(names + ["checksums.txt"]).issubset({asset["name"] for asset in release["assets"]}):
        raise RuntimeError("release does not contain all platform archives and checksums")
    with tempfile.TemporaryDirectory(prefix="circuit-tap-") as tmp:
        base = ["gh", "release", "download", tag, "--repo", SOURCE, "--dir", tmp]
        subprocess.run(base + ["--pattern", "checksums.txt"], check=True)
        hashes = read_checksums(Path(tmp) / "checksums.txt")
        if not set(names).issubset(hashes):
            raise RuntimeError("checksums are missing platform archives")
        new = render_formula(version, hashes)
        if formula.read_text() == new:
            print(f"Circuit {tag} formula is already current")
            return
        command = list(base)
        for name in names:
            command.extend(["--pattern", name])
        subprocess.run(command, check=True)
        for name in names:
            with (Path(tmp) / name).open("rb") as archive:
                actual = hashlib.file_digest(archive, "sha256").hexdigest()
            if actual != hashes.get(name):
                raise RuntimeError(f"checksum mismatch: {name}")
    formula.write_text(new)
    print(f"Updated Circuit to {tag}; exact-commit CI, release validation, and all four checksums passed")


if __name__ == "__main__":
    main()
