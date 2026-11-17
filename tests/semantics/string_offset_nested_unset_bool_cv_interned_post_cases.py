"""Nonstrict post-handler string conversion is quiet; its result is unused."""
import base64
import json

import string_offset_nested_unset_bool_cv_quiet_post_cases as prior

CASES, OUTPUTS, POST_BYTES, ENTRY_VALUES, THROWING, MASKS = {}, {}, {}, {}, {}, {}
for tag, value, initial, throwing, remask in (
    ('leading-return', b'7x', b'true', False, False),
    ('oob-string-throw', b'1e20', b'false', True, True),
    ('empty-return', b'', b'true', False, False),
    ('null-fraction-return', b'1.5', b'null', False, False),
):
    old_name = tuple(prior.CASES)[2 if throwing else 0]
    source = prior.CASES[old_name]
    quoted = json.dumps(value.decode()).encode()
    assert source.count(b'$GLOBALS["key"] = 7;') == source.count(b'$key === 7') == 1
    source = source.replace(b'$GLOBALS["key"] = 7;', b'$GLOBALS["key"] = ' + quoted + b';')
    source = source.replace(b'$key === 7', b'$key === ' + quoted)
    old_function = b'nestedUnsetBoolQuietPostWarning' + (b'Throw' if throwing else b'Return')
    new_function = b'nestedUnsetBoolInternedPost' + tag.title().replace('-', '').encode()
    assert source.count(old_function) == 2
    source = source.replace(old_function, new_function)
    if initial == b'null':
        assert source.count(b'$key = true;') == 1
        source = source.replace(b'$key = true;', b'$key = null;')
    if remask:
        old = b'throw new Exception("handler");'
        assert source.count(old) == 1
        source = source.replace(old, b'set_error_handler("' + new_function + b'", E_USER_WARNING); ' + old)
    name = 'nested-unset-bool-cv-interned-post-' + tag
    CASES[name], OUTPUTS[name], POST_BYTES[name] = source, prior.OUTPUTS[old_name], value
    ENTRY_VALUES[name] = 'PNULL' if initial == b'null' else '(PBOOL ' + initial.decode() + ')'
    THROWING[name], MASKS[name] = throwing, 512 if remask else 30719


def post_value(name):
    return '(PSTRING_CARRIER INTERNED_STRING ($base64(' + json.dumps(base64.b64encode(POST_BYTES[name]).decode()) + ')))'


WATCHED = prior.WATCHED + (
    'tests/semantics/string_offset_nested_unset_bool_cv_quiet_post_cases.py',
    'spec/semantics/30-string-carriers.watsup',
    'vendor/php-src/Zend/zend_operators.c',
    'vendor/php-src/Zend/zend_operators.h',
)
