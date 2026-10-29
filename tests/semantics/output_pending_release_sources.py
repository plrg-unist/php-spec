#!/usr/bin/env python3
"""Native-first pending-Throwable ownership originals; model work not started."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORIGINALS = {
    name: (HERE / ('output_pending_release_' + name + '.php')).read_bytes()
    for name in ('sole', 'retained', 'throw', 'peer')
}
