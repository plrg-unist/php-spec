#!/usr/bin/env python3
"""Positional null starts after output deactivation in pinned PHP and the model."""
from pathlib import Path

import function_scope as scope

HERE = Path(__file__).resolve().parent
EXPLICIT = (HERE / 'output_executor_post_deactivate_explicit.php').read_bytes()
ORIGINALS = {
    'explicit-null': EXPLICIT,
    'explicit-null-slow': EXPLICIT,
    'handled-null': (HERE / 'output_executor_post_deactivate_handled_ob08.php').read_bytes(),
}
ENVIRONMENTS = {'explicit-null-slow': [b'LC_ALL=C', b'TZ=UTC', b'FIRST=one', b'USE_ZEND_ALLOC=0']}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(ORIGINALS, 'output-executor-explicit-null',
                                    Path(__file__), publish=False, model_seconds=120,
                                    request_environments=ENVIRONMENTS) else 1)
