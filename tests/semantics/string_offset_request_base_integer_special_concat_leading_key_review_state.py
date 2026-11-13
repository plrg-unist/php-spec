#!/usr/bin/env python3
"""Integer/special CONCAT source states and the affected float-only exclusion."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_integer_special_concat_leading_key_cases as cases
import string_offset_request_base_special_concat_leading_key_review_state as runner

base_conditions = runner.conditions


def conditions(program, path, index):
    checks, derived = base_conditions(program, path, index)
    integer = 3 if index == 2 else 1
    old_value = ('PBOOL true', 'PNULL', 'PBOOL false')[index]
    new_value = 'PBOOL false' if index == 1 else 'PNULL'
    old = '$compiled_read(S, porigin_special) = (' + old_value + ')'
    assert checks.count(old) == 1
    checks[checks.index(old)] = '$compiled_read(S, porigin_special) = (' + new_value + ')'
    if index == 0:
        old = '$origin_child((porigin_key), [PCFIELD 0]) = (porigin_special)'
        checks[checks.index(old)] = '$origin_child((porigin_key), [PCFIELD 0, PCFIELD 1]) = (porigin_special)'
        old = 'expression_1 = NExprConstFetch name metadata_special'
        at = checks.index(old)
        checks[at:at + 1] = runner.lines(r'''
expression_1 = NExprBinaryOpConcat expression_11 expression_12 metadata_inner
expression_11 = NScalarInt (INTEGER 1) metadata_integer
expression_12 = NExprConstFetch name metadata_special
$origin_child((porigin_key), [PCFIELD 0]) = (porigin_inner)
$compiled_read(S, porigin_inner) = (PSTRING ($ptascii("1")))
''')
        old = 'S_wrong_child = S_after[.POOLS = $special_review_pools(S_after.POOLS, porigin_special, (PBOOL false))]'
        checks[checks.index(old)] = old.replace('(PBOOL false)', '(PBOOL true)')
        extra = runner.lines(r'''
S_drop_inner = S_after[.POOLS = $special_review_pools(S_after.POOLS, porigin_inner, eps)]
$compiled_read(S_drop_inner, porigin_inner) = eps
$compiled_special_concat_bytes(S_drop_inner, porigin_key) = eps
$string_read_request_base_saved(S_drop_inner, pstringread) = eps
''')
        checks += extra
        derived += len(extra)
    else:
        old = 'expression_11 = NScalarString (BYTES text_prefix) metadata_prefix'
        checks[checks.index(old)] = 'expression_11 = NScalarInt (INTEGER ' + str(integer) + ') metadata_integer'
        checks = [check for check in checks if not check.startswith('$base64(text_prefix) =')]
    at = checks.index('$parser_literal_at(NExprConstFetch name metadata_special, 14) = eps') + 1
    checks[at:at] = [
        '$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_integer)',
        '$origin_node(S.SOURCES, porigin_integer) = (NScalarInt (INTEGER ' + str(integer) + ') metadata_integer)',
        '$compiled_read(S, porigin_integer) = (PINT ' + str(integer) + ')',
        '$parser_literal_at(NScalarInt (INTEGER ' + str(integer) + ') metadata_integer, 14) = (PINT ' + str(integer) + ')',
        '$compiled_special_concat_bytes(S, porigin_integer) = ($ptascii("' + str(integer) + '"))']
    return checks, derived


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    own_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    runner.cases = cases
    runner.conditions = conditions
    runner.CONTROLS = {'mixed-float-special': runner.CONTROLS['mixed-float-special']}
    passed = runner.main()
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest() == own_hash
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'][str(Path(__file__).resolve())] = own_hash
    report['scope'] = 'Three fresh integer/special source-state fixtures and only the affected fresh float compiler exclusion; prior special383/compiler44 and source/native campaigns retain their original cuts without replay.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
