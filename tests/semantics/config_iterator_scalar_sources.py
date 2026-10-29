#!/usr/bin/env python3
"""Compare raw scalar CONFIG Iterator sends with the pinned PHP oracle."""
import config_iterator_scalar_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main(model_timeout=240) else 1)
