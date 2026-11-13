#!/usr/bin/env python3
"""Selected right or both precision-loss handlers return before FINAL MOD errors."""
from pathlib import Path
import function_scope as scope
import output_final_modulo_error_sources as prior

SETUP = (b"declare(strict_types=0); function selected_modulo_precision($level, $message) { echo 'H'; } "
         b"set_error_handler('selected_modulo_precision', E_DEPRECATED);")
VALUES = {'string': (b"'1.5'", b"'0.5'"), 'float': (b'1.5', b'0.5')}
CASES = {}
for role in ['right', 'both']:
    for kind, (left, right) in VALUES.items():
        for form in ['constant', 'left-cv', 'right-cv', 'cv-pair']:
            first = b'1' if role == 'right' else left
            assignments = []
            if form in ['left-cv', 'cv-pair']:
                assignments.append(b'$left = ' + first + b';')
            if form in ['right-cv', 'cv-pair']:
                assignments.append(b'$right = ' + right + b';')
            expression = ((b'$left' if form in ['left-cv', 'cv-pair'] else first) + b' % ' +
                          (b'$right' if form in ['right-cv', 'cv-pair'] else right))
            body = b'\n        '.join([*assignments, b'return ' + expression + b';'])
            CASES['native-selected-precision-modulo-error-' + role + '-' + form + '-' + kind] = prior.MODULO.replace(
                b'declare(strict_types=0);', SETUP).replace(b'return 1 % 0;', body)

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-precision-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
