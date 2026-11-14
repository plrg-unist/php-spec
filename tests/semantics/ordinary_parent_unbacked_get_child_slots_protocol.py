#!/usr/bin/env python3
"""Check inherited getter initialization, source authority and appended cleanup."""
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
SOURCES = Path(__file__).with_name('ordinary_parent_unbacked_get_child_slots')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = lambda s: json.dumps(base64.b64encode(s.encode()).decode())

PREFIX = r'''
var U : program
dec $ucsa_output(pevent*) : ptbytes
def $ucsa_output(eps) = eps
def $ucsa_output((OUTPUT ptbytes) :: pevent_tail*) = ptbytes ++ $ucsa_output(pevent_tail*)
dec $ucsa_phase(pstate,nat,nat) : bool
def $ucsa_phase(S,0,n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook
  -- if S.TODO = (EVAL expression) :: ptask_tail*
def $ucsa_phase(S,0,n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook
  -- if S.TODO = (STMT statement) :: ptask_tail*
def $ucsa_phase(S,1,n) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text_name) metadata)) :: ptask_tail*
  -- if $base64(text_name) = $ptascii("box289")
def $ucsa_phase(S,2,n) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_tail*
  -- if pinstancestorage.OBJECT = n /\ pinstancestorage.NEXT = 0
def $ucsa_phase(S,3,n) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_tail*
  -- if pinstancestorage.OBJECT = n /\ pinstancestorage.NEXT = 2
def $ucsa_phase(S,4,n) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_tail*
  -- if pinstancestorage.OBJECT = n /\ pinstancestorage.NEXT = 3
def $ucsa_phase(S,n_stage,n) = false -- otherwise
dec $ucsa_seek(pstate,nat,nat,nat) : pstate
def $ucsa_seek(S,n_stage,n_object,n) = S[.COMPLETION = NORMAL]
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $ucsa_phase(S,n_stage,n_object) \/ n = 0
def $ucsa_seek(S,n_stage,n_object,n) = $ucsa_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,n_object,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$ucsa_phase(S,n_stage,n_object) /\ $(n > 0)
def $ucsa_seek(S,n_stage,n_object,n) = S -- otherwise
'''


