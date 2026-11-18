#!/usr/bin/env python3
"""Independent literal-this body boundaries; fixture evidence only."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import scoped_class_parentless_short_reference_get_hook_review_protocol as names
from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
HELPER = '$hook_short_reference_literal_this_body'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def scalar(value, kind='NScalarString'):
    return kind + ' (BYTES ' + names.quoted(value) + ') eps'


def variable(value):
    return 'NExprVariable (' + value + ') eps'


def fetch(receiver, member, kind='NExprPropertyFetch'):
    return kind + ' (' + receiver + ') (' + member + ') eps'


def assertions():
    rows = []

    def check(label, helper, expression, field, expected):
        rows.append({'id': label, 'expected': expected,
                     'premise': ('' if expected else '~') + helper + '(' + expression + ',' + names.value(field) + ')'})

    literal = variable(scalar(b'this'))
    ordinary = variable('BYTES ' + names.quoted(b'this'))
    computed = variable('NExprBinaryOpConcat (' + scalar(b'thi') + ') (' + scalar(b's') + ') eps')
    nested = variable(variable('BYTES ' + names.quoted(b'receiver')))
    for field in (b'v', b'Case', b'\x80name'):
        for kind in ('NIdentifier', 'NScalarString'):
            label = field.hex() + '-' + kind
            member = scalar(field, kind)
            expression = fetch(literal, member)
            check(label + '-literal', HELPER, expression, field, True)
            check(label + '-old-literal-refusal', '$hook_short_reference_body', expression, field, False)
            check(label + '-existing-backing', '$hook_body_backed', expression, field, True)
            check(label + '-different-field', HELPER, expression, field + b'X', False)
            check(label + '-ordinary-refusal', HELPER, fetch(ordinary, member), field, False)
            check(label + '-old-ordinary-retained', '$hook_short_reference_body', fetch(ordinary, member), field, True)
            check(label + '-nullsafe', HELPER, fetch(literal, member, 'NExprNullsafePropertyFetch'), field, False)
            check(label + '-computed', HELPER, fetch(computed, member), field, False)
            check(label + '-variable-variable', HELPER, fetch(nested, member), field, False)
            check(label + '-nonvariable', HELPER, fetch(scalar(b'this'), member), field, False)
            check(label + '-dynamic-member', HELPER, fetch(literal, variable('BYTES ' + names.quoted(field))), field, False)
            check(label + '-integer-member', HELPER, fetch(literal, 'NScalarInt (INTEGER 0) eps'), field, False)
            for wrong in (b'', b'This', b'THIS', b'this\x00', b'other'):
                check(label + '-receiver-' + wrong.hex(), HELPER, fetch(variable(scalar(wrong)), member), field, False)
    check('bare-variable', HELPER, literal, b'v', False)
    check('bare-string', HELPER, scalar(b'this'), b'v', False)
    assert len({row['id'] for row in rows}) == len(rows)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(names.__file__), ROOT / 'tests/semantics/error_handler_run.py',
             ROOT / 'spec/semantics/modules.json', ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *modules]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'mode': 'fixture-SL',
              'source_agreement_credit': 0, 'native_observations': 0, 'passed': False}
    try:
        rows = assertions(); report['premises'] = len(rows)
        (out / 'assertions.json').write_text(json.dumps(rows, indent=2) + '\n')
        fixture = out / 'protocol.watsup'
        fixture.write_text('dec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + row['premise'] + '\n' for row in rows))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                      *map(str, modules), str(fixture)], out / 'check', 60)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after']
                            and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed'], report.get('stderr', '')[:2000]
    print('pass', report['premises'], 'independent literal-this body assertions, source0')


if __name__ == '__main__':
    main()
