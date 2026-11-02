#!/usr/bin/env python3
"""No-argument ob_start after real output deactivation and an early control."""
from pathlib import Path

import function_scope as scope

HERE = Path(__file__).resolve().parent
STEMS = ('plain', 'suppressed', 'handler', 'early')
ORIGINALS = {
    name: (HERE / ('output_executor_post_deactivate_' + name + '.php')).read_bytes()
    for name in STEMS
}
ORIGINALS['plain-slow'] = ORIGINALS['plain']
ENVIRONMENTS = {'plain-slow': [b'LC_ALL=C', b'TZ=UTC', b'FIRST=one', b'USE_ZEND_ALLOC=0']}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(ORIGINALS, 'output-executor-post-deactivate',
                                    Path(__file__), publish=False, model_seconds=120,
                                    request_environments=ENVIRONMENTS) else 1)
