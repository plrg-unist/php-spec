"""Single unary-minus raw-FLOAT cast RHSs expose the selected minus byte."""

from string_offset_runtime_allocated_raw_float_rhs_concat_base_initial_raw_leading_key_cases import CASES as RAW_CASES

WATCHED = ['tests/semantics/string_offset_runtime_allocated_raw_float_rhs_concat_base_initial_raw_leading_key_cases.py']

CASES = []
for index, case in enumerate(RAW_CASES):
    before = '(string)12.5' if index else '(string)0.0'
    after = '(string)(-12.5)' if index else '(string)(-0.0)'
    assert case['source'].count(before) == 1
    source = case['source'].replace(before, after)
    expected = case['expected_stdout']
    if index:
        assert source.count('$replacementKey = 12;') == source.count('"11x"') == 1
        source = source.replace('$replacementKey = 12;', '$replacementKey = 13;').replace('"11x"', '"9x"')
        expected = expected.replace('11x', '9x').replace('R:.;K:12;', 'R:-;K:13;')
    else:
        expected = expected.replace('R:0;', 'R:-;')
    CASES.append(dict(case, id=case['id'].replace('raw-float-rhs', 'unary-minus-float-rhs'),
                      source=source, expected_stdout=expected))
