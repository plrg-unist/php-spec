"""Raw FLOAT intermediate unset keys warn before the fixed nested Error."""
import string_offset_nested_unset_null_warning_cases as null

CASES = {}
OUTPUTS = {}
KEY_BITS = {}
for tag, literal, bits in (
    ('integral', b'1.0', 4607182418800017408),
    ('fractional', b'1.5', 4609434218613702656),
    ('infinite', b'1e309', 9218868437227405312),
):
    for name, source in null.CASES.items():
        own_name = name.replace('null-warning', 'float-' + tag + '-warning')
        assert source.count(b'[null]') == 1
        CASES[own_name] = source.replace(b'[null]', b'[' + literal + b']').replace(
            b'NullWarning', b'FloatWarning')
        OUTPUTS[own_name] = null.OUTPUTS[name]
        KEY_BITS[own_name] = bits

WATCHED = null.WATCHED + (
    'tests/semantics/string_offset_nested_unset_null_warning_cases.py',
    'spec/semantics/00-numeric.watsup', 'spec/semantics/33-runtime-compiler.watsup',
)
