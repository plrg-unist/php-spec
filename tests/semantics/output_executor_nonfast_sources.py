#!/usr/bin/env python3
"""Original request contexts for post-output queue and allocator-mode cleanup."""
from pathlib import Path

import function_scope as scope

HERE = Path(__file__).resolve().parent
STEMS = {
    'child-first': 'child_first', 'holder-first': 'holder_first',
    'global-order': 'global_order_peer', 'function-static': 'function_static_peer',
    'stack-order': 'stack_order_peer', 'shutdown-capture-slow': 'shutdown_capture_peer',
    'shutdown-throw': 'shutdown_throw', 'bound-fcc': 'bound_fcc',
    'inherited-static': 'inherited_static_peer', 'bound-fake': 'bound_fake_peer',
}
ORIGINALS = {name: (HERE / ('output_executor_nonfast_' + stem + '.php')).read_bytes()
             for name, stem in STEMS.items()}
ORIGINALS['shutdown-capture-fast'] = ORIGINALS['shutdown-capture-slow']
ORIGINALS['callback-owner-slow'] = (HERE / 'output_final_exception_callback_owner_peer.php').read_bytes()
ENVIRONMENTS = {name: [b'LC_ALL=C', b'TZ=UTC', b'FIRST=one', b'USE_ZEND_ALLOC=0']
                for name in ORIGINALS if name != 'shutdown-capture-fast'}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(ORIGINALS, 'output-executor-nonfast', Path(__file__),
                                    publish=False, model_seconds=120,
                                    request_environments=ENVIRONMENTS) else 1)
