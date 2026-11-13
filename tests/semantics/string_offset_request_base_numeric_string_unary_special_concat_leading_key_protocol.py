#!/usr/bin/env python3
"""Quiet numeric-string unary CONCAT keys retain real Warning history."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_numeric_string_unary_special_concat_leading_key_cases as cases
import string_offset_request_base_nested_unary_numeric_special_concat_leading_key_protocol as prior

runner = prior.runner


def conditions(program, path, index):
    checks, derived = prior.conditions(program, path, index)
    text = ('  +1 ', '1', '1.00000000000001', '4.00000000000001e0')[index]
    old_node = ('NScalarInt (INTEGER 1)' if index < 2 else 'NScalarFloat (FLOAT text_literal)')
    old_value = 'PINT 1' if index < 2 else 'PFLOAT n_bits_literal'
    replacements = {
        'expression_literal = ' + old_node + ' metadata_literal':
            'expression_literal = NScalarString (BYTES text_literal) metadata_literal',
        'pvalue_literal = ' + old_value:
            'pvalue_literal = PSTRING ($ptascii(' + json.dumps(text) + '))'}
    for old, new in replacements.items():
        assert checks.count(old) == 1, old
        checks[checks.index(old)] = new
    at = checks.index('pvalue_literal = PSTRING ($ptascii(' + json.dumps(text) + '))')
    numeric = 'PINT 1' if index < 2 else 'PFLOAT ' + str((4607182418800017453, 4616189618054758411)[index - 2])
    checks[at + 1:at + 1] = [
        '$base64(text_literal) = $ptascii(' + json.dumps(text) + ')',
        '$coerce_number(pvalue_literal) = COERCED pnumber_literal false',
        '$number_value(pnumber_literal) = ' + numeric]
    return checks, derived


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases = cases
    runner.OUTPUTS = cases.OUTPUTS
    runner.conditions = conditions
    passed = runner.main()
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four fresh actual full-numeric string-leaf unary chains plus resolved bool/null CONCAT source-state fixtures at compile14/live17. Decoded literal bytes, quiet coercion with exact numeric typing/bits, every own unary fact/precision and pure result are authenticated. Existing borrowed-owner, saved-index, throw, fixed bounds and budget laws remain. Prior source/native/state/compiler cuts retain their identities without replay.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
