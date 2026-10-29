#!/usr/bin/env python3
"""Compare independent CONFIG reference-current originals with pinned PHP."""
import config_iterator_reference_current_review_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main(model_timeout=240) else 1)
