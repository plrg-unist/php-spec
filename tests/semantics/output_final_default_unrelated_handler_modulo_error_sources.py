#!/usr/bin/env python3
"""A sole MOD Warning leaves an unrelated Deprecated handler uncalled."""
from pathlib import Path
import function_scope as scope
import output_final_default_left_modulo_nan_error_sources as previous

SETUP = (b"declare(strict_types=0); function unused_modulo_deprecated($level, $message) { echo 'H'; } "
         b"set_error_handler('unused_modulo_deprecated', E_DEPRECATED);")
CASES = {}
for form in ['constant', 'left-cv', 'right-cv', 'cv-pair']:
    source = previous.CASES['native-default-left-modulo-nan-error-' + form]
    assert source.count(b'NAN') == 1
    CASES['native-default-unrelated-handler-modulo-error-' + form] = source.replace(
        b'NAN', b"'1x'").replace(b'declare(strict_types=0);', SETUP)

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-unrelated-handler-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
