#!/usr/bin/env python3
"""Native-first literal-root CV keys and compile-invalid mixed guard."""
import incdec_warnings as runner
import list_literal_cv_missing_warning_cases as cases


if __name__ == '__main__':
    cases.CASES = {**cases.CASES, **cases.REJECTIONS}
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
