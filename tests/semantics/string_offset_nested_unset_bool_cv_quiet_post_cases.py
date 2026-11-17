"""BOOL CV handlers can leave a quiet NULL/INT value in the same ordinary slot."""
import string_offset_nested_unset_bool_cv_warning_cases as prior

CASES = {}
OUTPUTS = {}
POST_VALUES = {}
for tag, value, throwing in (
    ('integer-return', b'7', False),
    ('null-return', b'null', False),
    ('integer-throw', b'7', True),
    ('null-throw', b'null', True),
):
    old_name = tuple(prior.CASES)[int(throwing)]
    source = prior.CASES[old_name]
    name = 'nested-unset-bool-cv-quiet-post-' + tag
    assert source.count(b'{ echo "H:"') == 1
    source = source.replace(b'{ echo "H:"', b'{ $GLOBALS["key"] = ' + value + b'; echo "H:"')
    source = source.replace(b'BoolCvWarning', b'BoolQuietPostWarning')
    assert source.endswith(b' }\n')
    source = source[:-1] + b' echo "|", (int)($key === ' + value + b');\n'
    CASES[name] = source
    OUTPUTS[name] = prior.OUTPUTS[old_name] + b'|1'
    POST_VALUES[name] = 'PNULL' if value == b'null' else '(PINT 7)'

WATCHED = prior.WATCHED + (
    'tests/semantics/string_offset_nested_unset_bool_cv_warning_cases.py',
    'spec/semantics/76-globals.watsup',
    'spec/semantics/79-call-frames.watsup',
)
