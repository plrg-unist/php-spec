"""A warned BOOL CV can retain a finite FLOAT in its original ordinary slot."""
import string_offset_nested_unset_bool_cv_quiet_post_cases as prior

CASES = {}
OUTPUTS = {}
POST_VALUES = {}
for tag, value, bits, throwing in (
    ('fraction-return', b'1.5', 4609434218613702656, False),
    ('negative-fraction-throw', b'-1.5', 13832806255468478464, True),
    ('negative-zero-return', b'-0.0', 9223372036854775808, False),
    ('out-of-range-throw', b'1.0e20', 4906019910204099648, True),
):
    old_name = tuple(prior.CASES)[2 if throwing else 0]
    source = prior.CASES[old_name]
    assert source.count(b'$GLOBALS["key"] = 7;') == source.count(b'$key === 7') == 1
    source = source.replace(b'$GLOBALS["key"] = 7;', b'$GLOBALS["key"] = ' + value + b';')
    source = source.replace(b'$key === 7', b'$key === ' + value)
    source = source.replace(b'BoolQuietPostWarning', b'BoolFloatPostWarning')
    name = 'nested-unset-bool-cv-float-post-' + tag
    output = prior.OUTPUTS[old_name]
    if tag == 'negative-zero-return':
        assert source.endswith(b'\n')
        source = source[:-1] + b' echo ":", (string)$key;\n'
        output += b':-0'
    CASES[name], OUTPUTS[name] = source, output
    POST_VALUES[name] = '(PFLOAT ' + str(bits) + ')'

WATCHED = prior.WATCHED + (
    'tests/semantics/string_offset_nested_unset_bool_cv_quiet_post_cases.py',
    'spec/semantics/00-numeric.watsup',
    'spec/semantics/01-integer.watsup',
    'spec/semantics/02-numeric-text.watsup',
    'spec/semantics/03-numeric-format.watsup',
    'spec/semantics/04-numeric-context.watsup',
)
