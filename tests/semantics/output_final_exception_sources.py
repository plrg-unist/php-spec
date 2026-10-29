#!/usr/bin/env python3
"""Native-first selected exception handlers during request-end FINAL calls."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORIGINALS = {
    name: (HERE / ('output_final_exception_' + name + '.php')).read_bytes()
    for name in ('false', 'result', 'throw', 'result_throw', 'peer', 'lower_peer', 'warning_peer')
}
