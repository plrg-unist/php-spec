#!/usr/bin/env python3
"""Request-shutdown FINAL throws, fatal rendering and inactive buffer release."""
from pathlib import Path
import function_scope as scope

HERE = Path(__file__).resolve().parent
ORIGINALS = {
    'retired-global-error': (HERE / 'output_request_end_held_throw.php').read_bytes(),
    'captured-supplied': (HERE / 'output_request_end_peer_captured_throw.php').read_bytes(),
    'fresh-inside-final': (HERE / 'output_final_throw_fresh.php').read_bytes(),
    'late-cache-deactivate': (HERE / 'output_final_throw_late_capture.php').read_bytes(),
}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(ORIGINALS, 'output-final-throw', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
