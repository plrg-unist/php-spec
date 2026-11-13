#!/usr/bin/env python3
"""Own leading-number MOD left and quiet-zero right CVs preserve their reads."""
from pathlib import Path
import function_scope as scope
import output_final_default_constant_modulo_warning_error_sources as prior

VALUES = {'integer-zero': (b"'1x'", b'0'), 'string-zero': (b"'1.0x'", b"'0'")}
CASES = {'native-default-cv-pair-warning-modulo-' + name:
         prior.WARNING.replace(b"        return '1x' % 0;", b'        $b = ' + left +
             b';\n        $c = ' + right + b';\n        return $b % $c;')
         for name, (left, right) in VALUES.items()}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-cv-pair-modulo-warning-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
