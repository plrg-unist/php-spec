"""Initialized ordinary NULL-CV entries share the native NULL/BOOL cast path."""
import string_offset_nested_unset_bool_cv_warning_cases as boolean
import string_offset_nested_unset_bool_cv_float_post_cases as floating

CASES = {}
OUTPUTS = {}
POST_VALUES = {}
for tag, prior, index, old_value, post in (
    ('return', boolean, 0, b'true', 'PNULL'),
    ('throw', boolean, 1, b'false', 'PNULL'),
    ('fitting-float-return', floating, 0, b'true', '(PFLOAT 4609434218613702656)'),
    ('range-float-throw', floating, 3, b'false', '(PFLOAT 4906019910204099648)'),
):
    old_name = tuple(prior.CASES)[index]
    source = prior.CASES[old_name]
    old = b'$key = ' + old_value + b';'
    assert source.count(old) == 1
    source = source.replace(old, b'$key = null;')
    source = source.replace(b'BoolCvWarning', b'NullCvWarning').replace(b'BoolFloatPostWarning', b'NullCvFloatPostWarning')
    name = 'nested-unset-null-cv-warning-' + tag
    output = prior.OUTPUTS[old_name]
    if prior is boolean:
        assert source.endswith(b'\n')
        source = source[:-1] + b' echo "|", (int)($key === null);\n'
        output += b'|1'
    CASES[name], OUTPUTS[name], POST_VALUES[name] = source, output, post

WATCHED = floating.WATCHED + (
    'tests/semantics/string_offset_nested_unset_bool_cv_float_post_cases.py',
    'spec/semantics/206-error-handlers.watsup',
    'spec/semantics/207-error-handler-runtime.watsup',
)
