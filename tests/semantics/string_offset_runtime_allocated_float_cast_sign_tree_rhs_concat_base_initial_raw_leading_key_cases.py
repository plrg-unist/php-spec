"""FLOAT casts interleave with signs without allocating another RHS row."""

from string_offset_runtime_allocated_float_sign_tree_rhs_concat_base_initial_raw_leading_key_cases import CASES as SIGN_CASES, WATCHED as SIGN_WATCHED

WATCHED = [
    'tests/semantics/string_offset_runtime_allocated_float_sign_tree_rhs_concat_base_initial_raw_leading_key_cases.py',
    *SIGN_WATCHED,
]

CASES = []
for index, case in enumerate(SIGN_CASES):
    before = '(string)(-(-(+(-12.5))))' if index else '(string)(+(-(+0.0)))'
    after = '(string)(-((float)(-((float)(+(-12.5))))))' if index else '(string)(+((float)(-((float)(+0.0)))))'
    assert after.count('(') == after.count(')')
    assert case['source'].count(before) == 1
    CASES.append(dict(case,
        id=case['id'].replace('float-sign-tree-rhs', 'float-cast-sign-tree-rhs'),
        source=case['source'].replace(before, after)))
