"""Owning array aliases retain a child after its containing key retires."""
import string_offset_nested_unset_bool_cv_deep_array_post_cases as prior

CASES, OUTPUTS, FACTS, RETAINED_OUTPUTS = {}, {}, {}, {}
for old, original in prior.CASES.items():
    facts = prior.FACTS[old]
    source = original.replace(b'DeepArrayPost', b'ArrayAliasPost')
    start = source.index(b'$grand = ')
    marker = b'unset($grand, $middle);'
    end = source.index(marker, start) + len(marker)
    value = b'[$nine, &$GLOBALS["arrayAlias"], $obj, $text]' if facts['mixed'] else b'[$nine]'
    setup = (b'$nine = 9; $GLOBALS["arrayOwnerAlias"] = ' + value + b'; unset($nine); '
             b'$middle = [8, &$GLOBALS["arrayOwnerAlias"], &$GLOBALS["arrayOwnerAlias"]]; '
             b'$GLOBALS["key"] = [7, $middle]; unset($middle);')
    source = source[:start] + setup + source[end:]
    assert source.count(b'$last = 0;') == 1
    source = source.replace(b'$last = 0;', b'$last = 0; $arrayOwnerAlias = null;')
    start = source.index(b'echo "|", (int)($key')
    observer = (b'echo "|", (int)($key === [7, [8, [9], [9]]]), "|", '
                b'(int)($arrayOwnerAlias[0] === 9); $arrayOwnerAlias[0] = 11; '
                b'echo "|", (int)($key[1][1][0] === 11 && $key[1][2][0] === 11); '
                b'unset($key); echo "|", (int)isset($key), "|", '
                b'(int)($arrayOwnerAlias[0] === 11), "|R"; unset($arrayOwnerAlias); '
                b'echo "|", (int)isset($arrayOwnerAlias);')
    old_output = b'|1|0'
    retained = b'|1|1|1|0|1|R'
    output = retained + b'|0'
    if facts['mixed']:
        observer = (b'echo "|", (int)($key[0] === 7), "|", (int)($key[1][0] === 8), '
                    b'"|", (int)($key[1][1][0] === 9 && $key[1][2][0] === 9), '
                    b'"|", (int)($key[1][1][1] === 9), '
                    b'"|", (int)($arrayWeak->get() === $key[1][1][2]), '
                    b'"|", (int)($key[1][2][3] === "req-text"); $arrayAlias = 11; '
                    b'echo "|", (int)($key[1][1][1] === 11 && $key[1][2][1] === 11); '
                    b'unset($key); echo "|", (int)($arrayWeak->get() === $arrayOwnerAlias[2]), '
                    b'"|", (int)($arrayOwnerAlias[1] === 11), "|R"; '
                    b'unset($arrayOwnerAlias); '
                    b'echo "|", (int)($arrayWeak->get() === null), "|", $arrayAlias;')
        old_output = b'|1|1|1|1|1|1|1|1|11'
        retained = b'|1' * 9 + b'|R'
        output = retained + b'|1|11'
    source = source[:start] + observer + b'\n'
    name = old.replace('deep-array-post', 'array-alias-post')
    assert prior.OUTPUTS[old].endswith(old_output)
    prefix = prior.OUTPUTS[old][:-len(old_output)]
    CASES[name], OUTPUTS[name] = source, prefix + output
    FACTS[name] = dict(facts)
    RETAINED_OUTPUTS[name] = prefix + retained


def stderr(name, path):
    return b''


WATCHED = prior.WATCHED + (
    'tests/semantics/string_offset_nested_unset_bool_cv_deep_array_post_cases.py',
    'tests/semantics/string_offset_nested_unset_bool_cv_array_alias_post_sources.py',
)
