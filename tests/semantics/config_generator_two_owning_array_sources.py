#!/usr/bin/env python3
"""Compare the two-array COW snapshot regression with pinned PHP."""
import config_generator_two_owning_array_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main(model_timeout=240) else 1)
