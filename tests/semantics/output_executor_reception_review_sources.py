#!/usr/bin/env python3
"""Independent original-source ordering and returned-handler cleanup checks."""
from pathlib import Path

import function_scope as scope
from output_executor_reception_review_state import BASE, HANDLED

RETVAL = BASE.replace('<?php\n', '''<?php
class RetvalOB09 {
    public function __destruct() {
        echo "R1|";
        echo ob_start(...["chunk_size" => -1, "callback" => null, "flags" => 0]) ? "RT|" : "RF|";
        echo "R2|";
    }
}
set_error_handler(static function ($level, $message) { echo "H:", $level, "|"; return new RetvalOB09; });
''').replace('ob_start(...["flags" => -1, "chunk_size" => true])',
            'ob_start(callback: null)')
ORIGINALS = {
    'omitted-callback-unpack': BASE.encode(),
    'selected-deprecations-notice': HANDLED.encode(),
    'retval-arguments': RETVAL.encode(),
    'retval-arguments-slow': RETVAL.encode(),
}
ENVIRONMENTS = {
    'retval-arguments-slow': [b'LC_ALL=C', b'TZ=UTC', b'FIRST=one', b'USE_ZEND_ALLOC=0'],
}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(ORIGINALS, 'output-executor-reception-review',
                                    Path(__file__), publish=False, model_seconds=120,
                                    request_environments=ENVIRONMENTS) else 1)
