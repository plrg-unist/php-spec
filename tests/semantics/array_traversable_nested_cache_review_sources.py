#!/usr/bin/env python3
"""Independent original nested Traversable cache throw cases."""
import array_traversable_nested_cache_review_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
