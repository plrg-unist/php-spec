#!/usr/bin/env python3
"""A selected left precision-loss handler returns before the FINAL MOD Error."""
from pathlib import Path
import function_scope as scope
import output_final_default_unrelated_warning_handler_modulo_error_sources as previous

CASES = {}
for kind in ['string', 'float']:
    for form in ['constant', 'left-cv', 'right-cv', 'cv-pair']:
        name = form + '-' + kind
        source = previous.CASES['native-default-unrelated-warning-handler-modulo-error-' + name]
        assert source.count(b'unused_modulo_warning') == 2
        assert source.count(b'E_WARNING') == 1
        CASES['native-selected-left-deprecated-modulo-error-' + name] = source.replace(
            b'unused_modulo_warning', b'selected_lhs_modulo_deprecated').replace(b'E_WARNING', b'E_DEPRECATED')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-left-deprecated-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
