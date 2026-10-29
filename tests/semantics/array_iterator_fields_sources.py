#!/usr/bin/env python3
"""Compare generic Iterator field storage with pinned original-source PHP."""
import array_iterator_fields_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main(model_timeout=240) else 1)
