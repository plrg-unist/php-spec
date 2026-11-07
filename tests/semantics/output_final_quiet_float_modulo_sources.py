#!/usr/bin/env python3
"""FINAL conversion retains quiet exact float modulo-by-zero errors."""
from pathlib import Path
import function_scope as scope
import output_final_modulo_error_sources as prior

LEFT_FLOAT = prior.MODULO.replace(b'1 % 0', b'1.0 % 0')
RIGHT_FLOAT = prior.MODULO.replace(b'1 % 0', b'1 % 0.0')
BOTH_FLOAT = prior.MODULO.replace(b'1 % 0', b'1.0 % 0.0')
NORMAL = prior.MODULO.replace(b'1 % 0', b'1.0 % 1.0')
LOSSY = prior.MODULO.replace(b'1 % 0', b'1.5 % 0')
CASES = {'native-left-float-modulo-zero': LEFT_FLOAT,
         'native-right-float-modulo-zero': RIGHT_FLOAT,
         'native-both-float-modulo-zero': BOTH_FLOAT,
         'native-both-float-modulo-normal': NORMAL}
CATCH = BOTH_FLOAT.replace(b'        return 1.0 % 0.0;',
                           b"        try { return 1.0 % 0.0; } catch (DivisionByZeroError) { return 'H'; }")
OVERRIDE = BOTH_FLOAT.replace(b'        return 1.0 % 0.0;',
                              b"        try { return 1.0 % 0.0; } finally { return 'H'; }")

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-quiet-float-modulo', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
