#!/usr/bin/env python3
"""Original owning ARRAY-CV observations at undefined literal keys."""
import array_literal_undefined_key_array_cv_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
