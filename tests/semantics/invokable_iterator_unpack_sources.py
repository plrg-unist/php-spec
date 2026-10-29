#!/usr/bin/env python3
"""Pinned original-source comparisons for dynamic invokable Iterator-CV unpack."""
from pathlib import Path
import function_scope as scope


HERE = Path(__file__).resolve().parent
CASES = {
    name: (HERE / ('invokable_iterator_unpack_' + name + '.php')).read_bytes()
    for name in ('selected', 'named', 'reference', 'invalid_key', 'throwing_key')
}


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'invokable-iterator-unpack',
                                     Path(__file__), publish=False) else 1)
