#!/usr/bin/env python3
"""Native-first post-insert next() throw with one owning Iterator field."""
import array_iterator_owned_field_next_throw_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
