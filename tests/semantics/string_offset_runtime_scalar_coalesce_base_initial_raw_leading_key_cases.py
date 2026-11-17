"""Certified NULL and STRING left values select the coalesce header by nullness."""

from string_offset_runtime_null_shorthand_base_initial_raw_leading_key_cases import CASES as NULL_CASES, WATCHED as NULL_WATCHED
from string_offset_runtime_string_truthy_shorthand_base_initial_raw_leading_key_cases import CASES as STRING_CASES, WATCHED as STRING_WATCHED

WATCHED = ['tests/semantics/string_offset_runtime_null_shorthand_base_initial_raw_leading_key_cases.py',
           'tests/semantics/string_offset_runtime_string_truthy_shorthand_base_initial_raw_leading_key_cases.py',
           *NULL_WATCHED, *STRING_WATCHED]

CASES = []
for index, template in enumerate((NULL_CASES[0], STRING_CASES[1])):
    assert template['source'].count(' ?: ') == 1
    source = template['source'].replace(' ?: ', ' ?? ', 1)
    source = source.replace('runtimeNullShorthand', 'runtimeScalarCoalesce')
    source = source.replace('runtimeStringTruthyShorthand', 'runtimeScalarCoalesce')
    CASES.append(dict(template,
        id='runtime-scalar-coalesce-base-initial-raw-leading-' + ('reference-key' if index else 'current-key'),
        source=source, left_value=template['value'],
        value='PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))',
        right_bytes='XYZ' if index else 'abc',
        selected_kind='string' if index else 'null'))
