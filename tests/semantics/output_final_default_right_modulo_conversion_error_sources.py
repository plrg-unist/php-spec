#!/usr/bin/env python3
"""Own noisy-zero MOD right constants convert after a quiet left constant."""
from pathlib import Path
import function_scope as scope
import output_final_modulo_error_sources as prior

VALUES = {'warning': b"'0x'", 'deprecated': b"'0.5'", 'both': b"'0.5x'", 'float-deprecated': b'0.5'}
CASES = {'native-default-right-modulo-conversion-error-' + name:
         prior.MODULO.replace(b'return 1 % 0;', b'return 1 % ' + value + b';')
         for name, value in VALUES.items()}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-right-modulo-conversion-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
