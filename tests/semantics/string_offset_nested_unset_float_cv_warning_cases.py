"""FLOAT CV keys use a silent, discarded conversion after the Warning handler."""
import string_offset_nested_unset_null_warning_cases as null

CASES = {}
OUTPUTS = {}
KEY_BITS = {}
for tag, literal, bits, throwing, mutation in (
    ('integral-return', b'1.0', 0x3ff0000000000000, False, b''),
    ('fractional-throw', b'1.5', 0x3ff8000000000000, True, b''),
    ('infinite-return', b'1e309', 0x7ff0000000000000, False, b''),
    ('object-return', b'1.5', 0x3ff8000000000000, False, b'global $key; $key = new stdClass; '),
    ('unset-return', b'1.5', 0x3ff8000000000000, False, b'unset($GLOBALS["key"]); '),
    ('object-throw', b'1.5', 0x3ff8000000000000, True, b'global $key; $key = new stdClass; '),
):
    prior = tuple(null.CASES)[int(throwing)]
    source = null.CASES[prior]
    name = 'nested-unset-float-cv-' + tag
    assert source.count(b'[null]') == source.count(b'$last = 0;') == 1
    source = source.replace(b'[null]', b'[$key]').replace(b'$last = 0;', b'$last = 0; $key = ' + literal + b';')
    source = source.replace(b'NullWarning', b'FloatCvWarning')
    if mutation:
        assert source.count(b'{ echo "H:"') == 1
        source = source.replace(b'{ echo "H:"', b'{ ' + mutation + b'echo "H:"')
    CASES[name] = source
    OUTPUTS[name] = null.OUTPUTS[prior]
    KEY_BITS[name] = bits

WATCHED = null.WATCHED + (
    'tests/semantics/string_offset_nested_unset_null_warning_cases.py',
    'spec/semantics/00-numeric.watsup',
    'spec/semantics/33-runtime-compiler.watsup',
    'spec/semantics/41-array-control.watsup',
)
