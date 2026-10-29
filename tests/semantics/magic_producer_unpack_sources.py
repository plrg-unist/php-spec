#!/usr/bin/env python3
"""Array/Generator magic sends, shared key routing and producer lifetimes."""
from pathlib import Path
import function_scope as scope


HERE = Path(__file__).resolve().parent
CASES = {
    name: (HERE / ('magic_producer_unpack_' + name + '.php')).read_bytes()
    for name in ('array_copy_named', 'array_reference_input', 'array_mixed_static',
                 'array_duplicate', 'array_after_named', 'generator_copy_named',
                 'mixed_static', 'generator_invalid_temporary',
                 'generator_invalid_retained', 'generator_handler_throw',
                 'generator_body_throw', 'empty')
}


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'magic-producer-unpack',
                                     Path(__file__), publish=False, model_seconds=90) else 1)
