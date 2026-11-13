#!/usr/bin/env python3
"""Original fractional MOD prefixes retain Warning and precision-loss diagnostics."""
from pathlib import Path
import function_scope as scope
import output_final_default_constant_modulo_warning_error_sources as prior

VALUES = {'positive': b"'1.5x'", 'negative': b"'-1.5x'"}
CASES = {'native-default-fractional-warning-modulo-' + name:
         prior.WARNING.replace(b"'1x'", value) for name, value in VALUES.items()}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-fractional-modulo-warning-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
