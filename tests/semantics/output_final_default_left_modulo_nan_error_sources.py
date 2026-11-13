#!/usr/bin/env python3
"""NaN conversion notices precede an own quiet zero MOD divisor."""
from pathlib import Path
import function_scope as scope
import output_final_default_left_modulo_range_error_sources as previous

CASES = {}
for form in ['constant', 'left-cv', 'right-cv', 'cv-pair']:
    source = previous.CASES['native-default-left-modulo-range-error-' + form + '-finite']
    assert source.count(b'1e30') == 1
    CASES['native-default-left-modulo-nan-error-' + form] = source.replace(b'1e30', b'NAN')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-left-modulo-nan-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
