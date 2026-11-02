#!/usr/bin/env python3
"""Freeze final owning reference-cell yields against pinned PHP."""
import config_generator_reference_owning_cache_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main(model_timeout=240) else 1)
