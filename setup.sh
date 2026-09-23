#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if ! command -v uv >/dev/null 2>&1; then
    echo 'FOUT: uv ontbreekt. Installeer uv en voer dit script opnieuw uit.' >&2
    exit 2
fi
uv sync --locked
echo 'Gereed. Gebruik ./run.sh --help'
