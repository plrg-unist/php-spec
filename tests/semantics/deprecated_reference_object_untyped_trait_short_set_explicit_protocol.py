#!/usr/bin/env python3
"""Check actual trait short setter parameters, copied scope and physical storage."""
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
SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_trait_short_set_explicit')
sources = {'single': SOURCE / 'untyped-trait-short-set-explicit-singleton.php',
    'vector': SOURCE / 'untyped-trait-short-set-explicit-vector.php'}
EXECUTION_SOURCE = SOURCE / 'untyped-trait-short-set-explicit-execution.php'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = short.quoted
PREFIX = short.PREFIX
SELECTED = short.SELECTED
RECEIVE_SELECTED = short.RECEIVE_SELECTED.replace('269', '272')
short.EXECUTION_SOURCE = EXECUTION_SOURCE


def named(name, cls):
    namespace = 'Ns272UntypedTraitShortSetExplicit' + ('Single' if name == 'single' else 'Vector')
    return quoted((namespace + chr(92) + cls).encode())


def inventory(fixtures):
    checks = []
    for name, source in sources.items():
        s = '_' + name
        checks += ['U' + s + ' = ' + fixtures[name],
            'S_start' + s + ' = $php_run(U' + s + ',0,' + json.dumps(base64.b64encode(bytes(source)).decode()) + ')',
            'S_raw' + s + ' = $reference_fields_pause(S_start' + s + '[.COMPLETION = NORMAL],0,eps,30000)',
            '$reference_fields_ready(S_raw' + s + ',0,eps)',
            'S_raw' + s + '.TODO = (CLASS_CONST_CLASS expression_class' + s + ' expression_member' + s + ' z' + s + ') :: ptask_tail' + s + '*',
            'S_raw' + s + '.RESULT = REFERENCE n_reference' + s,
            'S_raw' + s + '.STORE[n_reference' + s + '] = DEFINED (POBJECT n_owner' + s + ')',
            'S_raw' + s + '.OBJECTS[n_owner' + s + '] = INSTANCE porigin_owner' + s,
            '$class_at(S_raw' + s + '.CLASSES,porigin_owner' + s + ') = (pclassdesc_owner' + s + ')',
            'pclassdesc_owner' + s + '.NAME = ' + named(name, 'Selected272' if name == 'single' else 'Wide272'),
            'S_raw' + s + '.CURRENT = eps', 'S_raw' + s + '.FRAMES = eps', 'S_raw' + s + '.HELD = eps',
            '$call_reference_operand_valid(S_raw' + s + ',S_raw' + s + '.RESULT)',
            '$call_descriptors_valid(S_raw' + s + ')', '$heap_valid($heap_graph(S_raw' + s + '))',
            '$ccn_output(S_raw' + s + '.EVENTS) = $ptascii("B|' + ('C' if name == 'single' else 'W') + '|")']
        fields = [('tag', 'PINT 17')] if name == 'single' else [
            ('first', 'POBJECT n_leaf_vector'), ('middle', 'POBJECT n_middle_vector'),
            ('last', 'POBJECT n_leaf_vector'), ('tag', 'PBOOL false')]
        slots = '[' + ','.join('ppropertyslot' + s + '_' + field for field, _ in fields) + ']'
        checks += ['$objectprops_at(S_raw' + s + '.OBJECTPROPS,n_owner' + s + ') = (' + slots + ')']
        for field, value in fields:
            slot = 'ppropertyslot' + s + '_' + field
            checks += [slot + '.NAME = $ptascii("' + field + '")', slot + '.STATE = PROP_VALUE (DIRECT (' + value + '))']
        checks += ['$property_slot_descriptor(S_raw' + s + ',n_owner' + s + ',ppropertyslot' + s + '_tag) = (ppropertydesc_imported' + s + ')',
            'ppropertyslot' + s + '_tag.DECL = (ppropertydesc_imported' + s + '.ORIGIN)',
            'ppropertydesc_imported' + s + '.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_consumer' + s + ' porigin_property' + s,
            '$class_at(S_raw' + s + '.CLASSES,porigin_consumer' + s + ') = (pclassdesc_consumer' + s + ')',
            'pclassdesc_consumer' + s + '.NAME = ' + named(name, 'Selected272' if name == 'single' else 'Fields272'),
            'pclassdesc_consumer' + s + '.PARENT = eps',
            '$trait_property_source_at(S_raw' + s + '.CLASSES,porigin_property' + s + ') = (ppropertydesc_source' + s + ')',
            '$property_declaring_class(S_raw' + s + '.CLASSES,porigin_property' + s + ') = (porigin_trait' + s + ')',
            '$class_at(S_raw' + s + '.CLASSES,porigin_trait' + s + ') = (pclassdesc_trait' + s + ')',
            'pclassdesc_trait' + s + '.KIND = "trait"', 'pclassdesc_trait' + s + '.NAME = ' + named(name, 'Tag272'),
            'pclassdesc_trait' + s + '.PROPERTIES = [ppropertydesc_source' + s + ']',
            'pclassdesc_trait' + s + '.METHODS = eps', '$trait_plan(S_raw' + s + ',pclassdesc_trait' + s + ').TRAITS = eps',
            '$trait_plan(S_raw' + s + ',pclassdesc_consumer' + s + ').TRAITS = [pclassdesc_trait' + s + '.NAME]',
            '$trait_plan(S_raw' + s + ',pclassdesc_consumer' + s + ').PRECEDENCES = eps',
            '$trait_plan(S_raw' + s + ',pclassdesc_consumer' + s + ').ALIASES = eps',
            'ppropertydesc_imported' + s + ' = $trait_data_property(pclassdesc_consumer' + s + ',ppropertydesc_source' + s + ')',
            'ppropertydesc_source' + s + '.TYPE = eps', 'ppropertydesc_imported' + s + '.TYPE = eps',
            '$property_set_origin(S_raw' + s + ',ppropertydesc_source' + s + ') = (porigin_hook_source' + s + ')',
            'porigin_hook_source' + s + ' = PORIGIN n_source' + s + ' pcpath_hook' + s,
            '$property_set_origin(S_raw' + s + ',ppropertydesc_imported' + s + ') = (porigin_hook' + s + ')',
            'porigin_hook' + s + ' = TRAIT_ORIGIN porigin_consumer' + s + ' porigin_hook_source' + s + ' ($property_set_name($ptascii("tag")))',
            '$function_at(S_raw' + s + '.FUNCTIONS,porigin_hook_source' + s + ') = (pfunction_source' + s + ')',
            '$property_hook_trait_function(S_raw' + s + ',ppropertydesc_imported' + s + ') = (pfunction_imported' + s + ')',
            'pfunction_imported' + s + ' = pfunction_source' + s + '[.ORIGIN = porigin_hook' + s + '][.NAME = pclassdesc_consumer' + s + '.NAME ++ $ptascii("::$tag::set")]',
            '$function_at($all_functions(S_raw' + s + '),porigin_hook' + s + ') = (pfunction_imported' + s + ')',
            '$function_at(S_raw' + s + '.FUNCTIONS,porigin_hook' + s + ') = eps',
            '$method_named(pclassdesc_consumer' + s + '.METHODS,$property_set_name($ptascii("tag"))) = eps',
            '$property_set_signature_at(S_raw' + s + ',ppropertydesc_imported' + s + ') = (pfunction_source' + s + '.SIGNATURE)',
            'pfunction_source' + s + '.SIGNATURE.PARAMETERS = [{NAME $ptascii("' + ('incoming272' if name == 'single' else 'received272') + '"), TYPE eps, BYREF false, VARIADIC false, REQUIRED true, DEFAULT PSNONE}]',
            'pfunction_source' + s + '.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "void"]))]',
            '$origin_node(S_raw' + s + '.SOURCES,porigin_hook_source' + s + ') = (NPropertyHook phpType14' + s + ' phpType24' + s + ' phpType4' + s + ' phpType11' + s + ' (SEQUENCE ([phpType17_parameter' + s + '])) expression_set' + s + ' metadata_hook' + s + ')',
            '$property_set_untyped_parameters(SEQUENCE ([phpType17_parameter' + s + ']))',
            '$origin_node(S_raw' + s + '.SOURCES,PORIGIN n_source' + s + ' (pcpath_hook' + s + ' ++ [PCFIELD 4,PCINDEX 0])) = (phpType17_parameter' + s + ')',
            '~$hook_body_backed(expression_set' + s + ',$ptascii("tag"))',
            '$property_set_expression(S_raw' + s + ',porigin_hook_source' + s + ') = ((ppropertydesc_source' + s + ',expression_set' + s + ',z_hook' + s + '))',
            '$property_set_expression(S_raw' + s + ',porigin_hook' + s + ') = ((ppropertydesc_imported' + s + ',expression_set' + s + ',z_hook' + s + '))',
            '$origin_node(S_raw' + s + '.SOURCES,PORIGIN n_source' + s + ' (pcpath_hook' + s + ' ++ [PCFIELD 5])) = (expression_set' + s + ')',
            '$code_expression(pfunction_source' + s + '.CODE.EXPRESSIONS,pfunction_source' + s + '.BODY) = ((z_expression' + s + ',b_expression' + s + '))',
            '$class_constant_reference_object_untyped_hook_field(S_raw' + s + ',n_owner' + s + ',ppropertydesc_imported' + s + ',ppropertyslot' + s + '_tag)',
            'S_class' + s + ' = $class_constant_selector(S_raw' + s + ',expression_class' + s + ',z' + s + ')',
            'S_class' + s + '.COMPLETION = NORMAL', '$class_constant_reference_object_graph(S_class' + s + ',n_owner' + s + ',eps)',
            '$class_constant_reference_object_capture_entry(S_class' + s + ',S_raw' + s + '.RESULT,expression_class' + s + ',expression_member' + s + ',z' + s + ',ptask_tail' + s + '*)',
            'S_pending' + s + ' = $class_constant_class_forward(S_class' + s + ',S_raw' + s + '.RESULT,expression_class' + s + ',expression_member' + s + ',z' + s + ',ptask_tail' + s + '*)',
            'S_release' + s + ' = $drive_steps(S_raw' + s + ',1)', 'S_release' + s + '.COMPLETION = BUDGET',
            'S_done' + s + ' = $drive(S_release' + s + '[.COMPLETION = NORMAL],30000)', 'S_done' + s + '.COMPLETION = NORMAL',
            '$ccn_output(S_done' + s + '.EVENTS) = $ptascii("' + ('B|C|D|I|M|H|10|N|Z|' if name == 'single' else 'B|W|D|I|P|Q|L|M|H|10|N|Z|') + '")',
            '~((HOBJECT n_owner' + s + ') <- S_done' + s + '.ALLOCATIONS)',
            '$call_descriptors_valid(S_done' + s + ')', '$heap_valid($heap_graph(S_done' + s + '))']
        if name == 'vector':
            checks += ['$heap_owners($heap_graph(S_raw_vector),HOBJECT n_leaf_vector) = 2',
                '$heap_owners($heap_graph(S_raw_vector),HOBJECT n_middle_vector) = 1',
                '~((HOBJECT n_leaf_vector) <- S_done_vector.ALLOCATIONS)',
                '~((HOBJECT n_middle_vector) <- S_done_vector.ALLOCATIONS)']
    return checks


