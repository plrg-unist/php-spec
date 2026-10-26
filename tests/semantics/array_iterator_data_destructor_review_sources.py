#!/usr/bin/env python3
"""Original Iterator DATA-destructor exception ordering witnesses."""
import array_iterator_data_destructor_review_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
