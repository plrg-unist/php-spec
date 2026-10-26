#!/usr/bin/env python3
"""Original-source Iterator DATA destruction under the pinned CLI profile."""
import array_iterator_data_destructor_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
