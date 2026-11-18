"""String aliases have live cells but their byte headers add no heap child."""
import string_offset_nested_unset_bool_cv_empty_array_post_cases as prior

CASES, OUTPUTS, FACTS, RETAINED_OUTPUTS = {}, {}, {}, {}
for requested in (False, True):
    for old, original in prior.CASES.items():
        facts = prior.FACTS[old]
        initial = b'req-text' if requested else b'' if facts['throwing'] else b'0'
        kind = b'Request' if requested else b'Interned'
        source = original.replace(b'EmptyArrayPost', b'StringAliasPost' + kind)
        setup = b'$GLOBALS["textAlias"] = "' + initial + b'"; '
        if requested:
            setup = (b'$textLeft = "req"; $textRight = "-text"; '
                     b'$GLOBALS["textAlias"] = $textLeft . $textRight; unset($textLeft, $textRight); ')
        setup += b'$GLOBALS["key"] = [7, [8, &$GLOBALS["textAlias"], &$GLOBALS["textAlias"]]];'
        assert source.count(b'$GLOBALS["key"] = [];') == source.count(b'$last = 0;') == 1
        source = source.replace(b'$GLOBALS["key"] = [];', setup)
        source = source.replace(b'$last = 0;', b'$last = 0; $textAlias = null;')
        at = source.index(b'echo "|", (int)($key')
        observer = (b'echo "|", (int)($key[0] === 7), "|", (int)($key[1][0] === 8), '
                    b'"|", (int)($key[1][1] === "' + initial + b'" && $key[1][2] === "' + initial + b'"); '
                    b'$afterLeft = "after"; $afterRight = "-text"; $textAlias = $afterLeft . $afterRight; '
                    b'unset($afterLeft, $afterRight); '
                    b'echo "|", (int)($key[1][1] === "after-text" && $key[1][2] === "after-text"); '
                    b'unset($key); echo "|", (int)isset($key), "|", (int)($textAlias === "after-text"), "|R"; '
                    b'unset($textAlias); echo "|", (int)isset($textAlias);')
        source = source[:at] + observer + b'\n'
        name = old.replace('empty-array-post', 'string-alias-post-' + ('request' if requested else 'interned'))
        assert prior.OUTPUTS[old].endswith(b'|1')
        prefix = prior.OUTPUTS[old][:-2]
        retained = prefix + b'|1|1|1|1|0|1|R'
        CASES[name], OUTPUTS[name] = source, retained + b'|0'
        RETAINED_OUTPUTS[name] = retained
        FACTS[name] = {**facts, 'requested': requested, 'initial': initial, 'mixed': False}


def stderr(name, path):
    return b''


WATCHED = prior.WATCHED + (
    'tests/semantics/string_offset_nested_unset_bool_cv_empty_array_post_cases.py',
    'tests/semantics/string_offset_nested_unset_bool_cv_empty_array_post_sources.py',
    'tests/semantics/string_offset_nested_unset_bool_cv_string_alias_post_sources.py',
    'spec/semantics/39-ownership.watsup',
)
