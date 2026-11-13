#!/usr/bin/env python3
"""Selected left and right Warning handlers return before the FINAL MOD Error."""
from pathlib import Path
import function_scope as scope
import output_final_default_unrelated_handler_both_modulo_conversion_error_sources as previous

CASES = {}
for form in ['constant', 'left-cv', 'right-cv', 'cv-pair']:
    source = previous.CASES['native-default-unrelated-handler-both-modulo-conversion-error-' + form + '-leading']
    assert source.count(b'unused_rhs_modulo_handler') == 2
    assert source.count(b'E_DEPRECATED') == 1
    CASES['native-selected-both-warning-modulo-error-' + form] = source.replace(
        b'unused_rhs_modulo_handler', b'selected_both_modulo_handler').replace(b'E_DEPRECATED', b'E_WARNING')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-both-warning-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
