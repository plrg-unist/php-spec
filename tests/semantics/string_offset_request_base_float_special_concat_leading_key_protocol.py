#!/usr/bin/env python3
"""Float/special CONCAT keys retain compiler precision across Warning callbacks."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_float_special_concat_leading_key_cases as cases
import string_offset_request_base_integer_special_concat_leading_key_protocol as runner

base_conditions = runner.conditions


def conditions(program, path, index):
    checks, derived = base_conditions(program, path, index)
    integer = 3 if index == 2 else 1
    checks = [check.replace('porigin_integer', 'porigin_float')
              .replace('metadata_integer', 'metadata_float') for check in checks]
    old = '$origin_node(S.SOURCES, porigin_float) = (NScalarInt (INTEGER ' + str(integer) + ') metadata_float)'
    at = checks.index(old)
    checks[at:at + 1] = [
        '$origin_node(S.SOURCES, porigin_float) = (NScalarFloat (FLOAT text_float) metadata_float)',
        '$parser_literal_at(NScalarFloat (FLOAT text_float) metadata_float, 14) = (PFLOAT n_bits)',
        '$compiled_precision(S, (porigin_float)) = (14)',
        'S.PRECISIONINI = $ptascii("17")',
        '$precision_value(S) = 17',
        '$parser_literal_text_at(PFLOAT n_bits, 14) = ($ptascii("' + str(integer) + '"))',
        '$parser_literal_text_at(PFLOAT n_bits, 17) = (n_live_text*)',
        'n_live_text* =/= $ptascii("' + str(integer) + '")']
    old = '$compiled_read(S, porigin_float) = (PINT ' + str(integer) + ')'
    checks[checks.index(old)] = '$compiled_read(S, porigin_float) = (PFLOAT n_bits)'
    return checks, derived


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    own_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    runner.cases = cases
    runner.OUTPUTS = cases.OUTPUTS
    runner.conditions = conditions
    passed = runner.main()
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest() == own_hash
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'][str(Path(__file__).resolve())] = own_hash
    report['scope'] = 'Three fresh rounded-float/special CONCAT source-state fixtures, with actual child precision14, live17, saved keys and unchanged owner/throw/fixed-bounds laws; older integer and numeric cuts retain their identities without replay.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
