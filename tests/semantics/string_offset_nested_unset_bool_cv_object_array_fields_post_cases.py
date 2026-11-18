"""DIRECT array fields copy containers while retaining embedded scalar references."""
import string_offset_nested_unset_bool_cv_empty_array_post_cases as prior

CASES, OUTPUTS, FACTS = {}, {}, {}
REBOUND_OUTPUTS, RETAINED_OUTPUTS, OUTSIDE_OUTPUTS = {}, {}, {}
for old, original in prior.CASES.items():
    source = original.replace(b'EmptyArrayPost', b'ObjectArrayFieldsPost')
    setup = (b'global $fieldValue, $outside; $fieldValue = 7; '
             b'$payload = [11, &$fieldValue]; $outside = $payload; '
             b'$obj = new stdClass; $obj->left = $payload; $obj->right = $payload; '
             b'$GLOBALS["objectAlias"] = $obj; '
             b'$GLOBALS["objectWeak"] = WeakReference::create($obj); unset($obj); '
             b'$GLOBALS["key"] = [7, [8, &$GLOBALS["objectAlias"], '
             b'&$GLOBALS["objectAlias"], $GLOBALS["objectAlias"]]];')
    assert source.count(b'$GLOBALS["key"] = [];') == source.count(b'$last = 0;') == 1
    source = source.replace(b'$GLOBALS["key"] = [];', setup)
    source = source.replace(b'$last = 0;',
        b'$last = 0; $objectAlias = null; $objectWeak = null; $fieldValue = null; $outside = null;')
    at = source.index(b'echo "|", (int)($key')
    observer = (b'echo "|", (int)($key[0] === 7), "|", (int)($key[1][0] === 8), '
        b'"|", (int)($objectWeak->get() === $objectAlias && '
        b'$key[1][1] === $objectAlias && $key[1][2] === $objectAlias && '
        b'$key[1][3] === $objectAlias), "|", '
        b'(int)($objectAlias->left[0] === 11 && $objectAlias->right[0] === 11 && '
        b'$outside[0] === 11 && $outside[1] === 7 && $fieldValue === 7); '
        b'$key[1][1]->left[0] = 19; '
        b'echo "|", (int)($objectAlias->left[0] === 19 && '
        b'$objectAlias->right[0] === 11 && $outside[0] === 11); '
        b'$key[1][3]->right[1] = 9; '
        b'echo "|", (int)($fieldValue === 9 && $objectAlias->left[1] === 9 && $outside[1] === 9); '
        b'$objectAlias = new stdClass; $objectWeakAfter = WeakReference::create($objectAlias); '
        b'$fieldValue = 13; '
        b'echo "|", (int)($objectWeak->get() === $key[1][3] && '
        b'$key[1][3] !== $objectAlias && $key[1][3]->left[0] === 19 && '
        b'$key[1][3]->right[1] === 13); unset($fieldValue); '
        b'echo "|", (int)(!isset($fieldValue) && $outside[1] === 13 && '
        b'$key[1][3]->left[1] === 13 && $key[1][1] === $objectAlias && '
        b'$key[1][2] === $objectAlias), "|B"; '
        b'unset($key); echo "|", (int)isset($key), "|", (int)($objectWeak->get() === null), '
        b'"|", (int)($objectWeakAfter->get() === $objectAlias), '
        b'"|", (int)($outside[0] === 11 && $outside[1] === 13), "|R"; '
        b'unset($outside); echo "|", (int)isset($outside), '
        b'"|", (int)($objectWeakAfter->get() === $objectAlias), "|O"; '
        b'unset($objectAlias); echo "|", (int)($objectWeakAfter->get() === null), '
        b'"|", (int)isset($objectAlias);')
    source = source[:at] + observer + b'\n'
    name = old.replace('empty-array-post', 'object-array-fields-post')
    assert prior.OUTPUTS[old].endswith(b'|1')
    rebound = prior.OUTPUTS[old][:-2] + b'|1' * 8 + b'|B'
    retained = rebound + b'|0|1|1|1|R'
    outside = retained + b'|0|1|O'
    CASES[name], OUTPUTS[name] = source, outside + b'|1|0'
    REBOUND_OUTPUTS[name], RETAINED_OUTPUTS[name], OUTSIDE_OUTPUTS[name] = rebound, retained, outside
    FACTS[name] = {**prior.FACTS[old], 'mixed': False}


def stderr(name, path):
    return b''


WATCHED = prior.WATCHED + (
    'tests/semantics/string_offset_nested_unset_bool_cv_empty_array_post_cases.py',
    'tests/semantics/string_offset_nested_unset_bool_cv_empty_array_post_sources.py',
    'tests/semantics/string_offset_nested_unset_bool_cv_object_array_fields_post_sources.py',
    'spec/semantics/84-call-integrity.watsup',
    'spec/semantics/130-stdclass-runtime.watsup',
    'spec/semantics/136-property-runtime.watsup',
    'spec/semantics/138-property-references.watsup',
    'spec/semantics/270-eager-destructors.watsup',
    'spec/semantics/296-weak-references.watsup',
    'spec/semantics/413-array-literal-key-warnings.watsup',
    'vendor/php-src/Zend/zend_object_handlers.c',
    'vendor/php-src/Zend/zend_objects.c',
    'vendor/php-src/Zend/zend_objects_API.c',
    'vendor/php-src/Zend/zend_weakrefs.c',
)
