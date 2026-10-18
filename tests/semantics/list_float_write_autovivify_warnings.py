#!/usr/bin/env python3
"""Native-first finite originals for writable-source initialization."""
import incdec_warnings as runner
import list_float_write_autovivify_cases as cases

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
