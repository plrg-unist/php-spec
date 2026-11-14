#!/usr/bin/env python3
"""Check strict ordered literal/null source headers and genuine typed aliases."""
import argparse
import base64
import json
from pathlib import Path
import subprocess

import literal_boolean_parentless_short_reference_get_hook_review_protocol as prior
import parentless_short_reference_get_hook_review_protocol as peer
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('union_literal_boolean_parentless_short_reference_get_hook_review')
PREFIX = prior.PREFIX.replace('302peer', '303peer')


def branches(kind, null_first):
    names = ['null', kind] if null_first else [kind, 'null']
    return '[' + ','.join('(PTBRANCH ([PTBUILTIN "' + name + '"]))' for name in names) + ']'


def raw_header(name, null_first):
    literal = 'NIdentifier (BYTES text_type_' + name + ') metadata_type_' + name
    null = 'NIdentifier (BYTES text_null_' + name + ') metadata_null_' + name
    members = [null, literal] if null_first else [literal, null]
    return 'NUnionType (SEQUENCE ([' + ','.join(members) + '])) metadata_union_' + name


def fields(fixture, source, form):
    null_first = form == 'null-literal'
    checks = prior.fields(fixture, source, 'nullable')
    checks = checks[:2] + [c.replace('302', '303') for c in checks[2:]]
    controls = [c for c in checks if c.lstrip('~').startswith('$hook_short_reference_header(NUnionType')]
    assert len(controls) == 2
    checks = [c.removeprefix('~') if c in controls else c for c in checks]
    for name, kind in (('f', 'false'), ('t', 'true')):
        old = 'phpType18_' + name + ' = NNullableType (NIdentifier (BYTES text_type_' + name + ') metadata_type_' + name + ') metadata_nullable_' + name
        assert checks.count(old) == 1
        checks[checks.index(old)] = 'phpType18_' + name + ' = ' + raw_header(name, null_first)
        old_type = 'ppropertydesc_' + name + '.TYPE = ' + branches(kind, False)
        assert checks.count(old_type) == 1
        checks[checks.index(old_type)] = 'ppropertydesc_' + name + '.TYPE = ' + branches(kind, null_first)
        checks += [
            '$base64(text_null_' + name + ') = $ptascii("null")',
            '~$hook_short_reference_header(phpType18_' + name + ',' + branches(kind, not null_first) + ')',
            '~$hook_short_reference_header(phpType18_' + name + ',' + branches('bool', null_first) + ')',
        ]
    checks += [
        '$source_unit(S_return.SOURCES,n_source) = (pcunit)',
        'statement_swapped = NStmtProperty (SEQUENCE eps) (INTEGER 1) (' + raw_header('f', not null_first) + ') (SEQUENCE ([NPropertyItem phpType40_f phpType5_f metadata_item_f])) (SEQUENCE ([phpType38_f])) metadata_group_f',
        'S_swapped = S_return[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group_f statement_swapped) :: pcunit.OCCURRENCES]]]',
        '~$property_hook_reference_decl(S_swapped,ppropertydesc_f)',
        '$property_hook_reference_expression_return(S_swapped,ppropertyhook.HOOK,4) = eps',
        '$property_current_line(S_swapped) = 0',
        '~$hook_short_reference_header(NUnionType (SEQUENCE ([NIdentifier (BYTES "ZmFsc2U=") eps,NIdentifier (BYTES "dHJ1ZQ==") eps])) eps,[(PTBRANCH ([PTBUILTIN "false"])),(PTBRANCH ([PTBUILTIN "true"]))])',
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['literal-null', 'null-literal'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    cases = json.loads((SOURCES/'cases.json').read_text())
    source = SOURCES/cases[args.form]['source']
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT/p for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(prior.__file__), Path(peer.__file__), prior.SOURCES/'cases.json', source, SOURCES/'cases.json', SOURCES/'hashes.json', *modules, *(ROOT/p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
        'frontend/SourcePrinter.php', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py',
        'tests/semantics/static_types.py', 'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): peer.sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'form': args.form,
              'mode': 'fixture-SL', 'source_agreement_credit': 0, 'passed': False}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension='+str(ROOT/'.tools/php-file.so'),
                           str(ROOT/'frontend/worker.php')], out/'frontend')
        adapter = Worker([str(ROOT/'_build/default/adapter/main.exe'), str(ROOT)], out/'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks = fields(checked['fixture'], source, args.form)
        report['premises'] = len(checks)
        (out/'assertions.json').write_text(json.dumps(checks, indent=2)+'\n')
        (out/'protocol.watsup').write_text(PREFIX+'\ndec $main() : bool\ndef $main() = true\n'
                                         + ''.join('  -- if '+check+'\n' for check in checks))
        report['process'] = recorded([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                      *map(str, modules), str(out/'protocol.watsup')], out/'check', 240)
        report['stdout'] = (out/'check.stdout').read_text(); report['stderr'] = (out/'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): peer.sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout']
                            and not report['process']['group_after'] and report['stdout'] == 'true\n'
                            and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    assert report['passed'], report.get('stderr', '')[:4000]
    print('pass', args.form, report['premises'])


if __name__ == '__main__':
    main()
