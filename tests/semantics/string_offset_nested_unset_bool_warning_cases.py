"""Literal Boolean intermediate unset keys warn before the nested Error."""
import string_offset_nested_unset_null_warning_cases as null

CASES = {}
OUTPUTS = {}
for literal in ('true', 'false'):
    for name, source in null.CASES.items():
        own_name = name.replace('null-warning', 'bool-' + literal + '-warning')
        assert source.count(b'[null]') == 1
        CASES[own_name] = source.replace(b'[null]', b'[' + literal.encode() + b']').replace(
            b'NullWarning', b'BoolWarning')
        OUTPUTS[own_name] = null.OUTPUTS[name]

WATCHED = null.WATCHED + ('tests/semantics/string_offset_nested_unset_null_warning_cases.py',)
