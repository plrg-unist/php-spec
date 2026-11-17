"""Mutable Boolean CV keys distinguish delayed reads and post-Warning conversion."""
import string_offset_nested_unset_null_warning_cases as null

CASES = {}
OUTPUTS = {}
for tag, initial, throwing, final, mutate in (
    ('true-return', b'true', False, b'$last = 7', False),
    ('false-throw', b'false', True, b'$last = 7', False),
    ('final-int-to-false', b'0', False, b'$last = ($key = false) + 7', False),
    ('final-true-to-int', b'true', False, b'$last = $key = 7', False),
    ('handler-object-return', b'true', False, b'$last = 7', True),
    ('handler-object-throw', b'true', True, b'$last = 7', True),
):
    prior = tuple(null.CASES)[int(throwing)]
    source = null.CASES[prior]
    name = 'nested-unset-bool-cv-' + tag
    assert source.count(b'[null]') == source.count(b'$last = 0;') == 1
    source = source.replace(b'[null]', b'[$key]').replace(b'$last = 0;', b'$last = 0; $key = ' + initial + b';')
    source = source.replace(b'$last = 7', final).replace(b'NullWarning', b'BoolCvWarning')
    if mutate:
        assert source.count(b'{ echo "H:"') == 1
        source = source.replace(b'{ echo "H:"', b'{ global $key; $key = new stdClass; echo "H:"')
    CASES[name] = source
    if not mutate:
        OUTPUTS[name] = (b'Cannot use string offset as an array|5|7|ab|1'
                         if tag == 'final-true-to-int' else null.OUTPUTS[prior])

OUTPUTS['nested-unset-bool-cv-handler-object-return'] = (
    b'H:2:String offset cast occurred;H:2:Object of class stdClass could not be converted to int;'
    b'Cannot use string offset as an array|5|7|ab|1')
OUTPUTS['nested-unset-bool-cv-handler-object-throw'] = null.OUTPUTS[tuple(null.CASES)[1]]
UNSUPPORTED = ('nested-unset-bool-cv-handler-object-return',
               'nested-unset-bool-cv-handler-object-throw')
QUIET_CONTROL = 'nested-unset-bool-cv-final-true-to-int'

WATCHED = null.WATCHED + (
    'tests/semantics/string_offset_nested_unset_null_warning_cases.py',
    'spec/semantics/33-runtime-compiler.watsup',
    'spec/semantics/41-array-control.watsup',
)
