#!/usr/bin/env python3
"""Independent quiet FQ class header counterexamples; fixture evidence only."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def raw(name, kind='NNameFullyQualified'):
    return kind + ' (BYTES "' + base64.b64encode(name).decode() + '") eps'


def branch(name):
    return '(PTBRANCH ([PTCLASS ([' + ','.join(map(str, name)) + '])]))'


def mask(*branches):
    return '[' + ','.join(branches) + ']'


def assertions():
    rows = []
    null = '(PTBRANCH ([PTBUILTIN "null"]))'
    def check(label, ast, normalized, expected):
        rows.append({'id': label, 'expected': expected,
                     'premise': ('' if expected else '~') + '$hook_short_reference_header(' + ast + ',' + normalized + ')'})
    names = [b'stdClass', b'sTdClAsS', b'Ns322\\Leaf', b'Ns322\\_', b'boolean',
             b'integer', b'double', b'resource', b'Class1', b'_C', b'\x80Name']
    for name in names:
        key = name.hex(); ast = raw(name); cls = branch(name)
        check(key + '-exact', ast, mask(cls), True)
        check(key + '-different-normalized-bytes', ast, mask(branch(name + b'X')), False)
        check(key + '-wrong-null-suffix', ast, mask(cls, null), False)
        check(key + '-nullable', 'NNullableType (' + ast + ') eps', mask(cls, null), True)
        check(key + '-nullable-reversed', 'NNullableType (' + ast + ') eps', mask(null, cls), False)
    for name in (b'sTdClAsS', b'Ns322\\lEaF'):
        check(name.hex() + '-case-mismatch', raw(name), mask(branch(name.lower())), False)
    for name in (b'', b'_', b'\\stdClass', b'Ns322\\', b'Ns322\\\\Leaf', b'1Leaf',
                 b'Ns322\\1Leaf', b'Leaf\x00', b'Ns322/Leaf', b'Leaf-Name'):
        check('invalid-or-warning-' + name.hex(), raw(name), mask(branch(name)), False)
    for name in (b'array', b'callable', b'bool', b'int', b'float', b'string', b'object',
                 b'mixed', b'null', b'true', b'false', b'void', b'never', b'iterable',
                 b'self', b'parent', b'static', b'Ns322\\INT', b'Ns322\\TrUe'):
        check('reserved-last-' + name.hex(), raw(name), mask(branch(name)), False)
    cls = branch(b'Ns322\\Leaf'); ast = raw(b'Ns322\\Leaf')
    for kind in ('NName', 'NNameRelative', 'NIdentifier'):
        check(kind + '-not-FQ', raw(b'Ns322\\Leaf', kind), mask(cls), False)
    check('class-normalized-as-builtin', ast, mask('(PTBRANCH ([PTBUILTIN "object"]))'), False)
    check('class-normalized-as-scope', ast, mask('(PTBRANCH ([PTSELF]))'), False)
    check('empty-normalization', ast, 'eps', False)
    check('duplicate-normalization', ast, mask(cls, cls), False)
    check('class-intersection-branch', ast, mask('(PTBRANCH ([PTCLASS ([65]),PTCLASS ([66])]))'), False)
    check('raw-class-null-union', 'NUnionType (SEQUENCE ([' + ast + ',' + raw(b'null', 'NIdentifier') + '])) eps', mask(cls, null), False)
    check('nullable-missing-null', 'NNullableType (' + ast + ') eps', mask(cls), False)
    check('nullable-duplicate-null', 'NNullableType (' + ast + ') eps', mask(cls, null, null), False)
    check('nullable-underscore-warning', 'NNullableType (' + raw(b'_') + ') eps', mask(branch(b'_'), null), False)
    check('old-int-header', raw(b'INT', 'NIdentifier'), mask('(PTBRANCH ([PTBUILTIN "int"]))'), True)
    check('old-mixed-header', raw(b'mixed', 'NIdentifier'), mask('(PTBRANCH ([PTBUILTIN "mixed"]))'), True)
    assert len({r['id'] for r in rows}) == len(rows)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), ROOT / 'tests/semantics/error_handler_run.py',
             ROOT / 'spec/semantics/modules.json', ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *modules]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'mode': 'fixture-SL',
              'source_agreement_credit': 0, 'native_observations': 0, 'passed': False}
    try:
        rows = assertions(); report['premises'] = len(rows)
        (out / 'assertions.json').write_text(json.dumps(rows, indent=2) + '\n')
        fixture = out / 'protocol.watsup'
        fixture.write_text('dec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + r['premise'] + '\n' for r in rows))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                      *map(str, modules), str(fixture)], out / 'check', 60)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after']
                            and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed'], report.get('stderr', '')[:2000]
    print('pass', report['premises'], 'independent FQ header assertions, source0')


if __name__ == '__main__':
    main()
