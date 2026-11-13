#!/usr/bin/env python3
"""Original quiet scalar-zero constants follow a leading-number MOD Warning."""
from pathlib import Path
import function_scope as scope
import output_final_default_constant_modulo_warning_error_sources as prior

VALUES = {'null': b'null', 'false': b'false', 'float': b'0.0', 'string': b"'0'"}
CASES = {'native-default-quiet-zero-warning-modulo-' + name:
         prior.WARNING.replace(b"'1x' % 0", b"'1x' % " + value)
         for name, value in VALUES.items()}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-quiet-zero-modulo-warning-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
