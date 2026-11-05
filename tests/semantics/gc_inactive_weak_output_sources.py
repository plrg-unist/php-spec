#!/usr/bin/env python3
"""Unchanged output-creation originals through inactive weak observer cleanup."""
from pathlib import Path
import hashlib

import function_scope as scope
import output_executor_creation_review_sources as output


HASHES = {
    'cycle-handler-gc': '6220b1e678bf359cffa3534706a4b8365cc49938c0cf24e2dfd6c748277d1e6d',
    'cycle-without-handler-gc': 'ee8d99dd44cd67c7d8a4fd6db38627b6749d81ce25130077409fdfab683cbe4c',
    'cycle-array-handler-gc': 'efc2ed31fefbed55636fc46b1562f30541b64ff07d66d8bea6d2f195b307eb8d',
}
ORIGINALS = {name: output.LATE_STORAGE_CONTROLS[name] for name in HASHES}
for name, source in ORIGINALS.items():
    assert hashlib.sha256(source).hexdigest() == HASHES[name]

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(ORIGINALS, 'gc-inactive-weak-output', Path(__file__),
                                    publish=False, model_seconds=240) else 1)
