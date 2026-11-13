#!/usr/bin/env python3
"""Both own MOD constants retain ordered integer-conversion diagnostics in FINAL."""
from pathlib import Path
import function_scope as scope
import output_final_modulo_error_sources as prior

VALUES = {'warnings': (b"'1x'", b"'0x'"),
          'string-notices': (b"'1.5x'", b"'0.5x'"),
          'float-deprecated': (b'1.5', b'0.5')}
CASES = {'native-default-both-modulo-conversion-error-' + name:
         prior.MODULO.replace(b'return 1 % 0;', b'return ' + left + b' % ' + right + b';')
         for name, (left, right) in VALUES.items()}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-both-modulo-conversion-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
