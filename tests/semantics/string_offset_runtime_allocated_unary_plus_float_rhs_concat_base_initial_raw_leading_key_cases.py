"""Single unary-plus raw-FLOAT cast RHSs in allocated CONCAT offset bases."""

from string_offset_runtime_allocated_raw_float_rhs_concat_base_initial_raw_leading_key_cases import CASES as RAW_CASES

WATCHED = ['tests/semantics/string_offset_runtime_allocated_raw_float_rhs_concat_base_initial_raw_leading_key_cases.py']

CASES = []
for case, before, after in zip(RAW_CASES, ('(string)0.0', '(string)12.5'),
                              ('(string)(+0.0)', '(string)(+12.5)'), strict=True):
    assert case['source'].count(before) == 1
    CASES.append(dict(case, id=case['id'].replace('raw-float-rhs', 'unary-plus-float-rhs'),
                      source=case['source'].replace(before, after)))
