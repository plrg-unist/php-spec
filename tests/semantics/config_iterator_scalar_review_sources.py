#!/usr/bin/env python3
"""Compare scalar Iterator argument binding and post-cleanup diagnostics."""
import config_iterator_scalar_review_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main(model_timeout=240) else 1)
