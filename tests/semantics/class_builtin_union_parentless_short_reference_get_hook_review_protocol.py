#!/usr/bin/env python3
"""Independent nominal/builtin union shape, authority and order counterexamples."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import scoped_class_parentless_short_reference_get_hook_review_protocol as names
from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
HELPER = '$hook_short_reference_class_builtin_union_header'


def union(*members):
    return 'NUnionType (SEQUENCE ([' + ','.join(members) + '])) eps'


def mask(name, members):
    parts = ['(PTBRANCH ([PTCLASS ' + names.value(name) + ']))' if member is None
             else '(PTBRANCH ([PTBUILTIN "' + member + '"]))' for member in members]
    return '[' + ','.join(parts) + ']'


def raw_union(name, kind, members):
    return union(*(names.raw(name, kind) if member is None else names.raw(member.encode(), 'NIdentifier') for member in members))


def assertions():
    rows = []
    def check(label, ast, normalized, lexical, expected):
        rows.append({'id': label, 'expected': expected, 'premise': ('' if expected else '~') +
                     HELPER + '(' + ast + ',' + normalized + ',' + lexical + ')'})
    plain = names.context(namespace=b'Def332')
    imported = names.context(namespace=b'Def332', imports=((b'TU', b'Payload332\\Leaf'), (b'Prefix', b'Payload332')))
    contexts = [
        ('global', b'stdClass', 'NName', b'stdClass', names.context(namespace=b'')),
        ('local', b'Leaf', 'NName', b'Def332\\Leaf', plain),
        ('qualified-local', b'Nested\\Leaf', 'NName', b'Def332\\Nested\\Leaf', plain),
        ('alias-case', b'tU', 'NName', b'Payload332\\Leaf', imported),
        ('prefix-case', b'pReFiX\\lEaF', 'NName', b'Payload332\\lEaF', imported),
        ('relative', b'Leaf', 'NNameRelative', b'Def332\\Leaf', plain),
        ('relative-bypasses-alias', b'TU', 'NNameRelative', b'Def332\\TU', imported),
        ('fq-case', b'sTdClAsS', 'NNameFullyQualified', b'sTdClAsS', imported),
        ('fq-confusable-quiet', b'boolean', 'NNameFullyQualified', b'boolean', plain),
        ('relative-confusable-quiet', b'boolean', 'NNameRelative', b'Def332\\boolean', plain),
        ('high-byte', b'\x80Leaf', 'NName', b'Def332\\\x80Leaf', plain),
        ('underscore-component', b'Nested\\_', 'NName', b'Def332\\Nested\\_', plain),
    ]
    old_helpers = ['header', 'scoped_header', *('class_' + kind + '_header' for kind in ('null','false','true','bool','int','float','string','array'))]
    selections = [
        (['int','float'], contexts), (['array','true'], contexts),
        (['array','string','null','true'], [contexts[i] for i in (1,3,5,7)]),
        (['array','int','float','string','null','bool'], [contexts[i] for i in (1,5,7)]),
        (['array','int','float','string','null','false'], [contexts[3]]),
    ]
    for builtins, choices in selections:
        for label, raw_name, kind, resolved, lexical in choices:
            for position in range(len(builtins)+1):
                members = list(builtins); members.insert(position, None)
                prefix = label + '-' + '-'.join(builtins) + '-class' + str(position)
                ast = raw_union(raw_name, kind, members); normalized = mask(resolved, members)
                check(prefix, ast, normalized, lexical, True)
                check(prefix+'-normalized-reversed', ast, mask(resolved, list(reversed(members))), lexical, False)
                check(prefix+'-class-case', ast, mask(resolved.swapcase(), members), lexical, False)
                check(prefix+'-class-bytes', ast, mask(resolved+b'X', members), lexical, False)
                for helper in old_helpers:
                    args = ast+','+normalized+('' if helper=='header' else ','+lexical)
                    rows.append({'id':prefix+'-old-'+helper, 'expected':False,
                                 'premise':'~$hook_short_reference_'+helper+'('+args+')'})
    members=[None,'int','float']; cls=names.raw(b'Leaf')
    ast=raw_union(b'Leaf','NName',members); normalized=mask(b'Def332\\Leaf',members)
    check('consumer-shadow',ast,normalized,names.context(namespace=b'Other332',imports=((b'Leaf',b'stdClass'),)),False)
    check('missing-file',ast,normalized,names.context(namespace=b'Def332',file=b''),False)
    check('missing-line',ast,normalized,names.context(namespace=b'Def332',line=0),False)
    for wrong in (b'',b'_',b'\\Leaf',b'Leaf\\',b'Leaf\\\\Child',b'1Leaf',b'Leaf\x00',b'Leaf-Child',b'self',b'parent',b'static',b'int',b'float',b'array',b'bool',b'string',b'null',b'true',b'false',b'object',b'mixed',b'callable',b'iterable',b'void',b'never',b'Nested\\INT'):
        for kind in ('NName','NNameRelative','NNameFullyQualified'):
            resolved=wrong if kind=='NNameFullyQualified' else b'Def332\\'+wrong
            check('invalid-class-'+kind+'-'+wrong.hex(),raw_union(wrong,kind,members),mask(resolved,members),plain,False)
    for wrong in (b'boolean',b'integer',b'double',b'resource'):
        check('ordinary-warning-'+wrong.decode(),raw_union(wrong,'NName',members),mask(b'Def332\\'+wrong,members),plain,False)
    for kind in ('NName','NNameRelative','NNameFullyQualified'):
        check('builtin-is-name-'+kind,union(cls,names.raw(b'int',kind),names.raw(b'float','NIdentifier')),normalized,plain,False)
    for wrong in ('object','mixed','callable','iterable','void','never','resource','', 'int\\Leaf', 'int\x00'):
        altered=[None,'int',wrong]
        malformed_text = '\\' in wrong or '\x00' in wrong
        expected_mask = normalized if malformed_text else mask(b'Def332\\Leaf',altered)
        check('unsupported-builtin-'+wrong.encode().hex(),raw_union(b'Leaf','NName',altered),expected_mask,plain,False)
    malformed=[
        ('no-builtin',[None]),('one-builtin',[None,'int']),('no-class',['int','float','array']),
        ('duplicate-int',[None,'int','int']),('bool-true',[None,'bool','true']),
        ('bool-false',[None,'bool','false']),('true-false',[None,'true','false']),
        ('too-many',[None,'array','int','float','string','null','bool','true']),
    ]
    for label,altered in malformed:
        check(label,raw_union(b'Leaf','NName',altered),mask(b'Def332\\Leaf',altered),plain,False)
    check('empty-raw',union(),normalized,plain,False)
    check('two-classes',union(cls,names.raw(b'Other'),names.raw(b'int','NIdentifier')),
          '[(PTBRANCH ([PTCLASS '+names.value(b'Def332\\Leaf')+'])),(PTBRANCH ([PTCLASS '+names.value(b'Def332\\Other')+'])),(PTBRANCH ([PTBUILTIN "int"]))]',plain,False)
    check('class-Identifier',raw_union(b'Leaf','NIdentifier',members),normalized,plain,False)
    check('nullable-wrapper','NNullableType ('+cls+') eps',normalized,plain,False)
    check('intersection-class',union('NIntersectionType (SEQUENCE (['+cls+','+names.raw(b'Other')+'])) eps',names.raw(b'int','NIdentifier'),names.raw(b'float','NIdentifier')),normalized,plain,False)
    for label, altered in [('empty','eps'),('missing',mask(b'Def332\\Leaf',[None,'int'])),('extra',mask(b'Def332\\Leaf',[None,'int','float','array'])),('wrong-kind',mask(b'Def332\\Leaf',[None,'int','string']))]:
        check('normalized-'+label,ast,altered,plain,False)
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
    print('pass', report['premises'], 'independent nominal/builtin assertions, source0')


if __name__ == '__main__':
    main()
