#!/usr/bin/env python3
"""Freeze owning prefix aborts with retained versus replaced cache ownership."""
import config_generator_owning_value_review_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main(model_timeout=240) else 1)
