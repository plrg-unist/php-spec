#!/usr/bin/env python3
"""Check primitive unions as a group and one ordinary storage retirement."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_global_constant_protocol import PREFIX
from deprecated_reference_object_nullable_primitive_protocol import SELECTED as NULLABLE_SELECTED, lifecycle as nullable_lifecycle
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('deprecated_reference_object_primitive_union')
sources = {'single': SOURCE / 'literal-singleton.php', 'values': SOURCE / 'value-vector.php'}
SELECTED = NULLABLE_SELECTED.replace('$nullable_primitive_', '$primitive_union_')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = lambda b: '$base64(' + json.dumps(base64.b64encode(b).decode()) + ')'
union = lambda names: '[' + ','.join('PTBRANCH ([PTBUILTIN "' + n + '"])' for n in names) + ']'
FIELDS = {
    'single': [('tag', ('int','string'), 'PSTRING_CARRIER INTERNED_STRING $ptascii("tag256")')],
    'values': [('integer', ('int','float'), 'PINT 17'),
        ('floating', ('float','int'), 'PFLOAT 4609434218613702656'),
        ('text', ('string','int'), 'PSTRING_CARRIER INTERNED_STRING $ptascii("wire256")'),
        ('onlyFalse', ('false','string'), 'PBOOL false'), ('onlyTrue', ('int','true'), 'PBOOL true'),
        ('nothing', ('null','bool','int'), 'PNULL'), ('boolean', ('float','string','bool'), 'PBOOL false'),
        ('request', ('null','string','int','bool','float'), 'PSTRING_CARRIER (REQUEST_STRING n_request) $ptascii("req256")')]}


def inventory(fixtures):
    checks = []
    for name, source in sources.items():
        raw = 'S_raw_' + name; cls = 'S_class_' + name; obj = 'n_object_' + name; ref = 'n_reference_' + name
        desc = 'pclassdesc_' + name; exp = 'expression_class_' + name; mem = 'expression_member_' + name
        line = 'z_' + name; tail = 'ptask_tail_' + name + '*'
        slots = '[' + ','.join('ppropertyslot_' + name + '_' + f for f, _, _ in FIELDS[name]) + ']'
        checks += ['U_' + name + ' = ' + fixtures[name],
            'S_start_' + name + ' = $php_run(U_' + name + ',0,' + json.dumps(base64.b64encode(bytes(source)).decode()) + ')',
            raw + ' = $primitive_union_pause(S_start_' + name + '[.COMPLETION = NORMAL],0,0,30000)',
            '$primitive_union_ready(' + raw + ',0,0)',
            raw + '.TODO = (CLASS_CONST_CLASS ' + exp + ' ' + mem + ' ' + line + ') :: ' + tail,
            raw + '.ORIGIN = (porigin_site_' + name + ')', raw + '.RESULT = REFERENCE ' + ref,
            '$call_reference_operand_valid(' + raw + ',' + raw + '.RESULT)',
            raw + '.STORE[' + ref + '] = DEFINED (POBJECT ' + obj + ')',
            '(HCELL ' + ref + ') <- ' + raw + '.ALLOCATIONS', '(HOBJECT ' + obj + ') <- ' + raw + '.ALLOCATIONS',
            raw + '.CURRENT = eps', raw + '.FRAMES = eps', raw + '.HELD = eps',
            raw + '.OBJECTS[' + obj + '] = INSTANCE porigin_' + name,
            '$class_at(' + raw + '.CLASSES,porigin_' + name + ') = (' + desc + ')',
            '$objectprops_at(' + raw + '.OBJECTPROPS,' + obj + ') = (' + slots + ')',
            raw + '.PROPREFS = eps', '$object_table_at(' + raw + '.OBJECTTABLES,' + obj + ') = eps',
            '$node_children(' + raw + ',HCELL ' + ref + ') = [HOBJECT ' + obj + ']',
            '$node_children(' + raw + ',HOBJECT ' + obj + ') = eps',
            '$heap_owners($heap_graph(' + raw + '),HCELL ' + ref + ') = 1',
            '$heap_owners($heap_graph(' + raw + '),HOBJECT ' + obj + ') = 1', '$call_descriptors_valid(' + raw + ')',
            '$ccn_output(' + raw + '.EVENTS) = $ptascii("B|' + ('C' if name == 'single' else 'W') + '|")']
        for field, names, expected in FIELDS[name]:
            slot = 'ppropertyslot_' + name + '_' + field; prop = 'ppropertydesc_' + name + '_' + field
            value = 'pvalue_' + name + '_' + field
            checks += [slot + '.STATE = PROP_VALUE (DIRECT ' + value + ')', value + ' = ' + expected,
                '$property_slot_descriptor(' + raw + ',' + obj + ',' + slot + ') = (' + prop + ')',
                prop + '.KEY = $ptascii("' + field + '")', prop + '.TYPE = ' + union(names),
                prop + '.DEFAULT = PROP_UNINITIALIZED', prop + '.VISIBILITY = PROPERTY_PUBLIC', prop + '.SETVISIBILITY = eps',
                '~' + prop + '.STATIC', '~' + prop + '.READONLY', '~$property_hook_source_declared(' + raw + ',' + prop + ')',
                '~$property_hook_declared(' + raw + ',' + obj + ',' + slot + '.NAME)',
                '$property_slot_release_job(' + raw + ',' + obj + ',' + slot + ') = eps', '$value_nodes(' + value + ') = eps',
                '$typed_exact(' + prop + '.TYPE,' + value + ')',
                '$class_constant_reference_object_primitive_union_type(' + prop + '.TYPE)',
                '$class_constant_reference_object_primitive_union_field_type(' + raw + ',' + prop + ',' + slot + ')',
                '$class_constant_reference_object_field_type(' + raw + ',' + prop + ',' + slot + ')']
        checks += [cls + ' = $class_constant_selector(' + raw + ',' + exp + ',' + line + ')',
            cls + '.COMPLETION = NORMAL', cls + '.RESULT = KNOWN (PSTRING ' + desc + '.NAME)',
            cls + '.STORE = ' + raw + '.STORE', cls + '.OBJECTPROPS = ' + raw + '.OBJECTPROPS',
            '$class_constant_reference_object_graph(' + cls + ',' + obj + ',eps)',
            '$class_constant_reference_object_fields(' + cls + ',' + obj + ',' + slots + ')',
            '$class_constant_reference_object_selector(' + cls + ',' + raw + '.RESULT) = (' + desc + ')',
            '$class_constant_reference_object_capture_entry(' + cls + ',' + raw + '.RESULT,' + exp + ',' + mem + ',' + line + ',' + tail + ')']
    return checks + ['S_raw_values.STRINGDATA[n_request] = $ptascii("req256")',
        '$string_carrier_valid(S_raw_values,pvalue_values_request)']


def boundaries():
    checks = []
    values = [('int','PINT 17'), ('float','PFLOAT 4609434218613702656'),
        ('string','PSTRING_CARRIER INTERNED_STRING $ptascii("matrix256")'),
        ('false','PBOOL false'), ('true','PBOOL true'), ('null','PNULL')]
    groups = [('int','string'), ('float','int'), ('false','string'), ('int','true'),
        ('null','bool','int'), ('float','string','bool'), ('null','string','int','bool','float'),
        ('null','false','float'), ('true','float','string','null')]
    for names in groups:
        desc = 'ppropertydesc_single_tag[.TYPE = ' + union(names) + ']'
        checks += ['$class_constant_reference_object_primitive_union_type(' + union(names) + ')']
        for tag, value in values:
            accepted = tag in names or (tag in ('true','false') and 'bool' in names)
            slot = 'ppropertyslot_single_tag[.STATE = PROP_VALUE (DIRECT (' + value + '))]'
            for helper in ['primitive_union_field_type','field_type']:
                checks += [('' if accepted else '~') + '$class_constant_reference_object_' + helper + '(S_class_single,' + desc + ',' + slot + ')']
    invalid = [union(names) for names in [('int','array'),('array','int'),('int','mixed'),('mixed','int'),
        ('int','String'),('int','int'),('bool','true'),('true','bool'),('bool','false'),('false','bool'),
        ('false','true'),('true','false'),('int','float','int')]]
    invalid += ['[PTBRANCH ([PTCLASS $ptascii("Named")]),PTBRANCH ([PTBUILTIN "int"])]',
        '[PTBRANCH ([PTBUILTIN "int",PTBUILTIN "string"]),PTBRANCH ([PTBUILTIN "float"])]',
        '[PTBRANCH eps,PTBRANCH ([PTBUILTIN "int"])]']
    for type_value in invalid:
        desc = 'ppropertydesc_values_integer[.TYPE = ' + type_value + ']'
        checks += ['~$class_constant_reference_object_primitive_union_type(' + type_value + ')',
            '~$class_constant_reference_object_primitive_union_field_type(S_class_values,' + desc + ',ppropertyslot_values_integer)',
            '~$class_constant_reference_object_field_type(S_class_values,' + desc + ',ppropertyslot_values_integer)']
    for type_value in ['eps', union(('int',)), union(('null',))]:
        checks += ['~$class_constant_reference_object_primitive_union_type(' + type_value + ')']
    for state in ['PROP_INITIAL','PROP_UNSET','PROP_VALUE UNINITIALIZED','PROP_VALUE (ALIAS n_reference_single)',
        'PROP_VALUE (DIRECT (POBJECT n_object_single))','PROP_VALUE (DIRECT (PARRAY 0))',
        'PROP_VALUE (DIRECT (PSTRING $ptascii("tag256")))',
        'PROP_VALUE (DIRECT (PSTRING_CARRIER (REQUEST_STRING (|S_class_single.STRINGDATA|)) $ptascii("tag256")))',
        'PROP_VALUE (DIRECT (PSTRING_CARRIER INTERNED_STRING $base64("dGEAZw==")))']:
        slot = 'ppropertyslot_single_tag[.STATE = ' + state + ']'
        checks += ['~$class_constant_reference_object_primitive_union_field_type(S_class_single,ppropertydesc_single_tag,' + slot + ')',
            '~$class_constant_reference_object_field_type(S_class_single,ppropertydesc_single_tag,' + slot + ')',
            '~$class_constant_reference_object_flat_field_type(S_class_single,n_object_single,ppropertydesc_single_tag,' + slot + ')']
    checks += ['$class_constant_reference_object_nullable_type(' + union(('int','null')) + ') = ("int")',
        '$class_constant_reference_object_nullable_field_type(S_class_single,ppropertydesc_single_tag[.TYPE = ' + union(('int','null')) + '],ppropertyslot_single_tag[.STATE = PROP_VALUE (DIRECT PNULL)])',
        '$class_constant_reference_object_field_type(S_class_single,ppropertydesc_single_tag[.TYPE = eps],ppropertyslot_single_tag)']
    return checks


def lifecycle():
    old = quoted(b'Ns255NullableSingle\\Selected255'); new = quoted(b'Ns256UnionSingle\\Selected256')
    return [c.replace(old,new).replace('255','256').replace('$nullable_primitive_', '$primitive_union_') for c in nullable_lifecycle()]


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), *sources.values(), *modules, *(ROOT / p for p in (
        'spec/semantics/modules.json','spec/php.watsup','spec/schema.json','frontend/worker.php',
        'tests/semantics/deprecated_reference_object_nullable_primitive_protocol.py',
        'tests/semantics/deprecated_reference_object_typed_null_protocol.py',
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
