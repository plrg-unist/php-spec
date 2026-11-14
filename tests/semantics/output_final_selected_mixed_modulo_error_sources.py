#!/usr/bin/env python3
"""Mixed Warning/Deprecated callbacks return before the FINAL MOD zero Error."""
from pathlib import Path
import function_scope as scope
import output_final_modulo_error_sources as prior

SETUP = (b"declare(strict_types=0); function selected_modulo_mixed($level, $message) { echo 'H'; } "
         b"set_error_handler('selected_modulo_mixed', E_WARNING | E_DEPRECATED);")
VALUES = {'string': (b"'1.5'", b"'0.5'"), 'float': (b'1.5', b'0.5')}
CASES = {}
for order in ['warning-deprecated', 'deprecated-warning']:
    for kind, (first, second) in VALUES.items():
        left, right = (b"'1x'", second) if order == 'warning-deprecated' else (first, b"'0x'")
        for form in ['constant', 'left-cv', 'right-cv', 'cv-pair']:
            assignments = []
            if form in ['left-cv', 'cv-pair']:
                assignments.append(b'$left = ' + left + b';')
            if form in ['right-cv', 'cv-pair']:
                assignments.append(b'$right = ' + right + b';')
            expression = ((b'$left' if form in ['left-cv', 'cv-pair'] else left) + b' % ' +
                          (b'$right' if form in ['right-cv', 'cv-pair'] else right))
            body = b'\n        '.join([*assignments, b'return ' + expression + b';'])
            CASES['native-selected-mixed-modulo-error-' + order + '-' + form + '-' + kind] = prior.MODULO.replace(
                b'declare(strict_types=0);', SETUP).replace(b'return 1 % 0;', body)

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-mixed-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
