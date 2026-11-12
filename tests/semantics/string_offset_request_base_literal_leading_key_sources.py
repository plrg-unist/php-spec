#!/usr/bin/env python3
"""Checked ordinary-source REQUEST-base literal-leading-key agreements."""
import string_offset_request_base_literal_leading_key_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main(model_timeout=90) else 1)
