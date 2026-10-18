#!/usr/bin/env python3
"""Compare mixed ordinary-CV key-conversion originals with the pinned engine."""
import array_literal_float_mixed_cv_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
