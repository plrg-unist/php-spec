#!/usr/bin/env python3
"""Independent scoped-self mixed-union counts, ordering and context controls."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import self_parentless_short_reference_get_hook_review_protocol as prior
import self_builtin_union_parentless_short_reference_get_hook_review_protocol as previous
from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
HELPER = '$hook_short_reference_mixed_nominal_union_header'
MEMBERS = '$hook_short_reference_mixed_nominal_union_members'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def assertions():
    rows = []; names = prior.names; owner = b'Def346\\Box346'
    lexical = prior.context(namespace=b'Def346', owner=owner, file=b'original346.php',
                            imports=((b'Alias346', b'Payload346\\Other346'),))
    atom = 'PTCLASS ' + names.value(owner)

    def check(label, raw, parts, expected=True, ctx=lexical, helper=HELPER):
        rows.append({'id': label, 'kind': 'header', 'expected': expected,
                     'premise': ('' if expected else '~') + helper + '(' + prior.union(raw) + ',' + prior.branches(parts) + ',' + ctx + ')'})

    def count(label, raw, parts, expected, ctx=lexical):
        result = 'eps' if expected is None else '((' + ','.join(map(str, expected)) + '))'
        rows.append({'id': label, 'kind': 'members', 'expected': True,
                     'premise': MEMBERS + '([' + ','.join(raw) + '],' + prior.branches(parts) + ',' + ctx + ') = ' + result})

    other_forms = [('NNameFullyQualified', b'Global346\\Other346', b'Global346\\Other346'),
                   ('NName', b'Alias346', b'Payload346\\Other346'),
                   ('NNameRelative', b'Other346', b'Def346\\Other346')]
    for kind in ('NName', 'NNameRelative'):
        selfraw = names.raw(b'SeLf', kind)
        for builtin in ('array', 'int', 'float', 'string', 'null', 'bool', 'false', 'true'):
            for position, (otherkind, spelling, resolved) in enumerate(other_forms):
                raw = [names.raw(spelling, otherkind), names.raw(builtin.encode(), 'NIdentifier')]
                parts = [['PTCLASS ' + names.value(resolved)], ['PTBUILTIN "' + builtin + '"']]
                raw.insert(position, selfraw); parts.insert(position, [atom])
                label = kind + '-' + builtin + '-' + str(position)
                check(label, raw, parts)
                check(label + '-raw-order', list(reversed(raw)), parts, False)
                check(label + '-normalized-order', raw, list(reversed(parts)), False)
                for suffix, badname in [('bytes', owner + b'X'), ('case', owner.swapcase())]:
                    altered = [part.copy() for part in parts]; altered[position] = ['PTCLASS ' + names.value(badname)]
                    check(label + '-self-' + suffix, raw, altered, False)
                check(label + '-missing', raw, parts[:-1], False)
                check(label + '-extra', raw, parts + [['PTBUILTIN "null"']], False)
                upper = raw.copy(); upper[raw.index(names.raw(builtin.encode(), 'NIdentifier'))] = names.raw(builtin.upper().encode(), 'NIdentifier')
                check(label + '-uppercase-builtin', upper, parts)
            count(kind + '-' + builtin + '-counts', raw, parts, (2, 1))

        for size in (2, 8, 17):
            classraw = [names.raw(('Arm' + str(i)).encode(), 'NNameRelative') for i in range(size - 1)]
            classparts = [['PTCLASS ' + names.value(b'Def346\\' + ('Arm' + str(i)).encode())] for i in range(size - 1)]
            raw = classraw.copy(); parts = [part.copy() for part in classparts]
            for i, builtin in enumerate(('array', 'int', 'float', 'string', 'bool', 'null')):
                raw.insert(2 * i, names.raw(builtin.encode(), 'NIdentifier'))
                parts.insert(2 * i, ['PTBUILTIN "' + builtin + '"'])
            for position in (0, len(raw) // 2, len(raw)):
                mixed = raw.copy(); normalized = [part.copy() for part in parts]
                mixed.insert(position, selfraw); normalized.insert(position, [atom])
                label = kind + '-finite-' + str(size) + '-' + str(position)
                check(label, mixed, normalized)
                check(label + '-order', mixed, list(reversed(normalized)), False)
                count(label + '-counts', mixed, normalized, (size, 6))

        other = names.raw(b'Global346\\Other346', 'NNameFullyQualified')
        otheratom = 'PTCLASS ' + names.value(b'Global346\\Other346')
        integer = names.raw(b'int', 'NIdentifier')
        raw = [selfraw, other, integer]; parts = [[atom], [otheratom], ['PTBUILTIN "int"']]
        consumer = prior.context(namespace=b'Consumer346', owner=owner,
                                 imports=((b'self', b'Wrong346\\Owner'), (b'Box346', b'stdClass')))
        check(kind + '-known-self-and-fq-other-ignore-consumer', raw, parts, ctx=consumer)
        for scope in ('PTGLOBAL', 'PTDEFERRED', 'PTANONYMOUS true', 'PTANONYMOUS false',
                      'PTTRAIT ' + names.value(b'Def346\\Trait346'),
                      'PTKNOWN ' + names.value(b'Wrong346\\Box346') + ' eps'):
            check(kind + '-scope-' + scope, raw, parts, False,
                  prior.context(namespace=b'Def346', owner=owner, scope=scope))
        for label, ctx in [('missing-file', prior.context(namespace=b'Def346', owner=owner, file=b'')),
                           ('missing-line', prior.context(namespace=b'Def346', owner=owner, line=0))]:
            check(kind + '-' + label, raw, parts, False, ctx)
        for wrongkind in ('NIdentifier', 'NNameFullyQualified'):
            check(kind + '-self-wrong-kind-' + wrongkind, [names.raw(b'self', wrongkind), other, integer], parts, False)
        for keyword in (b'parent', b'static'):
            check(kind + '-keyword-' + keyword.decode(), [names.raw(keyword, kind), other, integer], parts, False)
        parentname = b'Def346\\Parent346'
        parentctx = prior.context(namespace=b'Def346', owner=owner,
                                  scope='PTKNOWN ' + names.value(owner) + ' (' + names.value(parentname) + ')')
        parentraw = [names.raw(b'parent', kind), other, integer]
        parentparts = [['PTCLASS ' + names.value(parentname)], [otheratom], ['PTBUILTIN "int"']]
        rows.append({'id': kind + '-parent-normalizes', 'kind': 'normalizer', 'expected': True,
                     'premise': '$ptype_normalize(' + prior.union(parentraw) + ',' + parentctx + ') = PTOK (' + prior.branches(parentparts) + ') eps'})
        check(kind + '-known-parent-excluded', parentraw, parentparts, False, parentctx)
        for builtin in ('object', 'mixed', 'iterable', 'callable', 'void', 'never', 'integer', 'resource'):
            check(kind + '-excluded-builtin-' + builtin,
                  [selfraw, other, names.raw(builtin.encode(), 'NIdentifier')], [[atom], [otheratom], ['PTBUILTIN "' + builtin + '"']], False)
        for a, b in [('int', 'int'), ('INT', 'int'), ('bool', 'true'), ('bool', 'false'), ('true', 'false')]:
            check(kind + '-overlap-' + a + '-' + b,
                  [selfraw, names.raw(a.encode(), 'NIdentifier'), other, names.raw(b.encode(), 'NIdentifier')],
                  [[atom], ['PTBUILTIN "' + a.lower() + '"'], [otheratom], ['PTBUILTIN "' + b + '"']], False)
        for duplicate in (selfraw, names.raw(owner, 'NNameFullyQualified'), names.raw(owner.swapcase(), 'NNameFullyQualified')):
            target = owner.swapcase() if duplicate == names.raw(owner.swapcase(), 'NNameFullyQualified') else owner
            check(kind + '-duplicate-owner-' + str(len(rows)), [selfraw, duplicate, integer],
                  [[atom], ['PTCLASS ' + names.value(target)], ['PTBUILTIN "int"']], False)
        one_raw = [selfraw, integer, names.raw(b'null', 'NIdentifier')]
        one_parts = [[atom], ['PTBUILTIN "int"'], ['PTBUILTIN "null"']]
        check(kind + '-one-class-excluded', one_raw, one_parts, False)
        check(kind + '-one-class-345-retained', one_raw, one_parts,
              helper='$hook_short_reference_class_builtin_union_header')
        check(kind + '-no-builtin-excluded', [selfraw, other], [[atom], [otheratom]], False)
        check(kind + '-no-builtin-pair-retained', [selfraw, other], [[atom], [otheratom]],
              helper='$hook_short_reference_nominal_pair_header')
        count(kind + '-one-class-count', one_raw, one_parts, (1, 2))
        count(kind + '-no-builtin-count', [selfraw, other], [[atom], [otheratom]], (2, 0))
        count(kind + '-length-mismatch', raw, parts[:-1], None)
        check(kind + '-intersection-excluded', [prior.intersection([selfraw, other]), integer],
              [[atom, otheratom], ['PTBUILTIN "int"']], False)
        rows.append({'id': kind + '-DNF-unchanged', 'kind': 'header', 'expected': False,
                     'premise': '~$hook_short_reference_mixed_nominal_dnf_header(' +
                     prior.union([prior.intersection([selfraw, other]), integer]) + ',' +
                     prior.branches([[atom, otheratom], ['PTBUILTIN "int"']]) + ',' + lexical + ')'})

    check('no-classes', [names.raw(b'int', 'NIdentifier'), names.raw(b'float', 'NIdentifier')],
          [['PTBUILTIN "int"'], ['PTBUILTIN "float"']], False)
    check('empty', [], [], False)
    count('empty-count', [], [], (0, 0))
    promoted = [row for row in previous.assertions() if '-mixed-fold-' in row['id']]
    assert len(promoted) == 2 and all(row['expected'] for row in promoted)
    rows += [{**row, 'id': 'promoted-345-' + row['id'], 'kind': 'header'} for row in promoted]
    assert len({row['id'] for row in rows}) == len(rows)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(prior.__file__), Path(previous.__file__), Path(prior.names.__file__),
             ROOT / 'tests/semantics/error_handler_run.py', ROOT / 'spec/semantics/modules.json',
             ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *modules]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'mode': 'fixture-SL',
              'source_agreement_credit': 0, 'native_observations': 0, 'promoted_prior_queries': 2, 'passed': False}
    try:
        rows = assertions(); report['premises'] = len(rows)
        report['header_positive'] = sum(row['kind'] == 'header' and row['expected'] for row in rows)
        report['header_negative'] = sum(row['kind'] == 'header' and not row['expected'] for row in rows)
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
    print('pass', report['premises'], 'independent scoped-self mixed-union assertions, source0')


if __name__ == '__main__':
    main()