def boundaries():
    checks = ['S_reduced = S_class_single[.FUNCTIONS = [pfunction_source_single]]',
        'pfunction_source_single.SIGNATURE.PARAMETERS = [psparam_source_single]',
        '$property_set_origin(S_reduced,ppropertydesc_source_single) = (porigin_hook_source_single)',
        '$property_set_origin(S_reduced,ppropertydesc_imported_single) = (porigin_hook_single)',
        '$class_constant_reference_object_graph(S_reduced,n_owner_single,eps)']
    for tag, change in [('name', '.NAME = $ptascii("wrong")'), ('signature', '.SIGNATURE.PARAMETERS = eps'),
        ('mixed', '.SIGNATURE.PARAMETERS = [psparam_source_single[.TYPE = [PTBRANCH ([PTBUILTIN "mixed"])]]]'),
        ('body', '.BODY = eps'), ('return', '.SIGNATURE.RETURNS = eps'), ('code', '.CODE.EXPRESSIONS = eps')]:
        state = 'S_bad_' + tag
        checks += [state + ' = S_reduced[.FUNCTIONS = [pfunction_source_single[' + change + ']]]',
            '$property_set_origin(' + state + ',ppropertydesc_source_single) = eps',
            '$property_set_origin(' + state + ',ppropertydesc_imported_single) = eps',
            '~$class_constant_reference_object_graph(' + state + ',n_owner_single,eps)']
    for tag, change in [('trait_kind', '.KIND = "class"'), ('trait_parent', '.PARENT = ($ptascii("Other272"))')]:
        state = 'S_bad_' + tag
        checks += [state + ' = S_class_single[.CLASSES = $trait_class_set(S_class_single.CLASSES,pclassdesc_trait_single[' + change + '])]',
            '$property_set_origin(' + state + ',ppropertydesc_imported_single) = eps',
            '~$class_constant_reference_object_graph(' + state + ',n_owner_single,eps)',
            '~$call_descriptors_valid(' + state + ')']
    checks += ['S_class_single.SOURCES = [pcunit_single]',
        'S_bad_child = S_class_single[.SOURCES = [pcunit_single[.OCCURRENCES = (PCOCCURRENCE (pcpath_hook_single ++ [PCFIELD 5]) (NScalarInt (INTEGER 0) eps)) :: pcunit_single.OCCURRENCES]]]',
        '$property_set_origin(S_bad_child,ppropertydesc_source_single) = eps',
        '$property_set_origin(S_bad_child,ppropertydesc_imported_single) = eps',
        '~$class_constant_reference_object_graph(S_bad_child,n_owner_single,eps)']
    return checks


