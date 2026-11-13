#!/usr/bin/env python3
"""Check class SET-backed short GET pairs and ordered unique/shared release."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import deprecated_reference_object_untyped_hook_actual_pair_review_protocol as actual_pair
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('deprecated_reference_object_untyped_set_backed_class_hook_pair_review')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = actual_pair.quoted
PREFIX = actual_pair.PREFIX
SELECTED = actual_pair.SELECTED.replace('B|Q|C|D|H|9|P|', 'B|Q|S|C|R|D|H|9|P|').replace('pinstancestorage.NEXT = 3', 'pinstancestorage.NEXT = 4')


def fields(fixture, source, actual):
    form = 'Actual' if actual else 'Implicit'
    root = quoted('Ns285SetBackedClass' + form + 'PairPeer' + chr(92) + 'Root285')
    parameter = 'incoming' if actual else 'value'
    checks = [
        'U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(source)).decode()) + ')',
        'S_raw = $hook_peer_pause(S_start[.COMPLETION = NORMAL],0,0,30000)', '$hook_peer_ready(S_raw,0,0)',
        'S_raw.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask_tail*',
        'S_raw.ORIGIN = (porigin_site)', 'S_raw.RESULT = REFERENCE n_reference',
        'S_raw.STORE[n_reference] = DEFINED (POBJECT n_receiver)',
        'S_raw.CURRENT = eps', 'S_raw.FRAMES = eps', 'S_raw.HELD = eps',
        'S_raw.OBJECTS[n_receiver] = INSTANCE porigin_root', '$class_at(S_raw.CLASSES,porigin_root) = (pclassdesc_root)',
        'pclassdesc_root.NAME = ' + root, 'pclassdesc_root.KIND = "class"', 'pclassdesc_root.PARENT = eps',
        '~pclassdesc_root.READONLY', '$trait_plan(S_raw,pclassdesc_root).TRAITS = eps',
        'pclassdesc_root.PROPERTIES = [ppropertydesc_anchor,ppropertydesc_middle,ppropertydesc_tail,ppropertydesc_rootpad]',
        '$objectprops_at(S_raw.OBJECTPROPS,n_receiver) = ([ppropertyslot_anchor,ppropertyslot_middle,ppropertyslot_tail,ppropertyslot_rootpad])',
        'ppropertyslot_anchor.STATE = PROP_VALUE (DIRECT (PINT 31))',
        'ppropertyslot_middle.STATE = PROP_VALUE (DIRECT (POBJECT n_middle))',
        'ppropertyslot_tail.STATE = PROP_VALUE (DIRECT (POBJECT n_leaf))',
        'ppropertyslot_rootpad.STATE = PROP_VALUE (DIRECT (POBJECT n_padleaf))',
        'S_raw.OBJECTS[n_middle] = INSTANCE porigin_middle',
        '$objectprops_at(S_raw.OBJECTPROPS,n_middle) = ([ppropertyslot_middlepad,ppropertyslot_edge])',
        'S_raw.OBJECTS[n_leaf] = INSTANCE porigin_leaf', '$class_at(S_raw.CLASSES,porigin_leaf) = (pclassdesc_leaf)',
        '$objectprops_at(S_raw.OBJECTPROPS,n_leaf) = (eps)',
        'S_raw.OBJECTS[n_padleaf] = INSTANCE porigin_padleaf', '$objectprops_at(S_raw.OBJECTPROPS,n_padleaf) = (eps)',
        '$node_children(S_raw,HCELL n_reference) = [HOBJECT n_receiver]',
        '$node_children(S_raw,HOBJECT n_receiver) = [HOBJECT n_middle,HOBJECT n_leaf,HOBJECT n_padleaf]',
        '$node_children(S_raw,HOBJECT n_middle) = [HOBJECT n_leaf]', '$node_children(S_raw,HOBJECT n_leaf) = eps',
        '$node_children(S_raw,HOBJECT n_padleaf) = eps',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_receiver) = 1', '$heap_owners($heap_graph(S_raw),HOBJECT n_leaf) = 3',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_padleaf) = 1', '~(n_padleaf <- S_raw.DESTRUCTION.CALLED)',
        'S_global = $global_table_view(S_raw)', '$lookup(S_global.ENV,$ptascii("outside285peer")) = (n_outside)',
        'S_global.STORE[n_outside] = DEFINED (POBJECT n_leaf)',
        '$lookup(S_global.ENV,$ptascii("set285peer")) = (n_set)', 'S_global.STORE[n_set] = DEFINED (PBOOL false)',
        '$lookup(S_global.ENV,$ptascii("get285peer")) = (n_get)', 'S_global.STORE[n_get] = DEFINED (PBOOL false)',
        'S_raw.PROPREFS = eps', '$call_descriptors_valid(S_raw)', '$ccn_output(S_raw.EVENTS) = $ptascii("B|Q|S|C|")',
    ]
    for field, owner, name in [('anchor', 'n_receiver', 'anchor'), ('middle', 'n_receiver', 'middle'),
                             ('tail', 'n_receiver', 'tail'), ('rootpad', 'n_receiver', 'pad'),
                             ('middlepad', 'n_middle', 'pad'), ('edge', 'n_middle', 'edge')]:
        prop, slot = 'ppropertydesc_' + field, 'ppropertyslot_' + field
        checks += ['$property_slot_descriptor(S_raw,' + owner + ',' + slot + ') = (' + prop + ')',
                   slot + '.DECL = (' + prop + '.ORIGIN)', slot + '.NAME = ' + prop + '.KEY',
                   prop + '.NAME = $ptascii("' + name + '")', prop + '.KEY = ' + prop + '.NAME',
                   prop + '.TYPE = eps', prop + '.VISIBILITY = PROPERTY_PUBLIC', prop + '.SETVISIBILITY = eps',
                   '~' + prop + '.STATIC', '~' + prop + '.READONLY', '~' + prop + '.FINAL',
                   '$class_constant_reference_object_field_type(S_raw,' + prop + ',' + slot + ')']
        if field == 'rootpad':
            checks += [prop + '.DEFAULT = PROP_NULL', '$property_hook_source_declared(S_raw,' + prop + ')',
                       '$class_constant_reference_object_untyped_hook_field(S_raw,n_receiver,' + prop + ',' + slot + ')',
                       '$property_slot_release_job(S_raw,n_receiver,' + slot + ') = [DESTRUCTION_VALUE (HOBJECT n_padleaf)]']
        else:
            checks += ['~$property_hook_source_declared(S_raw,' + prop + ')']
    checks += [
        '$property_hook_pair_origins(S_raw,ppropertydesc_rootpad) = [porigin_get,porigin_set]',
        '$property_hook_origin(S_raw,ppropertydesc_rootpad) = (porigin_get)',
        '$property_set_origin(S_raw,ppropertydesc_rootpad) = (porigin_set)',
        '$property_hook_pair_backed(S_raw,ppropertydesc_rootpad)', '~$property_hook_virtual(S_raw,ppropertydesc_rootpad)',
        'porigin_get = PORIGIN n_source pcpath_get', 'porigin_set = PORIGIN n_source pcpath_set',
        'ppropertydesc_rootpad.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_get = pcpath_group ++ [PCFIELD 4,PCINDEX 0]', 'pcpath_set = pcpath_group ++ [PCFIELD 4,PCINDEX 1]',
        '$origin_node(S_raw.SOURCES,porigin_get) = (phpType38_get)', '$origin_node(S_raw.SOURCES,porigin_set) = (phpType38_set)',
        'phpType38_get = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) phpType11_get (SEQUENCE eps) expression_get metadata_get',
        'phpType38_set = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) phpType11_set phpType16_set (SEQUENCE statement_set*) metadata_set',
        '$hook_parameter_facts(metadata_get) = [false]', '$hook_parameter_facts(metadata_set) = [' + str(actual).lower() + ']',
        '~$hook_body_backed(expression_get,ppropertydesc_rootpad.NAME)',
        '$hook_body_backed(SEQUENCE statement_set*,ppropertydesc_rootpad.NAME)',
        '$hook_pair_backed_headers(phpType38_get,phpType38_set,ppropertydesc_rootpad.NAME)' if not actual else '$hook_pair_untyped_parameter_headers(phpType38_get,phpType38_set,ppropertydesc_rootpad.NAME)',
        '~$hook_pair_untyped_trait_set_backed_headers(phpType38_get,phpType38_set,ppropertydesc_rootpad.NAME)',
        'phpType38_no_backing_set = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) phpType11_set phpType16_set (SEQUENCE eps) metadata_set',
        '~$hook_pair_backed_headers(phpType38_get,phpType38_no_backing_set,ppropertydesc_rootpad.NAME)',
        '~$hook_pair_untyped_parameter_headers(phpType38_get,phpType38_no_backing_set,ppropertydesc_rootpad.NAME)',
        '$function_at(S_raw.FUNCTIONS,porigin_get) = (pfunction_get)', '$function_at(S_raw.FUNCTIONS,porigin_set) = (pfunction_set)',
        'pfunction_get.NAME = ' + root + ' ++ $ptascii("::$pad::get")',
        'pfunction_set.NAME = ' + root + ' ++ $ptascii("::$pad::set")',
        'pfunction_get.SIGNATURE = {PARAMETERS eps, RETURNS eps, BYREF false}',
        'pfunction_set.SIGNATURE.PARAMETERS = [{NAME $ptascii("' + parameter + '"), TYPE eps, BYREF false, VARIADIC false, REQUIRED true, DEFAULT PSNONE}]',
        'pfunction_set.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "void"]))]', '~pfunction_set.SIGNATURE.BYREF',
        'pfunction_get.DEFAULTS = eps', 'pfunction_set.DEFAULTS = eps', '~pfunction_get.EARLY', '~pfunction_set.EARLY',
        'pfunction_get.BODY = pcpath_get ++ [PCFIELD 5]', 'pfunction_set.BODY = pcpath_set ++ [PCFIELD 5]',
        '$origin_node(S_raw.SOURCES,PORIGIN n_source pfunction_get.BODY) = (expression_get)',
        '$code_expression(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = ((z_get,false))',
        '$arrow_line(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = (z_get)',
        r'$(z_get > 0 /\ z_get >= $source_line(metadata_get) /\ z_get <= $source_end_line(metadata_get))',
        '$hook_pair_parameter_get_receipts(S_raw,pfunction_get,expression_get,metadata_get)',
        '$hook_pair_parameter_set_receipts(S_raw,pfunction_set,SEQUENCE statement_set*,metadata_set)',
        '$ptascii("' + parameter + '") <- pfunction_set.CVS',
    ]
    if actual:
        checks += [
            'phpType16_set = SEQUENCE ([phpType17_parameter])', 'pcpath_parameter = pcpath_set ++ [PCFIELD 4,PCINDEX 0]',
            '$origin_node(S_raw.SOURCES,PORIGIN n_source pcpath_parameter) = (phpType17_parameter)',
            'phpType17_parameter = NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN false) (BOOLEAN false) (NExprVariable (BYTES text_parameter) metadata_variable) ABSENT (SEQUENCE eps) metadata_parameter',
            '$base64(text_parameter) = $ptascii("incoming")',
            '$code_expression(pfunction_set.CODE.EXPRESSIONS,pcpath_parameter) = (($psline(metadata_parameter),false))',
            r'$($psline(metadata_parameter) > 0 /\ $psline(metadata_parameter) >= $source_line(metadata_set) /\ $psline(metadata_parameter) <= $source_end_line(metadata_set))',
            'phpType38_short_set = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) phpType11_set phpType16_set (NScalarInt (INTEGER 0) eps) metadata_set',
            '~$hook_pair_untyped_parameter_headers(phpType38_get,phpType38_short_set,ppropertydesc_rootpad.NAME)',
            '$hook_pair_untyped_trait_set_backed_headers(phpType38_get,phpType38_short_set,ppropertydesc_rootpad.NAME)',
        ]
    else:
        checks += ['phpType16_set = SEQUENCE eps',
                   '$origin_node(S_raw.SOURCES,PORIGIN n_source (pcpath_set ++ [PCFIELD 4,PCINDEX 0])) = eps',
                   '$code_expression(pfunction_set.CODE.EXPRESSIONS,pcpath_set ++ [PCFIELD 4,PCINDEX 0]) = eps']
    checks += [
        'S_class = $class_constant_selector(S_raw,expression_class,z)', 'S_class.COMPLETION = NORMAL',
        'S_class.RESULT = KNOWN (PSTRING pclassdesc_root.NAME)', '$class_constant_reference_object_graph(S_class,n_receiver,eps)',
        '$class_constant_reference_object_capture_entry(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        'S_class.SOURCES = [pcunit]',
        '$origin_node(S_class.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty phpType14_group phpType24_group ABSENT phpType56_group (SEQUENCE ([phpType38_get,phpType38_set])) metadata_group)',
        'S_functions = S_class[.FUNCTIONS = [pfunction_get,pfunction_set]]',
        '$property_hook_pair_origins(S_functions,ppropertydesc_rootpad) = [porigin_get,porigin_set]',
        'S_get_code = S_functions[.FUNCTIONS = [pfunction_get[.CODE.EXPRESSIONS = $peer_without_param(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY)],pfunction_set]]',
        '$property_hook_pair_origins(S_get_code,ppropertydesc_rootpad) = eps',
        'S_parent = S_functions[.CLASSES = [pclassdesc_root[.PARENT = (pclassdesc_leaf.NAME)]]]',
        '$property_hook_pair_origins(S_parent,ppropertydesc_rootpad) = eps',
        'S_early = S_functions[.FUNCTIONS = [pfunction_get,pfunction_set[.EARLY = true]]]',
        '$property_hook_pair_origins(S_early,ppropertydesc_rootpad) = eps',
    ]
    for role in ('get', 'set'):
        fact = 'false' if role == 'set' and actual else 'true'
        params, body = ('(SEQUENCE eps)', 'expression_get') if role == 'get' else ('phpType16_set', '(SEQUENCE statement_set*)')
        checks += [
            'metadata_bad_' + role + ' = (MhookParameterList ' + fact + ') :: $hpr_without_fact(metadata_' + role + ')',
            'phpType38_bad_' + role + ' = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) phpType11_' + role + ' ' + params + ' ' + body + ' metadata_bad_' + role,
            'pcnode_bad_' + role + ' = NStmtProperty phpType14_group phpType24_group ABSENT phpType56_group (SEQUENCE ([' + ('phpType38_bad_get,phpType38_set' if role == 'get' else 'phpType38_get,phpType38_bad_set') + '])) metadata_group',
            'S_bad_' + role + ' = S_class[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group pcnode_bad_' + role + ') :: (PCOCCURRENCE pcpath_' + role + ' phpType38_bad_' + role + ') :: pcunit.OCCURRENCES]]]',
            '$property_hook_pair_origins(S_bad_' + role + ',ppropertydesc_rootpad) = eps',
            '~$class_constant_reference_object_graph(S_bad_' + role + ',n_receiver,eps)',
        ]
    if actual:
        checks += ['S_param_code = S_functions[.FUNCTIONS = [pfunction_get,pfunction_set[.CODE.EXPRESSIONS = $peer_without_param(pfunction_set.CODE.EXPRESSIONS,pcpath_parameter)]]]',
                   '$property_hook_pair_origins(S_param_code,ppropertydesc_rootpad) = eps']
    checks += [
        'S_step = $drive_steps(S_raw,1)', 'S_step.COMPLETION = BUDGET', 'S_release = S_step[.COMPLETION = NORMAL]',
        'S_release.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
        'ptask_marker = CLASS_CONST_OBJECT_CAPTURE porigin_site ' + root + ' z',
        'pdestructionoperation.SOURCE = ptask_marker', 'pdestructionoperation.VALUE = KNOWN PNULL',
        '$eager_operation_source_guard(S_release,pdestructionoperation)', '$task_nodes(ptask_marker) = eps',
        'S_middle = $hook_peer_pause(S_release,1,n_middle,30000)', '$hook_peer_ready(S_middle,1,n_middle)',
        '$instance_storage_for(S_middle,n_receiver) = (pinstancestorage_root)', 'pinstancestorage_root.NEXT = 2',
        '$heap_owners($heap_graph(S_middle),HOBJECT n_leaf) = 3',
        'S_pad = $hook_peer_pause(S_middle,2,n_middle,30000)', '$hook_peer_ready(S_pad,2,n_middle)',
        'S_edge = $hook_peer_pause(S_pad,3,n_middle,30000)', '$hook_peer_ready(S_edge,3,n_middle)',
        '$heap_owners($heap_graph(S_edge),HOBJECT n_leaf) = 2', '~(n_leaf <- S_edge.DESTRUCTION.CALLED)',
        '$heap_owners($heap_graph(S_edge),HOBJECT n_padleaf) = 1', '~(n_padleaf <- S_edge.DESTRUCTION.CALLED)',
        'S_tail = $hook_peer_pause(S_edge,4,n_receiver,30000)', '$hook_peer_ready(S_tail,4,n_receiver)',
        '$objectprops_at(S_tail.OBJECTPROPS,n_receiver) = ([ppropertyslot_anchor[.STATE = PROP_UNSET],ppropertyslot_middle[.STATE = PROP_UNSET],ppropertyslot_tail[.STATE = PROP_UNSET],ppropertyslot_rootpad[.STATE = PROP_UNSET]])',
        '$node_children(S_tail,HOBJECT n_receiver) = eps', '$heap_owners($heap_graph(S_tail),HOBJECT n_leaf) = 1',
        '$heap_owners($heap_graph(S_tail),HOBJECT n_padleaf) = 0', 'n_padleaf <- S_tail.DESTRUCTION.CALLED',
        '$ccn_output(S_tail.EVENTS) = $ptascii("B|Q|S|C|R|D|H|9|P|I|F|U|")',
        'S_pair = $hook_peer_pause(S_tail,5,n_middle,30000)', '$hook_peer_ready(S_pair,5,n_middle)',
        '$ccn_output(S_pair.EVENTS) = $ptascii("B|Q|S|C|R|D|H|9|P|I|F|U|M|N|")',
        'S_pair.STORE[n_set] = DEFINED (PBOOL false)', 'S_pair.STORE[n_get] = DEFINED (PBOOL false)',
        'S_pair.RESULT = KNOWN pvalue_member', '$string_bytes(pvalue_member) = ($ptascii("B"))',
        '~((HCELL n_reference) <- S_pair.ALLOCATIONS)', '~((HOBJECT n_receiver) <- S_pair.ALLOCATIONS)',
        '~((HOBJECT n_middle) <- S_pair.ALLOCATIONS)', '~((HOBJECT n_padleaf) <- S_pair.ALLOCATIONS)',
        '(HOBJECT n_leaf) <- S_pair.ALLOCATIONS', '$heap_owners($heap_graph(S_pair),HOBJECT n_leaf) = 1',
        'S_pair.DESTRUCTION.OPERATIONS = eps', '$call_descriptors_valid(S_pair)',
        'S_done = $drive(S_pair,30000)', 'S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = $ptascii("B|Q|S|C|R|D|H|9|P|I|F|U|M|N|H|10|Z|L|E|")',
        '~((HOBJECT n_leaf) <- S_done.ALLOCATIONS)', 'S_done.DESTRUCTION.OPERATIONS = eps',
        '$class_constant_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        'S_zero = $drive_steps(S_edge,0)', 'S_zero.COMPLETION = BUDGET', 'S_zero[.COMPLETION = NORMAL] = S_edge',
        'S_one = $drive_steps(S_edge,1)', 'S_one.COMPLETION = BUDGET',
        '$drive(S_zero[.COMPLETION = NORMAL],30000) = S_done', '$drive(S_one[.COMPLETION = NORMAL],30000) = S_done',
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['implicit', 'actual'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    source = SOURCES / ('set-backed-untyped-class-' + args.form + '-pair-shared.php')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(actual_pair.__file__), Path(actual_pair.implicit.__file__), Path(actual_pair.block.__file__),
             Path(actual_pair.pair.__file__), Path(actual_pair.peer.__file__), Path(actual_pair.header.__file__), source, *modules,
             *(ROOT / p for p in ('spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
                 'frontend/SourcePrinter.php', 'tests/semantics/deprecated_class_constant_fetch_protocol.py',
                 'tests/semantics/deprecated_parameter_default_protocol.py', 'tests/semantics/deprecated_global_constant_protocol.py',
                 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py',
                 'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe',
                 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'form': args.form,
              'mode': 'fixture-SL', 'source_agreement_credit': 0, 'passed': False}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks = fields(checked['fixture'], source, args.form == 'actual'); report['premises'] = len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        (out / 'protocol.watsup').write_text(PREFIX + SELECTED + '\ndec $main() : bool\ndef $main() = true\n'
                                           + ''.join('  -- if ' + c + '\n' for c in checks))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                      *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout']
                            and not report['process']['group_after'] and report['stdout'] == 'true\n'
                            and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed'], report.get('stderr', '')[:4000]
    print('pass', args.form, report['premises'])


if __name__ == '__main__': main()
