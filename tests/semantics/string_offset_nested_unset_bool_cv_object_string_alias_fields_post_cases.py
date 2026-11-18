"""Non-NUL STRING cells remain shared by two ordinary stdClass fields."""
import string_offset_nested_unset_bool_cv_object_primitive_alias_fields_post_cases as prior

CASES, OUTPUTS, FACTS, REBOUND_OUTPUTS, RETAINED_OUTPUTS = {}, {}, {}, {}, {}
for index, (old, original) in enumerate(prior.CASES.items()):
    source = original.replace(b'ObjectPrimitiveAliasFieldsPost', b'ObjectStringAliasFieldsPost')
    initial = (b'$suffix = "d"; $fieldValue = "ol" . $suffix;' if index else
               b'$fieldValue = "old";')
    assert source.count(b'$fieldValue = 7;') == 1
    source = source.replace(b'$fieldValue = 7;', initial)
    at = source.index(b'echo "|", (int)($key')
    observer = (b'echo "|", (int)($objectAlias->mirror === "old" && $fieldValue === "old"); '
                b'$key[1][1]->count = "field"; '
                b'echo "|", (int)($fieldValue === "field" && $key[1][2]->mirror === "field"); '
                b'$objectAlias = new stdClass; $objectWeakAfter = WeakReference::create($objectAlias); '
                b'$suffix = "r"; $fieldValue = "late" . $suffix; '
                b'echo "|", (int)($objectWeak->get() === $key[1][3] && '
                b'$key[1][3]->count === "later" && $key[1][3]->mirror === "later"); unset($fieldValue); '
                b'echo "|", (int)(!isset($fieldValue) && $key[1][3]->mirror === "later" && '
                b'$key[1][1] === $objectAlias && $key[1][2] === $objectAlias), "|B"; '
                b'unset($key); echo "|", (int)isset($key), "|", (int)($objectWeak->get() === null), "|", '
                b'(int)($objectWeakAfter->get() === $objectAlias), "|R"; '
                b'unset($objectAlias); echo "|", (int)($objectWeakAfter->get() === null), '
                b'"|", (int)isset($objectAlias);')
    source = source[:at] + observer + b'\n'
    kind = 'request' if index else 'interned'
    name = old.replace('object-primitive-alias-fields-post', 'object-string-alias-fields-post-' + kind)
    suffix = b'|1' * 7 + b'|B'
    assert prior.REBOUND_OUTPUTS[old].endswith(suffix)
    rebound = prior.REBOUND_OUTPUTS[old][:-len(suffix)] + b'|1' * 4 + b'|B'
    retained = rebound + b'|0|1|1|R'
    CASES[name], OUTPUTS[name] = source, retained + b'|1|0'
    REBOUND_OUTPUTS[name], RETAINED_OUTPUTS[name] = rebound, retained
    FACTS[name] = {**prior.FACTS[old], 'requested': bool(index)}


def stderr(name, path):
    return b''


WATCHED = prior.WATCHED + (
    'tests/semantics/string_offset_nested_unset_bool_cv_object_primitive_alias_fields_post_cases.py',
    'tests/semantics/string_offset_nested_unset_bool_cv_object_string_alias_fields_post_sources.py',
    'spec/semantics/425-string-offset-read-continuations.watsup',
)
