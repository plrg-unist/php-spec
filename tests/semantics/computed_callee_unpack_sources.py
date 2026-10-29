#!/usr/bin/env python3
"""Computed __invoke Iterator calls and shared dynamic-callee controls."""
from pathlib import Path
import function_scope as scope


HERE = Path(__file__).resolve().parent
CASES = {
    name: (HERE / ('computed_callee_unpack_' + name + '.php')).read_bytes()
    for name in ('direct', 'named', 'conditional', 'invalid', 'throwing',
                 'closure_control', 'array_control', 'early_throw_control', 'noncallable_control')
}
CASES['promoted-returned-callee'] = (HERE / 'invokable_iterator_unpack_temporary_boundary.php').read_bytes()


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'computed-callee-unpack',
                                     Path(__file__), publish=False) else 1)
