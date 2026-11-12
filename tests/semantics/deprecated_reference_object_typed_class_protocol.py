#!/usr/bin/env python3
"""Check resolved class fields, singleton dispatch and shared physical edges."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_global_constant_protocol import PREFIX
from deprecated_reference_object_fields_protocol import SELECTED
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('deprecated_reference_object_typed_class')
sources = {'single': SOURCE / 'literal-singleton.php', 'vector': SOURCE / 'shared-vector.php'}
FIELDS = {'single': [('edge','LeafBase257','Leaf257')],
    'vector': [('first','LeafBase257','Leaf257'),('middle','Middle257','Middle257'),('last','LeafBase257','Leaf257')]}
NAMESPACES = {'single':'Ns257TypedClassSingle', 'vector':'Ns257TypedClassVector'}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = lambda b: '$base64(' + json.dumps(base64.b64encode(b).decode()) + ')'
named = lambda name, cls: quoted((NAMESPACES[name] + chr(92) + cls).encode())
class_type = lambda value: '[PTBRANCH ([PTCLASS ' + value + '])]'


def inventory(fixtures):
    checks = []
    for name, source in sources.items():
        raw = 'S_raw_' + name; cls = 'S_class_' + name; obj = 'n_object_' + name; ref = 'n_reference_' + name
        desc = 'pclassdesc_' + name; exp = 'expression_class_' + name; mem = 'expression_member_' + name
        line = 'z_' + name; tail = 'ptask_tail_' + name + '*'
        slots = '[' + ','.join('ppropertyslot_' + name + '_' + f for f, _, _ in FIELDS[name]) + ']'
        checks += ['U_' + name + ' = ' + fixtures[name],
            'S_start_' + name + ' = $php_run(U_' + name + ',0,' + json.dumps(base64.b64encode(bytes(source)).decode()) + ')',
            raw + ' = $reference_fields_pause(S_start_' + name + '[.COMPLETION = NORMAL],0,eps,30000)',
            '$reference_fields_ready(' + raw + ',0,eps)',
            raw + '.TODO = (CLASS_CONST_CLASS ' + exp + ' ' + mem + ' ' + line + ') :: ' + tail,
            raw + '.ORIGIN = (porigin_site_' + name + ')', raw + '.RESULT = REFERENCE ' + ref,
            '$call_reference_operand_valid(' + raw + ',' + raw + '.RESULT)',
            raw + '.STORE[' + ref + '] = DEFINED (POBJECT ' + obj + ')',
            '(HCELL ' + ref + ') <- ' + raw + '.ALLOCATIONS', '(HOBJECT ' + obj + ') <- ' + raw + '.ALLOCATIONS',
            raw + '.CURRENT = eps', raw + '.FRAMES = eps', raw + '.HELD = eps', raw + '.PROPREFS = eps',
            raw + '.OBJECTS[' + obj + '] = INSTANCE porigin_' + name,
            '$class_at(' + raw + '.CLASSES,porigin_' + name + ') = (' + desc + ')',
            desc + '.NAME = ' + named(name, 'Selected257' if name == 'single' else 'Wide257'),
            '$objectprops_at(' + raw + '.OBJECTPROPS,' + obj + ') = (' + slots + ')',
            '$object_table_at(' + raw + '.OBJECTTABLES,' + obj + ') = eps',
            '$node_children(' + raw + ',HCELL ' + ref + ') = [HOBJECT ' + obj + ']',
            '$heap_owners($heap_graph(' + raw + '),HCELL ' + ref + ') = 1',
            '$heap_owners($heap_graph(' + raw + '),HOBJECT ' + obj + ') = 1', '$call_descriptors_valid(' + raw + ')',
            '$ccn_output(' + raw + '.EVENTS) = $ptascii("B|' + ('C' if name == 'single' else 'W') + '|")']
        for field, target, actual in FIELDS[name]:
            slot = 'ppropertyslot_' + name + '_' + field; prop = 'ppropertydesc_' + name + '_' + field
            child = 'n_child_' + name + '_' + field
            checks += [slot + '.STATE = PROP_VALUE (DIRECT (POBJECT ' + child + '))',
                '$property_slot_descriptor(' + raw + ',' + obj + ',' + slot + ') = (' + prop + ')',
                prop + '.KEY = $ptascii("' + field + '")', prop + '.TYPE = ' + class_type(named(name,target)),
                prop + '.DEFAULT = PROP_UNINITIALIZED', prop + '.VISIBILITY = PROPERTY_PUBLIC', prop + '.SETVISIBILITY = eps',
                '~' + prop + '.STATIC', '~' + prop + '.READONLY', '~$property_hook_source_declared(' + raw + ',' + prop + ')',
                '~$property_hook_declared(' + raw + ',' + obj + ',' + slot + '.NAME)',
                '(HOBJECT ' + child + ') <- ' + raw + '.ALLOCATIONS',
                raw + '.OBJECTS[' + child + '] = INSTANCE porigin_child_' + name + '_' + field,
                '$class_at(' + raw + '.CLASSES,porigin_child_' + name + '_' + field + ') = (pclassdesc_child_' + name + '_' + field + ')',
                'pclassdesc_child_' + name + '_' + field + '.NAME = ' + named(name,actual),
                '$objectprops_at(' + raw + '.OBJECTPROPS,' + child + ') = (eps)',
                '$node_children(' + raw + ',HOBJECT ' + child + ') = eps',
                '$value_nodes(POBJECT ' + child + ') = [HOBJECT ' + child + ']',
                '$property_slot_release_job(' + raw + ',' + obj + ',' + slot + ') = [DESTRUCTION_VALUE (HOBJECT ' + child + ')]',
                '$typed_object_exact(' + raw + ',' + prop + '.TYPE,POBJECT ' + child + ')',
                '$class_constant_reference_object_class_field_type(' + raw + ',' + prop + ',' + slot + ')',
                '$class_constant_reference_object_field_type(' + raw + ',' + prop + ',' + slot + ')']
        checks += [cls + ' = $class_constant_selector(' + raw + ',' + exp + ',' + line + ')',
            cls + '.COMPLETION = NORMAL', cls + '.RESULT = KNOWN (PSTRING ' + desc + '.NAME)',
            cls + '.STORE = ' + raw + '.STORE', cls + '.OBJECTPROPS = ' + raw + '.OBJECTPROPS',
            '$class_constant_reference_object_graph(' + cls + ',' + obj + ',eps)',
            '$class_constant_reference_object_fields(' + cls + ',' + obj + ',' + slots + ')',
            '$class_constant_reference_object_selector(' + cls + ',' + raw + '.RESULT) = (' + desc + ')',
            '$class_constant_reference_object_capture_entry(' + cls + ',' + raw + '.RESULT,' + exp + ',' + mem + ',' + line + ',' + tail + ')']
    checks += ['$node_children(S_raw_single,HOBJECT n_object_single) = [HOBJECT n_child_single_edge]',
        '$heap_owners($heap_graph(S_raw_single),HOBJECT n_child_single_edge) = 1',
        '~$class_constant_reference_object_scalar_value(POBJECT n_child_single_edge)',
        'ppropertydesc_single_edge.TYPE =/= eps',
        'n_child_vector_first = n_child_vector_last', 'n_child_vector_first =/= n_child_vector_middle',
        '$node_children(S_raw_vector,HOBJECT n_object_vector) = [HOBJECT n_child_vector_first,HOBJECT n_child_vector_middle,HOBJECT n_child_vector_last]',
        '$heap_owners($heap_graph(S_raw_vector),HOBJECT n_child_vector_first) = 2',
        '$heap_owners($heap_graph(S_raw_vector),HOBJECT n_child_vector_middle) = 1',
        'pclassdesc_vector.PROPERTIES = eps',
        '$class_link_at(S_raw_vector.LINKEDPARENTS,porigin_vector) = (SOURCE_PARENT porigin_fields)',
        '$class_at(S_raw_vector.CLASSES,porigin_fields) = (pclassdesc_fields)',
        'pclassdesc_fields.PROPERTIES = [ppropertydesc_vector_first,ppropertydesc_vector_middle,ppropertydesc_vector_last]']
    return checks


def boundaries():
    checks = []
    for target, accepted in [('LeafBase257',True),('Leaf257',True),('Selected257',False)]:
        desc = 'ppropertydesc_single_edge[.TYPE = ' + class_type(named('single',target)) + ']'
        for helper in ['class_field_type','field_type']:
            checks += [('' if accepted else '~') + '$class_constant_reference_object_' + helper + '(S_class_single,' + desc + ',ppropertyslot_single_edge)']
    bad_types = ['[PTBRANCH ([PTBUILTIN "object"])]','[PTBRANCH ([PTBUILTIN "mixed"])]',
        class_type('$ptascii("Unknown257")'),class_type('$base64("AA==")'),class_type('eps'),
        '[PTBRANCH ([PTSELF])]','[PTBRANCH ([PTPARENT])]',
        '[PTBRANCH ([PTCLASS ' + named('single','LeafBase257') + ']),PTBRANCH ([PTBUILTIN "null"])]',
        '[PTBRANCH ([PTCLASS ' + named('single','LeafBase257') + ',PTCLASS ' + named('single','Leaf257') + '])]']
    for type_value in bad_types:
        desc = 'ppropertydesc_single_edge[.TYPE = ' + type_value + ']'
        checks += ['~$class_constant_reference_object_class_field_type(S_class_single,' + desc + ',ppropertyslot_single_edge)']
        if type_value not in ['[PTBRANCH ([PTCLASS ' + named('single','LeafBase257') + ']),PTBRANCH ([PTBUILTIN "null"])]',
                '[PTBRANCH ([PTBUILTIN "object"])]', '[PTBRANCH ([PTBUILTIN "mixed"])]',
                '[PTBRANCH ([PTCLASS ' + named('single','LeafBase257') + ',PTCLASS ' + named('single','Leaf257') + '])]']:
            checks += ['~$class_constant_reference_object_field_type(S_class_single,' + desc + ',ppropertyslot_single_edge)',
                '~$class_constant_reference_object_flat_field_type(S_class_single,n_object_single,' + desc + ',ppropertyslot_single_edge)']
    for state in ['PROP_INITIAL','PROP_UNSET','PROP_VALUE UNINITIALIZED','PROP_VALUE (ALIAS n_reference_single)',
        'PROP_VALUE (DIRECT PNULL)','PROP_VALUE (DIRECT (PBOOL false))','PROP_VALUE (DIRECT (PINT 17))',
        'PROP_VALUE (DIRECT (PARRAY 0))','PROP_VALUE (DIRECT (POBJECT n_object_single))',
        'PROP_VALUE (DIRECT (POBJECT (|S_class_single.OBJECTS|)))']:
        slot = 'ppropertyslot_single_edge[.STATE = ' + state + ']'
        checks += ['~$class_constant_reference_object_class_field_type(S_class_single,ppropertydesc_single_edge,' + slot + ')',
            '~$class_constant_reference_object_field_type(S_class_single,ppropertydesc_single_edge,' + slot + ')',
            '~$class_constant_reference_object_flat_field_type(S_class_single,n_object_single,ppropertydesc_single_edge,' + slot + ')']
    checks += ['S_retired = S_class_single[.ALLOCATIONS = $native_remove_one(S_class_single.ALLOCATIONS,HOBJECT n_child_single_edge)]',
        '~$class_constant_reference_object_class_field_type(S_retired,ppropertydesc_single_edge,ppropertyslot_single_edge)',
        '~$class_constant_reference_object_graph(S_retired,n_object_single,eps)',
        '$class_constant_reference_object_selector(S_retired,S_raw_single.RESULT) = eps',
        '$class_named(S_class_single.CLASSNAMES,$ptlc(' + named('single','LeafBase257') + ')) = (porigin_target)',
        '$class_at(S_class_single.CLASSES,porigin_target) = (pclassdesc_target)',
        'S_interface = S_class_single[.CLASSES = $trait_class_set(S_class_single.CLASSES,pclassdesc_target[.KIND = "interface"])]',
        '$typed_object_exact(S_interface,ppropertydesc_single_edge.TYPE,POBJECT n_child_single_edge)',
        '~$class_constant_reference_object_class_field_type(S_interface,ppropertydesc_single_edge,ppropertyslot_single_edge)',
        '$class_constant_reference_object_graph(S_class_single,n_object_single,eps)',
        'n_invalid_owner = |S_class_single.OBJECTS|',
        'S_invalid_owner = S_class_single[.STORE = $set_cell(S_class_single.STORE,n_reference_single,DEFINED (POBJECT n_invalid_owner))][.OBJECTPROPS = $objectprops_set(S_class_single.OBJECTPROPS,n_invalid_owner,[ppropertyslot_single_edge])]',
        '$call_reference_operand_valid(S_invalid_owner,S_raw_single.RESULT)',
        '$class_constant_reference_object_selector(S_invalid_owner,S_raw_single.RESULT) = eps']
    return checks


def lifecycle():
    root = named('vector','Wide257')
    return ['S_neutral = $class_constant_class_forward(S_class_vector,S_raw_vector.RESULT,expression_class_vector,expression_member_vector,z_vector,ptask_tail_vector*)',
        'ptask_marker = CLASS_CONST_OBJECT_CAPTURE porigin_site_vector ' + root + ' z_vector',
        'ptask_member = $at_task($origin_child((porigin_site_vector),[PCFIELD 1]),EVAL expression_member_vector)',
        'S_neutral.TODO = ptask_member :: (CLASS_CONST_MEMBER expression_class_vector (KNOWN (PSTRING ' + root + ')) z_vector) :: (CLASS_CONST_CAPTURE porigin_site_vector (KNOWN (PSTRING ' + root + ')) z_vector) :: ptask_marker :: ptask_tail_vector*',
        'S_neutral.RESULT = KNOWN PNULL', 'S_neutral.BASE = BASE_VALUE (KNOWN PNULL)',
        '$task_nodes(ptask_marker) = eps', '$machine_base_roots(S_neutral) = eps',
        '$eager_slots(S_raw_vector,S_neutral) = [HCELL n_reference_vector]',
        '$eager_operation_source(S_raw_vector,CLASS_CONST_CLASS expression_class_vector expression_member_vector z_vector) = ptask_marker',
        'S_step = $drive_steps(S_raw_vector,1)', 'S_step.COMPLETION = BUDGET', 'S_release = S_step[.COMPLETION = NORMAL]',
        'S_release.DESTRUCTION.OPERATIONS = [pdestructionoperation]', 'pdestructionoperation.SOURCE = ptask_marker',
        'pdestructionoperation.VALUE = KNOWN PNULL', 'pdestructionoperation.BASE = BASE_VALUE (KNOWN PNULL)',
        'pdestructionoperation.PENDING = eps', '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps',
        '$eager_operation_source_guard(S_release,pdestructionoperation)', '$call_descriptors_valid(S_release)',
        'S_mid = $reference_fields_pause(S_release,1,$ptascii("B|W|D|P|Q|"),30000)',
        '$reference_fields_ready(S_mid,1,$ptascii("B|W|D|P|Q|"))',
        'S_mid.CURRENT = (pcallcontext_mid)', 'pcallcontext_mid.RECEIVER = (n_child_vector_middle)',
        '$instance_storage_for(S_mid,n_object_vector) = (pinstancestorage)', 'pinstancestorage.NEXT = 2',
        '$objectprops_at(S_mid.OBJECTPROPS,n_object_vector) = ([ppropertyslot_vector_first[.STATE = PROP_UNSET],ppropertyslot_vector_middle[.STATE = PROP_UNSET],ppropertyslot_vector_last])',
        '$node_children(S_mid,HOBJECT n_object_vector) = [HOBJECT n_child_vector_last]',
        '(HOBJECT n_object_vector) <- S_mid.ALLOCATIONS', '(HOBJECT n_child_vector_middle) <- S_mid.ALLOCATIONS',
        '$heap_owners($heap_graph(S_mid),HOBJECT n_child_vector_first) = 1',
        '~(n_child_vector_first <- S_mid.DESTRUCTION.CALLED)', 'n_child_vector_middle <- S_mid.DESTRUCTION.CALLED',
        'S_mid.PROPREFS = eps', '$call_descriptors_valid(S_mid)', '$eager_operation_source_guard(S_mid,pdestructionoperation)',
        'S_global_mid = $global_table_view(S_mid)', '$lookup(S_global_mid.ENV,$ptascii("released257vector")) = (n_released)',
        'S_global_mid.STORE[n_released] = DEFINED (PBOOL false)',
        'S_pair = $reference_fields_pause(S_mid,2,eps,30000)', '$reference_fields_ready(S_pair,2,eps)',
        '$ccn_output(S_pair.EVENTS) = $ptascii("B|W|D|P|Q|L|M|")',
        'S_pair.RESULT = KNOWN pvalue_member', '$string_bytes(pvalue_member) = ($ptascii("B"))',
        '~((HCELL n_reference_vector) <- S_pair.ALLOCATIONS)', '~((HOBJECT n_object_vector) <- S_pair.ALLOCATIONS)',
        '~((HOBJECT n_child_vector_first) <- S_pair.ALLOCATIONS)', '~((HOBJECT n_child_vector_middle) <- S_pair.ALLOCATIONS)',
        'S_pair.DESTRUCTION.OPERATIONS = eps', '$call_descriptors_valid(S_pair)',
        '$class_constant_object_member_entry(S_pair,S_pair.RESULT,expression_class_vector,KNOWN (PSTRING ' + root + '),z_vector,ptask_tail_vector*) = (pclassconstantdesc)',
        'S_warn = $ccn_pause(S_pair,0,30000)', '$ccn_ready(S_warn,0)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN ' + root + ' $ptascii("B") z_vector',
        '$task_nodes(perrorcall.RESUME) = eps', '$error_call_valid(S_warn,perrorcall)',
        'S_resume = $ccn_pause(S_warn,1,30000)', '$ccn_ready(S_resume,1)',
        '$ccn_output(S_resume.EVENTS) = $ptascii("B|W|D|P|Q|L|M|H|")',
        '$class_constant_notice_valid(S_resume,pclassconstantdesc.ORIGIN,' + root + ',$ptascii("B"),z_vector)',
        'S_value_step = $drive_steps(S_resume,1)', 'S_value_step.COMPLETION = BUDGET',
        'S_value = S_value_step[.COMPLETION = NORMAL]', 'S_value.RESULT = KNOWN (PINT 10)',
        '~$class_constant_notice_protected(S_value,pclassconstantdesc.ORIGIN)',
        'S_done = $drive_steps(S_value,30000)', 'S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = $ptascii("B|W|D|P|Q|L|M|H|10|Z|")',
        'S_global_done = $global_table_view(S_done)', 'S_global_done.STORE[n_released] = DEFINED (PBOOL true)',
        'S_done.CLASSCONSTANTCACHE = eps', 'S_done.CLASSCONSTANTHISTORY = S_raw_vector.CLASSCONSTANTHISTORY',
        '$class_constant_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        'S_zero = $drive_steps(S_mid,0)', 'S_zero.COMPLETION = BUDGET', 'S_zero[.COMPLETION = NORMAL] = S_mid',
        'S_one = $drive_steps(S_mid,1)', 'S_one.COMPLETION = BUDGET',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],30000) = S_done', '$drive_steps(S_one[.COMPLETION = NORMAL],30000) = S_done']


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), *sources.values(), *modules, *(ROOT / p for p in (
        'spec/semantics/modules.json','spec/php.watsup','spec/schema.json','frontend/worker.php',
        'tests/semantics/deprecated_reference_object_fields_protocol.py',
        'tests/semantics/deprecated_class_constant_fetch_protocol.py','tests/semantics/deprecated_parameter_default_protocol.py',
        'tests/semantics/deprecated_global_constant_protocol.py','tests/semantics/recorded_worker.py',
        'tests/semantics/error_handler_run.py','tests/semantics/static_types.py','tests/semantics/profile.json',
        '.tools/php/bin/php','.tools/php-file.so','_build/default/adapter/main.exe',
        'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    head = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
    try:
        frontend = Worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension=' + str(ROOT / '.tools/php-file.so'),str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'),str(ROOT)], out / 'adapter')
        fixtures = {}
        try:
            for name, source in sources.items():
                parsed = frontend.request({'op':'parse','source':base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted'] and not parsed['diagnostics']
                checked = adapter.request({'op':'check','ast':parsed['ast'],'fixture':True}); assert checked['ok']
                fixtures[name] = checked['fixture']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks = inventory(fixtures) + boundaries() + lifecycle(); report['premises'] = len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        (out / 'protocol.watsup').write_text(PREFIX + SELECTED + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + c + '\n' for c in checks))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),'--sl',*map(str,modules),str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after']
            and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    if not report['passed']: print(report.get('stdout','')[:2000], report.get('stderr','')[:4000])
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()
