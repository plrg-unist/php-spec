#!/usr/bin/env python3
"""Null-C FINAL non-Stringable conversion reports before the RV destructor."""
from pathlib import Path
import function_scope as scope

CASES = {
    'stdclass': b"<?php echo 'P';function h($b,$p){return new stdClass;}ob_start('h');echo 'A';",
    'user-dtor': b"<?php echo 'P';class T{function __destruct(){echo 'D';}}function h($b,$p){return new T;}ob_start('h');echo 'A';",
}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
