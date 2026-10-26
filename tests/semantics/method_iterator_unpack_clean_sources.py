#!/usr/bin/env python3
"""Exact source comparison for destructor-bearing method warning cleanup."""
from pathlib import Path
import hashlib
import function_scope as scope


SOURCE = Path(__file__).with_name('method_iterator_unpack_clean.php')
CASES = {'handler-result-cleanup': SOURCE.read_bytes()}
SOURCE_SHA = '8f903655c33a912df749c1843e384c1d1432d816c05020c73b2dfdcf3cfedc5b'


if __name__ == '__main__':
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA
    passed = scope.main(CASES, 'method-iterator-unpack-clean', Path(__file__), publish=False)
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA
    raise SystemExit(0 if passed else 1)
