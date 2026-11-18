#!/usr/bin/env python3
"""Compare scoped-self multi-builtin short-reference Get originals."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('self_builtin_union_parentless_short_reference_get_hook')
original = sources.recorded


def recorded(command, target, cap):
    if (command[0] == str(sources.ROOT / 'bin/php-semantics')
            and Path(command[1]).stem == 'weak-relative-self-seven'):
        assert command[-2:] == ['--timeout', '120'] and cap == 140
        return original([*command[:-1], '300'], target, 320)
    return original(command, target, cap)


sources.recorded = recorded

if __name__ == '__main__':
    sources.main()
