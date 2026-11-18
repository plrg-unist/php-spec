#!/usr/bin/env python3
"""Independent defining-context header counterexamples; fixture evidence only."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def quoted(value):
    return '"' + base64.b64encode(value).decode() + '"'


def value(data):
    return '([' + ','.join(map(str, data)) + '])' if data else 'eps'


def raw(name, kind='NName', nullable=False):
    ast = kind + ' (BYTES ' + quoted(name) + ') eps'
    return 'NNullableType (' + ast + ') eps' if nullable else ast


def mask(name, nullable=False):
    return '[(PTBRANCH ([PTCLASS ' + value(name) + ']))' + (',(PTBRANCH ([PTBUILTIN "null"]))]' if nullable else ']')


def context(namespace=b'Def323', imports=(), file=b'original323.php', line=7):
    pairs = '([' + ','.join('(' + value(alias) + ',' + value(target) + ')' for alias, target in imports) + '])' if imports else 'eps'
    owner = namespace + b'\\Box323' if namespace else b'Box323'
    return ('{NAMESPACE ' + value(namespace) + ', IMPORTS ' + pairs + ', SCOPE PTKNOWN ' + value(owner) + ' eps,'
            ' POSITION PTPROPERTY, OWNER ' + value(owner) + ', MEMBER ([118]), FILE ' + value(file) + ', LINE ' + str(line) + '}')


def assertions():
    rows = []
    def check(label, ast, normalized, lexical, expected):
        rows.append({'id': label, 'expected': expected, 'premise': ('' if expected else '~') +
                     '$hook_short_reference_scoped_header(' + ast + ',' + normalized + ',' + lexical + ')'})
    plain = context(); global_context = context(b''); shadow = context(b'Consumer323', ((b'Leaf', b'stdClass'),))
    imported = context(imports=((b'Target323', b'Payload323\\Leaf'), (b'Prefix323', b'Payload323')))
    accepted = [
        ('global', b'stdClass', 'NName', b'stdClass', global_context),
        ('local', b'Leaf', 'NName', b'Def323\\Leaf', plain),
        ('qualified-local', b'Nested\\Leaf', 'NName', b'Def323\\Nested\\Leaf', plain),
        ('alias-case', b'tArGeT323', 'NName', b'Payload323\\Leaf', imported),
        ('prefix-case', b'pReFiX323\\lEaF', 'NName', b'Payload323\\lEaF', imported),
        ('relative', b'Leaf', 'NNameRelative', b'Def323\\Leaf', plain),
        ('relative-bypasses-alias', b'Target323', 'NNameRelative', b'Def323\\Target323', imported),
        ('relative-bypasses-prefix', b'Prefix323\\Leaf', 'NNameRelative', b'Def323\\Prefix323\\Leaf', imported),
        ('ordinary-underscore-component', b'Nested\\_', 'NName', b'Def323\\Nested\\_', plain),
        ('high-byte-class', b'\x80Leaf', 'NName', b'Def323\\\x80Leaf', plain),
    ]
    for label, name, kind, resolved, lexical in accepted:
        for nullable in (False, True):
            suffix = '-nullable' if nullable else '-single'
            ast = raw(name, kind, nullable); normalized = mask(resolved, nullable)
            check(label + suffix, ast, normalized, lexical, True)
            check(label + suffix + '-different-class', ast, mask(resolved + b'X', nullable), lexical, False)
            check(label + suffix + '-wrong-case', ast, mask(resolved.swapcase(), nullable), lexical, False)
        check(label + '-nullable-reversed', raw(name, kind, True), '[(PTBRANCH ([PTBUILTIN "null"])),(PTBRANCH ([PTCLASS ' + value(resolved) + ']))]', lexical, False)
    check('consumer-shadow-does-not-authenticate', raw(b'Leaf'), mask(b'Def323\\Leaf'), shadow, False)
    check('alias-cannot-use-consumer-prefix', raw(b'pReFiX323\\lEaF'), mask(b'Consumer323\\pReFiX323\\lEaF'), imported, False)
    for name in (b'', b'_', b'\\Leaf', b'Leaf\\', b'Leaf\\\\Child', b'1Leaf', b'Leaf\\1Child', b'Leaf\x00', b'Leaf/Child', b'Leaf-Child'):
        for kind in ('NName', 'NNameRelative'):
            check('invalid-' + kind + '-' + name.hex(), raw(name, kind), mask(b'Def323\\' + name), plain, False)
    for name in (b'self', b'PaReNt', b'STATIC', b'array', b'callable', b'int', b'float', b'string', b'bool', b'object', b'mixed', b'null', b'true', b'false', b'void', b'never', b'iterable', b'Nested\\INT'):
        for kind in ('NName', 'NNameRelative'):
            check('reserved-' + kind + '-' + name.hex(), raw(name, kind), mask(b'Def323\\' + name), plain, False)
    for name in (b'boolean', b'integer', b'double', b'resource'):
        check('confusable-warning-' + name.decode(), raw(name), mask(b'Def323\\' + name), plain, False)
    for kind in ('NName', 'NNameRelative'):
        for nullable in (False, True):
            check('self-cannot-reuse-scope-' + kind + str(nullable), raw(b'SeLf', kind, nullable), mask(b'Def323\\Box323', nullable), plain, True)
    check('imported-global-underscore-warning', raw(b'Target323'), mask(b'_'), context(imports=((b'Target323', b'_'),)), False)
    check('other-raw-kind-NIdentifier', raw(b'Leaf', 'NIdentifier'), mask(b'Def323\\Leaf'), plain, False)
    check('other-raw-kind-NNameFullyQualified', raw(b'Leaf', 'NNameFullyQualified'), mask(b'Leaf'), plain, False)
    for label, normalized in (
        ('empty', 'eps'), ('builtin', '[(PTBRANCH ([PTBUILTIN "object"]))]'),
        ('scope', '[(PTBRANCH ([PTSELF]))]'), ('extra-null', mask(b'Def323\\Leaf', True)),
        ('duplicate-class', '[(PTBRANCH ([PTCLASS ([65])])),(PTBRANCH ([PTCLASS ([65])]))]'),
        ('intersection', '[(PTBRANCH ([PTCLASS ([65]),PTCLASS ([66])]))]')):
        check('wrong-shape-' + label, raw(b'Leaf'), normalized, plain, False)
    check('nullable-missing-null', raw(b'Leaf', nullable=True), mask(b'Def323\\Leaf'), plain, False)
    check('missing-file', raw(b'Leaf'), mask(b'Def323\\Leaf'), context(file=b''), False)
    check('missing-line', raw(b'Leaf'), mask(b'Def323\\Leaf'), context(line=0), False)
    check('explicit-class-null-union', 'NUnionType (SEQUENCE ([' + raw(b'Leaf') + ',' + raw(b'null', 'NIdentifier') + '])) eps', mask(b'Def323\\Leaf', True), plain, False)
    assert len({row['id'] for row in rows}) == len(rows)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), ROOT / 'tests/semantics/error_handler_run.py', ROOT / 'spec/semantics/modules.json',
             ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *modules]
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
    print('pass', report['premises'], 'independent scoped header assertions, source0')


if __name__ == '__main__':
    main()
