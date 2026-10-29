#!/usr/bin/env python3
"""Compare NULL-option callbacks after sole-DATA scalar reference retirement."""
import config_generator_reference_closed_review_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main(model_timeout=240) else 1)
