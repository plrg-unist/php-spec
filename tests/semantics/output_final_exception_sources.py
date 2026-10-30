#!/usr/bin/env python3
"""Native-first selected exception handlers during request-end FINAL calls."""
from pathlib import Path
import function_scope as scope

HERE = Path(__file__).resolve().parent
ORIGINALS = {
    name: (HERE / ('output_final_exception_' + name + '.php')).read_bytes()
    for name in ('false', 'result', 'throw', 'result_throw', 'peer', 'lower_peer', 'warning_peer', 'owner_peer', 'callback_owner_peer', 'original_throw_peer', 'normal_late_peer')
}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(ORIGINALS, 'output-final-exception-handler', Path(__file__),
                                    publish=False, model_seconds=120) else 1)
