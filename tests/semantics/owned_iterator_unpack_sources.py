#!/usr/bin/env python3
"""Owned non-CV Iterator INPUT across already-supported ordinary call targets."""
from pathlib import Path
import function_scope as scope


HERE = Path(__file__).resolve().parent
CASES = {
    name: (HERE / ('owned_iterator_unpack_' + name + '.php')).read_bytes()
    for name in ('method_invalid', 'method_throw', 'array_instance', 'array_static',
                 'arrow_value', 'closure_invalid', 'named_warning', 'invokable_reference')
}
CASES['promoted-method-temporary'] = (HERE / 'method_iterator_unpack_temporary_control.php').read_bytes()


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'owned-iterator-unpack',
                                     Path(__file__), publish=False) else 1)
