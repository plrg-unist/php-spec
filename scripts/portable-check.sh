#!/usr/bin/env bash
# Linux audit: fresh sources, no Git metadata, hidden workspace/cache, no network.
set -euo pipefail
project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
audit_dir=$(mktemp -d /var/tmp/php-spec-portable.XXXXXX)
tar -C "$project_dir" --exclude='./.git' --exclude='./.tools' \
  --exclude='./_build' --exclude='./build' -cf - . | tar -C "$audit_dir" -xf -
printf 'Portable checkout: %s\n' "$audit_dir"
sudo unshare --mount --net /bin/bash -s -- "$audit_dir" <<'AUDIT'
set -euo pipefail
mount --make-rprivate /
mount -t tmpfs tmpfs /home
mount -t tmpfs tmpfs /tmp
cd "$1"
exec env -i PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
  OPAMROOTISOK=1 bash -c '
    set -euo pipefail
    test ! -e .git
    python3 scripts/verify-inputs.py
    scripts/build-deps.sh
    make build
    make test
    make validate
    make inventory
    python3 scripts/verify-inputs.py
  '
AUDIT
printf 'Portable audit passed: %s\n' "$audit_dir"
