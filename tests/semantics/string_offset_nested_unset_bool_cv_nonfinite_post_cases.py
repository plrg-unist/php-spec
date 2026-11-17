"""Nonfinite postvalues warn again; first-handler throws keep their exception."""
import os

import string_offset_nested_unset_bool_cv_quiet_post_cases as prior

CASES, OUTPUTS, FACTS = {}, {}, {}
for tag, value, bits, mode, masked, initial in (
    ('infinity-return', b'INF', 9218868437227405312, 'return', False, b'true'),
    ('negative-infinity-second-throw', b'-INF', 18442240474082181120, 'second-throw', False, b'true'),
    ('nan-null-return', b'NAN', 9221120237041090560, 'return', False, b'null'),
    ('nan-masked-return', b'NAN', 9221120237041090560, 'return', True, b'true'),
    ('infinity-first-throw', b'INF', 9218868437227405312, 'first-throw', False, b'false'),
    ('negative-infinity-masked-first-throw', b'-INF', 18442240474082181120, 'first-throw', True, b'false'),
    ('nan-null-masked-first-throw', b'NAN', 9221120237041090560, 'first-throw', True, b'null'),
):
    throwing = mode == 'first-throw'
    old = tuple(prior.CASES)[2 if throwing else 0]
    source = prior.CASES[old]
    function = b'nestedUnsetNonfinitePost' + tag.title().replace('-', '').encode()
    old_function = b'nestedUnsetBoolQuietPostWarning' + (b'Throw' if throwing else b'Return')
    assert source.count(old_function) == 2
    source = source.replace(old_function, function)
    assert source.count(b'$GLOBALS["key"] = 7;') == source.count(b'$key === 7') == 1
    source = source.replace(b'$GLOBALS["key"] = 7;', b'$GLOBALS["key"] = ' + value + b';')
    observer = b'$key !== $key' if value == b'NAN' else b'$key === ' + value
    if mode == 'second-throw':
        assert source.count(b'return true;') == 1
        source = source.replace(b'return true;', b'if ($message !== "String offset cast occurred") { $GLOBALS["key"] = "done"; throw new Exception("range"); } return true;')
        observer = b'$key === "done"'
    source = source.replace(b'$key === 7', observer)
    if initial == b'null':
        original = b'$key = false;' if throwing else b'$key = true;'
        assert source.count(original) == 1
        source = source.replace(original, b'$key = null;')
    if masked:
        token = b'throw new Exception("handler");' if throwing else b'return true;'
        assert source.count(token) == 1
        source = source.replace(token, b'set_error_handler("' + function + b'", E_USER_WARNING); ' + token)
    message = b'The float ' + value + b' is not representable as an int, cast occurred'
    output = prior.OUTPUTS[old]
    if not throwing and not masked:
        first, rest = output.split(b';', 1)
        output = first + b';H:2:' + message + b';' + rest
    if mode == 'second-throw':
        suffix = b'Cannot use string offset as an array|5|7|ab|1|1'
        assert output.endswith(suffix)
        output = output[:-len(suffix)] + b'range|2|7|ab|0|1'
    name = 'nested-unset-bool-cv-nonfinite-post-' + tag
    CASES[name], OUTPUTS[name] = source, output
    FACTS[name] = {'bits': bits, 'mode': mode, 'masked': masked, 'message': message,
                   'entry': 'PNULL' if initial == b'null' else '(PBOOL ' + initial.decode() + ')'}


def stderr(name, path):
    facts = FACTS[name]
    return (b'Warning: ' + facts['message'] + b' in ' + os.fsencode(path) + b' on line 5\n'
            if facts['masked'] else b'')


WATCHED = prior.WATCHED + (
    'tests/semantics/string_offset_nested_unset_bool_cv_quiet_post_cases.py',
    'vendor/php-src/Zend/zend_execute.c',
    'vendor/php-src/Zend/zend_operators.c',
    'vendor/php-src/Zend/zend_operators.h',
    'vendor/php-src/Zend/zend.c',
    'vendor/php-src/Zend/zend_execute_API.c',
    'spec/semantics/387-integer-operator-warnings.watsup',
)
