"""Core arithmetic NaN CV keys are observed without Boolean/format coercion."""
import string_offset_nested_unset_null_warning_cases as null
import string_offset_nested_unset_float_cv_warning_cases as floating

CASES = {}
OUTPUTS = {}
for tag, expression, throwing, mutate in (
    ('arithmetic-return', b'(1e309 - 1e309)', False, False),
    ('arithmetic-throw', b'(1e309 - 1e309)', True, False),
    ('negated-return', b'-(1e309 - 1e309)', False, False),
    ('object-return', b'(1e309 - 1e309)', False, True),
):
    prior = tuple(null.CASES)[int(throwing)]
    source = null.CASES[prior]
    name = 'nested-unset-nan-cv-' + tag
    assert source.count(b'[null]') == source.count(b'$last = 0;') == 1
    source = source.replace(b'[null]', b'[$key]').replace(b'$last = 0;',
        b'$last = 0; $key = ' + expression + b'; echo "N:", (int)($key !== $key), ";";')
    source = source.replace(b'NullWarning', b'NanCvWarning')
    if mutate:
        assert source.count(b'{ echo "H:"') == 1
        source = source.replace(b'{ echo "H:"', b'{ global $key; $key = new stdClass; echo "H:"')
    CASES[name] = source
    OUTPUTS[name] = b'N:1;' + null.OUTPUTS[prior]

WATCHED = floating.WATCHED + (
    'tests/semantics/string_offset_nested_unset_float_cv_warning_cases.py',
)
