"""An emitted string-producing ternary supplies the truthy shorthand header."""

from string_offset_runtime_string_cast_truthy_shorthand_base_initial_raw_leading_key_cases import CASES as TEMPLATES

WATCHED = ['tests/semantics/string_offset_runtime_string_cast_truthy_shorthand_base_initial_raw_leading_key_cases.py']

CASES = []
for index, template in enumerate(TEMPLATES):
    old = '((string)(string)"abc")' if index else '((string)"abc")'
    inner = '((int)null ? "XYZ" : "abc")' if index else '((int)1 ? "abc" : "XYZ")'
    assert template['source'].count(old) == 1
    source = template['source'].replace(old, inner, 1)
    source = source.replace('runtimeStringCastTruthyShorthand', 'runtimeStringTruthyShorthand')
    CASES.append(dict(template,
        id=template['id'].replace('runtime-string-cast-truthy-shorthand', 'runtime-string-truthy-shorthand'),
        source=source, truth=True,
        value='PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))',
        selected='b', inner_truth=not bool(index),
        inner_value='PINT 0' if index else 'PINT 1'))
