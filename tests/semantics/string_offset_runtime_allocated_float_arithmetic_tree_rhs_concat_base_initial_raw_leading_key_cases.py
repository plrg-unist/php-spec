"""Raw-FLOAT arithmetic trees retain one RHS row and signed-zero operation order."""

from string_offset_runtime_allocated_unary_minus_float_rhs_concat_base_initial_raw_leading_key_cases import CASES as MINUS_CASES, WATCHED as MINUS_WATCHED

WATCHED = [
    'tests/semantics/string_offset_runtime_allocated_unary_minus_float_rhs_concat_base_initial_raw_leading_key_cases.py',
    *MINUS_WATCHED,
]

CASES = []
for index, case in enumerate(MINUS_CASES):
    before = '(string)(-12.5)' if index else '(string)(-0.0)'
    after = '(string)((((float)(-25.0) + 0.0) - (0.0 * 2.0)) / ((float)(1.0 + 1.0)))' if index else (
        '(string)((float)((((-0.0) - 0.0) * (+2.0)) / (1.0 + 1.0)))')
    assert after.count('(') == after.count(')')
    assert case['source'].count(before) == 1
    CASES.append(dict(case,
        id=case['id'].replace('unary-minus-float-rhs', 'float-arithmetic-tree-rhs'),
        source=case['source'].replace(before, after)))
