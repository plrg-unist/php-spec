#!/usr/bin/env python3
"""Map/ALIAS/empty-Map retirement through nonfast executor table release."""
from pathlib import Path

import function_scope as scope
import gc_inactive_weakmap_free_sources as sources


ORIGINALS = {'map-alias-empty-slow': sources.family.CASES['map-alias-empty']}
ENVIRONMENTS = {'map-alias-empty-slow': [
    b'LC_ALL=C', b'TZ=UTC', b'FIRST=one', b'USE_ZEND_ALLOC=0']}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(ORIGINALS, 'gc-inactive-weakmap-free-slow', Path(__file__),
                                    publish=False, model_seconds=240,
                                    request_environments=ENVIRONMENTS) else 1)
