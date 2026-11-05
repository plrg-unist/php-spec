#!/usr/bin/env python3
"""Normal Warning-handler retval destructor starts a nested failed buffer."""
from pathlib import Path

import function_scope as scope
from output_executor_invalid_sources import ORIGINALS as INVALID

BASE = INVALID['warning-return-object']
OLD_CLASS = b'class WarningReturnOB11 { function __destruct() { echo "R|"; } }'
NEW_CLASS = b'class WarningReturnOB14 { function __destruct() { echo "R1|"; echo ob_start() ? "RT|" : "RF|"; echo "R2|"; } }'
OLD_RETURN = b'return new WarningReturnOB11;'
NEW_RETURN = b'if ($level === 2) { return new WarningReturnOB14; } return true;'
assert BASE.count(OLD_CLASS) == 1 and BASE.count(OLD_RETURN) == 1
ORIGINALS = {'warning-return-nested-start': BASE.replace(OLD_CLASS, NEW_CLASS).replace(OLD_RETURN, NEW_RETURN)}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(ORIGINALS, 'output-executor-warning-retval-nested',
                                    Path(__file__), publish=False, model_seconds=180) else 1)
