#!/usr/bin/env python3
"""Freeze factory returned BYREF Generator ARRAY aliases against pinned PHP."""
import config_generator_factory_owning_alias_review_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main(model_timeout=240) else 1)
