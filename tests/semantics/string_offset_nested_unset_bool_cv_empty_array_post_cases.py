"""A saved ordinary NULL/BOOL CV can hold an empty array after its Warning."""
import string_offset_nested_unset_bool_cv_quiet_post_cases as prior

CASES, OUTPUTS, FACTS = {}, {}, {}
for tag, initial, throwing in (
    ('null-return', b'null', False),
    ('bool-first-throw', b'false', True),
):
    old = tuple(prior.CASES)[2 if throwing else 0]
    source = prior.CASES[old]
    function = b'nestedUnsetEmptyArrayPost' + (b'Throw' if throwing else b'Return')
    old_function = b'nestedUnsetBoolQuietPostWarning' + (b'Throw' if throwing else b'Return')
    assert source.count(old_function) == 2
    source = source.replace(old_function, function)
    assert source.count(b'$GLOBALS["key"] = 7;') == source.count(b'$key === 7') == 1
    source = source.replace(b'$GLOBALS["key"] = 7;', b'$GLOBALS["key"] = [];')
    source = source.replace(b'$key === 7', b'$key === []')
    if initial == b'null':
        assert source.count(b'$key = true;') == 1
        source = source.replace(b'$key = true;', b'$key = null;')
    name = 'nested-unset-bool-cv-empty-array-post-' + tag
    CASES[name], OUTPUTS[name] = source, prior.OUTPUTS[old]
    FACTS[name] = {'entry': 'PNULL' if initial == b'null' else '(PBOOL false)',
                   'throwing': throwing}


def stderr(name, path):
    return b''


WATCHED = prior.WATCHED + (
    'tests/semantics/string_offset_nested_unset_bool_cv_quiet_post_cases.py',
    'spec/semantics/20-machine.watsup',
    'spec/semantics/36-arrays.watsup',
    'spec/semantics/37-array-locations.watsup',
    'vendor/php-src/Zend/zend_execute.c',
    'vendor/php-src/Zend/zend_operators.c',
    'vendor/php-src/Zend/zend_variables.c',
)
