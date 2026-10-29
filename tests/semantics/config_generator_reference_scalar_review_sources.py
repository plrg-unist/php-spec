#!/usr/bin/env python3
"""Compare native and model CONFIG sends from live Generator reference cells."""
import config_generator_reference_scalar_review_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main(model_timeout=240) else 1)
