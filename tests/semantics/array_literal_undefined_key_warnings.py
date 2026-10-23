#!/usr/bin/env python3
"""Original undefined ARRAY-key Warning observations."""
import array_literal_undefined_key_warning_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
