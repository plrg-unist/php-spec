#!/usr/bin/env python3
"""Reach real short GET returns with either existing implicit SET body."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import deprecated_reference_object_untyped_pair_implicit_set_protocol as pair
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
BLOCK_SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_pair_short_get') / 'untyped-pair-short-get-execution.php'
SHORT_SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_pair_both_short') / 'untyped-pair-both-short-execution.php'
SOURCE = BLOCK_SOURCE
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
PAUSE = pair.PAUSE.replace('275', '278').replace(
    'pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n  -- if S.TODO = (STMT statement)',
    'pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n  -- if S.TODO = (EVAL expression)')


def fields(fixture):
    pair.SOURCE = SOURCE
    short = SOURCE == SHORT_SOURCE
    old_name = pair.b64(b'Ns275UntypedPairExecution\\Box275')
    new_name = pair.b64((b'Ns278UntypedPairBothShortExecution' if short else b'Ns278UntypedPairShortGetExecution') + b'\\Box278')
    checks = []
    for check in pair.fields(fixture):
        if not check.startswith('U = '):
            check = check.replace(old_name, new_name).replace('275', '278')
            check = check.replace('PROP_VALUE (DIRECT (PINT 17))', 'PROP_VALUE (DIRECT PNULL)')
            check = check.replace('(SEQUENCE statement_get*)', 'expression_get')
            check = check.replace('S_get.ORIGIN = (PORIGIN n_source (pfunction_get.BODY ++ [PCINDEX 0]))',
                'S_get.ORIGIN = (PORIGIN n_source pfunction_get.BODY)')
            if check.startswith('$function_body_tasks(S_get,pfunction_get) = '):
                checks += ['$origin_node(S_get.SOURCES,PORIGIN n_source pfunction_get.BODY) = (expression_get)',
                    '$code_expression(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = ((z_get_expr,false))',
                    '$arrow_line(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = (z_get_arrow)',
                    r'$(z_get_expr >= 5 /\ z_get_expr <= 8)',
                    r'$(z_get_arrow >= 5 /\ z_get_arrow <= 8)',
                    'S_get.TODO = (EVAL expression_get) :: (ORIGIN_RETURN (porigin_get)) :: (RETURN_VALUE z_get_arrow) :: ptask_get_tail*']
                check = '$function_body_tasks(S_get,pfunction_get) = [$at_task((PORIGIN n_source pfunction_get.BODY),EVAL expression_get),RETURN_VALUE z_get_arrow]'
            if short:
                check = check.replace('(SEQUENCE statement_set*)', 'expression_set')
                check = check.replace('S_set.ORIGIN = (PORIGIN n_source (pfunction_set.BODY ++ [PCINDEX 0]))',
                    'S_set.ORIGIN = (PORIGIN n_source pfunction_set.BODY)')
                if check.startswith('$function_body_tasks(S_set,pfunction_set) = '):
                    check = '$function_body_tasks(S_set,pfunction_set) = [$at_task((PORIGIN n_source pfunction_set.BODY),EVAL expression_set),AT pfunction_set.ORIGIN (ASSIGN_ARRAY (BASE_PROPERTY (POBJECT n_object) ppropertydesc.NAME) $source_line(metadata_set) false),DISCARD,$function_fallthrough(S_set,pfunction_set)]'
        checks.append(check)
    checks += ['ppropertydesc.DEFAULT = PROP_NULL',
        'ppropertydesc.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        '$origin_node(S_get.SOURCES,PORIGIN n_source pcpath_property) = (NPropertyItem (NVarLikeIdentifier (BYTES text_property) metadata_property_name) ABSENT metadata_property_item)',
        '$base64(text_property) = $ptascii("tag")',
        '$origin_node(S_get.SOURCES,PORIGIN n_source (pcpath_property ++ [PCFIELD 1])) = eps',
        '$pool_value(S_get.POOLS,PORIGIN n_source (pcpath_property ++ [PCFIELD 1])) = eps',
        '$property_default_state(S_get,ppropertydesc) = (PROP_VALUE (DIRECT PNULL))',
        '$property_hook_pair_backed(S_get,ppropertydesc)',
        '~$property_hook_virtual(S_get,ppropertydesc)',
        'pfunction_get.LINE = 5', 'pfunction_get.ENDLINE = 8',
        'pfunction_set.LINE = 9', 'pfunction_set.ENDLINE = ' + ('9' if short else '12'),
        'S_get.OBJECTS[n_object] = INSTANCE porigin_owner',
        '$node_children(S_get,HOBJECT n_object) = eps',
        'P = $ppstart(n_source,U,$base64(' + json.dumps(pair.b64(bytes(SOURCE))) + '))',
        'P.COMPLETION = PPCNORMAL',
        '$class_at(P.CLASSES,porigin_owner) = (pclassdesc_compiler)',
        'pclassdesc_compiler.PROPERTIES = [ppropertydesc]',
        '$function_at(P.FUNCTIONS,porigin_get) = (pfunction_get_compiler)',
        '$function_at(P.FUNCTIONS,porigin_set) = (pfunction_set_compiler)',
        'pfunction_get_compiler.SIGNATURE = pfunction_get.SIGNATURE',
        'pfunction_set_compiler.SIGNATURE = pfunction_set.SIGNATURE',
        'pfunction_get_compiler.BODY = pfunction_get.BODY',
        'pfunction_set_compiler.BODY = pfunction_set.BODY',
        'PPCCONSTANTS (pcpath_constant,pvalue_constant)* = $ppconstants(P)',
        '$ppconstant_at((pcpath_constant,pvalue_constant)*,pcpath_property ++ [PCFIELD 1]) = eps']
    if short:
        checks += ['$origin_node(S_set.SOURCES,PORIGIN n_source pfunction_set.BODY) = (expression_set)',
            '$code_expression(pfunction_set.CODE.EXPRESSIONS,pfunction_set.BODY) = ((z_set_rhs,false))',
            'z_set_rhs = 9',
            '$property_set_expression(S_set,porigin_set) = ((ppropertydesc,expression_set,9))',
            '~$hook_body_backed(expression_set,ppropertydesc.NAME)']
    return checks


def main():
    global SOURCE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--kind', required=True, choices=('block', 'short'))
    args = parser.parse_args(); SOURCE = SHORT_SOURCE if args.kind == 'short' else BLOCK_SOURCE
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(pair.__file__), BLOCK_SOURCE, SHORT_SOURCE, *modules, *(ROOT / p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
        'frontend/SourcePrinter.php', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py',
        'tests/semantics/static_types.py', 'tests/semantics/deprecated_class_constant_fetch_protocol.py',
        'tests/semantics/deprecated_parameter_default_protocol.py', 'tests/semantics/deprecated_global_constant_protocol.py',
        'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'source_agreement_credit': 0, 'kind': args.kind, 'passed': False}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': pair.b64(SOURCE.read_bytes())})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks = fields(checked['fixture']); report['premises'] = len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        pause = PAUSE.replace('pcallcontext.TARGET = PROPERTY_SET_TARGET ppropertyhook\n  -- if S.TODO = (STMT statement)', 'pcallcontext.TARGET = PROPERTY_SET_TARGET ppropertyhook\n  -- if S.TODO = (EVAL expression)') if args.kind == 'short' else PAUSE
        (out / 'protocol.watsup').write_text(pair.PREFIX + pair.SELECTED + pause + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + c + '\n' for c in checks))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after']
            and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    if not report['passed']: print(report.get('stdout', '')[:2000], report.get('stderr', '')[:4000])
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()
