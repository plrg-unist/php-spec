#!/usr/bin/env python3
"""FLOAT range Warnings leave an unrelated Deprecated handler uncalled."""
from pathlib import Path
import function_scope as scope
import output_final_default_left_modulo_range_error_sources as previous
from output_final_default_unrelated_handler_modulo_error_sources import SETUP

CASES = {name.replace('native-default-left-modulo-range-error-',
                      'native-default-unrelated-handler-left-modulo-range-error-'):
         source.replace(b'declare(strict_types=0);', SETUP)
         for name, source in previous.CASES.items()}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-unrelated-handler-left-modulo-range-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
