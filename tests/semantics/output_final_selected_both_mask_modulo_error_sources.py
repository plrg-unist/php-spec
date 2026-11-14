#!/usr/bin/env python3
"""Homogeneous MOD notices use a handler registered for both numeric classes."""
from pathlib import Path
import function_scope as scope
import output_final_modulo_error_sources as prior

SETUP = (b"declare(strict_types=0); function selected_modulo_both_mask($level, $message) { echo 'H'; } "
         b"set_error_handler('selected_modulo_both_mask', E_WARNING | E_DEPRECATED);")
CASES = {}
for level in ['warning', 'deprecated']:
    for role in ['left', 'right', 'both']:
        for form in ['constant', 'cv-pair']:
            left, right = ((b"'1x'", b"'0x'") if level == 'warning' else
                           (b'1.5', b'0.5') if form == 'constant' else (b"'1.5'", b"'0.5'"))
            if role == 'right':
                left = b'1'
            if role == 'left':
                right = b'0'
            assignments = [b'$left = ' + left + b';', b'$right = ' + right + b';'] if form == 'cv-pair' else []
            expression = b'$left % $right' if form == 'cv-pair' else left + b' % ' + right
            body = b'\n        '.join([*assignments, b'return ' + expression + b';'])
            CASES['native-selected-both-mask-modulo-error-' + level + '-' + role + '-' + form] = prior.MODULO.replace(
                b'declare(strict_types=0);', SETUP).replace(b'return 1 % 0;', body)

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-both-mask-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
