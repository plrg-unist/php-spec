#!/usr/bin/env python3
"""Compound internal-Key cleanup through nonfast table retirement."""
from pathlib import Path

import function_scope as scope
import gc_compound_key_sources as sources


ORIGINALS = {'compound-key-cross-slow': sources.family.CASES['map-key-cross-shared']}
ENVIRONMENTS = {'compound-key-cross-slow': [
    b'LC_ALL=C', b'TZ=UTC', b'FIRST=one', b'USE_ZEND_ALLOC=0']}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(ORIGINALS, 'gc-compound-key-slow', Path(__file__),
                                    publish=False, model_seconds=240,
                                    request_environments=ENVIRONMENTS) else 1)
