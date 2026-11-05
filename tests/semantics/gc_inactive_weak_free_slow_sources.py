#!/usr/bin/env python3
"""The observer-chain original under nonfast executor shutdown."""
from pathlib import Path

import function_scope as scope
import gc_inactive_weak_free_sources as sources


ORIGINALS = {'observer-chain-slow': sources.SOURCE}
ENVIRONMENTS = {'observer-chain-slow': [
    b'LC_ALL=C', b'TZ=UTC', b'FIRST=one', b'USE_ZEND_ALLOC=0']}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(ORIGINALS, 'gc-inactive-weak-free-slow', Path(__file__),
                                    publish=False, model_seconds=240,
                                    request_environments=ENVIRONMENTS) else 1)
