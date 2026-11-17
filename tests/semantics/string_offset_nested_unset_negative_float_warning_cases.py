"""A unary minus over a raw FLOAT warns before the fixed nested unset Error."""
import string_offset_nested_unset_float_warning_cases as raw

CASES = {}
OUTPUTS = {}
KEY_BITS = {}
CHILD_BITS = {}
for name, source in raw.CASES.items():
    own_name = name.replace('float-', 'negative-float-')
    bits = raw.KEY_BITS[name]
    literal = {4607182418800017408: b'1.0', 4609434218613702656: b'1.5',
               9218868437227405312: b'1e309'}[bits]
    assert source.count(b'[' + literal + b']') == 1
    CASES[own_name] = source.replace(b'[' + literal + b']', b'[-' + literal + b']').replace(
        b'FloatWarning', b'NegativeFloatWarning')
    OUTPUTS[own_name] = raw.OUTPUTS[name]
    KEY_BITS[own_name] = bits ^ (1 << 63)
    CHILD_BITS[own_name] = bits

WATCHED = raw.WATCHED + (
    'tests/semantics/string_offset_nested_unset_float_warning_cases.py',
)
