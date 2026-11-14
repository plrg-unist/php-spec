#!/usr/bin/env python3
"""Nested runtime NOT retains typed Boolean links and real key ownership."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_nested_float_boolnot_special_concat_leading_key_cases as cases
import string_offset_request_base_float_boolnot_special_concat_leading_key_protocol as prior

runner = prior.runner
LEVELS = (2, 2, 3, 3)


def authority(index):
    bits, truth, levels = prior.BITS[index], index >= 2, LEVELS[index]
    checks = [
        '$origin_child((porigin_key), [PCFIELD 0]) = (porigin_float_concat)',
        '$origin_node(S.SOURCES, porigin_float_concat) = (expression_1)',
        'expression_1 = NExprBinaryOpConcat expression_prefix expression_nested_not metadata_float_concat',
        '$origin_child((porigin_float_concat), [PCFIELD 0]) = (porigin_float_prefix)',
        '$origin_child((porigin_float_concat), [PCFIELD 1]) = (porigin_nested_not)',
        '$origin_node(S.SOURCES, porigin_float_prefix) = (expression_prefix)',
        'porigin_nested_not = porigin_nested_not_0',
        '$origin_node(S.SOURCES, porigin_nested_not) = (expression_nested_not)',
        r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    for tag in ('key', 'float_concat'):
        checks += ['porigin_' + tag + ' = PORIGIN n_runtime_unit pcpath_runtime_' + tag,
                   '$code_at(S.CODE, n_runtime_unit) = (pcode_runtime)',
                   '$code_expression(pcode_runtime.EXPRESSIONS, pcpath_runtime_' + tag + ') = ((5, false))',
                   '$compiled_read(S, porigin_' + tag + ') = eps',
                   '$compiled_precision(S, (porigin_' + tag + ')) = (14)',
                   '$compiled_special_concat_bytes(S, porigin_' + tag + ') = eps']
    for depth in range(levels):
        origin = 'porigin_nested_not_' + str(depth)
        child = 'porigin_nested_float' if depth + 1 == levels else 'porigin_nested_not_' + str(depth + 1)
        result = truth != ((levels - depth) % 2 == 1)
        child_value = 'PFLOAT ' + str(bits) if depth + 1 == levels else 'PBOOL ' + str(not result).lower()
        checks += [origin + ' = PORIGIN n_runtime_unit pcpath_nested_not_' + str(depth),
                   '$origin_node(S.SOURCES, ' + origin + ') = (NExprBooleanNot expression_nested_child_' + str(depth) + ' metadata_nested_' + str(depth) + ')',
                   '$origin_child((' + origin + '), [PCFIELD 0]) = (' + child + ')',
                   '$origin_node(S.SOURCES, ' + child + ') = (expression_nested_child_' + str(depth) + ')',
                   '$code_expression(pcode_runtime.EXPRESSIONS, pcpath_nested_not_' + str(depth) + ') = ((5, false))',
                   '$compiled_read(S, ' + origin + ') = eps',
                   '$compiled_precision(S, (' + origin + ')) = (14)',
                   '$compiled_special_concat_bytes(S, ' + origin + ') = eps',
                   '$string_read_runtime_value(S, ' + child + ') = (' + child_value + ')',
                   '$truth_value(S, ' + child_value + ', 5) = S[.RESULT = KNOWN (PBOOL ' + str(not result).lower() + ')]',
                   '$string_read_runtime_value(S, ' + origin + ') = (PBOOL ' + str(result).lower() + ')',
                   '$string_read_runtime_bytes(S, ' + origin + ') = ($echo_value(PBOOL ' + str(result).lower() + '))']
    checks += ['porigin_nested_float_not = porigin_nested_not_' + str(levels - 1),
               '$compiled_read(S, porigin_nested_float) = (PFLOAT ' + str(bits) + ')',
               '$compiled_identity_value(S, porigin_nested_float) = (PFLOAT ' + str(bits) + ')',
               '$compiled_precision(S, (porigin_nested_float)) = (14)',
               '$number_bool(NFLOAT ' + str(bits) + ') = (' + str(truth).lower() + ', false)',
               '$string_read_runtime_value(S, porigin_nested_float) = (PFLOAT ' + str(bits) + ')',
               '$string_read_runtime_bytes(S, porigin_key) = ($ptascii(' + json.dumps(prior.KEYS[index]) + '))',
               '$origin_node(S.SOURCES, porigin_nested_float) = (expression_nested_float)']
    leaf = prior.authority(index)
    first = next(i for i, check in enumerate(leaf) if check.startswith('expression_float_child = '))
    checks += [check.replace('expression_float_child', 'expression_nested_float')
                    .replace('porigin_float_child', 'porigin_nested_float') for check in leaf[first:]]
    return checks


def conditions(program, path, index):
    checks, derived = prior.conditions(program, path, index)
    old = prior.authority(index)
    at = checks.index(old[0])
    assert checks[at:at + len(old)] == old
    checks[at:at + len(old)] = authority(index)
    return checks, derived


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
    report['scope'] = 'Four original-source nested2/nested3 NOT fixtures retain typed quiet PFLOAT leaves and real PBOOL links, actual false descriptors/read-eps/source/precision and full-state truth. Every innermost single NOT keeps its prior byte result; CONCAT preserves the actual REQUEST key and existing returning/negative/supplied-throw/bounds owner and budget histories. No compiler BOOL/BYTE or carrier relabeling is introduced; source0 fixtures reuse native originals once.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
