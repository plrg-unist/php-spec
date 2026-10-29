#!/usr/bin/env python3
"""FINAL fatal reporting, local Throwable release and raw output-handler retirement."""
from pathlib import Path
import function_scope as scope

HERE = Path(__file__).resolve().parent
ORIGINALS = {
    name: (HERE / ('output_pending_release_' + name + '.php')).read_bytes()
    for name in ('sole', 'retained', 'throw', 'peer')
}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(ORIGINALS, 'output-pending-release', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
