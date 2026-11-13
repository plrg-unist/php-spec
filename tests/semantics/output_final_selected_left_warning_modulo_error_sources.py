#!/usr/bin/env python3
"""A selected left Warning handler returns before the FINAL MOD zero Error."""
from pathlib import Path
import function_scope as scope
import output_final_default_unrelated_handler_modulo_error_sources as previous

CASES = {}
for form in ['constant', 'left-cv', 'right-cv', 'cv-pair']:
    source = previous.CASES['native-default-unrelated-handler-modulo-error-' + form]
    assert source.count(b'unused_modulo_deprecated') == 2
    assert source.count(b'E_DEPRECATED') == 1
    CASES['native-selected-left-warning-modulo-error-' + form] = source.replace(
        b'unused_modulo_deprecated', b'selected_lhs_modulo_handler').replace(b'E_DEPRECATED', b'E_WARNING')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-left-warning-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
