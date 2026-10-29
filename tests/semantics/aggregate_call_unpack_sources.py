#!/usr/bin/env python3
"""Target-neutral Aggregate acquisition, send routing and owner lifetimes."""
from pathlib import Path
import function_scope as scope


HERE = Path(__file__).resolve().parent
CASES = {
    name: (HERE / ('aggregate_call_unpack_' + name + '.php')).read_bytes()
    for name in ('ordinary_byref', 'magic_static', 'reference_closure',
                 'nested_generator', 'self_reject', 'self_rebound',
                 'getter_throw', 'closed_generator', 'empty', 'mixed_duplicate')
}


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'aggregate-call-unpack', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
