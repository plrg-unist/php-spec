#!/usr/bin/env python3
"""Pinned PHP/source comparisons for CV Iterator unpack into array callables."""
from pathlib import Path
import function_scope as scope


HERE = Path(__file__).resolve().parent
CASES = {
    name: (HERE / ('array_callable_iterator_' + name + '.php')).read_bytes()
    for name in ('object_selection', 'static_named', 'static_reference',
                 'invalid_key', 'key_throw', 'independent')
}


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'array-callable-iterator-unpack',
                                     Path(__file__), publish=False) else 1)
