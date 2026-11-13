#!/usr/bin/env python3
"""Check own-class automatic short SET backing and physical child cleanup."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import deprecated_reference_object_untyped_set_backed_class_hook_pair_review_protocol as base
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('deprecated_reference_object_untyped_automatic_short_set_class_hook_pair_review')
sha = base.sha
actual_pair = base.actual_pair
PREFIX = base.PREFIX
SELECTED = base.SELECTED


def fields(fixture, source, actual):
    form = 'Actual' if actual else 'Implicit'
    old = 'Ns285SetBackedClass' + form + 'PairPeer' + chr(92) + 'Root285'
    new = 'Ns286AutomaticShortSetClass' + form + 'PairPeer' + chr(92) + 'Root286'
    checks = []
    for check in base.fields(fixture, source, actual):
        if check.startswith('U = '):
            checks.append(check)
            continue
        check = check.replace(base.quoted(old), base.quoted(new)).replace('285', '286')
        if 'phpType38_short_set' in check:
            continue
        if check == '$hook_body_backed(SEQUENCE statement_set*,ppropertydesc_rootpad.NAME)':
            checks.append('~$hook_body_backed(expression_set,ppropertydesc_rootpad.NAME)')
            continue
        check = check.replace('(SEQUENCE statement_set*)', 'expression_set').replace('SEQUENCE statement_set*', 'expression_set')
        check = check.replace('pcpath_get = pcpath_group ++ [PCFIELD 4,PCINDEX 0]',
                              'pcpath_get = pcpath_group ++ [PCFIELD 4,PCINDEX 1]')
        check = check.replace('pcpath_set = pcpath_group ++ [PCFIELD 4,PCINDEX 1]',
                              'pcpath_set = pcpath_group ++ [PCFIELD 4,PCINDEX 0]')
        check = check.replace('[phpType38_get,phpType38_set]', '[phpType38_set,phpType38_get]')
        check = check.replace('[phpType38_bad_get,phpType38_set]', '[phpType38_set,phpType38_bad_get]')
        check = check.replace('[phpType38_get,phpType38_bad_set]', '[phpType38_bad_set,phpType38_get]')
        if not actual:
            if check.startswith(('$origin_node(S_raw.SOURCES,PORIGIN n_source pfunction_get.BODY)',
                                 '$code_expression(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY)',
                                 '$arrow_line(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY)',
                                 '$(z_get >', '$hook_pair_parameter_get_receipts(',
                                 'S_get_code = ', '$property_hook_pair_origins(S_get_code,')):
                continue
            check = check.replace('(SEQUENCE eps) expression_get metadata_get',
                                  '(SEQUENCE eps) (SEQUENCE statement_get*) metadata_get')
            check = check.replace('(SEQUENCE eps) expression_get metadata_bad_get',
                                  '(SEQUENCE eps) (SEQUENCE statement_get*) metadata_bad_get')
            check = check.replace('$hook_body_backed(expression_get,', '$hook_body_backed(SEQUENCE statement_get*,')
        checks.append(check)
    receipts = [
        '$origin_node(S_raw.SOURCES,PORIGIN n_source pfunction_set.BODY) = (expression_set)',
        '$code_expression(pfunction_set.CODE.EXPRESSIONS,pfunction_set.BODY) = ((z_set,false))',
        r'$(z_set > 0 /\ z_set >= $source_line(metadata_set) /\ z_set <= $source_end_line(metadata_set))',
        '$property_set_expression(S_raw,porigin_set) = ((ppropertydesc_rootpad,expression_set,$source_line(metadata_set)))',
        'S_set_code = S_functions[.FUNCTIONS = [pfunction_get,pfunction_set[.CODE.EXPRESSIONS = eps]]]',
        '$property_hook_pair_origins(S_set_code,ppropertydesc_rootpad) = eps',
        '~$class_constant_reference_object_graph(S_set_code,n_receiver,eps)',
    ]
    if not actual:
        receipts += ['$function_body_tasks(S_raw,pfunction_get) = $statement_tasks(statement_get*,(PORIGIN n_source pfunction_get.BODY),0) ++ [$function_fallthrough(S_raw,pfunction_get)]']
    at = checks.index('S_step = $drive_steps(S_raw,1)')
    checks[at:at] = receipts
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['implicit', 'actual'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    source = SOURCES / ('automatic-short-set-untyped-class-' + args.form + '-pair-shared.php')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(base.__file__), Path(actual_pair.__file__), Path(actual_pair.implicit.__file__), Path(actual_pair.block.__file__),
             Path(actual_pair.pair.__file__), Path(actual_pair.peer.__file__), Path(actual_pair.header.__file__), source, *modules,
             *(ROOT / p for p in ('spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
                 'frontend/SourcePrinter.php', 'tests/semantics/deprecated_class_constant_fetch_protocol.py',
                 'tests/semantics/deprecated_parameter_default_protocol.py', 'tests/semantics/deprecated_global_constant_protocol.py',
                 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py',
                 'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe',
                 'tests/semantics/_build/default/numeric_runner.exe'))]
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
