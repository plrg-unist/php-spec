#!/usr/bin/env python3
"""Freeze retained BYREF Generator two-owning sources against pinned PHP."""
import config_generator_reference_two_owning_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main(model_timeout=240) else 1)
