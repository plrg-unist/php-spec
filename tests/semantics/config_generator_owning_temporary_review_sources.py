#!/usr/bin/env python3
"""Freeze temporary INPUT/DATA cleanup before array TraceArgs or saved catch."""
import config_generator_owning_temporary_review_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main(model_timeout=240) else 1)
