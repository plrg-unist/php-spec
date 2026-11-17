"""An emitted nested NULL condition selects the literal shorthand fallback."""

from string_offset_runtime_null_truth_base_initial_raw_leading_key_cases import CASES as TEMPLATES, WATCHED as TEMPLATE_WATCHED

WATCHED = ['tests/semantics/string_offset_runtime_null_truth_base_initial_raw_leading_key_cases.py', *TEMPLATE_WATCHED]

CASES = []
for template in TEMPLATES:
    old = ' ? "XYZ" : "abc"'
    assert template['source'].count(old) == 1
    source = template['source'].replace(old, ' ?: "abc"', 1)
    source = source.replace('runtimeNullTruth', 'runtimeNullShorthand')
    CASES.append(dict(template,
        id=template['id'].replace('runtime-null-truth', 'runtime-null-shorthand'),
        source=source))
