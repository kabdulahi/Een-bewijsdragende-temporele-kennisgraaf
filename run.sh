#!/usr/bin/env bash
set -euo pipefail
projectmap="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ ! -x "$projectmap/.venv/bin/python" ]]; then
    echo "FOUT: virtuele omgeving ontbreekt. Voer $projectmap/setup.sh uit." >&2
    exit 2
fi
exec "$projectmap/.venv/bin/python" "$projectmap/main.py" "$@"
