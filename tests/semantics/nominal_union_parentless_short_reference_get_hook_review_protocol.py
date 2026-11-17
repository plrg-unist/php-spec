#!/usr/bin/env python3
"""Independent finite nominal-list order, shape and quiet-normalization checks."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import scoped_class_parentless_short_reference_get_hook_review_protocol as names
from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
HELPER = '$hook_short_reference_nominal_union_header'
MEMBERS = '$hook_short_reference_nominal_union_members'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def union(*members):
    return 'NUnionType (SEQUENCE ([' + ','.join(members) + '])) eps'


def branches(*classes):
    return '[' + ','.join('(PTBRANCH ([PTCLASS ' + names.value(name) + ']))' for name in classes) + ']'


def assertions():
    rows = []

    def check(label, ast, normalized, lexical, expected):
        rows.append({'id': label, 'expected': expected, 'premise': ('' if expected else '~') +
                     HELPER + '(' + ast + ',' + normalized + ',' + lexical + ')'})

    plain = names.context(namespace=b'Header334', file=b'original334.php')
    for length in (3, 4, 5, 8, 17):
        raw, resolved = [], []
        for i in range(length):
            name = ('Arm' + str(i)).encode()
            kind = ('NName', 'NNameRelative', 'NNameFullyQualified')[i % 3]
            raw.append(names.raw(name, kind))
            resolved.append(name if kind == 'NNameFullyQualified' else b'Header334\\' + name)
        label = 'finite-' + str(length)
        ast, normalized = union(*raw), branches(*resolved)
        check(label, ast, normalized, plain, True)
        check(label + '-raw-reverse', union(*reversed(raw)), normalized, plain, False)
        check(label + '-normalized-reverse', ast, branches(*reversed(resolved)), plain, False)
        check(label + '-missing', ast, branches(*resolved[:-1]), plain, False)
        check(label + '-extra', ast, branches(*resolved, b'Extra'), plain, False)
        for position in sorted({0, length // 2, length - 1}):
            altered = resolved.copy(); altered[position] += b'X'
            check(label + '-bytes-' + str(position), ast, branches(*altered), plain, False)
            altered = resolved.copy(); altered[position] = altered[position].swapcase()
            check(label + '-case-' + str(position), ast, branches(*altered), plain, False)
        check(label + '-old-pair', ast, normalized, plain, False)
        rows[-1]['premise'] = rows[-1]['premise'].replace(HELPER, '$hook_short_reference_nominal_pair_header')
        check(label + '-old-builtin', ast, normalized, plain, False)
        rows[-1]['premise'] = rows[-1]['premise'].replace(HELPER, '$hook_short_reference_class_builtin_union_header')

    raw = [names.raw(name) for name in (b'First', b'Middle', b'Last')]
    resolved = [b'Header334\\' + name for name in (b'First', b'Middle', b'Last')]
    ast, normalized = union(*raw), branches(*resolved)
    for position in range(3):
        for invalid in (b'', b'_', b'1Name', b'Name\x00', b'Name-Child', b'self', b'parent',
                        b'static', b'int', b'float', b'array', b'bool', b'string', b'null',
                        b'true', b'false', b'object', b'mixed', b'callable', b'iterable', b'void', b'never'):
            altered = raw.copy(); altered[position] = names.raw(invalid)
            check('invalid-' + str(position) + '-' + invalid.hex(), union(*altered), normalized, plain, False)
        for warning in (b'boolean', b'integer', b'double', b'resource'):
            altered = raw.copy(); altered[position] = names.raw(warning)
            target = resolved.copy(); target[position] = b'Header334\\' + warning
            check('warning-' + str(position) + '-' + warning.decode(), union(*altered), branches(*target), plain, False)
        altered = raw.copy(); altered[position] = names.raw(b'Middle', 'NIdentifier')
        check('identifier-' + str(position), union(*altered), normalized, plain, False)
        altered = raw.copy(); altered[position] = names.raw(b'int', 'NIdentifier')
        mixed = ['(PTBRANCH ([PTCLASS ' + names.value(name) + ']))' for name in resolved]
        mixed[position] = '(PTBRANCH ([PTBUILTIN "int"]))'
        check('mixed-builtin-' + str(position), union(*altered), '[' + ','.join(mixed) + ']', plain, False)
        for label, branch in (
            ('empty', '(PTBRANCH eps)'), ('builtin', '(PTBRANCH ([PTBUILTIN "object"]))'),
            ('scope', '(PTBRANCH ([PTSELF]))'),
            ('intersection', '(PTBRANCH ([PTCLASS ' + names.value(resolved[position]) + ',PTCLASS ([65])]))')):
            mixed = ['(PTBRANCH ([PTCLASS ' + names.value(name) + ']))' for name in resolved]
            mixed[position] = branch
            check('branch-' + str(position) + '-' + label, ast, '[' + ','.join(mixed) + ']', plain, False)
    for length in (0, 1, 2):
        check('too-short-' + str(length), union(*raw[:length]), branches(*resolved[:length]), plain, False)
    check('not-union', raw[0], normalized, plain, False)
    check('nullable', 'NNullableType (' + raw[0] + ') eps', normalized, plain, False)
    intersection = 'NIntersectionType (SEQUENCE ([' + raw[0] + ',' + raw[1] + '])) eps'
    check('DNF', union(intersection, raw[1], raw[2]), normalized, plain, False)
    check('empty-normalized', ast, 'eps', plain, False)
    for position in (1, 2):
        altered = raw.copy(); altered[position] = names.raw(b'fIrSt')
        target = resolved.copy(); target[position] = b'Header334\\fIrSt'
        check('case-duplicate-' + str(position), union(*altered), branches(*target), plain, False)
    imported = names.context(namespace=b'Header334', file=b'original334.php',
                             imports=((b'Lead', b'Payload334\\First'), (b'Tree', b'Payload334')))
    imported_raw = [names.raw(b'lEaD'), names.raw(b'tReE\\Middle'), names.raw(b'Last', 'NNameRelative')]
    imported_resolved = [b'Payload334\\First', b'Payload334\\Middle', b'Header334\\Last']
    check('alias-prefix-relative', union(*imported_raw), branches(*imported_resolved), imported, True)
    duplicate = names.context(namespace=b'Header334', file=b'original334.php',
                              imports=((b'Left', b'Payload334\\First'), (b'Right', b'Payload334\\First')))
    check('alias-duplicate', union(names.raw(b'Left'), raw[1], names.raw(b'Right')),
          branches(b'Payload334\\First', resolved[1], b'Payload334\\First'), duplicate, False)
    for label, lexical in (
        ('consumer', names.context(namespace=b'Consumer334', file=b'original334.php')),
        ('missing-file', names.context(namespace=b'Header334', file=b'')),
        ('missing-line', names.context(namespace=b'Header334', file=b'original334.php', line=0))):
        check(label, ast, normalized, lexical, False)
    rows.append({'id': 'members-empty-base', 'expected': True, 'premise': MEMBERS + '(eps,eps)'})
    rows.append({'id': 'members-empty-raw', 'expected': False, 'premise': '~' + MEMBERS + '(eps,' + normalized + ')'})
    rows.append({'id': 'members-empty-normalized', 'expected': False,
                 'premise': '~' + MEMBERS + '([' + ','.join(raw) + '],eps)'})
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
    print('pass', report['premises'], 'independent nominal-union assertions, source0')


if __name__ == '__main__':
    main()
