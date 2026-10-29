#!/usr/bin/env python3
"""Compare owning CONFIG Iterator argument originals with pinned PHP."""
import config_iterator_argument_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main(model_timeout=240) else 1)
