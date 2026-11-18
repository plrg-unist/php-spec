"""Nonnull FLOAT coalesce trees retain falsey values and skip abrupt children."""

from string_offset_runtime_allocated_unary_minus_float_rhs_concat_base_initial_raw_leading_key_cases import CASES as MINUS_CASES, WATCHED as MINUS_WATCHED

WATCHED = [
    'tests/semantics/string_offset_runtime_allocated_unary_minus_float_rhs_concat_base_initial_raw_leading_key_cases.py',
    *MINUS_WATCHED,
]

CASES = []
for index, case in enumerate(MINUS_CASES):
    before = '(string)(-12.5)' if index else '(string)(-0.0)'
    skipped = '((float)(1.0 / 0.0))'
    selected = '((float)(-25.0))' if index else '((float)(-0.0))'
    coalesce = f'({selected} ?? {skipped})'
    after = f'(string)((({coalesce} - (0.0 * 2.0)) + 0.0) / ((float)(1.0 + 1.0)))' if index else (
        f'(string){coalesce}')
    assert after.count('(') == after.count(')')
    assert case['source'].count(before) == 1
    CASES.append(dict(case,
        id=case['id'].replace('unary-minus-float-rhs', 'float-coalesce-tree-rhs'),
        source=case['source'].replace(before, after)))
