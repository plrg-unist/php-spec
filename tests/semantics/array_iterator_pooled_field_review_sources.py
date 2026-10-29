#!/usr/bin/env python3
"""Compare the independent retained empty-field original with pinned PHP."""
import array_iterator_pooled_field_review_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main(model_timeout=120) else 1)
