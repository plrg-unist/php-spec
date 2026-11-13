#!/usr/bin/env python3
"""Check actual untyped block SET parameters, statement tasks and physical release."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import deprecated_reference_object_untyped_short_set_explicit_protocol as short
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_set_explicit')
sources = {'single': SOURCE / 'untyped-set-explicit-singleton.php', 'vector': SOURCE / 'untyped-set-explicit-vector.php'}
EXECUTION_SOURCE = SOURCE / 'untyped-set-explicit-execution.php'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = short.quoted
PREFIX = short.PREFIX
SELECTED = short.SELECTED
RECEIVE_SELECTED = short.RECEIVE_SELECTED.replace('269', '270').replace('$short_parameter_', '$block_parameter_').replace('S.TODO = (EVAL expression) :: ptask*', 'S.TODO = (STMT statement) :: ptask*')


def named(name, cls):
    namespace = 'Ns270UntypedSetExplicit' + ('Single' if name == 'single' else 'Vector')
    return quoted((namespace + chr(92) + cls.replace('269', '270')).encode())


short.sources = sources
short.EXECUTION_SOURCE = EXECUTION_SOURCE
short.named = named


def adjusted(check):
    return check.replace('269', '270').replace('$short_parameter_', '$block_parameter_').replace(
        quoted(b'Ns269UntypedShortSetExplicitExecution\\Box269'),
        quoted(b'Ns270UntypedSetExplicitExecution\\Box270'))


def inventory(fixtures):
    checks = []
    for check in short.inventory(fixtures):
        check = adjusted(check)
        for name in sources:
            check = check.replace('phpType39_' + name + '_tag = expression_set_' + name,
                'phpType39_' + name + '_tag = SEQUENCE statement_set_' + name + '*')
            check = check.replace('~$hook_body_backed(phpType39_' + name + '_tag,',
                '$hook_body_backed(phpType39_' + name + '_tag,')
            check = check.replace('$property_set_expression(S_raw_' + name + ',porigin_hook_' + name + '_tag) = ((ppropertydesc_' + name + '_tag,expression_set_' + name + ',z_hook_' + name + '))',
                '$property_set_expression(S_raw_' + name + ',porigin_hook_' + name + '_tag) = eps')
        checks.append(check)
    return checks


def boundaries():
    checks = []
    for check in short.boundaries():
        check = adjusted(check)
        if 'S_receipt_code' in check:
            continue
        check = check.replace('$property_set_expression(S_receipt_base,porigin_hook_single_tag) = ((ppropertydesc_single_tag,expression_set_single,z_hook_single))',
            '$property_set_expression(S_receipt_base,porigin_hook_single_tag) = eps')
        if check.startswith('S_wrong_child = '):
            checks.append('phpType38_wrong_body = NPropertyHook phpType14_single_tag phpType24_single_tag phpType4_single_tag phpType11_single_tag phpType16_single_tag (SEQUENCE eps) metadata_single_tag')
            check = 'S_wrong_child = S_class_single[.SOURCES = [pcunit_single[.OCCURRENCES = (PCOCCURRENCE pcpath_hook_single phpType38_wrong_body) :: pcunit_single.OCCURRENCES]]]'
        checks.append(check)
        if check == '$property_set_expression(S_receipt_base,porigin_hook_single_tag) = eps':
            checks.append('$function_body_tasks(S_receipt_base,pfunction_set_single) = $statement_tasks(statement_set_single*,(PORIGIN n_source_single pfunction_set_single.BODY),0) ++ [$function_fallthrough(S_receipt_base,pfunction_set_single)]')
    return checks


def compiler():
    return [adjusted(check) for check in short.compiler()]


def lifecycle():
    return [adjusted(check) for check in short.lifecycle()]


def reception(fixture):
    checks = []
    for check in short.reception(fixture):
        check = adjusted(check).replace('(SEQUENCE ([phpType17_receive])) expression_receive metadata_receive_hook',
            '(SEQUENCE ([phpType17_receive])) (SEQUENCE statement_receive*) metadata_receive_hook')
        check = check.replace('$property_set_expression(S_receive,pfunction_receive.ORIGIN) = ((ppropertydesc_receive,expression_receive,z_receive_hook))',
            '$property_set_expression(S_receive,pfunction_receive.ORIGIN) = eps')
        check = check.replace('S_receive.TODO = (EVAL expression_receive) :: ptask_receive_tail*',
            'S_receive.TODO = (STMT statement_receive*[0]) :: ptask_receive_tail*')
        checks.append(check)
        if check == '$property_set_expression(S_receive,pfunction_receive.ORIGIN) = eps':
            checks.append('$function_body_tasks(S_receive,pfunction_receive) = $statement_tasks(statement_receive*,(PORIGIN n_receive_unit pfunction_receive.BODY),0) ++ [$function_fallthrough(S_receive,pfunction_receive)]')
        if check == 'S_receive.TODO = (STMT statement_receive*[0]) :: ptask_receive_tail*':
            checks.append('S_receive.ORIGIN = (PORIGIN n_receive_unit (pcpath_receive_hook ++ [PCFIELD 5,PCINDEX 0]))')
    return checks


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args(); out=args.output.resolve(); out.mkdir(parents=True,exist_ok=False)
    modules=[ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths=[Path(__file__),*sources.values(),EXECUTION_SOURCE,*modules,*(ROOT / p for p in (
        'spec/semantics/modules.json','spec/php.watsup','spec/schema.json','frontend/worker.php',
        'tests/semantics/deprecated_reference_object_untyped_short_set_explicit_protocol.py',
        'tests/semantics/deprecated_reference_object_typed_class_protocol.py',
        'tests/semantics/deprecated_reference_object_fields_protocol.py',
        'tests/semantics/deprecated_class_constant_fetch_protocol.py','tests/semantics/deprecated_parameter_default_protocol.py',
        'tests/semantics/deprecated_global_constant_protocol.py','tests/semantics/recorded_worker.py',
        'tests/semantics/error_handler_run.py','tests/semantics/static_types.py','tests/semantics/profile.json',
        '.tools/php/bin/php','.tools/php-file.so','_build/default/adapter/main.exe',
        'tests/semantics/_build/default/numeric_runner.exe'))]
    before={str(p.relative_to(ROOT)):sha(p) for p in paths}
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    report={'head':head,'inputs':before,'module_count':len(modules),'source_agreement_credit':0,'passed':False}
    try:
        frontend=Worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT / '.tools/php-file.so'),str(ROOT / 'frontend/worker.php')],out / 'frontend')
        adapter=Worker([str(ROOT / '_build/default/adapter/main.exe'),str(ROOT)],out / 'adapter')
        fixtures={}
        try:
            for name,source in {**sources,'receive':EXECUTION_SOURCE}.items():
                parsed=frontend.request({'op':'parse','source':base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted'] and not parsed['diagnostics']
                checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True}); assert checked['ok']
                fixtures[name]=checked['fixture']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks=inventory(fixtures)+boundaries()+compiler()+lifecycle()+reception(fixtures['receive']); report['premises']=len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks,indent=2)+'\n')
        (out / 'protocol.watsup').write_text(PREFIX+SELECTED+RECEIVE_SELECTED+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+c+'\n' for c in checks))
        report['process']=recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),'--sl',*map(str,modules),str(out / 'protocol.watsup')],out / 'check',240)
        report['stdout']=(out / 'check.stdout').read_text(); report['stderr']=(out / 'check.stderr').read_text()
        report['head_stable']=head==subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        report['inputs_stable']=before=={str(p.relative_to(ROOT)):sha(p) for p in paths}
        report['passed']=(report['process']['exit']==0 and not report['process']['timeout'] and not report['process']['group_after']
            and report['stdout']=='true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report,indent=2)+'\n')
    if not report['passed']: print(report.get('stdout','')[:2000],report.get('stderr','')[:4000])
    assert report['passed']; print('pass',report['premises'])


if __name__ == '__main__': main()
