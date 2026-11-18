"""Two stdClass fields retain one real primitive reference cell after a Warning."""
import string_offset_nested_unset_bool_cv_empty_array_post_cases as prior

CASES, OUTPUTS, FACTS, REBOUND_OUTPUTS, RETAINED_OUTPUTS = {}, {}, {}, {}, {}
for old, original in prior.CASES.items():
    source = original.replace(b'EmptyArrayPost', b'ObjectPrimitiveAliasFieldsPost')
    setup = (b'global $fieldValue; $fieldValue = 7; $obj = new stdClass; '
             b'$obj->count =& $fieldValue; $obj->mirror =& $fieldValue; '
             b'$GLOBALS["objectAlias"] = $obj; '
             b'$GLOBALS["objectWeak"] = WeakReference::create($obj); unset($obj); '
             b'$GLOBALS["key"] = [7, [8, &$GLOBALS["objectAlias"], '
             b'&$GLOBALS["objectAlias"], $GLOBALS["objectAlias"]]];')
    assert source.count(b'$GLOBALS["key"] = [];') == source.count(b'$last = 0;') == 1
    source = source.replace(b'$GLOBALS["key"] = [];', setup)
    source = source.replace(b'$last = 0;',
                            b'$last = 0; $objectAlias = null; $objectWeak = null; $fieldValue = null;')
    at = source.index(b'echo "|", (int)($key')
    observer = (b'echo "|", (int)($key[0] === 7), "|", (int)($key[1][0] === 8), '
                b'"|", (int)($objectWeak->get() === $objectAlias && '
                b'$key[1][1] === $objectAlias && $key[1][2] === $objectAlias && '
                b'$key[1][3] === $objectAlias), "|", '
                b'(int)($objectAlias->count === 7 && $objectAlias->mirror === 7 && $fieldValue === 7); '
                b'$key[1][1]->count = 9; '
                b'echo "|", (int)($key[1][2]->mirror === 9 && $fieldValue === 9); '
                b'$objectAlias = new stdClass; '
                b'$objectWeakAfter = WeakReference::create($objectAlias); $fieldValue = 13; '
                b'echo "|", (int)($objectWeak->get() === $key[1][3] && '
                b'$key[1][3] !== $objectAlias && $key[1][3]->count === 13 && '
                b'$key[1][3]->mirror === 13); unset($fieldValue); '
                b'echo "|", (int)($key[1][1] === $objectAlias && $key[1][2] === $objectAlias && '
                b'$objectWeakAfter->get() === $objectAlias && !isset($fieldValue) && '
                b'$key[1][3]->count === 13), "|B"; '
                b'unset($key); echo "|", (int)isset($key), "|", '
                b'(int)($objectWeak->get() === null), "|", '
                b'(int)($objectWeakAfter->get() === $objectAlias), "|R"; '
                b'unset($objectAlias); echo "|", (int)($objectWeakAfter->get() === null), '
                b'"|", (int)isset($objectAlias);')
    source = source[:at] + observer + b'\n'
    name = old.replace('empty-array-post', 'object-primitive-alias-fields-post')
    assert prior.OUTPUTS[old].endswith(b'|1')
    rebound = prior.OUTPUTS[old][:-2] + b'|1' * 7 + b'|B'
    retained = rebound + b'|0|1|1|R'
    CASES[name], OUTPUTS[name] = source, retained + b'|1|0'
    REBOUND_OUTPUTS[name], RETAINED_OUTPUTS[name] = rebound, retained
    FACTS[name] = {**prior.FACTS[old], 'mixed': False}


def stderr(name, path):
    return b''


WATCHED = prior.WATCHED + (
    'tests/semantics/string_offset_nested_unset_bool_cv_empty_array_post_cases.py',
    'tests/semantics/string_offset_nested_unset_bool_cv_empty_array_post_sources.py',
    'tests/semantics/string_offset_nested_unset_bool_cv_object_primitive_alias_fields_post_sources.py',
    'spec/semantics/84-call-integrity.watsup',
    'spec/semantics/130-stdclass-runtime.watsup',
    'spec/semantics/136-property-runtime.watsup',
    'spec/semantics/137-property-reference-compiler.watsup',
    'spec/semantics/138-property-references.watsup',
    'spec/semantics/261-object-casts.watsup',
    'spec/semantics/270-eager-destructors.watsup',
    'spec/semantics/296-weak-references.watsup',
    'spec/semantics/413-array-literal-key-warnings.watsup',
    'vendor/php-src/Zend/zend_object_handlers.c',
    'vendor/php-src/Zend/zend_objects.c',
    'vendor/php-src/Zend/zend_objects_API.c',
    'vendor/php-src/Zend/zend_weakrefs.c',
)
