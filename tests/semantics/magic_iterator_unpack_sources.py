#!/usr/bin/env python3
"""Original-source magic trampoline Iterator unpack and prior call controls."""
from pathlib import Path
import function_scope as scope


HERE = Path(__file__).resolve().parent
CASES = {
    name: (HERE / ('magic_iterator_unpack_' + name + '.php')).read_bytes()
    for name in ('copy_named', 'prefix_reference', 'static_cross', 'empty',
                 'invalid', 'after_named', 'throwing', 'scoped', 'handler_throw')
}
CASES['instance-positional-control'] = (HERE / 'magic-call-snapshot.php').read_bytes()
CASES['static-positional-control'] = (HERE / 'magic-static-call-snapshot.php').read_bytes()


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'magic-iterator-unpack',
                                     Path(__file__), publish=False, model_seconds=90) else 1)
