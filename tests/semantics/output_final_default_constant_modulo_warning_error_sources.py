#!/usr/bin/env python3
"""Leading-number CONST strings warn before native FINAL modulo-by-zero errors."""
from pathlib import Path
import function_scope as scope
import output_final_modulo_error_sources as prior

WARNING = prior.MODULO.replace(b'return 1 % 0;', b"return '1x' % 0;")
CASES = {'native-default-constant-warning-modulo-integer-string': WARNING,
         'native-default-constant-warning-modulo-float-string': WARNING.replace(b"'1x'", b"'1.0x'")}
NONZERO = WARNING.replace(b"'1x' % 0", b"'1x' % 1")
NOISY = WARNING.replace(b"'1x'", b"'1.5x'")

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-constant-modulo-warning-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
