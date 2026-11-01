#!/usr/bin/env bash
# Install pinned shellcheck, actionlint, and gitleaks into .tools/.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${LINT_TOOLS_DIR:-$ROOT/.tools}"
mkdir -p "$DEST"

SHELLCHECK_VERSION="${SHELLCHECK_VERSION:-0.11.0}"
SHELLCHECK_SHA256="${SHELLCHECK_SHA256:-8c3be12b05d5c177a04c29e3c78ce89ac86f1595681cab149b65b97c4e227198}"
ACTIONLINT_VERSION="${ACTIONLINT_VERSION:-1.7.12}"
ACTIONLINT_SHA256="${ACTIONLINT_SHA256:-8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8}"
GITLEAKS_VERSION="${GITLEAKS_VERSION:-8.30.1}"
GITLEAKS_SHA256="${GITLEAKS_SHA256:-551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb}"

need_install() {
    local bin_name="$1"
    local version_cmd="$2"
    local expected="$3"
    if [[ ! -x "$DEST/$bin_name" ]]; then
        return 0
    fi
    if ! "$DEST/$bin_name" "$version_cmd" 2>/dev/null | grep -q "$expected"; then
        return 0
    fi
    return 1
}

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

if need_install shellcheck --version "$SHELLCHECK_VERSION"; then
    curl -fsSL -o "$tmp/shellcheck.tar.xz" \
        "https://github.com/koalaman/shellcheck/releases/download/v${SHELLCHECK_VERSION}/shellcheck-v${SHELLCHECK_VERSION}.linux.x86_64.tar.xz"
    echo "${SHELLCHECK_SHA256}  $tmp/shellcheck.tar.xz" | sha256sum -c -
    tar -xJf "$tmp/shellcheck.tar.xz" -C "$tmp"
    install -m 0755 \
        "$tmp/shellcheck-v${SHELLCHECK_VERSION}/shellcheck" \
        "$DEST/shellcheck"
fi

if need_install actionlint -version "$ACTIONLINT_VERSION"; then
    curl -fsSL -o "$tmp/actionlint.tar.gz" \
        "https://github.com/rhysd/actionlint/releases/download/v${ACTIONLINT_VERSION}/actionlint_${ACTIONLINT_VERSION}_linux_amd64.tar.gz"
    echo "${ACTIONLINT_SHA256}  $tmp/actionlint.tar.gz" | sha256sum -c -
    tar -xzf "$tmp/actionlint.tar.gz" -C "$tmp" actionlint
    install -m 0755 "$tmp/actionlint" "$DEST/actionlint"
fi

if need_install gitleaks version "$GITLEAKS_VERSION"; then
    curl -fsSL -o "$tmp/gitleaks.tar.gz" \
        "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz"
    echo "${GITLEAKS_SHA256}  $tmp/gitleaks.tar.gz" | sha256sum -c -
    tar -xzf "$tmp/gitleaks.tar.gz" -C "$tmp" gitleaks
    install -m 0755 "$tmp/gitleaks" "$DEST/gitleaks"
fi

echo "lint tools in $DEST:"
"$DEST/shellcheck" --version
"$DEST/actionlint" -version
"$DEST/gitleaks" version