def reception(fixture):
    checks = []
    for check in short.reception(fixture):
        if not check.startswith('U_receive = '):
            check = check.replace('269', '272').replace(quoted(b'Ns269UntypedShortSetExplicitExecution\\Box269'), quoted(b'Ns272UntypedTraitShortSetExplicitExecution\\Box272'))
        checks.append(check)
    checks += ['pcallcontext_receive.LEXICAL_CLASS = (porigin_receive_owner)',
        'pcallcontext_receive.CALLED_CLASS = (porigin_receive_owner)',
        'ppropertydesc_receive.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_receive_owner porigin_receive_source_property',
        'pfunction_receive.ORIGIN = TRAIT_ORIGIN porigin_receive_owner (PORIGIN n_receive_unit pcpath_receive_hook) ($property_set_name($ptascii("tag")))',
        '$function_at(S_receive.FUNCTIONS,pfunction_receive.ORIGIN) = eps',
        '$function_at($all_functions(S_receive),pfunction_receive.ORIGIN) = (pfunction_receive)',
        'S_receive.ORIGIN = (PORIGIN n_receive_unit (pcpath_receive_hook ++ [PCFIELD 5]))',
        '$function_body_tasks(S_receive,pfunction_receive) = [$at_task((PORIGIN n_receive_unit pfunction_receive.BODY),EVAL expression_receive),AT pfunction_receive.ORIGIN (ASSIGN_ARRAY (BASE_PROPERTY (POBJECT n_receive_object) ppropertydesc_receive.NAME) z_receive_hook false),DISCARD,$function_fallthrough(S_receive,pfunction_receive)]']
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
