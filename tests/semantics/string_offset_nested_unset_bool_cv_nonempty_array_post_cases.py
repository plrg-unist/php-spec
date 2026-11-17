"""Nonempty array postvalues retain real descendants in the saved ordinary CV."""
import string_offset_nested_unset_bool_cv_empty_array_post_cases as prior

CASES, OUTPUTS, FACTS = {}, {}, {}
for mixed in (False, True):
    for index, throwing in enumerate((False, True)):
        old = tuple(prior.CASES)[index]
        source = prior.CASES[old]
        kind = b'Mixed' if mixed else b'Scalar'
        source = source.replace(b'EmptyArrayPost', b'NonemptyArrayPost' + kind)
        setup = b'$GLOBALS["key"] = [7];'
        observer = b'echo "|", (int)($key === [7]); unset($key); echo "|", (int)isset($key);'
        output = b'|1|0'
        if mixed:
            setup = (b'$obj = new stdClass(); $GLOBALS["arrayWeak"] = WeakReference::create($obj); '
                     b'$textLeft = "req"; $textRight = "-text"; $text = $textLeft . $textRight; '
                     b'$GLOBALS["key"] = [7, [8], &$GLOBALS["arrayAlias"], $obj, $text]; '
                     b'unset($obj, $textLeft, $textRight, $text);')
            observer = (b'echo "|", (int)($key[0] === 7), "|", (int)($key[1][0] === 8), '
                        b'"|", (int)($key[2] === 9), "|", (int)($arrayWeak->get() === $key[3]), '
                        b'"|", (int)($key[4] === "req-text"); $arrayAlias = 11; '
                        b'echo "|", (int)($key[2] === 11); unset($key); '
                        b'echo "|", (int)($arrayWeak->get() === null), "|", $arrayAlias;')
            output = b'|1|1|1|1|1|1|1|11'
            assert source.count(b'$last = 0;') == 1
            source = source.replace(b'$last = 0;', b'$last = 0; $arrayAlias = 9;')
        assert source.count(b'$GLOBALS["key"] = [];') == 1
        source = source.replace(b'$GLOBALS["key"] = [];', setup)
        assert source.count(b'echo "|", (int)($key === []);') == 1
        source = source.replace(b'echo "|", (int)($key === []);', observer)
        tag = ('mixed-' if mixed else 'scalar-') + ('bool-first-throw' if throwing else 'null-return')
        name = 'nested-unset-bool-cv-nonempty-array-post-' + tag
        assert prior.OUTPUTS[old].endswith(b'|1')
        CASES[name], OUTPUTS[name] = source, prior.OUTPUTS[old][:-2] + output
        FACTS[name] = {'entry': '(PBOOL false)' if throwing else 'PNULL',
                       'throwing': throwing, 'mixed': mixed}


def stderr(name, path):
    return b''


WATCHED = prior.WATCHED + (
    'tests/semantics/string_offset_nested_unset_bool_cv_empty_array_post_cases.py',
    'tests/semantics/string_offset_nested_unset_bool_cv_empty_array_post_sources.py',
    'tests/semantics/string_offset_nested_unset_bool_cv_nonempty_array_post_sources.py',
    'spec/semantics/39-ownership.watsup',
)
