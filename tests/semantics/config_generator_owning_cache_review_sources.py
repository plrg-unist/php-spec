#!/usr/bin/env python3
"""Freeze final cached-array release before TypeError or a supplied throw."""
import config_generator_owning_cache_review_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main(model_timeout=240) else 1)
