"""Already-certified quiet scalar conditions select both raw ternary arms."""

from string_offset_runtime_cast_truth_base_initial_raw_leading_key_cases import CASES as TEMPLATES

WATCHED = ['tests/semantics/string_offset_runtime_cast_truth_base_initial_raw_leading_key_cases.py']

CONDITIONS = [
    ('identity-true', '(int)null === 0', True, 'PBOOL true'),
    ('equality-false', '(int)null == 1', False, 'PBOOL false'),
    ('positive-int', '+(int)true', True, 'PINT 1'),
    ('negative-zero', '-(float)0', False, 'PFLOAT 9223372036854775808'),
    ('integer-add-zero', '(int)null + 0', False, 'PINT 0'),
    ('float-divide', '(float)true / 2', True, 'PFLOAT 4602678819172646912'),
    ('string-not', r'~((string)"\xce")', True, 'PSTRING_CARRIER INTERNED_STRING ($ptascii("1"))'),
    ('string-xor', r'((string)"\xff" ^ (string)"\xcf")', False, 'PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))'),
    ('and-skipped', '(int)null && (1 / 0)', False, 'PBOOL false'),
    ('or-skipped', '(int)1 || (1 / 0)', True, 'PBOOL true'),
    ('logical-xor', '(int)1 xor (bool)true', False, 'PBOOL false'),
    ('boolean-not', '!((int)null)', True, 'PBOOL true'),
]

CASES = []
for index, (name, condition, truth, value) in enumerate(CONDITIONS):
    reference = index % 2
    template = TEMPLATES[reference]
    old = '((float)(bool)"0")' if reference else '((bool)(int)"1")'
    assert template['source'].count(old) == 1
    source = template['source'].replace(old, '(' + condition + ')', 1)
    source = source.replace('runtimeCastTruth', 'runtimeScalarTruth')
    selected = 'b' if truth != bool(reference) else 'Y'
    CASES.append(dict(template,
        id='runtime-scalar-truth-base-' + name + ('-reference-key' if reference else '-current-key'),
        source=source, expected_stdout=template['expected_stdout'].replace('R:b;', 'R:' + selected + ';'),
        condition=condition, truth=truth, value=value, selected=selected))
