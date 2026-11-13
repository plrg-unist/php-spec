#!/usr/bin/env python3
"""Resolved integer ConstFetch CONCAT keys retain real Warning continuations."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_integer_const_special_concat_leading_key_cases as cases
import string_offset_request_base_integer_special_concat_leading_key_protocol as runner

base_conditions = runner.conditions
base_outputs = runner.OUTPUTS


def conditions(program, path, index):
    route = (0, 0, 1, 2)[index]
    checks, derived = base_conditions(program, path, route)
    old_integer, integer = (3 if route == 2 else 1), (1, 2, 1, 4)[index]
    old_key, key = str(old_integer) + 'x', str(integer) + 'x'
    replacements = {
        '"' + old_key + '"': '"' + key + '"',
        'STRING_LEADING ' + str(old_integer): 'STRING_LEADING ' + str(integer),
        'STRING_BOUNDS ' + str(old_integer): 'STRING_BOUNDS ' + str(integer),
        '"Uninitialized string offset ' + str(old_integer) + '"':
            '"Uninitialized string offset ' + str(integer) + '"',
        '$string_read_request_base_saved(S, pstringread) = (' + str(old_integer) + ')':
            '$string_read_request_base_saved(S, pstringread) = (' + str(integer) + ')',
        runner.prior.watbytes(('Illegal string offset "' + old_key + '"').encode()):
            runner.prior.watbytes(('Illegal string offset "' + key + '"').encode()),
        runner.prior.watbytes(('2|Illegal string offset "' + old_key + '"|5;').encode()):
            runner.prior.watbytes(('2|Illegal string offset "' + key + '"|5;').encode()),
        runner.prior.watbytes(base_outputs[route]): runner.prior.watbytes(cases.OUTPUTS[index])}
    if index == 1:
        replacements['$ptascii("b")'] = '$ptascii("c")'
    for old, new in replacements.items():
        checks = [check.replace(old, new) for check in checks]
    node = 'NExprConstFetch name_integer metadata_integer'
    checks = [check.replace('NScalarInt (INTEGER ' + str(old_integer) + ') metadata_integer', node)
              for check in checks]
    replacements = {
        '$compiled_read(S, porigin_integer) = (PINT ' + str(old_integer) + ')':
            '$compiled_read(S, porigin_integer) = (PINT ' + str(integer) + ')',
        '$compiled_special_concat_bytes(S, porigin_integer) = ($ptascii("' + str(old_integer) + '"))':
            '$compiled_special_concat_bytes(S, porigin_integer) = ($ptascii("' + str(integer) + '"))'}
    for old, new in replacements.items():
        assert checks.count(old) == 1, old
        checks[checks.index(old)] = new
    checks = [check.replace('$compiled_read(S, porigin_inner) = (PSTRING ($ptascii("' + str(old_integer) + '")))',
                            '$compiled_read(S, porigin_inner) = (PSTRING ($ptascii("' + str(integer) + '")))')
              for check in checks]
    qualifier = 'PTFULL' if index == 2 else 'PTPLAIN'
    spelling = ('E_ERROR', 'Leaf', 'E_ERROR', 'E_PARSE')[index]
    checks += [
        '$ptast(name_integer) = PTNAME ' + qualifier + ' ($ptascii("' + spelling + '"))',
        '$parser_literal_at(' + node + ', 14) = eps',
        '$compiled_precision(S, (porigin_integer)) = (14)',
        r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    return checks, derived


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(__file__), Path(runner.__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases = cases
    runner.OUTPUTS = cases.OUTPUTS
    runner.conditions = conditions
    passed = runner.main()
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four fresh direct compiler-proved PINT ConstFetch plus bool/null CONCAT source-state fixtures authenticate actual names/qualifiers, own facts and exact pools at compile14/live17. Existing borrowed-owner, fixed-index, supplied-throw, genuine later-bounds and budget laws remain. Module32 internal compiler-proof authority is unchanged; arbitrary forged pools are not validated. Older source/native/state/compiler cuts retain their identities without replay.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
