# Circuit Homebrew tap

```sh
brew install hgayan7/circuit/circuit
# Already installed:
brew update
brew upgrade circuit
```

The formula supplies Linux/macOS amd64/arm64 binaries from [Circuit releases](https://github.com/hgayan7/circuit/releases).

An hourly GitHub Actions workflow tracks the newest published stable release. It verifies successful main CI and release-artifact validation for the exact tagged commit, downloads all four platform archives, checks their SHA-256 values, and commits the formula only after verification. Drafts and prereleases are excluded. Scheduled runs may be delayed by GitHub; maintainers can run the workflow manually too.

The updater uses this repository's scoped workflow token and requires no personal access token. It never publishes packages or containers. It refuses downgrades and fails without changing the formula when validation is missing or checksums disagree.
