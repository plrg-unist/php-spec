#!/usr/bin/env python3
"""Original observations for nested runtime ARRAY TMPs at NULL keys."""
import array_literal_null_key_array_tmp_subtree_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
