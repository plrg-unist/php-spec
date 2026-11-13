#!/usr/bin/env python3
"""Check actual untyped block SET parameters and nested physical cleanup."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import deprecated_reference_object_untyped_set_review_protocol as block
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_set_explicit_review') / 'nested-untyped-set-explicit-shared.php'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def fields(fixture):
    block.SOURCE = SOURCE
    replacements = {block.quoted('Ns267UntypedSetPeer\\' + name + '267'):
        block.quoted('Ns270UntypedSetExplicitPeer\\' + name + '270') for name in ('Root', 'Middle', 'Leaf')}
    checks = []
    for check in block.fields(fixture):
        if check.startswith('U = '):
            checks.append(check)
            continue
        for old, new in replacements.items(): check = check.replace(old, new)
        check = check.replace('267', '270')
        for field, name in [('rootpad', 'outerValue270'), ('middlepad', 'innerValue270')]:
            if check == 'phpType16_' + field + ' = SEQUENCE eps':
                check = 'phpType16_' + field + ' = SEQUENCE ([phpType17_parameter_' + field + '])'
            check = check.replace('psparam_' + field + '.NAME = $ptascii("value")',
                'psparam_' + field + '.NAME = $ptascii("' + name + '")')
        if check == '$class_constant_reference_object_graph(S_missing,n_receiver,eps)': check = '~' + check
        checks.append(check)
    extra = []
    for field in ('rootpad', 'middlepad'):
        origin = 'porigin_set_' + field; function = 'pfunction_set_' + field; param = 'phpType17_parameter_' + field
        extra += [param + ' = NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN false) (BOOLEAN false) (NExprVariable (BYTES text_parameter_' + field + ') metadata_parameter_name_' + field + ') ABSENT (SEQUENCE eps) metadata_parameter_' + field,
            '~$property_set_parameters(phpType16_' + field + ')',
            '$property_set_untyped_parameters(phpType16_' + field + ')',
            '~$property_set_explicit_origin(S_raw,' + origin + ')',
            'psparam_' + field + '.NAME = $base64(text_parameter_' + field + ')',
            '$origin_source(' + origin + ') = PORIGIN n_source_' + field + ' pcpath_hook_' + field,
            '$origin_node(S_raw.SOURCES,PORIGIN n_source_' + field + ' (pcpath_hook_' + field + ' ++ [PCFIELD 4,PCINDEX 0])) = (' + param + ')',
            function + '.BODY = pcpath_hook_' + field + ' ++ [PCFIELD 5]',
            function + '.DEFAULTS = eps', '~' + function + '.EARLY',
            '$function_body_tasks(S_raw,' + function + ') = $statement_tasks(statement_' + field + '*,(PORIGIN n_source_' + field + ' ' + function + '.BODY),0) ++ [$function_fallthrough(S_raw,' + function + ')]']
    at = checks.index('S_class = $class_constant_selector(S_raw,expression_class,z)')
    checks[at:at] = extra
    extra = ['S_function_base = S_class[.FUNCTIONS = [pfunction_set_middlepad]]',
        '$property_set_origin(S_function_base,ppropertydesc_middlepad) = (porigin_set_middlepad)',
        '$class_constant_reference_object_graph(S_function_base,n_middle,[n_receiver])']
    for tag, change in [
        ('name', '.NAME = $ptascii("wrong")'),
        ('parameter_name', '.SIGNATURE.PARAMETERS = [psparam_middlepad[.NAME = $ptascii("value")]]'),
        ('body', '.BODY = pcpath_hook_middlepad'),
        ('type', '.SIGNATURE.PARAMETERS = [psparam_middlepad[.TYPE = [PTBRANCH ([PTBUILTIN "mixed"])]]]'),
        ('byref', '.SIGNATURE.PARAMETERS = [psparam_middlepad[.BYREF = true]]'),
        ('optional', '.SIGNATURE.PARAMETERS = [psparam_middlepad[.REQUIRED = false]]'),
        ('returns', '.SIGNATURE.RETURNS = eps')]:
        state = 'S_function_' + tag
        extra += [state + ' = S_function_base[.FUNCTIONS = [pfunction_set_middlepad[' + change + ']]]',
            '$property_set_origin(' + state + ',ppropertydesc_middlepad) = eps',
            '~$class_constant_reference_object_untyped_hook_field(' + state + ',n_middle,ppropertydesc_middlepad,ppropertyslot_middlepad)',
            '~$class_constant_reference_object_graph(' + state + ',n_middle,[n_receiver])']
    extra += ['pcpath_parameter = pcpath_hook ++ [PCFIELD 4,PCINDEX 0]',
        'S_parameter_child = S_class[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_parameter (NScalarInt (INTEGER 0) eps)) :: pcunit.OCCURRENCES]]]',
        '$property_set_origin(S_parameter_child,ppropertydesc_middlepad) = eps',
        '~$class_constant_reference_object_graph(S_parameter_child,n_receiver,eps)']
    for tag, raw_type, byref, variadic, variable, default in [
        ('type', '(NIdentifier (BYTES "aW50") eps)', 'false', 'false', 'text_parameter_middlepad', 'ABSENT'),
        ('byref', 'ABSENT', 'true', 'false', 'text_parameter_middlepad', 'ABSENT'),
        ('variadic', 'ABSENT', 'false', 'true', 'text_parameter_middlepad', 'ABSENT'),
        ('default', 'ABSENT', 'false', 'false', 'text_parameter_middlepad', '(NScalarInt (INTEGER 0) eps)'),
        ('name', 'ABSENT', 'false', 'false', '"dmFsdWU="', 'ABSENT')]:
        param = 'phpType17_forged_' + tag; hook = 'phpType38_parameter_' + tag
        group = 'pcnode_parameter_' + tag; state = 'S_parameter_' + tag
        extra += [param + ' = NParam (SEQUENCE eps) (INTEGER 0) ' + raw_type + ' (BOOLEAN ' + byref + ') (BOOLEAN ' + variadic + ') (NExprVariable (BYTES ' + variable + ') metadata_parameter_name_middlepad) ' + default + ' (SEQUENCE eps) metadata_parameter_middlepad',
            hook + ' = NPropertyHook phpType14_middlepad phpType24_middlepad phpType4_middlepad phpType11_middlepad (SEQUENCE ([' + param + '])) phpType39_middlepad metadata_middlepad',
            group + ' = NStmtProperty phpType14_group phpType24_group ABSENT phpType56_group (SEQUENCE ([' + hook + '])) metadata_group',
            state + ' = S_class[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group ' + group + ') :: (PCOCCURRENCE pcpath_hook ' + hook + ') :: (PCOCCURRENCE pcpath_parameter ' + param + ') :: pcunit.OCCURRENCES]]]',
            '$property_set_origin(' + state + ',ppropertydesc_middlepad) = eps',
            '~$class_constant_reference_object_graph(' + state + ',n_receiver,eps)']
    extra += ['phpType38_arity = NPropertyHook phpType14_middlepad phpType24_middlepad phpType4_middlepad phpType11_middlepad (SEQUENCE ([phpType17_parameter_middlepad,phpType17_parameter_middlepad])) phpType39_middlepad metadata_middlepad',
        'pcnode_arity = NStmtProperty phpType14_group phpType24_group ABSENT phpType56_group (SEQUENCE ([phpType38_arity])) metadata_group',
        'S_arity = S_class[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group pcnode_arity) :: (PCOCCURRENCE pcpath_hook phpType38_arity) :: pcunit.OCCURRENCES]]]',
        '$property_set_origin(S_arity,ppropertydesc_middlepad) = eps',
        '~$class_constant_reference_object_graph(S_arity,n_receiver,eps)']
    at = checks.index('S_neutral = $class_constant_class_forward(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)')
    checks[at:at] = extra
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(block.__file__), SOURCE, *modules, *(ROOT / p for p in (
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
        (out / 'protocol.watsup').write_text(block.PREFIX + block.SELECTED + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + c + '\n' for c in checks))
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
