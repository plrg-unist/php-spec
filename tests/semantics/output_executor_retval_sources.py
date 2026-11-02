#!/usr/bin/env python3
"""Selected failed-start Notice handlers with an object return value."""
from pathlib import Path

import function_scope as scope

HERE = Path(__file__).resolve().parent
ECHO = (HERE / 'output_executor_retval_echo_ob07.php').read_bytes()
NESTED = (HERE / 'output_executor_post_deactivate_retval.php').read_bytes()
ORIGINALS = {'echo-only': ECHO, 'echo-only-slow': ECHO,
             'nested-start': NESTED, 'nested-start-slow': NESTED}
SLOW = [b'LC_ALL=C', b'TZ=UTC', b'FIRST=one', b'USE_ZEND_ALLOC=0']
ENVIRONMENTS = {'echo-only-slow': SLOW, 'nested-start-slow': SLOW}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(ORIGINALS, 'output-executor-retval',
                                    Path(__file__), publish=False, model_seconds=120,
                                    request_environments=ENVIRONMENTS) else 1)
