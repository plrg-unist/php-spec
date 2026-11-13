#!/usr/bin/env python3
"""Check implicit trait short SET source absence, header facts and real reception."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import deprecated_reference_object_untyped_trait_short_set_explicit_protocol as trait
import property_hook_header_presence_review_protocol as header
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_trait_implicit_short_set')
sources = {'single': SOURCE / 'untyped-trait-implicit-short-set-singleton.php',
    'vector': SOURCE / 'untyped-trait-implicit-short-set-vector.php'}
EXECUTION_SOURCE = SOURCE / 'untyped-trait-implicit-short-set-execution.php'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = trait.quoted
PREFIX = trait.PREFIX + header.PREFIX.replace('var U : program', '')
SELECTED = trait.SELECTED
RECEIVE_SELECTED = trait.short.RECEIVE_SELECTED.replace('269', '274').replace('input274', 'value')
trait.sources = sources
trait.short.EXECUTION_SOURCE = EXECUTION_SOURCE
trait.named = lambda name, cls: quoted(('Ns274UntypedTraitImplicitShortSet' + ('Single' if name == 'single' else 'Vector') + chr(92) + cls.replace('272', '274')).encode())


def inventory(fixtures):
    checks = []
    for check in trait.inventory(fixtures):
        if check.startswith('U_'):
            checks.append(check); continue
        check = check.replace('272', '274').replace('incoming274', 'value').replace('received274', 'value')
        for tag in ['single', 'vector']:
            check = check.replace('$property_set_untyped_parameters(SEQUENCE ([phpType17_parameter_' + tag + ']))', '~$property_set_untyped_parameters(SEQUENCE eps)')
            check = check.replace('(SEQUENCE ([phpType17_parameter_' + tag + ']))', '(SEQUENCE eps)')
            check = check.replace('= (phpType17_parameter_' + tag + ')', '= eps')
        checks.append(check)
    for tag in ['single', 'vector']:
        checks += ['$hook_parameter_facts(metadata_hook_' + tag + ') = [false]',
            '$property_set_parameters(SEQUENCE eps)',
            '$code_expression(pfunction_source_' + tag + '.CODE.EXPRESSIONS,pcpath_hook_' + tag + ' ++ [PCFIELD 4,PCINDEX 0]) = eps',
            '$ptascii("value") <- pfunction_source_' + tag + '.CVS']
    assert not any('phpType17_parameter' in c for c in checks)
    return checks


def boundaries():
    checks = [c.replace('272', '274') for c in trait.boundaries()]
    checks += ['pcpath_group_single = pcpath_hook_single[0:$nabs($( |pcpath_hook_single| - 2))]',
        '$origin_node(S_class_single.SOURCES,PORIGIN n_source_single pcpath_group_single) = (NStmtProperty phpType14_group (INTEGER flags_group) ABSENT phpType56_group (SEQUENCE ([NPropertyHook phpType14_single phpType24_single phpType4_single phpType11_single (SEQUENCE eps) expression_set_single metadata_hook_single])) metadata_group)']
    for name, fact in [('empty', '(MhookParameterList true) :: eps'), ('unknown', 'eps')]:
        hook = 'phpType38_' + name
        checks += ['metadata_' + name + ' = (' + fact + ') ++ $hpr_without_fact(metadata_hook_single)',
            hook + ' = NPropertyHook phpType14_single phpType24_single phpType4_single phpType11_single (SEQUENCE eps) expression_set_single metadata_' + name,
            'pcnode_' + name + ' = NStmtProperty phpType14_group (INTEGER flags_group) ABSENT phpType56_group (SEQUENCE ([' + hook + '])) metadata_group',
            'S_header_' + name + ' = S_class_single[.SOURCES = [pcunit_single[.OCCURRENCES = (PCOCCURRENCE pcpath_group_single pcnode_' + name + ') :: (PCOCCURRENCE pcpath_hook_single ' + hook + ') :: pcunit_single.OCCURRENCES]]]',
            '$property_set_origin_body(S_header_' + name + ',ppropertydesc_source_single) = (porigin_hook_source_single)',
            '$property_set_origin(S_header_' + name + ',ppropertydesc_source_single) = eps',
            '$property_set_origin(S_header_' + name + ',ppropertydesc_imported_single) = eps',
            '~$class_constant_reference_object_graph(S_header_' + name + ',n_owner_single,eps)']
    return checks


def reception(fixture):
    checks = []
    for check in trait.short.reception(fixture):
        if check.startswith('U_receive = '):
            checks.append(check); continue
        check = check.replace('269', '274').replace(quoted(rb'Ns269UntypedShortSetExplicitExecution\Box269'), quoted(rb'Ns274UntypedTraitImplicitShortSetExecution\Box274'))
        if check.startswith(('phpType17_receive = ', '$base64(text_receive_parameter)',
            '$default_parameter_origin(', '$origin_node(S_receive.SOURCES,$default_parameter_origin(')):
            continue
        check = check.replace('(SEQUENCE ([phpType17_receive]))', '(SEQUENCE eps)')
        check = check.replace('$default_parameter_line(S_receive,pfunction_receive.ORIGIN,0) = $psline(metadata_receive_parameter)',
            '$default_parameter_line(S_receive,pfunction_receive.ORIGIN,0) = $source_line(metadata_receive_hook)')
        if check == '$property_set_explicit_origin(S_receive,pfunction_receive.ORIGIN)': check = '~' + check
        if check == '$lookup(S_receive.ENV,$ptascii("value")) = eps': check = '$lookup(S_receive.ENV,$ptascii("input274")) = eps'
        elif check == '~($ptascii("value") <- pfunction_receive.CVS)': check = '~($ptascii("input274") <- pfunction_receive.CVS)'
        else: check = check.replace('input274', 'value')
        checks.append(check)
    checks += ['pcallcontext_receive.LEXICAL_CLASS = (porigin_receive_owner)',
        'pcallcontext_receive.CALLED_CLASS = (porigin_receive_owner)',
        'ppropertydesc_receive.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_receive_owner porigin_receive_source_property',
        'pfunction_receive.ORIGIN = TRAIT_ORIGIN porigin_receive_owner (PORIGIN n_receive_unit pcpath_receive_hook) ($property_set_name($ptascii("tag")))',
        '$function_at(S_receive.FUNCTIONS,pfunction_receive.ORIGIN) = eps',
        '$function_at($all_functions(S_receive),pfunction_receive.ORIGIN) = (pfunction_receive)',
        '$hook_parameter_facts(metadata_receive_hook) = [false]',
        '$origin_node(S_receive.SOURCES,PORIGIN n_receive_unit (pcpath_receive_hook ++ [PCFIELD 4,PCINDEX 0])) = eps',
        '$code_expression(pfunction_receive.CODE.EXPRESSIONS,pcpath_receive_hook ++ [PCFIELD 4,PCINDEX 0]) = eps',
        'S_receive.ORIGIN = (PORIGIN n_receive_unit (pcpath_receive_hook ++ [PCFIELD 5]))',
        '$function_body_tasks(S_receive,pfunction_receive) = [$at_task((PORIGIN n_receive_unit pfunction_receive.BODY),EVAL expression_receive),AT pfunction_receive.ORIGIN (ASSIGN_ARRAY (BASE_PROPERTY (POBJECT n_receive_object) ppropertydesc_receive.NAME) z_receive_hook false),DISCARD,$function_fallthrough(S_receive,pfunction_receive)]']
    return checks


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args(); out=args.output.resolve(); out.mkdir(parents=True,exist_ok=False)
    modules=[ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths=[Path(__file__),*sources.values(),EXECUTION_SOURCE,*modules,*(ROOT / p for p in (
        'spec/semantics/modules.json','spec/php.watsup','spec/schema.json','frontend/worker.php',
        'tests/semantics/deprecated_reference_object_untyped_trait_short_set_explicit_protocol.py',
        'tests/semantics/property_hook_header_presence_review_protocol.py',
        'frontend/SourcePrinter.php',
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
        checks=inventory(fixtures)+boundaries()+reception(fixtures['receive']); report['premises']=len(checks)
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
