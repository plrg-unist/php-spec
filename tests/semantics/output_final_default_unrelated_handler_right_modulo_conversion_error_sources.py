#!/usr/bin/env python3
"""One noisy-zero MOD RHS leaves the opposite numeric handler uncalled."""
from pathlib import Path
import function_scope as scope
import output_final_modulo_error_sources as previous

VALUES = {'leading': (b"'0x'", b'E_DEPRECATED'),
          'string': (b"'0.5'", b'E_WARNING'),
          'float': (b'0.5', b'E_WARNING'),
          'finite': (b'18446744073709551616.0', b'E_DEPRECATED'),
          'infinite': (b'1e999', b'E_DEPRECATED')}
CASES = {}
for kind, (right, levels) in VALUES.items():
    setup = (b"declare(strict_types=0); function unused_rhs_modulo_handler($level, $message) { echo 'H'; } "
             b"set_error_handler('unused_rhs_modulo_handler', " + levels + b');')
    for form in ['constant', 'left-cv', 'right-cv', 'cv-pair']:
        assignments = []
        if form in ['left-cv', 'cv-pair']:
            assignments.append(b'$left = 1;')
        if form in ['right-cv', 'cv-pair']:
            assignments.append(b'$right = ' + right + b';')
        expression = ((b'$left' if form in ['left-cv', 'cv-pair'] else b'1') + b' % ' +
                      (b'$right' if form in ['right-cv', 'cv-pair'] else right))
        body = b'\n        '.join([*assignments, b'return ' + expression + b';'])
        CASES['native-default-unrelated-handler-right-modulo-conversion-error-' + form + '-' + kind] = previous.MODULO.replace(
            b'return 1 % 0;', body).replace(b'declare(strict_types=0);', setup)

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-unrelated-handler-right-modulo-conversion-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
