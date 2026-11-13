#!/usr/bin/env python3
"""Float range conversion warns before an own quiet zero MOD divisor."""
from pathlib import Path
import function_scope as scope
import output_final_default_left_modulo_deprecation_error_sources as previous

VALUES = {'finite': b'1e30', 'infinite': b'1e999'}
CASES = {}
for name, left in VALUES.items():
    for form in ['constant', 'left-cv', 'right-cv', 'cv-pair']:
        source = previous.CASES['native-default-left-modulo-deprecation-error-' + form + '-float']
        assert source.count(b'1.5') == 1
        CASES['native-default-left-modulo-range-error-' + form + '-' + name] = source.replace(b'1.5', left)

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-left-modulo-range-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
