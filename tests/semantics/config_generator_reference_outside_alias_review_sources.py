#!/usr/bin/env python3
"""Compare post-DATA alias mutation with copied NULL/scalar INI arguments."""
import config_generator_reference_outside_alias_review_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main(model_timeout=240) else 1)
