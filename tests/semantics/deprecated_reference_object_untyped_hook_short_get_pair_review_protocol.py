#!/usr/bin/env python3
"""Check both short hooks, getter return receipts and outside ownership."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import deprecated_reference_object_untyped_hook_pair_no_default_review_protocol as block
pair = block.pair
peer = block.peer
header = block.header
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_hook_short_get_pair_review') / 'nested-untyped-hook-short-get-pair-shared.php'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = peer.quoted
PREFIX = block.PREFIX
SELECTED = block.SELECTED


def fields(fixture):
    block.SOURCE = SOURCE
    oldroot = quoted('Ns276UntypedHookPairNoDefaultPeer' + chr(92) + 'Root276')
    root = quoted('Ns278UntypedHookShortGetPairPeer' + chr(92) + 'Root278')
    checks = []
    for check in block.fields(fixture):
        if check.startswith('U = '):
            checks.append(check); continue
        check = check.replace(oldroot,root).replace('276','278')
        if check.startswith('$function_body_tasks(S_raw,pfunction_get) = '):
            checks += ['$origin_node(S_raw.SOURCES,PORIGIN n_source pfunction_get.BODY) = (expression_get)',
                '$code_expression(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = ((z_expr,false))',
                '$arrow_line(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = (z_arrow)',
                'z_expr = $source_line(metadata_get)', 'z_arrow = z_expr',
                'z_expr = $source_end_line(metadata_get)',
                '$function_body_tasks(S_raw,pfunction_get) = [$at_task((PORIGIN n_source pfunction_get.BODY),EVAL expression_get),RETURN_VALUE z_arrow]']
            continue
        if check.startswith('$function_body_tasks(S_raw,pfunction_set) = '):
            checks += ['$origin_node(S_raw.SOURCES,PORIGIN n_source pfunction_set.BODY) = (expression_set)',
                '$code_expression(pfunction_set.CODE.EXPRESSIONS,pfunction_set.BODY) = ((z_set_rhs,false))',
                'z_set_hook = $source_line(metadata_set)', 'z_set_rhs = z_set_hook',
                '$property_set_expression(S_raw,porigin_set) = ((ppropertydesc_rootpad,expression_set,z_set_hook))']
            continue
        check = check.replace('(SEQUENCE statement_get*)','expression_get').replace('SEQUENCE statement_get*','expression_get')
        check = check.replace('(SEQUENCE statement_set*)','expression_set').replace('SEQUENCE statement_set*','expression_set')
        if check.startswith('$hook_body_backed(expression_set,'):
            check = '~' + check
        checks.append(check)
    expr = '(CODEEXPR pfunction_get.BODY z_expr false)'
    arrow = '(CODEARROW pfunction_get.BODY z_arrow)'
    extra = []
    for name, receipt in [('no_expr','[' + arrow + ']'), ('no_arrow','[' + expr + ']'),
            ('expr_zero','[(CODEEXPR pfunction_get.BODY 0 false),' + arrow + ']'),
            ('arrow_zero','[' + expr + ',(CODEARROW pfunction_get.BODY 0)]'),
            ('expr_after','[(CODEEXPR pfunction_get.BODY $(z_expr + 1) false),' + arrow + ']'),
            ('arrow_after','[' + expr + ',(CODEARROW pfunction_get.BODY $(z_arrow + 1))]')]:
        state = 'S_code_' + name
        extra += [state + ' = S_functions[.FUNCTIONS = [pfunction_get[.CODE.EXPRESSIONS = ' + receipt + '],pfunction_set]]',
            '$property_hook_pair_origins(' + state + ',ppropertydesc_rootpad) = eps',
            '$property_hook_origin(' + state + ',ppropertydesc_rootpad) = eps',
            '$property_set_origin(' + state + ',ppropertydesc_rootpad) = eps']
    extra += ['S_child = S_class[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pfunction_get.BODY (NScalarInt (INTEGER 0) eps)) :: pcunit.OCCURRENCES]]]',
        '$property_hook_pair_origins(S_child,ppropertydesc_rootpad) = eps',
        '$property_hook_origin(S_child,ppropertydesc_rootpad) = eps',
        '$property_set_origin(S_child,ppropertydesc_rootpad) = eps',
        '~$class_constant_reference_object_graph(S_child,n_receiver,eps)']
    extra += ['S_set_code = S_functions[.FUNCTIONS = [pfunction_get,pfunction_set[.CODE.EXPRESSIONS = eps]]]',
        '$property_hook_pair_origins(S_set_code,ppropertydesc_rootpad) = eps',
        '$property_hook_origin(S_set_code,ppropertydesc_rootpad) = eps',
        '$property_set_origin(S_set_code,ppropertydesc_rootpad) = eps',
        '$property_set_expression(S_set_code,porigin_set) = eps',
        'S_set_child = S_class[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pfunction_set.BODY (NScalarInt (INTEGER 0) eps)) :: pcunit.OCCURRENCES]]]',
        '$property_hook_pair_origins(S_set_child,ppropertydesc_rootpad) = eps',
        '$property_hook_origin(S_set_child,ppropertydesc_rootpad) = eps',
        '$property_set_origin(S_set_child,ppropertydesc_rootpad) = eps',
        '~$class_constant_reference_object_graph(S_set_child,n_receiver,eps)']
    at = checks.index('S_neutral = $class_constant_class_forward(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)')
    checks[at:at] = extra
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(block.__file__), Path(pair.__file__), Path(peer.__file__), Path(header.__file__), SOURCE, *modules, *(ROOT / p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php', 'frontend/SourcePrinter.php',
        'tests/semantics/deprecated_class_constant_fetch_protocol.py', 'tests/semantics/deprecated_parameter_default_protocol.py',
        'tests/semantics/deprecated_global_constant_protocol.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py', 'tests/semantics/profile.json',
        '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe',
        'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(SOURCE.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks = fields(checked['fixture']); report['premises'] = len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        (out / 'protocol.watsup').write_text(PREFIX + SELECTED + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + c + '\n' for c in checks))
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
