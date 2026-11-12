#!/usr/bin/env python3
"""Check one bounded nullable primitive family and one ordinary retirement path."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_global_constant_protocol import PREFIX
from deprecated_reference_object_typed_null_protocol import SELECTED as NULL_SELECTED
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('deprecated_reference_object_nullable_primitive')
sources = {'single': SOURCE / 'literal-singleton.php', 'nulls': SOURCE / 'null-vector.php', 'values': SOURCE / 'value-vector.php'}
TYPES = [('int','i'), ('float','f'), ('string','s'), ('bool','b'), ('false','onlyFalse'), ('true','onlyTrue')]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = lambda b: '$base64(' + json.dumps(base64.b64encode(b).decode()) + ')'
nullable = lambda t: '[PTBRANCH ([PTBUILTIN "' + t + '"]),PTBRANCH ([PTBUILTIN "null"])]'
SELECTED = NULL_SELECTED.replace('$typed_null_', '$nullable_primitive_').replace('B|C|D|N|', 'B|C|D|S|')


def inventory(fixtures):
    checks = []
    for name, source in sources.items():
        fields = ['tag'] if name == 'single' else ['i','f','s','b','onlyFalse','onlyTrue']
        raw = 'S_raw_' + name; cls = 'S_class_' + name; obj = 'n_object_' + name; ref = 'n_reference_' + name
        desc = 'pclassdesc_' + name; origin = 'porigin_child_' + name
        exp = 'expression_class_' + name; mem = 'expression_member_' + name; line = 'z_' + name; tail = 'ptask_tail_' + name + '*'
        slotlist = '[' + ','.join('ppropertyslot_' + name + '_' + f for f in fields) + ']'
        checks += ['U_' + name + ' = ' + fixtures[name],
            'S_start_' + name + ' = $php_run(U_' + name + ',0,' + json.dumps(base64.b64encode(bytes(source)).decode()) + ')',
            raw + ' = $nullable_primitive_pause(S_start_' + name + '[.COMPLETION = NORMAL],0,0,30000)',
            '$nullable_primitive_ready(' + raw + ',0,0)',
            raw + '.TODO = (CLASS_CONST_CLASS ' + exp + ' ' + mem + ' ' + line + ') :: ' + tail,
            raw + '.ORIGIN = (porigin_site_' + name + ')', raw + '.RESULT = REFERENCE ' + ref,
            '$call_reference_operand_valid(' + raw + ',' + raw + '.RESULT)',
            raw + '.STORE[' + ref + '] = DEFINED (POBJECT ' + obj + ')',
            '(HCELL ' + ref + ') <- ' + raw + '.ALLOCATIONS', '(HOBJECT ' + obj + ') <- ' + raw + '.ALLOCATIONS',
            raw + '.CURRENT = eps', raw + '.FRAMES = eps', raw + '.HELD = eps',
            raw + '.OBJECTS[' + obj + '] = INSTANCE ' + origin,
            '$class_at(' + raw + '.CLASSES,' + origin + ') = (' + desc + ')',
            '$objectprops_at(' + raw + '.OBJECTPROPS,' + obj + ') = (' + slotlist + ')',
            raw + '.PROPREFS = eps', '$object_table_at(' + raw + '.OBJECTTABLES,' + obj + ') = eps',
            '$node_children(' + raw + ',HCELL ' + ref + ') = [HOBJECT ' + obj + ']',
            '$node_children(' + raw + ',HOBJECT ' + obj + ') = eps',
            '$heap_owners($heap_graph(' + raw + '),HCELL ' + ref + ') = 1',
            '$heap_owners($heap_graph(' + raw + '),HOBJECT ' + obj + ') = 1',
            '$call_descriptors_valid(' + raw + ')',
            '$ccn_output(' + raw + '.EVENTS) = $ptascii("B|' + ('C' if name == 'single' else 'W') + '|")']
        for field in fields:
            slot = 'ppropertyslot_' + name + '_' + field; prop = 'ppropertydesc_' + name + '_' + field; value = 'pvalue_' + name + '_' + field
            checks += [slot + '.STATE = PROP_VALUE (DIRECT ' + value + ')',
                '$property_slot_descriptor(' + raw + ',' + obj + ',' + slot + ') = (' + prop + ')',
                prop + '.KEY = $ptascii("' + field + '")', prop + '.TYPE =/= eps', prop + '.DEFAULT = PROP_UNINITIALIZED',
                prop + '.VISIBILITY = PROPERTY_PUBLIC', prop + '.SETVISIBILITY = eps', '~' + prop + '.STATIC', '~' + prop + '.READONLY',
                '~$property_hook_source_declared(' + raw + ',' + prop + ')', '~$property_hook_declared(' + raw + ',' + obj + ',' + slot + '.NAME)',
                '$property_slot_release_job(' + raw + ',' + obj + ',' + slot + ') = eps', '$value_nodes(' + value + ') = eps',
                '$class_constant_reference_object_graph_value(' + raw + ',' + value + ',[' + obj + '])',
                '$class_constant_reference_object_scalar_value(' + value + ')',
                '$class_constant_reference_object_field_type(' + raw + ',' + prop + ',' + slot + ')']
            type_name = 'string' if name == 'single' else dict((f, t) for t, f in TYPES)[field]
            expected_value = 'PSTRING_CARRIER INTERNED_STRING $ptascii("tag255")' if name == 'single' else ('PNULL' if name == 'nulls' else {
                'i':'PINT 17', 'f':'PFLOAT 4609434218613702656', 's':'PSTRING_CARRIER INTERNED_STRING $ptascii("wire255")',
                'b':'PBOOL false', 'onlyFalse':'PBOOL false', 'onlyTrue':'PBOOL true'}[field])
            checks += [value + ' = ' + expected_value, prop + '.TYPE = ' + nullable(type_name),
                '$typed_exact(' + prop + '.TYPE,' + value + ')',
                '$class_constant_reference_object_nullable_type(' + prop + '.TYPE) = ("' + type_name + '")',
                '$class_constant_reference_object_nullable_field_type(' + raw + ',' + prop + ',' + slot + ')']
        checks += [cls + ' = $class_constant_selector(' + raw + ',' + exp + ',' + line + ')',
            cls + '.COMPLETION = NORMAL', cls + '.RESULT = KNOWN (PSTRING ' + desc + '.NAME)',
            cls + '.STORE = ' + raw + '.STORE', cls + '.OBJECTPROPS = ' + raw + '.OBJECTPROPS',
            '$class_constant_reference_object_graph(' + cls + ',' + obj + ',eps)',
            '$class_constant_reference_object_fields(' + cls + ',' + obj + ',' + slotlist + ')',
            '$class_constant_reference_object_selector(' + cls + ',' + raw + '.RESULT) = (' + desc + ')',
            '$class_constant_reference_object_capture_entry(' + cls + ',' + raw + '.RESULT,' + exp + ',' + mem + ',' + line + ',' + tail + ')']
    return checks



def boundaries():
    checks = []
    for type_name, field in TYPES:
        checks += ['$class_constant_reference_object_nullable_type(' + nullable(type_name) + ') = ("' + type_name + '")',
            '$class_constant_reference_object_nullable_type([PTBRANCH ([PTBUILTIN "null"]),PTBRANCH ([PTBUILTIN "' + type_name + '"])]) = ("' + type_name + '")']
    bad_types = ['eps', '[PTBRANCH ([PTBUILTIN "string"])]', '[PTBRANCH ([PTBUILTIN "null"])]',
        '[PTBRANCH ([PTBUILTIN "mixed"]),PTBRANCH ([PTBUILTIN "null"])]',
        '[PTBRANCH ([PTBUILTIN "array"]),PTBRANCH ([PTBUILTIN "null"])]',
        '[PTBRANCH ([PTCLASS $ptascii("Named")]),PTBRANCH ([PTBUILTIN "null"])]',
        '[PTBRANCH ([PTBUILTIN "String"]),PTBRANCH ([PTBUILTIN "null"])]',
        '[PTBRANCH ([PTBUILTIN "null"]),PTBRANCH ([PTBUILTIN "null"])]',
        '[PTBRANCH ([PTBUILTIN "int",PTBUILTIN "null"])]',
        '[PTBRANCH ([PTBUILTIN "int"]),PTBRANCH ([PTBUILTIN "string"])]',
        '[PTBRANCH ([PTBUILTIN "string"]),PTBRANCH ([PTBUILTIN "null"]),PTBRANCH ([PTBUILTIN "int"])]']
    for type_value in bad_types:
        checks += ['$class_constant_reference_object_nullable_type(' + type_value + ') = eps',
            '~$class_constant_reference_object_nullable_field_type(S_class_single,ppropertydesc_single_tag[.TYPE = ' + type_value + '],ppropertyslot_single_tag)']
    for field, bad_value in [('i','PBOOL false'),('f','PINT 17'),('s','PSTRING $ptascii("wire255")'),
                             ('b','PINT 0'),('onlyFalse','PBOOL true'),('onlyTrue','PBOOL false')]:
        slot = 'ppropertyslot_values_' + field + '[.STATE = PROP_VALUE (DIRECT (' + bad_value + '))]'
        desc = 'ppropertydesc_values_' + field
        checks += ['~$class_constant_reference_object_nullable_field_type(S_class_values,' + desc + ',' + slot + ')',
            '~$class_constant_reference_object_field_type(S_class_values,' + desc + ',' + slot + ')',
            '~$class_constant_reference_object_flat_field_type(S_class_values,n_object_values,' + desc + ',' + slot + ')']
    for state in ['PROP_INITIAL','PROP_UNSET','PROP_VALUE UNINITIALIZED','PROP_VALUE (ALIAS n_reference_single)',
                  'PROP_VALUE (DIRECT (POBJECT n_object_single))','PROP_VALUE (DIRECT (PARRAY 0))',
                  'PROP_VALUE (DIRECT (PSTRING_CARRIER (REQUEST_STRING (|S_class_single.STRINGDATA|)) $ptascii("tag255")))',
                  'PROP_VALUE (DIRECT (PSTRING_CARRIER INTERNED_STRING $base64("dGEAZw==")))']:
        slot = 'ppropertyslot_single_tag[.STATE = ' + state + ']'
        checks += ['~$class_constant_reference_object_nullable_field_type(S_class_single,ppropertydesc_single_tag,' + slot + ')',
            '~$class_constant_reference_object_field_type(S_class_single,ppropertydesc_single_tag,' + slot + ')',
            '~$class_constant_reference_object_flat_field_type(S_class_single,n_object_single,ppropertydesc_single_tag,' + slot + ')']
    checks += ['$typed_exact(ppropertydesc_values_s.TYPE,PSTRING $ptascii("wire255"))',
        '$class_constant_reference_object_field_type(S_class_single,ppropertydesc_single_tag[.TYPE = eps],ppropertyslot_single_tag)',
        '$class_constant_reference_object_field_type(S_class_single,ppropertydesc_single_tag[.TYPE = [PTBRANCH ([PTBUILTIN "string"])]],ppropertyslot_single_tag)',
        '$class_constant_reference_object_graph(S_class_values,n_object_values,eps)']
    return checks


def lifecycle():
    child = quoted(b'Ns255NullableSingle\\Selected255')
    return [
        'S_neutral = $class_constant_class_forward(S_class_single,S_raw_single.RESULT,expression_class_single,expression_member_single,z_single,ptask_tail_single*)',
        'ptask_marker = CLASS_CONST_OBJECT_CAPTURE porigin_site_single ' + child + ' z_single',
        'ptask_member = $at_task($origin_child((porigin_site_single),[PCFIELD 1]),EVAL expression_member_single)',
        'S_neutral.TODO = ptask_member :: (CLASS_CONST_MEMBER expression_class_single (KNOWN (PSTRING ' + child + ')) z_single) :: (CLASS_CONST_CAPTURE porigin_site_single (KNOWN (PSTRING ' + child + ')) z_single) :: ptask_marker :: ptask_tail_single*',
        'S_neutral.RESULT = KNOWN PNULL', 'S_neutral.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_neutral.PROPREFS = eps', 'S_neutral.STRINGDATA = S_raw_single.STRINGDATA',
        '$task_nodes(ptask_marker) = eps', '$machine_base_roots(S_neutral) = eps',
        '$eager_operation_source(S_raw_single,CLASS_CONST_CLASS expression_class_single expression_member_single z_single) = ptask_marker',
        'S_step = $drive_steps(S_raw_single,1)', 'S_step.COMPLETION = BUDGET', 'S_release = S_step[.COMPLETION = NORMAL]',
        'S_release.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
        'pdestructionoperation.SOURCE = ptask_marker', 'pdestructionoperation.VALUE = KNOWN PNULL',
        'pdestructionoperation.BASE = BASE_VALUE (KNOWN PNULL)', 'pdestructionoperation.PENDING = eps',
        '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps',
        '$eager_operation_source_guard(S_release,pdestructionoperation)', '$call_descriptors_valid(S_release)',
        'S_dtor = $nullable_primitive_pause(S_release,1,n_object_single,30000)', '$nullable_primitive_ready(S_dtor,1,n_object_single)',
        '(HOBJECT n_object_single) <- S_dtor.ALLOCATIONS', '$node_children(S_dtor,HOBJECT n_object_single) = eps',
        '$objectprops_at(S_dtor.OBJECTPROPS,n_object_single) = ([ppropertyslot_single_tag])',
        '$eager_operation_source_guard(S_dtor,pdestructionoperation)', '$call_descriptors_valid(S_dtor)',
        'S_storage = $nullable_primitive_pause(S_dtor,2,n_object_single,30000)', '$nullable_primitive_ready(S_storage,2,n_object_single)',
        '$instance_storage_for(S_storage,n_object_single) = (pinstancestorage)', 'pinstancestorage.NEXT = 1',
        'pinstancestorage.SLOTS = [ppropertyslot_single_tag]',
        '$objectprops_at(S_storage.OBJECTPROPS,n_object_single) = ([ppropertyslot_single_tag[.STATE = PROP_UNSET]])',
        '(HOBJECT n_object_single) <- S_storage.ALLOCATIONS', '$node_children(S_storage,HOBJECT n_object_single) = eps',
        'S_storage.PROPREFS = eps', 'S_storage.STRINGDATA = S_raw_single.STRINGDATA',
        '$instance_storage_basic(S_storage,pinstancestorage)', '$call_descriptors_valid(S_storage)',
        '$eager_operation_source_guard(S_storage,pdestructionoperation)',
        'S_pair = $nullable_primitive_pause(S_storage,3,n_object_single,30000)', '$nullable_primitive_ready(S_pair,3,n_object_single)',
        '$ccn_output(S_pair.EVENTS) = $ptascii("B|C|D|S|M|")',
        'S_pair.RESULT = KNOWN pvalue_member', '$string_bytes(pvalue_member) = ($ptascii("B"))',
        '~((HCELL n_reference_single) <- S_pair.ALLOCATIONS)', '~((HOBJECT n_object_single) <- S_pair.ALLOCATIONS)',
        'S_pair.DESTRUCTION.OPERATIONS = eps', 'S_pair.PROPREFS = eps', '$call_descriptors_valid(S_pair)',
        '$class_constant_object_member_entry(S_pair,S_pair.RESULT,expression_class_single,KNOWN (PSTRING ' + child + '),z_single,ptask_tail_single*) = (pclassconstantdesc)',
        'S_warn = $ccn_pause(S_pair,0,30000)', '$ccn_ready(S_warn,0)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN ' + child + ' $ptascii("B") z_single',
        '$task_nodes(perrorcall.RESUME) = eps', '$error_call_valid(S_warn,perrorcall)',
        'S_resume = $ccn_pause(S_warn,1,30000)', '$ccn_ready(S_resume,1)',
        '$ccn_output(S_resume.EVENTS) = $ptascii("B|C|D|S|M|H|")',
        'S_global = $global_table_view(S_resume)', '$lookup(S_global.ENV,$ptascii("member255single")) = (n_member)',
        'S_global.STORE[n_member] = DEFINED pvalue_now', '$string_bytes(pvalue_now) = ($ptascii("A"))',
        '$class_constant_notice_valid(S_resume,pclassconstantdesc.ORIGIN,' + child + ',$ptascii("B"),z_single)',
        'S_value_step = $drive_steps(S_resume,1)', 'S_value_step.COMPLETION = BUDGET',
        'S_value = S_value_step[.COMPLETION = NORMAL]', 'S_value.RESULT = KNOWN (PINT 10)',
        '~$class_constant_notice_protected(S_value,pclassconstantdesc.ORIGIN)',
        'S_done = $drive_steps(S_value,30000)', 'S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = $ptascii("B|C|D|S|M|H|10|Z|")',
        'S_done.CLASSCONSTANTCACHE = eps', 'S_done.CLASSCONSTANTHISTORY = S_raw_single.CLASSCONSTANTHISTORY',
        '$class_constant_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        'S_zero = $drive_steps(S_storage,0)', 'S_zero.COMPLETION = BUDGET', 'S_zero[.COMPLETION = NORMAL] = S_storage',
        'S_one = $drive_steps(S_storage,1)', 'S_one.COMPLETION = BUDGET',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],30000) = S_done', '$drive_steps(S_one[.COMPLETION = NORMAL],30000) = S_done']

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), *sources.values(), *modules, *(ROOT / p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
        'tests/semantics/deprecated_reference_object_typed_null_protocol.py',
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
        fixtures = {}
        try:
            for name, source in sources.items():
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted'] and not parsed['diagnostics']
                checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
                fixtures[name] = checked['fixture']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks = inventory(fixtures) + boundaries() + lifecycle(); report['premises'] = len(checks)
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
