#!/usr/bin/env python3
"""Referenced Map values retire during nonfast table-triggered Key notification."""
from pathlib import Path

import function_scope as scope
import gc_key_notify_sources as sources


ORIGINALS = {'key-notify-alias-slow': sources.family.CASES['shared-reference-value']}
ENVIRONMENTS = {'key-notify-alias-slow': [
    b'LC_ALL=C', b'TZ=UTC', b'FIRST=one', b'USE_ZEND_ALLOC=0']}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(ORIGINALS, 'gc-key-notify-slow', Path(__file__),
                                    publish=False, model_seconds=240,
                                    request_environments=ENVIRONMENTS) else 1)
