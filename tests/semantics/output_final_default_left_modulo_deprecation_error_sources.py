#!/usr/bin/env python3
"""Precision-only left MOD conversion precedes an own quiet zero divisor."""
from pathlib import Path
import function_scope as scope
import output_final_modulo_error_sources as prior

VALUES = {'string': b"'1.5'", 'float': b'1.5'}
CASES = {}
for name, left in VALUES.items():
    for form in ['constant', 'left-cv', 'right-cv', 'cv-pair']:
        assignments = []
        if form in ['left-cv', 'cv-pair']:
            assignments.append(b'$left = ' + left + b';')
        if form in ['right-cv', 'cv-pair']:
            assignments.append(b'$right = 0;')
        expression = ((b'$left' if form in ['left-cv', 'cv-pair'] else left) + b' % ' +
                      (b'$right' if form in ['right-cv', 'cv-pair'] else b'0'))
        body = b'\n        '.join([*assignments, b'return ' + expression + b';'])
        CASES['native-default-left-modulo-deprecation-error-' + form + '-' + name] = prior.MODULO.replace(
            b'return 1 % 0;', body)

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-left-modulo-deprecation-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
