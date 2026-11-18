"""Scalar stdClass fields survive shared DIRECT/ALIAS post-Warning owners."""
import string_offset_nested_unset_bool_cv_empty_array_post_cases as prior

CASES, OUTPUTS, FACTS, REBOUND_OUTPUTS, RETAINED_OUTPUTS = {}, {}, {}, {}, {}
for old, original in prior.CASES.items():
    source = original.replace(b'EmptyArrayPost', b'ObjectScalarFieldsPost')
    setup = (b'$obj = new stdClass; $obj->count = 7; $obj->enabled = true; '
             b'$obj->tag = "old"; $obj->empty = null; $obj->ratio = 1.5; '
             b'$GLOBALS["objectAlias"] = $obj; '
             b'$GLOBALS["objectWeak"] = WeakReference::create($obj); unset($obj); '
             b'$GLOBALS["key"] = [7, [8, &$GLOBALS["objectAlias"], '
             b'&$GLOBALS["objectAlias"], $GLOBALS["objectAlias"]]];')
    assert source.count(b'$GLOBALS["key"] = [];') == source.count(b'$last = 0;') == 1
    source = source.replace(b'$GLOBALS["key"] = [];', setup)
    source = source.replace(b'$last = 0;',
                            b'$last = 0; $objectAlias = null; $objectWeak = null;')
    at = source.index(b'echo "|", (int)($key')
    observer = (b'echo "|", (int)($key[0] === 7), "|", (int)($key[1][0] === 8), '
                b'"|", (int)($objectWeak->get() === $objectAlias && '
                b'$key[1][1] === $objectAlias && $key[1][2] === $objectAlias && '
                b'$key[1][3] === $objectAlias), "|", '
                b'(int)($objectAlias->count === 7 && $objectAlias->enabled === true && '
                b'$objectAlias->tag === "old" && $objectAlias->empty === null && '
                b'$objectAlias->ratio === 1.5); '
                b'$key[1][1]->count = 9; $key[1][3]->tag = "changed"; '
                b'echo "|", (int)($key[1][2]->count === 9 && '
                b'$objectAlias->tag === "changed"); '
                b'$objectAlias = new stdClass; $objectAlias->count = 11; '
                b'$objectAlias->enabled = false; $objectAlias->tag = "new"; '
                b'$objectAlias->empty = null; $objectAlias->ratio = 2.5; '
                b'$objectWeakAfter = WeakReference::create($objectAlias); '
                b'echo "|", (int)($objectWeak->get() === $key[1][3] && '
                b'$key[1][3] !== $objectAlias && $key[1][3]->count === 9 && '
                b'$key[1][3]->tag === "changed"), "|", '
                b'(int)($key[1][1] === $objectAlias && $key[1][2] === $objectAlias && '
                b'$objectAlias->count === 11 && $objectAlias->enabled === false && '
                b'$objectAlias->tag === "new" && $objectAlias->empty === null && '
                b'$objectAlias->ratio === 2.5), "|B"; '
                b'unset($key); echo "|", (int)isset($key), "|", '
                b'(int)($objectWeak->get() === null), "|", '
                b'(int)($objectWeakAfter->get() === $objectAlias), "|R"; '
                b'unset($objectAlias); echo "|", (int)($objectWeakAfter->get() === null), '
                b'"|", (int)isset($objectAlias);')
    source = source[:at] + observer + b'\n'
    name = old.replace('empty-array-post', 'object-scalar-fields-post')
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
    'tests/semantics/string_offset_nested_unset_bool_cv_object_scalar_fields_post_sources.py',
    'spec/semantics/130-stdclass-runtime.watsup',
    'spec/semantics/136-property-runtime.watsup',
    'spec/semantics/270-eager-destructors.watsup',
    'spec/semantics/296-weak-references.watsup',
    'vendor/php-src/Zend/zend_object_handlers.c',
    'vendor/php-src/Zend/zend_objects.c',
    'vendor/php-src/Zend/zend_objects_API.c',
    'vendor/php-src/Zend/zend_weakrefs.c',
)