def fields(fixture, source, kind):
    namespace = 'Ns289UnbackedChildSlot' + kind.title() + chr(92)
    checks = [
        'U = ' + fixture, 'S_start = $php_run(U,0,' + quoted(str(source)) + ')',
        'S_get = $ucsa_seek(S_start,0,0,30000)', '$ucsa_phase(S_get,0,0)', 'S_get.COMPLETION = NORMAL',
        'S_get.CURRENT = (pcallcontext)', 'pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook',
        'ppropertyhook.OBJECT = n_root', 'S_get.OBJECTS[n_root] = INSTANCE porigin_root',
        '$class_at(S_get.CLASSES,porigin_root) = (pclassdesc_root)',
        'pclassdesc_root.NAME = $base64(' + quoted(namespace + 'Box289') + ')',
        'pclassdesc_root.PARENT = (ptbytes_parent)',
        'ptbytes_parent = $base64(' + quoted(namespace + 'Parent289') + ')',
        'pclassdesc_root.PROPERTIES = [ppropertydesc_tag,ppropertydesc_middle,ppropertydesc_tail]',
        '$class_named(S_get.CLASSNAMES,$ptlc(ptbytes_parent)) = (porigin_parent)',
        '$class_at(S_get.CLASSES,porigin_parent) = (pclassdesc_parent)',
        'pclassdesc_parent.PARENT = eps', 'pclassdesc_parent.KIND = "class"',
        'pclassdesc_parent.PROPERTIES = [ppropertydesc_anchor,ppropertydesc_parenttag]',
        '$trait_plan(S_get,pclassdesc_root).TRAITS = eps', '$trait_plan(S_get,pclassdesc_parent).TRAITS = eps',
        '$class_link_at(S_get.LINKEDPARENTS,porigin_root) = (SOURCE_PARENT porigin_parent)',
        '$property_hook_pair_source_headers(S_get,pclassdesc_root,pclassdesc_parent)',
        '$property_hook_pair_plain_parent(S_get,pclassdesc_parent.PROPERTIES)',
        '$property_default_state(S_get,ppropertydesc_parenttag) = (PROP_VALUE (DIRECT (PINT 99)))',
        '$property_default_state(S_get,ppropertydesc_tag) = (PROP_VALUE (DIRECT PNULL))',
        '$property_layout(S_get,porigin_root,|S_get.CLASSES|) = [ppropertydesc_anchor,ppropertydesc_middle,ppropertydesc_tail,ppropertydesc_tag]',
        '$property_info_layout(S_get,porigin_root,|S_get.CLASSES|) = [ppropertydesc_tag,ppropertydesc_middle,ppropertydesc_tail,ppropertydesc_anchor]',
        '$objectprops_at(S_get.OBJECTPROPS,n_root) = ([ppropertyslot_anchor,ppropertyslot_middle,ppropertyslot_tail,ppropertyslot_tag])',
        'ppropertyslot_anchor.STATE = PROP_VALUE (DIRECT (PINT 31))',
        'ppropertyslot_middle.STATE = PROP_VALUE (DIRECT PNULL)', 'ppropertyslot_tail.STATE = PROP_VALUE (DIRECT PNULL)',
        'ppropertyslot_tag.STATE = PROP_VALUE (DIRECT PNULL)',
        '$property_slot_descriptor(S_get,n_root,ppropertyslot_tag) = (ppropertydesc_tag)',
        'ppropertyslot_tag.DECL = (ppropertydesc_tag.ORIGIN)',
        '$property_slot_descriptor(S_get,n_root,ppropertyslot_tag[.DECL = (ppropertydesc_parenttag.ORIGIN)]) = eps',
        '$property_hook_ordinary_parent(S_get,ppropertydesc_tag,|S_get.CLASSES|) = (ppropertydesc_parenttag)',
        '$property_hook_ordinary_backing(S_get,ppropertydesc_tag,|S_get.CLASSES|)',
        '~$property_hook_virtual(S_get,ppropertydesc_tag)', '~$property_hook_override_backed(S_get,ppropertydesc_tag)',
        '~$property_hook_pair_declared(S_get,ppropertydesc_tag)', '$property_set_origin(S_get,ppropertydesc_tag) = eps',
        '$property_hook_child_append_slot(S_get,ppropertydesc_parenttag,ppropertydesc_tag)',
        '~$property_hook_child_own_slot(S_get,ppropertydesc_parenttag,ppropertydesc_tag)',
        '$property_layout_appended(S_get,pclassdesc_parent.PROPERTIES,pclassdesc_root.PROPERTIES,[ppropertydesc_anchor,ppropertydesc_tag,ppropertydesc_middle,ppropertydesc_tail]) = [ppropertydesc_anchor,ppropertydesc_middle,ppropertydesc_tail,ppropertydesc_tag]',
        '$property_hook_origin(S_get,ppropertydesc_tag) = (porigin_get)',
        '$property_hook_function(S_get,ppropertyhook) = (pfunction_get)', 'pfunction_get.ORIGIN = porigin_get',
        'pfunction_get.NAME = pclassdesc_root.NAME ++ $ptascii("::$tag::get")',
        'pfunction_get.SIGNATURE = {PARAMETERS eps,RETURNS eps,BYREF false}',
        'pfunction_get.DEFAULTS = eps', '~pfunction_get.EARLY', 'pfunction_get.LINE = 18', 'pfunction_get.ENDLINE = 21',
        'ppropertydesc_tag.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        'porigin_get = PORIGIN n_source (pcpath_group ++ [PCFIELD 4,PCINDEX 0])',
        'pfunction_get.BODY = pcpath_group ++ [PCFIELD 4,PCINDEX 0,PCFIELD 5]',
        '$source_unit(S_get.SOURCES,n_source) = (pcunit)', 'pcunit = $pcsource(pcunit.ID,pcunit.AST)',
        '$origin_node(S_get.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER 1) ABSENT (SEQUENCE ([NPropertyItem (NVarLikeIdentifier (BYTES text_tag) metadata_tag) ABSENT metadata_item])) (SEQUENCE ([phpType38_get])) metadata_group)',
        '$base64(text_tag) = $ptascii("tag")',
        'phpType38_get = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) phpType11_get (SEQUENCE eps) phpType39_get metadata_get',
        '$hook_parameter_facts(metadata_get) = [false]', '~$hook_body_backed(phpType39_get,$ptascii("tag"))',
        '$hook_pair_parameter_get_receipts(S_get,pfunction_get,phpType39_get,metadata_get)',
        'S_globals = $global_table_view(S_get)', '$lookup(S_globals.ENV,$ptascii("gets289execution")) = (n_getcell)',
        'S_globals.STORE[n_getcell] = DEFINED (PINT 0)',
        'S_no_link = S_get[.LINKEDPARENTS = eps]',
        '$property_layout(S_no_link,porigin_root,|S_no_link.CLASSES|) = pclassdesc_root.PROPERTIES',
    ]
    if kind == 'short':
        # Ternary children leave LOCATION at the last literal before CODE/ARROW.
        checks += ['phpType39_get = expression_get', 'S_get.TODO = (EVAL expression_get) :: ptask_tail*',
                   '$code_expression(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = ((21,false))',
                   '$arrow_line(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = (21)']
    else:
        checks += ['phpType39_get = SEQUENCE (statement_first :: statement_tail*)',
                   'S_get.TODO = (STMT statement_first) :: ptask_tail*']
    for change in ('[.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]]', '[.VISIBILITY = PROPERTY_PRIVATE]',
                   '[.SETVISIBILITY = (PROPERTY_PRIVATE)]', '[.STATIC = true]', '[.READONLY = true]', '[.FINAL = true]'):
        checks += ['~$property_hook_child_append_slot(S_get,ppropertydesc_parenttag,ppropertydesc_tag' + change + ')']
    checks += [
        'S_raw = $ucsa_seek(S_get,1,n_root,30000)', '$ucsa_phase(S_raw,1,n_root)',
        'S_raw.CURRENT = eps', 'S_raw.FRAMES = eps', 'S_raw.HELD = eps',
        '$ucsa_output(S_raw.EVENTS) = $ptascii("N|B|")',
        '$lookup(S_raw.ENV,$ptascii("box289")) = (n_rootcell)', 'S_raw.STORE[n_rootcell] = DEFINED (POBJECT n_root)',
        '$objectprops_at(S_raw.OBJECTPROPS,n_root) = ([ppropertyslot_anchor,ppropertyslot_middle_live,ppropertyslot_tail_live,ppropertyslot_tag_live])',
        'ppropertyslot_middle_live.STATE = PROP_VALUE (DIRECT (POBJECT n_middle))',
        'ppropertyslot_tail_live.STATE = PROP_VALUE (DIRECT (POBJECT n_tail))',
        'ppropertyslot_tag_live.STATE = PROP_VALUE (DIRECT (POBJECT n_leaf))',
        '$node_children(S_raw,HOBJECT n_root) = [HOBJECT n_middle,HOBJECT n_tail,HOBJECT n_leaf]',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_root) = 1',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_middle) = 1', '$heap_owners($heap_graph(S_raw),HOBJECT n_tail) = 1',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_leaf) = 1',
        '$call_descriptors_valid(S_raw)', '$property_state_valid(S_raw)', '$heap_valid($heap_prune($heap_graph(S_raw)))',
        'S_storage = $ucsa_seek(S_raw,2,n_root,30000)', '$ucsa_phase(S_storage,2,n_root)',
        '$instance_storage_for(S_storage,n_root) = (pinstancestorage)', '$instance_storage_valid(S_storage,pinstancestorage)',
        '$ucsa_output(S_storage.EVENTS) = $ptascii("N|B|")',
        'S_middle = $ucsa_seek(S_storage,3,n_root,30000)', '$ucsa_phase(S_middle,3,n_root)',
        '$ucsa_output(S_middle.EVENTS) = $ptascii("N|B|M|")',
        '$node_children(S_middle,HOBJECT n_root) = [HOBJECT n_tail,HOBJECT n_leaf]',
        '~((HOBJECT n_middle) <- S_middle.ALLOCATIONS)', '~(n_tail <- S_middle.DESTRUCTION.CALLED)',
        '~(n_leaf <- S_middle.DESTRUCTION.CALLED)',
        'S_tail = $ucsa_seek(S_middle,4,n_root,30000)', '$ucsa_phase(S_tail,4,n_root)',
        '$ucsa_output(S_tail.EVENTS) = $ptascii("N|B|M|T|")',
        '$node_children(S_tail,HOBJECT n_root) = [HOBJECT n_leaf]',
        '~((HOBJECT n_tail) <- S_tail.ALLOCATIONS)', '~(n_leaf <- S_tail.DESTRUCTION.CALLED)',
        'S_done = $drive(S_tail,30000)', 'S_done.COMPLETION = NORMAL',
        '$ucsa_output(S_done.EVENTS) = $ptascii("N|B|M|T|U|Z|")',
        '~((HOBJECT n_root) <- S_done.ALLOCATIONS)', '~((HOBJECT n_leaf) <- S_done.ALLOCATIONS)',
        'S_done.DESTRUCTION.OPERATIONS = eps', '$call_descriptors_valid(S_done)', '$property_state_valid(S_done)',
        '$heap_valid($heap_prune($heap_graph(S_done)))',
        'S_zero = $drive_steps(S_middle,0)', 'S_zero.COMPLETION = BUDGET', 'S_zero[.COMPLETION = NORMAL] = S_middle',
        'S_one = $drive_steps(S_middle,1)', 'S_one.COMPLETION = BUDGET',
        '$drive(S_zero[.COMPLETION = NORMAL],30000) = S_done', '$drive(S_one[.COMPLETION = NORMAL],30000) = S_done',
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kind', required=True, choices=['short', 'block'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    source = SOURCES / ('child-slot-' + args.kind + '.php')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), source, *modules, *(ROOT / p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
        'frontend/SourcePrinter.php', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py',
        'tests/semantics/static_types.py', 'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'kind': args.kind,
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
        checks = fields(checked['fixture'], source, args.kind); report['premises'] = len(checks)
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
    print('pass', args.kind, report['premises'])


if __name__ == '__main__': main()
