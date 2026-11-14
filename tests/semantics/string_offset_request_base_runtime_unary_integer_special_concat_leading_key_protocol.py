#!/usr/bin/env python3
"""Runtime signs preserve typed values and actual Warning/owner histories."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_unary_integer_special_concat_leading_key_cases as cases
import string_offset_request_base_float_boolnot_special_concat_leading_key_protocol as prior

runner = prior.runner
BITS = (0, 9223372036854775808, 9218868437227405312, 0)
RESULTS = ('1', '$(-1)', '0', '$(-1)')


def authority(index):
    truth = index == 2
    child = 'PBOOL ' + str(not truth).lower()
    unary = 'POSITIVE' if index in (0, 2) else 'NEGATIVE'
    result = 'PINT ' + RESULTS[index]
    checks = [
        '$origin_child((porigin_key), [PCFIELD 0]) = (porigin_runtime_concat)',
        '$origin_node(S.SOURCES, porigin_runtime_concat) = (expression_1)',
        'expression_1 = NExprBinaryOpConcat expression_runtime_left expression_runtime_right metadata_runtime_concat',
        '$origin_child((porigin_runtime_concat), [PCFIELD 0]) = (porigin_runtime_left)',
        '$origin_child((porigin_runtime_concat), [PCFIELD 1]) = (porigin_runtime_right)',
        '$origin_node(S.SOURCES, porigin_runtime_left) = (expression_runtime_left)',
        '$origin_node(S.SOURCES, porigin_runtime_right) = (expression_runtime_right)',
        r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    if index < 3:
        other = 'PNULL' if index == 0 else 'PBOOL false'
        checks += ['porigin_runtime_unary = porigin_runtime_left',
                   '$compiled_read(S, porigin_runtime_right) = (' + other + ')',
                   '$compiled_precision(S, (porigin_runtime_right)) = (14)',
                   '$compiled_special_concat_bytes(S, porigin_runtime_right) = (eps)',
                   '$string_read_runtime_bytes(S, porigin_runtime_right) = (eps)']
    else:
        checks += ['porigin_runtime_outer_not = porigin_runtime_right',
                   '$origin_node(S.SOURCES, porigin_runtime_outer_not) = (NExprBooleanNot expression_runtime_unary metadata_runtime_outer_not)',
                   '$origin_child((porigin_runtime_outer_not), [PCFIELD 0]) = (porigin_runtime_unary)',
                   '$compiled_read(S, porigin_runtime_left) = (PSTRING ($ptascii("-4")))',
                   '$compiled_precision(S, (porigin_runtime_left)) = (14)',
                   '$string_read_runtime_bytes(S, porigin_runtime_left) = ($ptascii("-4"))',
                   '$truth_value(S, ' + result + ', 5) = S[.RESULT = KNOWN (PBOOL true)]',
                   '$string_read_runtime_value(S, porigin_runtime_outer_not) = (PBOOL false)',
                   '$string_read_runtime_bytes(S, porigin_runtime_outer_not) = (eps)']
    checks += ['$origin_node(S.SOURCES, porigin_runtime_unary) = (expression_runtime_unary)',
               '$pfshape(expression_runtime_unary) = PFUNARY ' + unary + ' expression_runtime_not',
               '$origin_child((porigin_runtime_unary), [PCFIELD 0]) = (porigin_runtime_not)',
               '$origin_node(S.SOURCES, porigin_runtime_not) = (NExprBooleanNot expression_runtime_float metadata_runtime_not)',
               'expression_runtime_not = NExprBooleanNot expression_runtime_float metadata_runtime_not',
               '$origin_child((porigin_runtime_not), [PCFIELD 0]) = (porigin_runtime_float)',
               '$origin_node(S.SOURCES, porigin_runtime_float) = (expression_runtime_float)',
               '$compiled_read(S, porigin_runtime_float) = (PFLOAT ' + str(BITS[index]) + ')',
               '$compiled_identity_value(S, porigin_runtime_float) = (PFLOAT ' + str(BITS[index]) + ')',
               '$compiled_precision(S, (porigin_runtime_float)) = (14)',
               '$number_bool(NFLOAT ' + str(BITS[index]) + ') = (' + str(truth).lower() + ', false)',
               '$truth_value(S, PFLOAT ' + str(BITS[index]) + ', 5) = S[.RESULT = KNOWN (PBOOL ' + str(truth).lower() + ')]',
               '$string_read_runtime_value(S, porigin_runtime_float) = (PFLOAT ' + str(BITS[index]) + ')',
               '$string_read_runtime_value(S, porigin_runtime_not) = (' + child + ')',
               '$coerce_number(' + child + ') = COERCED (NINT ' + ('0' if truth else '1') + ') false',
               '$unary_apply(S, ' + unary + ', ' + child + ', 5) = S[.RESULT = KNOWN (' + result + ')]',
               '$string_read_runtime_value(S, porigin_runtime_unary) = (' + result + ')',
               '$string_read_runtime_bytes(S, porigin_runtime_unary) = ($echo_value(' + result + '))']
    for tag in ('key', 'runtime_concat', 'runtime_unary', 'runtime_not') + (('runtime_outer_not',) if index == 3 else ()):
        checks += ['porigin_' + tag + ' = PORIGIN n_runtime_unit pcpath_' + tag,
                   '$code_at(S.CODE, n_runtime_unit) = (pcode_runtime)',
                   '$code_expression(pcode_runtime.EXPRESSIONS, pcpath_' + tag + ') = ((5, false))',
                   '$compiled_read(S, porigin_' + tag + ') = eps',
                   '$compiled_precision(S, (porigin_' + tag + ')) = (14)',
                   '$compiled_special_concat_bytes(S, porigin_' + tag + ') = eps']
    leaf = prior.authority(index if index < 3 else 0)
    first = next(i for i, check in enumerate(leaf) if check.startswith('expression_float_child = '))
    checks += [check.replace('expression_float_child', 'expression_runtime_float')
                    .replace('porigin_float_child', 'porigin_runtime_float') for check in leaf[first:]]
    checks += ['$string_read_runtime_bytes(S, porigin_key) = ($ptascii(' + json.dumps(prior.KEYS[index]) + '))']
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
    report['scope'] = 'Four source-reached runtime POSITIVE/NEGATIVE expressions over typed Boolean NOT results retain genuine quiet PFLOAT leaves, false CODE/read-eps/source/equal captured precision and quiet NINT/full-state fitting PINT results. Outer NOT consumes the real integer. Decimal PINT BYTE and actual REQUEST CONCAT carriers preserve returning/negative/supplied-throw/bounds owners, cleanup and budgets; source0 fixtures reuse native originals once. No compiler, FLOAT formatting, carrier relabeling or ownership changes.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
