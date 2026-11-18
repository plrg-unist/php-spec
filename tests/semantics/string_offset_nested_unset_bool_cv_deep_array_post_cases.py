"""Deep postarrays with a shared grandchild retain real leaf ownership."""
import string_offset_nested_unset_bool_cv_nonempty_array_post_cases as prior

CASES, OUTPUTS, FACTS = {}, {}, {}
for old, original in prior.CASES.items():
    facts = prior.FACTS[old]
    source = original.replace(b'NonemptyArrayPost', b'DeepArrayPost')
    setup = (b'$grand = [9]; $middle = [8, $grand, $grand]; '
             b'$GLOBALS["key"] = [7, $middle]; unset($grand, $middle);')
    observer = (b'echo "|", (int)($key === [7, [8, [9], [9]]]); '
                b'unset($key); echo "|", (int)isset($key);')
    output = b'|1|0'
    if facts['mixed']:
        old_setup = (b'$GLOBALS["key"] = [7, [8], &$GLOBALS["arrayAlias"], $obj, $text]; ')
        setup = (b'$grand = [9, &$GLOBALS["arrayAlias"], $obj, $text]; '
                 b'$middle = [8, $grand, $grand]; $GLOBALS["key"] = [7, $middle]; '
                 b'unset($grand, $middle); ')
        old_observer = (b'echo "|", (int)($key[0] === 7), "|", (int)($key[1][0] === 8), '
                        b'"|", (int)($key[2] === 9), "|", (int)($arrayWeak->get() === $key[3]), '
                        b'"|", (int)($key[4] === "req-text"); $arrayAlias = 11; '
                        b'echo "|", (int)($key[2] === 11); unset($key); '
                        b'echo "|", (int)($arrayWeak->get() === null), "|", $arrayAlias;')
        observer = (b'echo "|", (int)($key[0] === 7), "|", (int)($key[1][0] === 8), '
                    b'"|", (int)($key[1][1][0] === 9 && $key[1][2][0] === 9), '
                    b'"|", (int)($key[1][1][1] === 9), '
                    b'"|", (int)($arrayWeak->get() === $key[1][1][2]), '
                    b'"|", (int)($key[1][2][3] === "req-text"); $arrayAlias = 11; '
                    b'echo "|", (int)($key[1][1][1] === 11 && $key[1][2][1] === 11); '
                    b'unset($key); echo "|", (int)($arrayWeak->get() === null), "|", $arrayAlias;')
        old_output = b'|1|1|1|1|1|1|1|11'
        output = b'|1|1|1|1|1|1|1|1|11'
    else:
        old_setup = b'$GLOBALS["key"] = [7];'
        old_observer = b'echo "|", (int)($key === [7]); unset($key); echo "|", (int)isset($key);'
        old_output = b'|1|0'
    assert source.count(old_setup) == source.count(old_observer) == 1
    source = source.replace(old_setup, setup).replace(old_observer, observer)
    name = old.replace('nonempty-array-post', 'deep-array-post')
    assert prior.OUTPUTS[old].endswith(old_output)
    CASES[name] = source
    OUTPUTS[name] = prior.OUTPUTS[old][:-len(old_output)] + output
    FACTS[name] = dict(facts)


def stderr(name, path):
    return b''


WATCHED = prior.WATCHED + (
    'tests/semantics/string_offset_nested_unset_bool_cv_nonempty_array_post_cases.py',
    'tests/semantics/string_offset_nested_unset_bool_cv_deep_array_post_sources.py',
)
