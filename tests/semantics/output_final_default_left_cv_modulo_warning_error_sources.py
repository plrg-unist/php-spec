#!/usr/bin/env python3
"""Leading MOD left CVs retain their own initialized value before constant zero."""
from pathlib import Path
import function_scope as scope
import output_final_default_constant_modulo_warning_error_sources as prior

VALUES = {'integer-prefix': b"'1x'", 'float-prefix': b"'1.0x'"}
CASES = {'native-default-left-cv-warning-modulo-' + name:
         prior.WARNING.replace(b"        return '1x' % 0;", b'        $b = ' + value +
             b';\n        $c = ' + value + b';\n        return $b % 0;')
         for name, value in VALUES.items()}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-left-cv-modulo-warning-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
