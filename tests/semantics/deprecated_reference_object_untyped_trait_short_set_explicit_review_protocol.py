#!/usr/bin/env python3
"""Check direct trait short SET expression receipts and outside-owner release."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import deprecated_reference_object_untyped_trait_set_explicit_review_protocol as trait
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_trait_short_set_explicit_review') / 'nested-untyped-trait-short-set-explicit-shared.php'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = trait.quoted


def fields(fixture):
    trait.SOURCE = SOURCE
    replacements = {quoted('Ns271UntypedTraitSetExplicitPeer' + chr(92) + name + '271'):
        quoted('Ns272UntypedTraitShortSetExplicitPeer' + chr(92) + name + '272') for name in ('Root', 'RootPad')}
    checks = []
    for check in trait.fields(fixture):
        if check.startswith('U = '):
            checks.append(check)
            continue
        for old, new in replacements.items(): check = check.replace(old, new)
        check = check.replace('271', '272')
        if check.startswith('$function_body_tasks(S_raw,pfunction_imported) = '):
            checks += ['$origin_node(S_raw.SOURCES,PORIGIN n_source pfunction_source.BODY) = (expression_set)',
                '$code_expression(pfunction_source.CODE.EXPRESSIONS,pfunction_source.BODY) = ((z_hook,false))',
                '$property_set_expression(S_raw,porigin_hook_source) = ((ppropertydesc_source,expression_set,z_hook))']
            continue
        check = check.replace('phpType16_hook (SEQUENCE statement_set*) metadata_hook', 'phpType16_hook expression_set metadata_hook')
        check = check.replace('$hook_body_backed(SEQUENCE statement_set*,ppropertydesc_source.NAME)',
            '~$hook_body_backed(expression_set,ppropertydesc_source.NAME)')
        check = check.replace('$property_set_expression(S_raw,porigin_hook) = eps',
            '$property_set_expression(S_raw,porigin_hook) = ((ppropertydesc_rootpad,expression_set,z_hook))')
        checks.append(check)
    extra = ['S_code = S_function_base[.FUNCTIONS = [pfunction_source[.CODE.EXPRESSIONS = eps]]]',
        '$property_set_origin(S_code,ppropertydesc_source) = eps',
        '$property_set_origin(S_code,ppropertydesc_rootpad) = eps',
        '~$class_constant_reference_object_graph(S_code,n_receiver,eps)',
        'S_child = S_class[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE (pcpath_hook ++ [PCFIELD 5]) (NScalarInt (INTEGER 0) eps)) :: pcunit.OCCURRENCES]]]',
        '$property_set_origin(S_child,ppropertydesc_source) = eps',
        '$property_set_origin(S_child,ppropertydesc_rootpad) = eps',
        '~$class_constant_reference_object_graph(S_child,n_receiver,eps)']
    at = checks.index('S_neutral = $class_constant_class_forward(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)')
    checks[at:at] = extra
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(trait.__file__), Path(trait.peer.__file__), Path(trait.peer.block.__file__), SOURCE, *modules, *(ROOT / p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
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
        (out / 'protocol.watsup').write_text(trait.peer.block.PREFIX + trait.peer.block.SELECTED + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + c + '\n' for c in checks))
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
