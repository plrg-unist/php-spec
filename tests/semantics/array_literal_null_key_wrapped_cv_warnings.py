#!/usr/bin/env python3
"""Original-source observations for NULL-key captured reference payloads."""
import array_literal_null_key_wrapped_cv_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
