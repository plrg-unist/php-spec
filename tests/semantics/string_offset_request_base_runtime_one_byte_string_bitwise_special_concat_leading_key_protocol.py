#!/usr/bin/env python3
"""One-byte string bitwise operations preserve typed carriers and complete state."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_one_byte_string_bitwise_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_interned_string_cast_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
TRUTH = prior.TRUTH


def selected(text):
    return 'TERNARY', TRUTH, ('STRING', text, None), True


TREES = (
    ('CAST', 'CASTINT', ('IDENTICAL', ('STRING_BINARY', 'BITAND', selected('1'), ('STRING', '3', None), [49]), ('STRING', '1', None), True), 'PINT 1'),
    ('BITNOT', ('CAST', 'CASTINT', ('STRING_BINARY', 'BITOR', selected('0'), ('STRING', '0', None), [48]), 'PINT 0'), -1),
    ('CAST', 'CASTINT', ('STRING_NOT', selected('1'), [206]), 'PINT 0'),
    ('BITNOT', ('CAST', 'CASTINT', ('STRING_BINARY', 'BITXOR', selected('p'), ('STRING', 'C', None), [51]), 'PINT 3'), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    kind = tree[0]
    if kind not in ('STRING_BINARY', 'STRING_NOT'):
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    integers.emitted(checks, tag)
    binary = kind == 'STRING_BINARY'
    children = tree[2:4] if binary else tree[1:2]
    shape = 'PFBINARY ' + tree[1] if binary else 'PFBITNOT'
    checks += ['$pfshape(' + expression + ') = ' + shape + ' ' + ' '.join(expression + '_' + str(i) for i in range(len(children))),
               'S.COMPLETION = NORMAL']
    values = []
    for index, child in enumerate(children):
        child_tag = tag + '_' + str(index)
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(index) + ']) = (porigin_' + child_tag + ')']
        child_value = value(checks, child_tag, child)[0]
        checks += ['$string_bytes(' + child_value + ') = ([n_byte_' + child_tag + '])']
        values.append(child_value)
    payload = str(tree[-1])
    result = 'PSTRING_CARRIER INTERNED_STRING (' + payload + ')'
    operation = ('$binary_apply(S, ' + tree[1] + ', ' + ', '.join(values) + ', 5)' if binary else
                 '$bitnot_value(S, ' + values[0] + ', 5)')
    checks += [operation + ' = S[.RESULT = KNOWN (' + result + ')]',
               '$startup_bytes(' + payload + ')', '$c_string(' + payload + ') = ' + payload,
               '$string_read_runtime_value(S, ' + origin + ') = (' + result + ')',
               '$string_read_runtime_bytes(S, ' + origin + ') = (' + payload + ')']
    return result, None


module = prior
while module is not integers:
    module.value = value
    module = module.prior
integers.value, integers.TREES = value, TREES
conditions = prior.conditions


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = {Path(module.__file__).resolve() for module in tuple(sys.modules.values())
               if getattr(module, '__file__', None)
               and Path(module.__file__).resolve().parent == Path(__file__).resolve().parent}
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.OUTPUTS, runner.conditions = cases, tuple(cases.OUTPUTS.values()), conditions
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four emitted STRING BITAND/BITOR/BITXOR and BITNOT trees consume certified one-byte nonNUL INTERNED values through existing NORMAL/source/CODEfalse/read-eps/positive-line/equal captured precision and exact whole-state binary_apply or bitnot_value. The existing one-character fast paths retain actual INTERNED results without REQUEST allocation; strict identity distinguishes AND STRING1 from PINT1, while NOT produces byte206 before quiet explicit INT0. Exact INT1/STRING0/INT0/INT3 parents preserve real REQUEST keys1/-1/0/-4, Warning/Throwable/bounds, ownership, cleanup and budget rejoining. NUL results, empty/multibyte/raw/REQUEST inputs, mixed dispatch, formatter/compiler/owner bodies and exact holds gain no authority. Native originals reused once and fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
