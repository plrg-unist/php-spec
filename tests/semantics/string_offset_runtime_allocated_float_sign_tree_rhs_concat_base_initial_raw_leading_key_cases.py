"""Finite raw-FLOAT sign trees retain allocated RHS bytes and saved offsets."""

from string_offset_runtime_allocated_unary_minus_float_rhs_concat_base_initial_raw_leading_key_cases import CASES as MINUS_CASES

WATCHED = [
    'tests/semantics/string_offset_runtime_allocated_unary_minus_float_rhs_concat_base_initial_raw_leading_key_cases.py',
    'tests/semantics/string_offset_runtime_allocated_raw_float_rhs_concat_base_initial_raw_leading_key_cases.py',
]

CASES = []
for index, case in enumerate(MINUS_CASES):
    before = '(string)(-12.5)' if index else '(string)(-0.0)'
    after = '(string)(-(-(+(-12.5))))' if index else '(string)(+(-(+0.0)))'
    assert case['source'].count(before) == 1
    CASES.append(dict(case,
        id=case['id'].replace('unary-minus-float-rhs', 'float-sign-tree-rhs'),
        source=case['source'].replace(before, after)))
