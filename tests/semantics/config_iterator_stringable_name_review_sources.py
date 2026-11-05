#!/usr/bin/env python3
"""Independent normal Iterator/Stringable option source comparisons."""
import config_iterator_stringable_name_review_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main(model_timeout=300) else 1)
