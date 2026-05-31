#!/usr/bin/env bash
set -euo pipefail

env_file="${1:-.env}"

usage() {
  cat <<'EOF'
Usage: scripts/env-to-base64-secret.sh [env-file]

Prints an env file as a single-line base64 value suitable for the
ENV_FILE_B64 GitHub Actions secret.

Examples:
  scripts/env-to-base64-secret.sh
  scripts/env-to-base64-secret.sh .env.example

Decode check:
  scripts/env-to-base64-secret.sh .env | base64 -d
EOF
}

if [[ "${env_file}" == "-h" || "${env_file}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ ! -f "${env_file}" ]]; then
  echo "error: env file not found: ${env_file}" >&2
  exit 1
fi

if [[ ! -s "${env_file}" ]]; then
  echo "error: env file is empty: ${env_file}" >&2
  exit 1
fi

if base64 --help 2>&1 | grep -q -- '-w'; then
  base64 -w 0 "${env_file}"
elif base64 --help 2>&1 | grep -q -- '-b'; then
  base64 -b 0 "${env_file}"
else
  base64 "${env_file}" | tr -d '\n'
fi

printf '\n'
