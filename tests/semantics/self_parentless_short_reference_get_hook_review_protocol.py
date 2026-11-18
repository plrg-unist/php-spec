#!/usr/bin/env python3
"""Independent defining-self, nullable, ordered-pair and contextual controls."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import scoped_class_parentless_short_reference_get_hook_review_protocol as names
from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def union(raw):
    return 'NUnionType (SEQUENCE ([' + ','.join(raw) + '])) eps'


def intersection(raw):
    return 'NIntersectionType (SEQUENCE ([' + ','.join(raw) + '])) eps'


def branches(parts):
    return '[' + ','.join('(PTBRANCH ([' + ','.join(part) + ']))' for part in parts) + ']'


def context(namespace=b'Def341', owner=b'Def341\\Box341', imports=(), file=b'original341.php', line=11, scope=None):
    default = namespace + b'\\Box323' if namespace else b'Box323'
    known = 'PTKNOWN ' + names.value(default) + ' eps'
    result = names.context(namespace, imports, file, line)
    result = result.replace(known, scope or 'PTKNOWN ' + names.value(owner) + ' eps')
    return result.replace('OWNER ' + names.value(default), 'OWNER ' + names.value(owner))


def assertions():
    rows = []; owner = b'Def341\\Box341'; lexical = context()
    atom = 'PTCLASS ' + names.value(owner); typed = branches([[atom]])

    def check(label, premise, expected=True):
        rows.append({'id': label, 'expected': expected, 'premise': ('' if expected else '~') + premise})

    def scoped(label, raw, normalized=typed, ctx=lexical, expected=True):
        check(label, '$hook_short_reference_scoped_header(' + raw + ',' + normalized + ',' + ctx + ')', expected)

    for spelling in (b'self', b'SeLf', b'SELF'):
        label = spelling.decode(); raw = names.raw(spelling)
        scoped(label + '-single', raw)
        scoped(label + '-nullable', names.raw(spelling, nullable=True), names.mask(owner, True))
        scoped(label + '-wrong-class', raw, names.mask(owner + b'X'), expected=False)
        scoped(label + '-wrong-case-class', raw, names.mask(owner.swapcase()), expected=False)
        scoped(label + '-nullable-order', names.raw(spelling, nullable=True), branches([['PTBUILTIN "null"'], [atom]]), expected=False)
        scoped(label + '-nullable-missing-null', names.raw(spelling, nullable=True), expected=False)
        scoped(label + '-scope-atom', raw, branches([['PTSELF']]), expected=False)
        scoped(label + '-extra-null', raw, names.mask(owner, True), expected=False)
    raw = names.raw(b'SeLf')
    for namespace, imports, label in ((b'Consumer341', (), 'namespace-does-not-rebind'),
            (b'Def341', ((b'self', b'Foreign341\\Other'),), 'self-bypasses-fake-import'),
            (b'Def341', ((b'Box341', b'Foreign341\\Other'),), 'self-bypasses-class-alias')):
        scoped(label, raw, ctx=context(namespace=namespace, imports=imports))
    for scope in ('PTGLOBAL', 'PTDEFERRED', 'PTANONYMOUS true', 'PTANONYMOUS false',
                  'PTTRAIT ' + names.value(b'Def341\\Trait341'),
                  'PTKNOWN ' + names.value(b'Consumer341\\Box341') + ' eps'):
        scoped('excluded-scope-' + scope, raw, ctx=context(scope=scope), expected=False)
    for label, ctx in (('missing-file', context(file=b'')), ('missing-line', context(line=0))):
        scoped(label, raw, ctx=ctx, expected=False)
    for kind in ('NIdentifier', 'NNameFullyQualified', 'NNameRelative'):
        scoped('other-raw-kind-' + kind, names.raw(b'self', kind), expected=False)
    parent_scope = 'PTKNOWN ' + names.value(owner) + ' (' + names.value(b'Def341\\Parent341') + ')'
    for excluded in (b'parent', b'static', b'int', b'array', b'iterable', b'callable'):
        scoped('other-keyword-' + excluded.decode(), names.raw(excluded), ctx=context(scope=parent_scope), expected=False)

    domain = ('null', 'false', 'true', 'bool', 'int', 'float', 'string', 'array')
    for builtin in domain:
        helper = '$hook_short_reference_class_' + builtin + '_header'
        for reverse in (False, True):
            raw_parts = [raw, names.raw(builtin.encode(), 'NIdentifier')]
            normalized = [[atom], ['PTBUILTIN "' + builtin + '"']]
            if reverse: raw_parts.reverse(); normalized.reverse()
            label = builtin + '-' + str(reverse); ast = union(raw_parts); mask = branches(normalized)
            check(label + '-accepted', helper + '(' + ast + ',' + mask + ',' + lexical + ')')
            check(label + '-raw-order', helper + '(' + union(list(reversed(raw_parts))) + ',' + mask + ',' + lexical + ')', False)
            check(label + '-normalized-order', helper + '(' + ast + ',' + branches(list(reversed(normalized))) + ',' + lexical + ')', False)
            check(label + '-wrong-owner', helper + '(' + ast + ',' + mask + ',' + context(scope='PTKNOWN ' + names.value(owner + b'X') + ' eps') + ')', False)
            upper = [part.replace(names.quoted(builtin.encode()), names.quoted(builtin.upper().encode())) for part in raw_parts]
            check(label + '-uppercase-builtin', helper + '(' + union(upper) + ',' + mask + ',' + lexical + ')')

    other = names.raw(b'Other341'); other_atom = 'PTCLASS ' + names.value(b'Def341\\Other341')
    pair = union([raw, other]); pair_type = branches([[atom], [other_atom]])
    check('self-ordinary-pair-stays-partial', '$hook_short_reference_nominal_pair_header(' + pair + ',' + pair_type + ',' + lexical + ')', False)
    inter = intersection([raw, other]); inter_type = branches([[atom, other_atom]])
    check('known-self-intersection-normalizes', '$ptype_normalize(' + inter + ',' + lexical + ') = PTOK (' + inter_type + ') eps')
    check('known-self-intersection-hook-stays-partial', '$hook_short_reference_nominal_intersection_header(' + inter + ',' + inter_type + ',' + lexical + ')', False)
    three = union([raw, names.raw(b'int', 'NIdentifier'), names.raw(b'null', 'NIdentifier')])
    three_type = branches([[atom], ['PTBUILTIN "int"'], ['PTBUILTIN "null"']])
    check('three-arm-builtin-self-stays-partial', '$hook_short_reference_class_builtin_union_header(' + three + ',' + three_type + ',' + lexical + ')', False)
    grouped = intersection([names.raw(b'A341'), names.raw(b'B341')])
    group_type = ['PTCLASS ' + names.value(b'Def341\\A341'), 'PTCLASS ' + names.value(b'Def341\\B341')]
    check('dnf-self-stays-partial', '$hook_short_reference_nominal_dnf_header(' + union([grouped, raw]) + ',' + branches([group_type, [atom]]) + ',' + lexical + ')', False)
    check('mixed-dnf-self-stays-partial', '$hook_short_reference_mixed_nominal_dnf_header(' + union([grouped, raw, names.raw(b'int', 'NIdentifier')]) + ',' + branches([group_type, [atom], ['PTBUILTIN "int"']]) + ',' + lexical + ')', False)

    # Exactly these two old323 guards change meaning; their historical cut is not renewed.
    for nullable in (False, True):
        check('promoted-old323-NName-' + str(nullable), '$hook_short_reference_scoped_header(' + names.raw(b'SeLf', 'NName', nullable) + ',' + names.mask(b'Def323\\Box323', nullable) + ',' + names.context() + ')')
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
              'source_agreement_credit': 0, 'native_observations': 0, 'promoted_old323_queries': 2, 'passed': False}
    try:
        rows = assertions(); report['premises'] = len(rows)
        (out / 'assertions.json').write_text(json.dumps(rows, indent=2) + '\n')
        fixture = out / 'protocol.watsup'
        fixture.write_text('dec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + row['premise'] + '\n' for row in rows))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(fixture)], out / 'check', 60)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after']
                            and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed'], report.get('stderr', '')[:2000]
    print('pass', report['premises'], 'independent self header assertions, source0')


if __name__ == '__main__':
    main()
