#!/usr/bin/env python3
"""Runtime empty CONCAT preserves exact typed headers under actual const facts."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_empty_string_concat_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_one_byte_string_bitwise_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
EMPTY = ('CAST', 'CASTSTRING', prior.prior.FALSE, 'PSTRING_CARRIER INTERNED_STRING eps')
TREES = (
    ('CAST', 'CASTINT', ('IDENTICAL', ('STRING_CONCAT', EMPTY, prior.selected('1'), [49]), ('STRING', '1', None), True), 'PINT 1'),
    ('BITNOT', ('CAST', 'CASTINT', ('STRING_CONCAT', ('STRING', '0', None), EMPTY, [48]), 'PINT 0'), -1),
    ('CAST', 'CASTINT', ('STRING_CONCAT', EMPTY, EMPTY, []), 'PINT 0'),
    ('BITNOT', ('CAST', 'CASTINT', ('STRING_CONCAT', ('STRING_CONCAT', prior.selected('003'), EMPTY, [48, 48, 51]), EMPTY, [48, 48, 51]), 'PINT 3'), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    if tree[0] != 'STRING_CONCAT':
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    integers.emitted(checks, tag)
    checks += ['$pfshape(' + expression + ') = PFBINARY CONCAT ' + expression + '_0 ' + expression + '_1',
               'S.COMPLETION = NORMAL', 'S.CONSTCONTEXT = eps']
    values, flags = [], []
    for index, child in enumerate(tree[1:3]):
        child_tag = tag + '_' + str(index)
        child_origin, flag = 'porigin_' + child_tag, 'b_concat_' + child_tag
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(index) + ']) = (' + child_origin + ')']
        child_value = value(checks, child_tag, child)[0]
        checks += [flag + ' = $concat_constant(S, (' + child_origin + '))',
                   '$concat_operand(S, KNOWN (' + child_value + '), ' + flag + ', 5) = (S, KNOWN (' + child_value + '))',
                   '$stringify(S, ' + child_value + ', 5) = S[.RESULT = KNOWN (' + child_value + ')]']
        values.append(child_value)
        flags.append(flag)
    payload = str(tree[-1])
    result = 'PSTRING_CARRIER INTERNED_STRING (' + payload + ')'
    checks += ['$string_concat(S, ' + ', '.join([*values, *flags]) + ') = S[.RESULT = KNOWN (' + result + ')]',
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
    report['scope'] = 'Four emitted CONCAT trees reuse canonical nonNUL INTERNED STRING headers under NORMAL and empty CONSTCONTEXT, exact own/child source/CODEfalse/read-eps/positive-line/equal captured precision, recursive typed STRING values, actual concat_constant facts and unchanged full-state string_concat. Runtime empty-left, empty-right, both-empty and nested multi-byte003 survivor results remain typed under explicit INT/strict identity consumers, preserving real REQUEST keys1/-1/0/-4 and existing Warning/Throwable/bounds/ownership/cleanup/budget histories. Constant-empty allocation routes, both-nonempty, raw/REQUEST/NUL, deferred constant contexts and wider lifetimes remain outside. No binary_apply unknown identity, compiler/formatter/owner or held-boundary change; native originals reused once and fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
