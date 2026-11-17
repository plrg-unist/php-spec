"""An emitted nested ternary returns actual NULL before selecting a raw base."""

from string_offset_runtime_cast_truth_base_initial_raw_leading_key_cases import CASES as TEMPLATES

WATCHED = ['tests/semantics/string_offset_runtime_cast_truth_base_initial_raw_leading_key_cases.py']

CASES = []
for index, template in enumerate(TEMPLATES):
    old = '((float)(bool)"0")' if index else '((bool)(int)"1")'
    inner = '(int)null ? 1 : null' if index else '(int)1 ? null : 1'
    assert template['source'].count(old) == 1
    source = template['source'].replace(old, '(' + inner + ')', 1)
    source = source.replace('runtimeCastTruth', 'runtimeNullTruth')
    if not index:
        source = source.replace('? "abc" : "XYZ"', '? "XYZ" : "abc"', 1)
    CASES.append(dict(template,
        id=template['id'].replace('runtime-cast-truth', 'runtime-null-truth'),
        source=source, truth=False, value='PNULL', selected='b',
        inner_truth=not bool(index), inner_value='PINT 0' if index else 'PINT 1'))
