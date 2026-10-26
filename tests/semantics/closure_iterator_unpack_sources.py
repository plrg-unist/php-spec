#!/usr/bin/env python3
"""Pinned original-source comparisons for Closure targets with Iterator-CV unpack."""
from pathlib import Path
import function_scope as scope


HERE = Path(__file__).resolve().parent
CASES = {
    name: (HERE / ('closure_iterator_unpack_' + name + '.php')).read_bytes()
    for name in ('real_selected', 'real_named', 'named_firstclass',
                 'named_reference', 'invalid_key', 'throwing_key')
}


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'closure-iterator-unpack',
                                     Path(__file__), publish=False) else 1)
