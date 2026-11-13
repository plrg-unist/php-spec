#!/usr/bin/env python3
"""Check SET-backed trait pairs, constant GET receipts and shared cleanup."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import deprecated_reference_object_untyped_parented_trait_hook_pair_review_protocol as base
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('deprecated_reference_object_untyped_set_backed_trait_hook_pair_review')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
PREFIX = base.PREFIX.replace('281', '283')
SELECTED = base.SELECTED


def fields(fixture, source, actual):
    form = 'Actual' if actual else 'Implicit'
    old = 'Ns281ParentedTrait' + form + 'PairPeer' + chr(92)
    new = 'Ns283SetBackedTrait' + form + 'PairPeer' + chr(92)
    quoted = base.base.quoted
    body_queries = {
        'phpType39_get = expression_get', 'phpType39_set = expression_set',
        'phpType39_get = SEQUENCE statement_get*', 'phpType39_set = SEQUENCE statement_set*',
        '$code_expression(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = ((z_get,false))',
        '$arrow_line(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = (z_get)',
        '$code_expression(pfunction_set.CODE.EXPRESSIONS,pfunction_set.BODY) = ((z_set,false))',
        '$origin_node(S_raw.SOURCES,PORIGIN n_source pfunction_get.BODY) = (expression_get)',
        '$origin_node(S_raw.SOURCES,PORIGIN n_source pfunction_set.BODY) = (expression_set)',
    }
    checks = []
    for check in base.fields(fixture, source, actual):
        if check.startswith('U = '):
            checks.append(check)
            continue
        for name in ('Root', 'RootPad', 'Parent'):
            check = check.replace(quoted(old + name + '281'), quoted(new + name + '283'))
        check = check.replace('281', '283')
        if check in body_queries:
            continue
        if check == '$hook_body_backed(phpType39_get,ppropertydesc_source.NAME)':
            checks += [
                'phpType39_get = expression_get', 'phpType39_set = SEQUENCE statement_set*',
                '~$hook_body_backed(expression_get,ppropertydesc_source.NAME)',
                '$hook_body_backed(SEQUENCE statement_set*,ppropertydesc_source.NAME)',
                '~$hook_pair_untyped_parameter_headers(phpType38_get,phpType38_set,ppropertydesc_source.NAME)',
                ('' if actual else '~') + '$hook_pair_untyped_trait_set_backed_headers(phpType38_get,phpType38_set,ppropertydesc_source.NAME)',
                'phpType38_no_backing_set = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) phpType11_set phpType16_set (SEQUENCE eps) metadata_set',
                '~$hook_pair_untyped_trait_headers(phpType38_get,phpType38_no_backing_set,ppropertydesc_source.NAME)',
                '~$hook_pair_untyped_trait_bodies(expression_get,SEQUENCE eps,ppropertydesc_source.NAME)',
            ]
            continue
        checks.append(check)
    at = checks.index('pfunction_set.BODY = pcpath_set ++ [PCFIELD 5]') + 1
    checks[at:at] = [
        '$origin_node(S_raw.SOURCES,PORIGIN n_source pfunction_get.BODY) = (expression_get)',
        '$origin_node(S_raw.SOURCES,PORIGIN n_source pfunction_set.BODY) = (SEQUENCE statement_set*)',
        '$code_expression(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = ((z_get,false))',
        '$arrow_line(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = (z_get)',
        r'$(z_get > 0 /\ z_get >= $source_line(metadata_get) /\ z_get <= $source_end_line(metadata_get))',
    ]
    if not actual:
        at = checks.index('S_functions = S_class[.FUNCTIONS = [pfunction_get,pfunction_set]]') + 1
        checks[at:at] = [
            'S_get_code = S_functions[.FUNCTIONS = [pfunction_get[.CODE.EXPRESSIONS = eps],pfunction_set]]',
            '$property_hook_pair_origins(S_get_code,ppropertydesc_source) = eps',
            '$property_hook_trait_pair_functions(S_get_code,ppropertydesc_rootpad) = eps',
            '~$class_constant_reference_object_graph(S_get_code,n_receiver,eps)',
        ]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['implicit', 'actual'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    source = SOURCES / ('set-backed-untyped-trait-' + args.form + '-pair-shared.php')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(base.__file__), Path(base.base.__file__), Path(base.base.pair.__file__),
             Path(base.base.peer.__file__), Path(base.base.header.__file__), source, *modules, *(ROOT / p for p in (
                 'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
                 'frontend/SourcePrinter.php', 'tests/semantics/deprecated_class_constant_fetch_protocol.py',
                 'tests/semantics/deprecated_parameter_default_protocol.py', 'tests/semantics/deprecated_global_constant_protocol.py',
                 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py',
                 'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
                 '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'form': args.form,
              'mode': 'fixture-SL', 'source_agreement_credit': 0, 'passed': False}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks = fields(checked['fixture'], source, args.form == 'actual'); report['premises'] = len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        (out / 'protocol.watsup').write_text(PREFIX + SELECTED + '\ndec $main() : bool\ndef $main() = true\n'
                                           + ''.join('  -- if ' + c + '\n' for c in checks))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                      *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout']
                            and not report['process']['group_after'] and report['stdout'] == 'true\n'
                            and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed'], report.get('stderr', '')[:4000]
    print('pass', args.form, report['premises'])


if __name__ == '__main__': main()
