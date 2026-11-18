#!/usr/bin/env python3
"""Independent mixed-list counts, order, compatibility and namespace controls."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import scoped_class_parentless_short_reference_get_hook_review_protocol as names
from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
HELPER = '$hook_short_reference_mixed_nominal_union_header'
MEMBERS = '$hook_short_reference_mixed_nominal_union_members'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def union(raw):
    return 'NUnionType (SEQUENCE ([' + ','.join(raw) + '])) eps'


def branches(rows):
    return '[' + ','.join('(PTBRANCH ([PTCLASS ' + names.value(row['class']) + ']))'
                          if 'class' in row else '(PTBRANCH ([PTBUILTIN "' + row['builtin'] + '"]))'
                          for row in rows) + ']'


def assertions():
    rows = []
    lexical = names.context(namespace=b'Mixed335', file=b'original335.php')

    def check(label, raw, normalized, expected, context=lexical):
        rows.append({'id': label, 'expected': expected, 'premise': ('' if expected else '~') +
                     HELPER + '(' + union(raw) + ',' + normalized + ',' + context + ')'})

    def count(label, raw, normalized, expected):
        result = 'eps' if expected is None else '((' + ','.join(map(str, expected)) + '))'
        rows.append({'id': label, 'expected': expected, 'premise': MEMBERS +
                     '([' + ','.join(raw) + '],' + normalized + ',' + lexical + ') = ' + result})

    kinds = [('NName', 'NNameRelative'), ('NNameFullyQualified', 'NName'),
             ('NNameRelative', 'NNameFullyQualified')]
    allowed = ('array', 'int', 'float', 'string', 'null', 'bool', 'false', 'true')
    for builtin in allowed:
        for position in range(3):
            classraw = [names.raw(b'Mixed335\\' + name if kind == 'NNameFullyQualified' else name, kind)
                        for name, kind in zip((b'First', b'Last'), kinds[position])]
            raw = classraw.copy(); raw.insert(position, names.raw(builtin.encode(), 'NIdentifier'))
            resolved = [{'class': b'Mixed335\\First'}, {'class': b'Mixed335\\Last'}]
            resolved.insert(position, {'builtin': builtin})
            label = builtin + '-' + str(position); normalized = branches(resolved)
            check(label, raw, normalized, True)
            check(label + '-raw-reverse', list(reversed(raw)), normalized, False)
            check(label + '-normalized-reverse', raw, branches(list(reversed(resolved))), False)
            check(label + '-missing', raw, branches(resolved[:-1]), False)
            check(label + '-extra', raw, branches(resolved + [{'class': b'Mixed335\\Extra'}]), False)
            rawupper = raw.copy(); rawupper[position] = names.raw(builtin.upper().encode(), 'NIdentifier')
            check(label + '-uppercase-builtin', rawupper, normalized, True)
        count(builtin + '-counts', raw, normalized, (2, 1))

    for size in (2, 3, 8, 17):
        classnames = [('Arm' + str(i)).encode() for i in range(size)]
        raw = [names.raw(name) for name in classnames]
        resolved = [{'class': b'Mixed335\\' + name} for name in classnames]
        for i, builtin in enumerate(('array', 'string', 'int', 'float', 'bool', 'null')):
            raw.insert(2 * i, names.raw(builtin.encode(), 'NIdentifier'))
            resolved.insert(2 * i, {'builtin': builtin})
        normalized = branches(resolved)
        check('finite-' + str(size), raw, normalized, True)
        count('finite-count-' + str(size), raw, normalized, (size, 6))
        for position in (0, len(resolved) // 2, len(resolved) - 1):
            altered = [dict(value) for value in resolved]
            if 'class' in altered[position]: altered[position]['class'] += b'X'
            else: altered[position]['builtin'] = 'object'
            check('finite-corruption-' + str(size) + '-' + str(position), raw, branches(altered), False)

    first, last = names.raw(b'First'), names.raw(b'Last')
    raw = [first, names.raw(b'int', 'NIdentifier'), last]
    resolved = [{'class': b'Mixed335\\First'}, {'builtin': 'int'}, {'class': b'Mixed335\\Last'}]
    normalized = branches(resolved)
    for position in (0, 2):
        for invalid in (b'', b'_', b'1Name', b'Name\x00', b'self', b'parent', b'static', b'int', b'array'):
            altered = raw.copy(); altered[position] = names.raw(invalid)
            check('invalid-class-' + str(position) + '-' + invalid.hex(), altered, normalized, False)
        altered = raw.copy(); altered[position] = names.raw(b'First', 'NIdentifier')
        check('identifier-class-' + str(position), altered, normalized, False)
        for warning in (b'boolean', b'integer', b'double', b'resource'):
            altered = raw.copy(); altered[position] = names.raw(warning)
            target = [dict(value) for value in resolved]; target[position] = {'class': b'Mixed335\\' + warning}
            check('nonquiet-' + str(position) + '-' + warning.decode(), altered, branches(target), False)
    for builtin in ('iterable', 'object', 'mixed', 'callable', 'void', 'never', 'resource'):
        altered = raw.copy(); altered[1] = names.raw(builtin.encode(), 'NIdentifier')
        target = [dict(value) for value in resolved]; target[1] = {'builtin': builtin}
        check('unsupported-builtin-' + builtin, altered, branches(target), False)
        count('unsupported-count-' + builtin, altered, branches(target), None)
    altered = raw.copy(); altered[1] = names.raw(b'int')
    check('builtin-wrong-raw-kind', altered, normalized, False)
    count('builtin-wrong-kind-count', altered, normalized, None)
    for a, b in (('bool', 'true'), ('bool', 'false'), ('true', 'false'), ('int', 'int')):
        altered = [first, names.raw(a.encode(), 'NIdentifier'), last, names.raw(b.encode(), 'NIdentifier')]
        target = [resolved[0], {'builtin': a}, resolved[2], {'builtin': b}]
        check('incompatible-' + a + '-' + b, altered, branches(target), False)
        count('incompatible-structural-count-' + a + '-' + b, altered, branches(target), (2, 2))
    duplicate = [first, raw[1], names.raw(b'fIrSt')]
    check('case-duplicate', duplicate, branches([resolved[0], resolved[1], {'class': b'Mixed335\\fIrSt'}]), False)
    imported = names.context(namespace=b'Mixed335', file=b'original335.php',
                             imports=((b'Left', b'Payload335\\First'), (b'Right', b'Payload335\\First')))
    check('alias-duplicate', [names.raw(b'Left'), raw[1], names.raw(b'Right')],
          branches([{'class': b'Payload335\\First'}, resolved[1], {'class': b'Payload335\\First'}]), False, imported)
    check('one-class', [first, raw[1]], branches(resolved[:2]), False)
    check('zero-classes', [raw[1], names.raw(b'float', 'NIdentifier')],
          branches([{'builtin': 'int'}, {'builtin': 'float'}]), False)
    check('no-builtin', [first, last], branches([resolved[0], resolved[2]]), False)
    check('empty-union', [], 'eps', False)
    count('empty-counts', [], 'eps', (0, 0))
    count('different-length-counts', raw, branches(resolved[:-1]), None)
    check('empty-normalized', raw, 'eps', False)
    check('intersection-branch', raw,
          '[(PTBRANCH ([PTCLASS ([65]),PTCLASS ([66])])),(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTCLASS ([67])]))]', False)
    for label, context in (
        ('consumer-shadow', names.context(namespace=b'Consumer335', file=b'original335.php')),
        ('missing-file', names.context(namespace=b'Mixed335', file=b'')),
        ('missing-line', names.context(namespace=b'Mixed335', file=b'original335.php', line=0))):
        check(label, raw, normalized, False, context)
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
    print('pass', report['premises'], 'independent mixed nominal/builtin assertions, source0')


if __name__ == '__main__':
    main()
