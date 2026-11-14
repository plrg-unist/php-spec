#!/usr/bin/env python3
"""Selected MOD handlers echo a literal and explicitly return null or NULL."""
from pathlib import Path
import function_scope as scope
import output_final_selected_both_mask_modulo_error_sources as homogeneous
import output_final_selected_mixed_modulo_error_sources as mixed

CASES = {}
for name, source, handler, literal in [
    ('warning-left-constant',
     homogeneous.CASES['native-selected-both-mask-modulo-error-warning-left-constant'],
     b'selected_modulo_both_mask', b'null'),
    ('deprecated-both-cv-pair',
     homogeneous.CASES['native-selected-both-mask-modulo-error-deprecated-both-cv-pair'],
     b'selected_modulo_both_mask', b'null'),
    ('warning-right-cv-pair',
     homogeneous.CASES['native-selected-both-mask-modulo-error-warning-right-cv-pair'],
     b'selected_modulo_both_mask', b'NULL'),
    ('warning-deprecated-constant-float',
     mixed.CASES['native-selected-mixed-modulo-error-warning-deprecated-constant-float'],
     b'selected_modulo_mixed', b'NULL')]:
    assert source.count(handler) == 2 and source.count(b"{ echo 'H'; }") == 1
    CASES['native-selected-explicit-null-modulo-error-' + name] = source.replace(
        handler, b'selected_modulo_explicit_null').replace(
        b"{ echo 'H'; }", b"{ echo 'H'; return " + literal + b'; }')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-explicit-null-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
