#!/usr/bin/env python3
"""Check nested NaN fields, real shared edges and outside child retention."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_global_constant_protocol import PREFIX
from deprecated_class_constant_fetch_protocol import SELECTED as FETCH_SELECTED
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('deprecated_reference_object_float_review') / 'nested-nan-shared.php'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = lambda s: '$base64(' + json.dumps(base64.b64encode(s.encode()).decode()) + ')'
SELECTED = FETCH_SELECTED + r'''
dec $float_peer_ready(pstate,nat,nat) : bool
def $float_peer_ready(S,0,n_middle) = true
  -- if S.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask*
  -- if S.RESULT = REFERENCE n_reference
  -- if $call_reference_operand_valid(S,S.RESULT)
def $float_peer_ready(S,1,n_middle) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n_middle)
  -- if $ccn_output(S.EVENTS) = $ptascii("B|C|D|H|9|I|N|")
def $float_peer_ready(S,2,n_middle) = true
  -- if $instance_storage_for(S,n_middle) = (pinstancestorage)
  -- if pinstancestorage.NEXT = 1
def $float_peer_ready(S,3,n_middle) = true
  -- if $instance_storage_for(S,n_middle) = (pinstancestorage)
  -- if pinstancestorage.NEXT = 2
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask*
def $float_peer_ready(S,4,n_middle) = true
  -- if S.TODO = (CLASS_CONST_MEMBER expression_class poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: (CLASS_CONST_OBJECT_CAPTURE porigin ptbytes_class z) :: ptask*
def $float_peer_ready(S,n_phase,n_middle) = false -- otherwise
dec $float_peer_pause(pstate,nat,nat,nat) : pstate
def $float_peer_pause(S,n_phase,n_middle,n_budget) = S -- if $float_peer_ready(S,n_phase,n_middle)
def $float_peer_pause(S,n_phase,n_middle,n_budget) = $float_peer_pause(S_next[.COMPLETION = NORMAL],n_phase,n_middle,$nabs($(n_budget - 1)))
  -- if ~$float_peer_ready(S,n_phase,n_middle)
  -- if S.COMPLETION = NORMAL /\ $(n_budget > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $float_peer_pause(S,n_phase,n_middle,n_budget) = S -- otherwise
'''


def fields(fixture):
    root = quoted('Ns246NestedFloat\\Root246')
    checks = ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(SOURCE)).decode()) + ')',
        'S_raw = $float_peer_pause(S_start[.COMPLETION = NORMAL],0,0,30000)', '$float_peer_ready(S_raw,0,0)',
        'S_raw.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask_tail*',
        'S_raw.ORIGIN = (porigin_site)', 'S_raw.RESULT = REFERENCE n_reference',
        'S_raw.STORE[n_reference] = DEFINED (POBJECT n_receiver)',
        '(HCELL n_reference) <- S_raw.ALLOCATIONS', '(HOBJECT n_receiver) <- S_raw.ALLOCATIONS',
        'S_raw.CURRENT = eps', 'S_raw.FRAMES = eps', 'S_raw.HELD = eps',
        'S_raw.OBJECTS[n_receiver] = INSTANCE porigin_root',
        '$class_at(S_raw.CLASSES,porigin_root) = (pclassdesc_root)', 'pclassdesc_root.NAME = ' + root,
        '$objectprops_at(S_raw.OBJECTPROPS,n_receiver) = ([ppropertyslot_middle,ppropertyslot_tail])',
        'ppropertyslot_middle.STATE = PROP_VALUE (DIRECT (POBJECT n_middle))',
        'ppropertyslot_tail.STATE = PROP_VALUE (DIRECT (POBJECT n_leaf))',
        'S_raw.OBJECTS[n_middle] = INSTANCE porigin_middle',
        '$class_at(S_raw.CLASSES,porigin_middle) = (pclassdesc_middle)',
        '$objectprops_at(S_raw.OBJECTPROPS,n_middle) = ([ppropertyslot_tag,ppropertyslot_edge])',
        'ppropertyslot_tag.STATE = PROP_VALUE (DIRECT (PFLOAT n_nan))',
        'n_nan = 9221120237041090560',
        'ppropertyslot_edge.STATE = PROP_VALUE (DIRECT (POBJECT n_leaf))',
        '$property_slot_descriptor(S_raw,n_middle,ppropertyslot_tag) = (ppropertydesc_tag)',
        '$property_slot_descriptor(S_raw,n_middle,ppropertyslot_edge) = (ppropertydesc_edge)',
        'S_raw.OBJECTS[n_leaf] = INSTANCE porigin_leaf',
        '$class_at(S_raw.CLASSES,porigin_leaf) = (pclassdesc_leaf)',
        '$objectprops_at(S_raw.OBJECTPROPS,n_leaf) = (eps)',
        '$node_children(S_raw,HCELL n_reference) = [HOBJECT n_receiver]',
        '$node_children(S_raw,HOBJECT n_receiver) = [HOBJECT n_middle,HOBJECT n_leaf]',
        '$node_children(S_raw,HOBJECT n_middle) = [HOBJECT n_leaf]',
        '$node_children(S_raw,HOBJECT n_leaf) = eps', '$value_nodes(PFLOAT n_nan) = eps',
        '$heap_owners($heap_graph(S_raw),HCELL n_reference) = 1',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_receiver) = 1',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_middle) = 1',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_leaf) = 3',
        'S_global = $global_table_view(S_raw)',
        '$lookup(S_global.ENV,$ptascii("outside246peer")) = (n_outside)',
        'S_global.STORE[n_outside] = DEFINED (POBJECT n_leaf)',
        '$call_descriptors_valid(S_raw)', '$ccn_output(S_raw.EVENTS) = $ptascii("B|C|")',
        'S_class = $class_constant_selector(S_raw,expression_class,z)',
        'S_class.COMPLETION = NORMAL', 'S_class.RESULT = KNOWN (PSTRING ' + root + ')',
        'S_class.STORE = S_raw.STORE', 'S_class.OBJECTPROPS = S_raw.OBJECTPROPS',
        'S_class.ALLOCATIONS = S_raw.ALLOCATIONS',
        '$class_constant_reference_object_graph_value(S_class,PFLOAT n_nan,[n_receiver,n_middle])',
        '$class_constant_reference_object_scalar_value(PFLOAT n_nan)',
        '$class_constant_reference_object_field_value(S_class,n_middle,PFLOAT n_nan)',
        '$class_constant_reference_object_graph(S_class,n_middle,[n_receiver])',
        '$class_constant_reference_object_graph(S_class,n_receiver,eps)',
        '$class_constant_reference_object_fields(S_class,n_middle,[ppropertyslot_tag,ppropertyslot_edge])',
        '~$class_constant_reference_object_fields(S_class,n_receiver,[ppropertyslot_middle,ppropertyslot_tail])',
        '$class_constant_reference_object_selector(S_class,S_raw.RESULT) = (pclassdesc_root)',
        '$class_constant_reference_object_capture_entry(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        'ptbytes_anonymous = $ptascii("class@anonymous") ++ $base64("AA==") ++ $ptascii("fixture:1$0")',
        'pclassdesc_anonymous = pclassdesc_leaf[.NAME = ptbytes_anonymous]',
        'S_anonymous = S_class[.CLASSES = $trait_class_set(S_class.CLASSES,pclassdesc_anonymous)][.CLASSNAMES = [($ptlc(ptbytes_anonymous),porigin_leaf)] ++ S_class.CLASSNAMES]',
        '$class_named(S_anonymous.CLASSNAMES,$ptlc(ptbytes_anonymous)) = (porigin_leaf)',
        '$class_constant_reference_object_field_value(S_anonymous,n_middle,POBJECT n_leaf)',
        '~$class_constant_reference_object_graph(S_anonymous,n_middle,eps)',
        '~$class_constant_reference_object_field_value(S_anonymous,n_middle,PFLOAT n_nan)',
        '$class_constant_reference_object_selector(S_anonymous,S_raw.RESULT) = eps',
        'S_typed = S_class[.CLASSES = $trait_class_set(S_class.CLASSES,pclassdesc_middle[.PROPERTIES = [ppropertydesc_tag[.TYPE = [PTBRANCH ([PTBUILTIN "float"])]],ppropertydesc_edge]])]',
        '~$class_constant_reference_object_field_value(S_typed,n_middle,PFLOAT n_nan)',
        '$class_constant_reference_object_selector(S_typed,S_raw.RESULT) = eps']
    for state in ['PROP_VALUE (DIRECT (POBJECT n_receiver))', 'PROP_VALUE (ALIAS n_reference)',
                  'PROP_VALUE (DIRECT (PSTRING $ptascii("x")))', 'PROP_VALUE (DIRECT (PARRAY 0))']:
        view = 'S_class[.OBJECTPROPS = $objectprops_set(S_class.OBJECTPROPS,n_middle,[ppropertyslot_tag,ppropertyslot_edge[.STATE = ' + state + ']])]'
        checks += ['~$class_constant_reference_object_graph(' + view + ',n_receiver,eps)',
                   '~$class_constant_reference_object_field_value(' + view + ',n_middle,PFLOAT n_nan)',
                   '$class_constant_reference_object_selector(' + view + ',S_raw.RESULT) = eps']
    checks += ['S_neutral = $class_constant_class_forward(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        'ptask_marker = CLASS_CONST_OBJECT_CAPTURE porigin_site ' + root + ' z',
        'ptask_member = $at_task($origin_child((porigin_site),[PCFIELD 1]),EVAL expression_member)',
        'S_neutral.TODO = ptask_member :: (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING ' + root + ')) z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING ' + root + ')) z) :: ptask_marker :: ptask_tail*',
        'S_neutral.RESULT = KNOWN PNULL', 'S_neutral.BASE = BASE_VALUE (KNOWN PNULL)',
        '$task_nodes(ptask_marker) = eps', '$machine_base_roots(S_neutral) = eps',
        '$eager_operation_source(S_raw,CLASS_CONST_CLASS expression_class expression_member z) = ptask_marker',
        'S_step = $drive_steps(S_raw,1)', 'S_step.COMPLETION = BUDGET', 'S_release = S_step[.COMPLETION = NORMAL]',
        'S_release.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
        'pdestructionoperation.SOURCE = ptask_marker', 'pdestructionoperation.VALUE = KNOWN PNULL',
        'pdestructionoperation.BASE = BASE_VALUE (KNOWN PNULL)', 'pdestructionoperation.PENDING = eps',
        '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps',
        '$eager_operation_source_guard(S_release,pdestructionoperation)', '$call_descriptors_valid(S_release)',
        'S_middle = $float_peer_pause(S_release,1,n_middle,30000)', '$float_peer_ready(S_middle,1,n_middle)',
        '$instance_storage_for(S_middle,n_receiver) = (pinstancestorage_root)', 'pinstancestorage_root.NEXT = 1',
        '$objectprops_at(S_middle.OBJECTPROPS,n_middle) = ([ppropertyslot_tag,ppropertyslot_edge])',
        '$heap_owners($heap_graph(S_middle),HOBJECT n_leaf) = 3', '~(n_leaf <- S_middle.DESTRUCTION.CALLED)',
        '$eager_operation_source_guard(S_middle,pdestructionoperation)', '$call_descriptors_valid(S_middle)',
        'S_tag = $float_peer_pause(S_middle,2,n_middle,30000)', '$float_peer_ready(S_tag,2,n_middle)',
        '$instance_storage_for(S_tag,n_middle) = (pinstancestorage_middle)', 'pinstancestorage_middle.NEXT = 1',
        '$objectprops_at(S_tag.OBJECTPROPS,n_middle) = ([ppropertyslot_tag[.STATE = PROP_UNSET],ppropertyslot_edge])',
        '$heap_owners($heap_graph(S_tag),HOBJECT n_leaf) = 3',
        '$node_children(S_tag,HOBJECT n_middle) = [HOBJECT n_leaf]',
        '$call_descriptors_valid(S_tag)',
        'S_edge = $float_peer_pause(S_tag,3,n_middle,30000)', '$float_peer_ready(S_edge,3,n_middle)',
        '$instance_storage_for(S_edge,n_receiver) = (pinstancestorage_root)',
        '$instance_storage_for(S_edge,n_middle) = (pinstancestorage_middle[.NEXT = 2])',
        '$objectprops_at(S_edge.OBJECTPROPS,n_middle) = ([ppropertyslot_tag[.STATE = PROP_UNSET],ppropertyslot_edge[.STATE = PROP_UNSET]])',
        '$node_children(S_edge,HOBJECT n_middle) = eps',
        '$heap_owners($heap_graph(S_edge),HOBJECT n_leaf) = 2', '~(n_leaf <- S_edge.DESTRUCTION.CALLED)',
        '(HOBJECT n_receiver) <- S_edge.ALLOCATIONS', '(HOBJECT n_middle) <- S_edge.ALLOCATIONS',
        '$eager_operation_source_guard(S_edge,pdestructionoperation)', '$call_descriptors_valid(S_edge)',
        'S_pair = $float_peer_pause(S_edge,4,n_middle,30000)', '$float_peer_ready(S_pair,4,n_middle)',
        '$ccn_output(S_pair.EVENTS) = $ptascii("B|C|D|H|9|I|N|M|")',
        'S_pair.RESULT = KNOWN pvalue_member', '$string_bytes(pvalue_member) = ($ptascii("B"))',
        '~((HCELL n_reference) <- S_pair.ALLOCATIONS)', '~((HOBJECT n_receiver) <- S_pair.ALLOCATIONS)',
        '~((HOBJECT n_middle) <- S_pair.ALLOCATIONS)', '(HOBJECT n_leaf) <- S_pair.ALLOCATIONS',
        '$heap_owners($heap_graph(S_pair),HOBJECT n_leaf) = 1', '~(n_leaf <- S_pair.DESTRUCTION.CALLED)',
        'S_pair.DESTRUCTION.OPERATIONS = eps', '$call_descriptors_valid(S_pair)',
        'S_warn = $ccn_pause(S_pair,0,30000)', '$ccn_ready(S_warn,0)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ' + root + ' $ptascii("B") z',
        '$task_nodes(perrorcall.RESUME) = eps', '$class_constant_notice_protected(S_warn,porigin_decl)',
        '$error_call_valid(S_warn,perrorcall)', '$call_descriptors_valid(S_warn)',
        'S_resume = $ccn_pause(S_warn,1,30000)', '$ccn_ready(S_resume,1)',
        '$ccn_output(S_resume.EVENTS) = $ptascii("B|C|D|H|9|I|N|M|H|")',
        '$heap_owners($heap_graph(S_resume),HOBJECT n_leaf) = 1', '~(n_leaf <- S_resume.DESTRUCTION.CALLED)',
        '$class_constant_notice_valid(S_resume,porigin_decl,' + root + ',$ptascii("B"),z)',
        'S_value_step = $drive_steps(S_resume,1)', 'S_value_step.COMPLETION = BUDGET',
        'S_value = S_value_step[.COMPLETION = NORMAL]', 'S_value.RESULT = KNOWN (PINT 10)',
        '~$class_constant_notice_protected(S_value,porigin_decl)',
        'S_done = $drive(S_value,30000)', 'S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = $ptascii("B|C|D|H|9|I|N|M|H|10|Z|L|E|")',
        '~((HOBJECT n_leaf) <- S_done.ALLOCATIONS)', 'S_done.DESTRUCTION.OPERATIONS = eps',
        'S_done.CLASSCONSTANTCACHE = eps', 'S_done.CLASSCONSTANTHISTORY = S_raw.CLASSCONSTANTHISTORY',
        '$class_constant_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        'S_zero = $drive_steps(S_edge,0)', 'S_zero.COMPLETION = BUDGET', 'S_zero[.COMPLETION = NORMAL] = S_edge',
        'S_one = $drive_steps(S_edge,1)', 'S_one.COMPLETION = BUDGET',
        '$drive(S_zero[.COMPLETION = NORMAL],30000) = S_done', '$drive(S_one[.COMPLETION = NORMAL],30000) = S_done']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), SOURCE, *modules, *(ROOT / p for p in (
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
