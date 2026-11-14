#!/usr/bin/env python3
"""Check appended getter storage, shared children and direct-unset cleanup."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('ordinary_parent_unbacked_get_child_slot_review')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = lambda s: json.dumps(base64.b64encode(s.encode()).decode())

PREFIX = r'''
var U : program
dec $ucsp_output(pevent*) : ptbytes
def $ucsp_output(eps) = eps
def $ucsp_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $ucsp_output(pevent*)
dec $ucsp_phase(pstate,nat,nat) : bool
def $ucsp_phase(S,0,n) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text_name) metadata)) :: ptask*
  -- if $base64(text_name) = $ptascii("root289")
def $ucsp_phase(S,1,n) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask*
  -- if pinstancestorage.OBJECT = n /\ pinstancestorage.NEXT = 0
def $ucsp_phase(S,2,n) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask*
  -- if pinstancestorage.OBJECT = n /\ pinstancestorage.NEXT = 2
def $ucsp_phase(S,3,n) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask*
  -- if pinstancestorage.OBJECT = n /\ pinstancestorage.NEXT = 3
def $ucsp_phase(S,4,n) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text_name) metadata)) :: ptask*
  -- if $base64(text_name) = $ptascii("outside289peer")
def $ucsp_phase(S,n_stage,n) = false -- otherwise
dec $ucsp_seek(pstate,nat,nat,nat) : pstate
def $ucsp_seek(S,n_stage,n_object,n) = S[.COMPLETION = NORMAL]
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $ucsp_phase(S,n_stage,n_object) \/ n = 0
def $ucsp_seek(S,n_stage,n_object,n) = $ucsp_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,n_object,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$ucsp_phase(S,n_stage,n_object) /\ $(n > 0)
def $ucsp_seek(S,n_stage,n_object,n) = S -- otherwise
'''


def fields(fixture, source, form):
    namespace = 'Ns289UnbackedChildSlot' + form.title() + 'Peer' + chr(92)
    checks = [
        'U = ' + fixture, 'S_start = $php_run(U,0,' + quoted(str(source)) + ')',
        'S_raw = $ucsp_seek(S_start,0,0,30000)', '$ucsp_phase(S_raw,0,0)', 'S_raw.COMPLETION = NORMAL',
        'S_raw.CURRENT = eps', 'S_raw.FRAMES = eps', 'S_raw.HELD = eps',
        '$lookup(S_raw.ENV,$ptascii("root289")) = (n_rootcell)', 'S_raw.STORE[n_rootcell] = DEFINED (POBJECT n_root)',
        '$lookup(S_raw.ENV,$ptascii("outside289peer")) = (n_outside)', 'S_raw.STORE[n_outside] = DEFINED (POBJECT n_leaf)',
        '$lookup(S_raw.ENV,$ptascii("get289peer")) = (n_get)', 'S_raw.STORE[n_get] = DEFINED (PBOOL false)',
        'S_raw.OBJECTS[n_root] = INSTANCE porigin_root', '$class_at(S_raw.CLASSES,porigin_root) = (pclassdesc_root)',
        'pclassdesc_root.NAME = $base64(' + quoted(namespace + 'Root289') + ')',
        'pclassdesc_root.KIND = "class"', 'pclassdesc_root.PARENT = (ptbytes_parent)', '~pclassdesc_root.READONLY',
        'pclassdesc_root.PROPERTIES = [ppropertydesc_middle,ppropertydesc_pad,ppropertydesc_tail]',
        'ptbytes_parent = $base64(' + quoted(namespace + 'Parent289') + ')',
        '$class_named(S_raw.CLASSNAMES,$ptlc(ptbytes_parent)) = (porigin_parent)',
        '$class_at(S_raw.CLASSES,porigin_parent) = (pclassdesc_parent)',
        'pclassdesc_parent.NAME = ptbytes_parent', 'pclassdesc_parent.KIND = "class"',
        'pclassdesc_parent.PARENT = eps', '~pclassdesc_parent.READONLY',
        'pclassdesc_parent.PROPERTIES = [ppropertydesc_anchor,ppropertydesc_parentpad]',
        '$trait_plan(S_raw,pclassdesc_root).TRAITS = eps', '$trait_plan(S_raw,pclassdesc_parent).TRAITS = eps',
        '$class_link_at(S_raw.LINKEDPARENTS,porigin_root) = (SOURCE_PARENT porigin_parent)',
        '$property_hook_pair_source_headers(S_raw,pclassdesc_root,pclassdesc_parent)',
        '$property_hook_pair_plain_parent(S_raw,pclassdesc_parent.PROPERTIES)',
        '$property_layout(S_raw,porigin_root,|S_raw.CLASSES|) = [ppropertydesc_anchor,ppropertydesc_middle,ppropertydesc_tail,ppropertydesc_pad]',
        '$property_info_layout(S_raw,porigin_root,|S_raw.CLASSES|) = [ppropertydesc_middle,ppropertydesc_pad,ppropertydesc_tail,ppropertydesc_anchor]',
        '$objectprops_at(S_raw.OBJECTPROPS,n_root) = ([ppropertyslot_anchor,ppropertyslot_middle,ppropertyslot_tail,ppropertyslot_pad])',
        'ppropertyslot_anchor.STATE = PROP_VALUE (DIRECT (PINT 31))',
        'ppropertyslot_middle.STATE = PROP_VALUE (DIRECT (POBJECT n_middle))',
        'ppropertyslot_tail.STATE = PROP_VALUE (DIRECT (POBJECT n_tail))',
        'ppropertyslot_pad.STATE = PROP_VALUE (DIRECT (POBJECT n_pad))',
        'ppropertydesc_pad.DEFAULT = PROP_NULL',
        '$property_default_state(S_raw,ppropertydesc_parentpad) = (PROP_VALUE (DIRECT (PINT 99)))',
        '$property_default_state(S_raw,ppropertydesc_pad) = (PROP_VALUE (DIRECT PNULL))',
        '$property_hook_ordinary_parent(S_raw,ppropertydesc_pad,|S_raw.CLASSES|) = (ppropertydesc_parentpad)',
        '$property_hook_ordinary_backing(S_raw,ppropertydesc_pad,|S_raw.CLASSES|)',
        '~$property_hook_override_backed(S_raw,ppropertydesc_pad)', '~$property_hook_virtual(S_raw,ppropertydesc_pad)',
        '~$property_hook_pair_declared(S_raw,ppropertydesc_pad)', '$property_set_origin(S_raw,ppropertydesc_pad) = eps',
        '$property_hook_origin(S_raw,ppropertydesc_pad) = (porigin_get)',
        'ppropertydesc_pad.ORIGIN = PORIGIN n_source pcpath_property',
        '$property_declaring_class(S_raw.CLASSES,PORIGIN n_source pcpath_property) = (porigin_root)',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        'porigin_get = PORIGIN n_source (pcpath_group ++ [PCFIELD 4,PCINDEX 0])',
        '$origin_node(S_raw.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER 1) ABSENT (SEQUENCE ([NPropertyItem (NVarLikeIdentifier (BYTES text_pad) metadata_pad) ABSENT metadata_item])) (SEQUENCE ([phpType38_get])) metadata_group)',
        '$source_unit(S_raw.SOURCES,n_source) = (pcunit)', 'pcunit = $pcsource(pcunit.ID,pcunit.AST)',
        '$base64(text_pad) = $ptascii("pad")',
        'phpType38_get = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) phpType11_get (SEQUENCE eps) phpType39_get metadata_get',
        '$hook_parameter_facts(metadata_get) = [false]', '~$hook_body_backed(phpType39_get,$ptascii("pad"))',
        '$function_at(S_raw.FUNCTIONS,porigin_get) = (pfunction_get)',
        'pfunction_get.NAME = pclassdesc_root.NAME ++ $ptascii("::$pad::get")',
        'pfunction_get.SIGNATURE = {PARAMETERS eps, RETURNS eps, BYREF false}',
        'pfunction_get.DEFAULTS = eps', '~pfunction_get.EARLY',
        'pfunction_get.BODY = pcpath_group ++ [PCFIELD 4,PCINDEX 0,PCFIELD 5]',
        '$objectprops_at(S_raw.OBJECTPROPS,n_middle) = ([ppropertyslot_middlepad,ppropertyslot_middleedge])',
        'ppropertyslot_middlepad.STATE = PROP_VALUE (DIRECT (PBOOL true))',
        'ppropertyslot_middleedge.STATE = PROP_VALUE (DIRECT (POBJECT n_leaf))',
        '$objectprops_at(S_raw.OBJECTPROPS,n_tail) = ([ppropertyslot_tailedge])',
        'ppropertyslot_tailedge.STATE = PROP_VALUE (DIRECT (POBJECT n_leaf))',
        '$objectprops_at(S_raw.OBJECTPROPS,n_pad) = (eps)', '$objectprops_at(S_raw.OBJECTPROPS,n_leaf) = (eps)',
        '$node_children(S_raw,HOBJECT n_root) = [HOBJECT n_middle,HOBJECT n_tail,HOBJECT n_pad]',
        '$node_children(S_raw,HOBJECT n_middle) = [HOBJECT n_leaf]', '$node_children(S_raw,HOBJECT n_tail) = [HOBJECT n_leaf]',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_leaf) = 3', '$heap_owners($heap_graph(S_raw),HOBJECT n_pad) = 1',
        '$ucsp_output(S_raw.EVENTS) = $ptascii("B|Q|G|W|C|")',
        '$property_slot_descriptor(S_raw,n_root,ppropertyslot_pad[.DECL = (ppropertydesc_parentpad.ORIGIN)]) = eps',
        '$property_slot_descriptor(S_raw,n_middle,ppropertyslot_middlepad) = (ppropertydesc_middlepad)',
        '$property_hook_child_append_slot(S_raw,ppropertydesc_parentpad,ppropertydesc_pad)',
        '$property_layout_appended(S_raw,pclassdesc_parent.PROPERTIES,pclassdesc_root.PROPERTIES,[ppropertydesc_anchor,ppropertydesc_pad,ppropertydesc_middle,ppropertydesc_tail]) = [ppropertydesc_anchor,ppropertydesc_middle,ppropertydesc_tail,ppropertydesc_pad]',
        '~$property_hook_child_append_slot(S_raw,ppropertydesc_parentpad,ppropertydesc_middlepad[.DEFAULT = PROP_NULL])',
        '~$property_hook_child_append_slot(S_raw,ppropertydesc_pad,ppropertydesc_middlepad[.DEFAULT = PROP_NULL])',
        'statement_default = NStmtProperty (SEQUENCE eps) (INTEGER 1) ABSENT (SEQUENCE ([NPropertyItem (NVarLikeIdentifier (BYTES text_pad) metadata_pad) (NScalarInt (INTEGER 0) eps) metadata_item])) (SEQUENCE ([phpType38_get])) metadata_group',
        'S_default = S_raw[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group statement_default) :: pcunit.OCCURRENCES]]]',
        '~$property_hook_child_append_slot(S_default,ppropertydesc_parentpad,ppropertydesc_pad)',
        'phpType39_backed = NExprPropertyFetch (NExprVariable (BYTES "dGhpcw==") eps) (NIdentifier (BYTES "cGFk") eps) eps',
        '$hook_body_backed(phpType39_backed,$ptascii("pad"))',
        'phpType38_backed = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) phpType11_get (SEQUENCE eps) phpType39_backed metadata_get',
        'statement_backed = NStmtProperty (SEQUENCE eps) (INTEGER 1) ABSENT (SEQUENCE ([NPropertyItem (NVarLikeIdentifier (BYTES text_pad) metadata_pad) ABSENT metadata_item])) (SEQUENCE ([phpType38_backed])) metadata_group',
        'S_backed = S_raw[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group statement_backed) :: pcunit.OCCURRENCES]]]',
        '~$property_hook_child_append_slot(S_backed,ppropertydesc_parentpad,ppropertydesc_pad)',
        '$property_layout_appended(S_backed,pclassdesc_parent.PROPERTIES,pclassdesc_root.PROPERTIES,[ppropertydesc_anchor,ppropertydesc_pad,ppropertydesc_middle,ppropertydesc_tail]) = [ppropertydesc_anchor,ppropertydesc_pad,ppropertydesc_middle,ppropertydesc_tail]',
        'phpType38_byref = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11_get (SEQUENCE eps) phpType39_get metadata_get',
        'statement_byref = NStmtProperty (SEQUENCE eps) (INTEGER 1) ABSENT (SEQUENCE ([NPropertyItem (NVarLikeIdentifier (BYTES text_pad) metadata_pad) ABSENT metadata_item])) (SEQUENCE ([phpType38_byref])) metadata_group',
        'S_byref = S_raw[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group statement_byref) :: pcunit.OCCURRENCES]]]',
        '~$property_hook_child_append_slot(S_byref,ppropertydesc_parentpad,ppropertydesc_pad)',
        'pclassdesc_parented = pclassdesc_parent[.PARENT = (pclassdesc_root.NAME)]',
        'S_parented = S_raw[.CLASSES = [pclassdesc_root,pclassdesc_parented]]',
        '~$property_hook_child_append_slot(S_parented,ppropertydesc_parentpad,ppropertydesc_pad)',
        'pclassdesc_parent.ORIGIN = PORIGIN n_source pcpath_parent',
        '$origin_node(S_raw.SOURCES,pclassdesc_parent.ORIGIN) = (NStmtClass phpType14_parent phpType24_parent phpType3_parent ABSENT phpType42_parent phpType23_parent metadata_parent)',
        '$origin_node(S_raw.SOURCES,pclassdesc_root.ORIGIN) = (NStmtClass phpType14_root phpType24_root phpType3_root phpType44_root phpType42_root phpType23_root metadata_root)',
        'phpType44_root =/= ABSENT',
        'statement_parented = NStmtClass phpType14_parent phpType24_parent phpType3_parent phpType44_root phpType42_parent phpType23_parent metadata_parent',
        'S_parent_header = S_raw[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_parent statement_parented) :: pcunit.OCCURRENCES]]]',
        '~$property_hook_child_append_slot(S_parent_header,ppropertydesc_parentpad,ppropertydesc_pad)',
        '$call_descriptors_valid(S_raw)', '$property_state_valid(S_raw)', '$heap_valid($heap_prune($heap_graph(S_raw)))',
    ]
    if form == 'short':
        checks += ['phpType39_get = expression_get',
                   '$origin_node(S_raw.SOURCES,PORIGIN n_source pfunction_get.BODY) = (expression_get)']
    else:
        checks += ['phpType39_get = SEQUENCE statement_get*',
                   '$function_body_tasks(S_raw,pfunction_get) = $statement_tasks(statement_get*,(PORIGIN n_source pfunction_get.BODY),0) ++ [$function_fallthrough(S_raw,pfunction_get)]']
    for name in ('anchor', 'middle', 'tail', 'pad'):
        desc, slot = 'ppropertydesc_' + name, 'ppropertyslot_' + name
        checks += ['$property_slot_descriptor(S_raw,n_root,' + slot + ') = (' + desc + ')',
                   slot + '.DECL = (' + desc + '.ORIGIN)', slot + '.NAME = ' + desc + '.KEY',
                   desc + '.NAME = $ptascii("' + name + '")',
                   desc + '.TYPE = eps', desc + '.VISIBILITY = PROPERTY_PUBLIC', desc + '.SETVISIBILITY = eps',
                   '~' + desc + '.STATIC', '~' + desc + '.READONLY', '~' + desc + '.FINAL']
    for change in ('[.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]]', '[.VISIBILITY = PROPERTY_PRIVATE]',
                   '[.SETVISIBILITY = (PROPERTY_PRIVATE)]', '[.STATIC = true]', '[.READONLY = true]', '[.FINAL = true]'):
        checks += ['~$property_hook_child_append_slot(S_raw,ppropertydesc_parentpad,ppropertydesc_pad' + change + ')']
    checks += [
        'S_storage = $ucsp_seek(S_raw,1,n_root,30000)', '$ucsp_phase(S_storage,1,n_root)',
        '$instance_storage_for(S_storage,n_root) = (pinstancestorage)', 'pinstancestorage.NEXT = 0',
        '$instance_storage_valid(S_storage,pinstancestorage)',
        '$ucsp_output(S_storage.EVENTS) = $ptascii("B|Q|G|W|C|R|")',
        '$heap_owners($heap_graph(S_storage),HOBJECT n_leaf) = 3',
        'S_middle = $ucsp_seek(S_storage,2,n_root,30000)', '$ucsp_phase(S_middle,2,n_root)',
        '$ucsp_output(S_middle.EVENTS) = $ptascii("B|Q|G|W|C|R|I|F|")',
        '$node_children(S_middle,HOBJECT n_root) = [HOBJECT n_tail,HOBJECT n_pad]',
        '$heap_owners($heap_graph(S_middle),HOBJECT n_leaf) = 2', '~((HOBJECT n_middle) <- S_middle.ALLOCATIONS)',
        '~(n_tail <- S_middle.DESTRUCTION.CALLED)', '~(n_pad <- S_middle.DESTRUCTION.CALLED)',
        'S_tail = $ucsp_seek(S_middle,3,n_root,30000)', '$ucsp_phase(S_tail,3,n_root)',
        '$ucsp_output(S_tail.EVENTS) = $ptascii("B|Q|G|W|C|R|I|F|T|")',
        '$node_children(S_tail,HOBJECT n_root) = [HOBJECT n_pad]',
        '$heap_owners($heap_graph(S_tail),HOBJECT n_leaf) = 1', '$heap_owners($heap_graph(S_tail),HOBJECT n_pad) = 1',
        '~((HOBJECT n_tail) <- S_tail.ALLOCATIONS)', '~(n_pad <- S_tail.DESTRUCTION.CALLED)',
        'S_outside = $ucsp_seek(S_tail,4,n_root,30000)', '$ucsp_phase(S_outside,4,n_root)',
        '$ucsp_output(S_outside.EVENTS) = $ptascii("B|Q|G|W|C|R|I|F|T|U|Z|")',
        '~((HOBJECT n_root) <- S_outside.ALLOCATIONS)', '~((HOBJECT n_pad) <- S_outside.ALLOCATIONS)',
        '(HOBJECT n_leaf) <- S_outside.ALLOCATIONS', '$heap_owners($heap_graph(S_outside),HOBJECT n_leaf) = 1',
        'S_outside.STORE[n_get] = DEFINED (PBOOL false)', 'S_outside.DESTRUCTION.OPERATIONS = eps',
        '$call_descriptors_valid(S_outside)', '$property_state_valid(S_outside)',
        'S_done = $drive(S_outside,30000)', 'S_done.COMPLETION = NORMAL',
        '$ucsp_output(S_done.EVENTS) = $ptascii("B|Q|G|W|C|R|I|F|T|U|Z|L|E|")',
        '~((HOBJECT n_leaf) <- S_done.ALLOCATIONS)', 'S_done.DESTRUCTION.OPERATIONS = eps',
        '$call_descriptors_valid(S_done)', '$property_state_valid(S_done)', '$heap_valid($heap_prune($heap_graph(S_done)))',
        'S_zero = $drive_steps(S_middle,0)', 'S_zero.COMPLETION = BUDGET', 'S_zero[.COMPLETION = NORMAL] = S_middle',
        'S_one = $drive_steps(S_middle,1)', 'S_one.COMPLETION = BUDGET',
        '$drive(S_zero[.COMPLETION = NORMAL],30000) = S_done', '$drive(S_one[.COMPLETION = NORMAL],30000) = S_done',
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['short', 'block'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    source = SOURCES / ('child-slot-' + args.form + '-shared.php')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), source, *modules, *(ROOT / p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
        'frontend/SourcePrinter.php', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py',
        'tests/semantics/static_types.py', 'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
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
        checks = fields(checked['fixture'], source, args.form); report['premises'] = len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        (out / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
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
