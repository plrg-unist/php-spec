#!/usr/bin/env python3
"""Freeze direct temporary reference sends and NULL-handler outcomes."""
import config_generator_temporary_reference_review_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main(model_timeout=240) else 1)
