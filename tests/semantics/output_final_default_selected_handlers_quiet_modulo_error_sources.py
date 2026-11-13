#!/usr/bin/env python3
"""Quiet MOD operands leave a handler for both numeric notice classes uncalled."""
from pathlib import Path
import function_scope as scope
import output_final_modulo_error_sources as previous

SETUP = (b"declare(strict_types=0); function unused_quiet_modulo_handler($level, $message) { echo 'H'; } "
         b"set_error_handler('unused_quiet_modulo_handler', E_WARNING | E_DEPRECATED);")
CASES = {}
for form in ['constant', 'left-cv', 'right-cv', 'cv-pair']:
    assignments = []
    if form in ['left-cv', 'cv-pair']:
        assignments.append(b'$left = 1;')
    if form in ['right-cv', 'cv-pair']:
        assignments.append(b'$right = 0;')
    expression = ((b'$left' if form in ['left-cv', 'cv-pair'] else b'1') + b' % ' +
                  (b'$right' if form in ['right-cv', 'cv-pair'] else b'0'))
    body = b'\n        '.join([*assignments, b'return ' + expression + b';'])
    CASES['native-default-selected-handlers-quiet-modulo-error-' + form] = previous.MODULO.replace(
        b'return 1 % 0;', body).replace(b'declare(strict_types=0);', SETUP)
CASES['native-default-selected-handlers-quiet-modulo-error-same-cv'] = previous.MODULO.replace(
    b'return 1 % 0;', b'$value = 0;\n        return $value % $value;').replace(
    b'declare(strict_types=0);', SETUP)

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-selected-handlers-quiet-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
