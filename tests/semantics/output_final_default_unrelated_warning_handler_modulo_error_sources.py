#!/usr/bin/env python3
"""A sole MOD Deprecated notice leaves an unrelated Warning handler uncalled."""
from pathlib import Path
import function_scope as scope
import output_final_default_left_modulo_deprecation_error_sources as previous

SETUP = (b"declare(strict_types=0); function unused_modulo_warning($level, $message) { echo 'H'; } "
         b"set_error_handler('unused_modulo_warning', E_WARNING);")
CASES = {}
for kind in ['string', 'float']:
    for form in ['constant', 'left-cv', 'right-cv', 'cv-pair']:
        name = form + '-' + kind
        source = previous.CASES['native-default-left-modulo-deprecation-error-' + name]
        CASES['native-default-unrelated-warning-handler-modulo-error-' + name] = source.replace(
            b'declare(strict_types=0);', SETUP)

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-unrelated-warning-handler-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
