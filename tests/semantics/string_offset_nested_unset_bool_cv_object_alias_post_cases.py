"""A real object alias outlives its containing post-Warning array."""
import string_offset_nested_unset_bool_cv_empty_array_post_cases as prior

CASES, OUTPUTS, FACTS, RETAINED_OUTPUTS = {}, {}, {}, {}
for old, original in prior.CASES.items():
    source = original.replace(b'EmptyArrayPost', b'ObjectAliasPost')
    setup = (b'$obj = new stdClass; $GLOBALS["objectAlias"] = $obj; '
             b'$GLOBALS["objectWeak"] = WeakReference::create($obj); unset($obj); '
             b'$GLOBALS["key"] = [7, [8, &$GLOBALS["objectAlias"], &$GLOBALS["objectAlias"]]];')
    assert source.count(b'$GLOBALS["key"] = [];') == source.count(b'$last = 0;') == 1
    source = source.replace(b'$GLOBALS["key"] = [];', setup)
    source = source.replace(b'$last = 0;',
                            b'$last = 0; $objectAlias = null; $objectWeak = null;')
    at = source.index(b'echo "|", (int)($key')
    observer = (b'echo "|", (int)($key[0] === 7), "|", (int)($key[1][0] === 8), '
                b'"|", (int)($objectWeak->get() === $objectAlias && '
                b'$key[1][1] === $objectAlias && $key[1][2] === $objectAlias); '
                b'$objectAlias = new stdClass; $objectWeakAfter = WeakReference::create($objectAlias); '
                b'echo "|", (int)($objectWeak->get() === null), "|", '
                b'(int)($key[1][1] === $objectAlias && $key[1][2] === $objectAlias); '
                b'unset($key); echo "|", (int)isset($key), "|", '
                b'(int)($objectWeakAfter->get() === $objectAlias), "|R"; '
                b'unset($objectAlias); echo "|", (int)($objectWeakAfter->get() === null), '
                b'"|", (int)isset($objectAlias);')
    source = source[:at] + observer + b'\n'
    name = old.replace('empty-array-post', 'object-alias-post')
    assert prior.OUTPUTS[old].endswith(b'|1')
    prefix = prior.OUTPUTS[old][:-2]
    retained = prefix + b'|1|1|1|1|1|0|1|R'
    CASES[name], OUTPUTS[name] = source, retained + b'|1|0'
    RETAINED_OUTPUTS[name] = retained
    FACTS[name] = {**prior.FACTS[old], 'mixed': False}


def stderr(name, path):
    return b''


WATCHED = prior.WATCHED + (
    'tests/semantics/string_offset_nested_unset_bool_cv_empty_array_post_cases.py',
    'tests/semantics/string_offset_nested_unset_bool_cv_empty_array_post_sources.py',
    'tests/semantics/string_offset_nested_unset_bool_cv_object_alias_post_sources.py',
    'spec/semantics/296-weak-references.watsup',
    'vendor/php-src/Zend/zend_weakrefs.c',
)
