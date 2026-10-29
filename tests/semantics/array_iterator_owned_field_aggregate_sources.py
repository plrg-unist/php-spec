#!/usr/bin/env python3
"""Native-first Aggregate promotion into a field-owning Iterator."""
import array_iterator_owned_field_aggregate_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main(model_timeout=120) else 1)
