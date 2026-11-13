#!/usr/bin/env python3
"""Ground distinct ordinary object field cells, one payload edge per cell, and real reference cycles."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('stdclass_alias_object_field_reference_notice_review_cases.json')

PREFIX = r"""
dec $nrpr_output(pevent*) : ptbytes
def $nrpr_output(eps) = eps
def $nrpr_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $nrpr_output(pevent*)
dec $nrpr_ready(pstate, nat) : bool
def $nrpr_ready(S, 0) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("ReviewNotice47\\Primary\\make")
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;")
def $nrpr_ready(S, 1) = true
  -- if S.TODO = (NAMED_SEND pcalltarget phpType7* n pnamedargs porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("ReviewNotice47\\Primary\\take")
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;")
def $nrpr_ready(S, 9) = true
  -- if S.TODO = (CALL_SEND pcalltarget phpType7* n poperand* porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("ReviewNotice47\\SelfCycle\\take")
  -- if $nrpr_output(S.EVENTS) = $ptascii("S;M;")
def $nrpr_ready(S, 10) = true
  -- if S.TODO = (CALL_SEND pcalltarget phpType7* n poperand* porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("ReviewNotice47\\AncestorCycle\\take")
  -- if $nrpr_output(S.EVENTS) = $ptascii("A;M;")
def $nrpr_ready(S, n_stage) = false -- otherwise
dec $nrpr_seek(pstate, nat, nat) : pstate
def $nrpr_seek(S, n_stage, n) = S
  -- if $nrpr_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $nrpr_seek(S, n_stage, n) = $nrpr_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$nrpr_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $nrpr_seek(S, n_stage, n) = S -- otherwise
"""

RETURN = r"""
S_initial.COMPLETION = BUDGET
S_return = $nrpr_seek(S_initial, 0, 6000)[.COMPLETION = NORMAL]
$nrpr_ready(S_return, 0)
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
S_return.CURRENT = (pcallcontext_return)
$function_at($all_functions(S_return), pcallcontext_return.FUNCTION) = (pfunction_producer)
pfunction_producer.NAME = $ptascii("ReviewNotice47\\Primary\\make")
~pfunction_producer.SIGNATURE.BYREF /\ pfunction_producer.CODE.STRICT
pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]
$typed_return_task_valid(S_return, z_return)
$lookup(S_return.ENV, $ptascii("input")) = (n_formal)
$lookup(S_return.ENV, $ptascii("source")) = (n_source_return)
n_formal =/= n_source_return
~(n_formal <- S_return.REFCELLS) /\ n_source_return <- S_return.REFCELLS
S_return.STORE[n_formal] = DEFINED (PARRAY n_root)
S_return.STORE[n_source_return] = DEFINED (PINT 31)
S_return.RESULT = VARIABLE ($ptascii("input")) z_input
S_return.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("source")) = (n_source_return)
$lookup(psymboltable_caller.ENV, $ptascii("sourceAlias")) = (n_source_return)
$lookup(psymboltable_caller.ENV, $ptascii("parent")) = (n_parent_cv)
$lookup(psymboltable_caller.ENV, $ptascii("keep")) = (n_keep)
$lookup(psymboltable_caller.ENV, $ptascii("outsideChild")) = (n_old_cv)
$lookup(psymboltable_caller.ENV, $ptascii("left")) = (n_left)
$lookup(psymboltable_caller.ENV, $ptascii("leftAlias")) = (n_left)
$lookup(psymboltable_caller.ENV, $ptascii("right")) = (n_right)
$lookup(psymboltable_caller.ENV, $ptascii("next")) = (n_next_cv)
$lookup(psymboltable_caller.ENV, $ptascii("snapshot")) = (n_snapshot)
$lookup(psymboltable_caller.ENV, $ptascii("watchParent")) = (n_watch_parent)
$lookup(psymboltable_caller.ENV, $ptascii("watchOld")) = (n_watch_old)
$lookup(psymboltable_caller.ENV, $ptascii("watchNew")) = (n_watch_new)
$lookup(psymboltable_caller.ENV, $ptascii("child")) = eps /\ $lookup(psymboltable_caller.ENV, $ptascii("seed")) = eps /\ $lookup(psymboltable_caller.ENV, $ptascii("nextText")) = eps
S_return.STORE[n_parent_cv] = DEFINED PNULL
S_return.STORE[n_keep] = DEFINED (POBJECT n_parent)
S_return.STORE[n_old_cv] = DEFINED (POBJECT n_old)
S_return.STORE[n_left] = DEFINED (POBJECT n_old) /\ S_return.STORE[n_right] = DEFINED (POBJECT n_old)
S_return.STORE[n_next_cv] = DEFINED (POBJECT n_new)
n_left =/= n_right
n_parent =/= n_old /\ n_parent =/= n_new /\ n_old =/= n_new
n_left <- S_return.REFCELLS /\ n_right <- S_return.REFCELLS
$call_reference_operand_valid(S_return, REFERENCE n_left) /\ $call_reference_operand_valid(S_return, REFERENCE n_right)
S_return.STORE[n_snapshot] = DEFINED pvalue_original
pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))
$string_carrier_valid(S_return, pvalue_original)
S_return.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("root"))) (DIRECT (POBJECT n_parent))]
S_return.OBJECTS[n_parent] = STDINSTANCE /\ S_return.OBJECTS[n_old] = STDINSTANCE /\ S_return.OBJECTS[n_new] = STDINSTANCE
$objectprops_record_at(S_return.OBJECTPROPS, n_parent) = (pobjectprops_parent)
pobjectprops_parent.SLOTS = [ppropertyslot_one, ppropertyslot_two]
ppropertyslot_one = {DECL eps, NAME ($ptascii("one")), STATE (PROP_VALUE (ALIAS n_left))}
ppropertyslot_two = {DECL eps, NAME ($ptascii("two")), STATE (PROP_VALUE (ALIAS n_right))}
$objectprops_record_at(S_return.OBJECTPROPS, n_old) = (pobjectprops_old)
pobjectprops_old.SLOTS = [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT pvalue_original))}]
$objectprops_record_at(S_return.OBJECTPROPS, n_new) = (pobjectprops_new)
pobjectprops_new.SLOTS = [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT pvalue_next))}]
pvalue_next = PSTRING_CARRIER (REQUEST_STRING n_next_string) ($ptascii("23"))
$string_carrier_valid(S_return, pvalue_next)
$objectprops_valid(S_return, [pobjectprops_parent, pobjectprops_old, pobjectprops_new])
S_return.STORE[n_watch_parent] = DEFINED (POBJECT n_weak_parent)
S_return.STORE[n_watch_old] = DEFINED (POBJECT n_weak_old)
S_return.STORE[n_watch_new] = DEFINED (POBJECT n_weak_new)
S_return.OBJECTS[n_weak_parent] = WEAKREFERENCE (n_parent) /\ S_return.OBJECTS[n_weak_old] = WEAKREFERENCE (n_old) /\ S_return.OBJECTS[n_weak_new] = WEAKREFERENCE (n_new)
S_return.PARAMETERBACKINGS = eps /\ S_return.PROPREFS = eps /\ S_return.REFCOERCIONS = eps
S_checked = $typed_return_value(S_return, z_return)
S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN (PARRAY n_root)
S_checked.STORE = S_return.STORE /\ S_checked.ARRAYS = S_return.ARRAYS /\ S_checked.OBJECTPROPS = S_return.OBJECTPROPS
S_after_return = $drive(S_return, 1)[.COMPLETION = NORMAL]
S_after_return.TODO = (RETURN_UNWIND (KNOWN (PARRAY n_root)) porigin_return?) :: ptask_return_tail*
H_return = $heap_graph(S_after_return)
$heap_owners(H_return, HOBJECT n_parent) = 2 /\ $heap_owners(H_return, HOBJECT n_old) = 3 /\ $heap_owners(H_return, HOBJECT n_new) = 1
$heap_owners(H_return, HCELL n_left) = 3 /\ $heap_owners(H_return, HCELL n_right) = 2
$heap_owners(H_return, HCELL n_formal) = 1 /\ $heap_owners(H_return, HCELL n_source_return) = 3
$node_children(S_after_return, HOBJECT n_parent) = [HCELL n_left, HCELL n_right]
$node_children(S_after_return, HCELL n_left) = [HOBJECT n_old] /\ $node_children(S_after_return, HCELL n_right) = [HOBJECT n_old]
$node_children(S_after_return, HOBJECT n_old) = eps /\ $node_children(S_after_return, HOBJECT n_new) = eps
$heap_valid(H_return) /\ $call_descriptors_valid(S_after_return)
""".strip().splitlines()

COMMON = r"""
S_pre = $nrpr_seek(S_after_return, 1, 4000)[.COMPLETION = NORMAL]
$nrpr_ready(S_pre, 1)
S_pre.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
pnamedargs.SLOTS = [NAMED_SENT (KNOWN (PINT 4))] /\ pnamedargs.NAMED = eps
$named_origin(S_pre, (porigin_call), 1) = (porigin_argument)
porigin_argument = PORIGIN n_unit pcpath_argument
$exit_fixed(S_pre, porigin_argument) = ((preqbytes, preqbytes_fallback?))
preqbytes = $ptascii("ReviewNotice47\\Primary\\make")
preqbytes_fallback? = ($ptascii("make"))
$call_target(S_pre, preqbytes, eps) = (pfunction_producer)
pfunction_producer.ORIGIN = PORIGIN n_unit pcpath_producer
pfunction_producer.NAME = preqbytes /\ pfunction_producer.EARLY
$call_target(S_pre, $ptascii("make"), eps) = (pfunction_global)
pfunction_global.ORIGIN =/= pfunction_producer.ORIGIN
$origin_node(S_pre.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 phpType16 phpType18 phpType23 metadata_function)
pfunction_producer.SIGNATURE.PARAMETERS = [psparam]
psparam.REQUIRED /\ ~psparam.BYREF /\ psparam.TYPE = [(PTBRANCH ([PTBUILTIN "array"]))] /\ ~psparam.VARIADIC /\ psparam.DEFAULT = PSNONE
~pfunction_producer.SIGNATURE.BYREF /\ ~$function_generator(S_pre, pfunction_producer)
phpType16 = SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_type) metadata_type) (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter])
$ptlc($base64(text_type)) = $ptascii("array")
$named_expression($named_source(S_pre, (porigin_call), 1)) = NExprFuncCall phpType19_producer phpType6_producer metadata_producer_call
phpType6_producer = SEQUENCE ([NArg ABSENT expression_input (BOOLEAN false) (BOOLEAN false) metadata_input])
$reference_cv(expression_input) = ($ptascii("source"))
phpType18 = NIdentifier (BYTES text_return) metadata_return
$ptlc($base64(text_return)) = $ptascii("array")
pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]
$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE)
(PDEFUNCTION n_unit pfunction_producer.ORIGIN) <- S_pre.DECLARATIONS
$declaration_early(S_pre.DECLARATIONS, pfunction_producer.ORIGIN, PPFUNCTION)
$declaration_history_valid(S_pre)
$reference_notice_producer_target(S_pre, porigin_argument) = (pfunction_producer)
$named_reference_notice_source(S_pre, pcalltarget, 1, (porigin_call))
S_pre.PARAMETERBACKINGS = eps /\ S_pre.CONTAINERINITS = eps /\ S_pre.PROPREFS = eps /\ S_pre.REFCOERCIONS = eps
S_pre.FRAMES = eps /\ S_pre.CURRENT = eps
~((HCELL n_formal) <- S_pre.ALLOCATIONS)
$lookup(S_pre.ENV, $ptascii("input")) = eps
$lookup(S_pre.ENV, $ptascii("source")) = (n_source_cv)
$lookup(S_pre.ENV, $ptascii("sourceAlias")) = (n_source_cv)
n_source_cv = n_source_return
S_pre.STORE[n_source_cv] = DEFINED (PINT 31) /\ S_pre.STORE[n_parent_cv] = DEFINED PNULL
S_pre.STORE[n_keep] = DEFINED (POBJECT n_parent)
S_pre.STORE[n_old_cv] = DEFINED (POBJECT n_old) /\ S_pre.STORE[n_next_cv] = DEFINED (POBJECT n_new)
S_pre.STORE[n_left] = DEFINED (POBJECT n_old) /\ S_pre.STORE[n_right] = DEFINED (POBJECT n_old)
S_pre.STORE[n_snapshot] = DEFINED pvalue_original
$objectprops_record_at(S_pre.OBJECTPROPS, n_parent) = (pobjectprops_parent)
$objectprops_record_at(S_pre.OBJECTPROPS, n_old) = (pobjectprops_old)
$objectprops_record_at(S_pre.OBJECTPROPS, n_new) = (pobjectprops_new)
$named_reference_notice_object(S_pre, POBJECT n_old) /\ $named_reference_notice_object(S_pre, POBJECT n_new)
$call_reference_operand_valid(S_pre, REFERENCE n_left) /\ $call_reference_operand_valid(S_pre, REFERENCE n_right)
$named_reference_notice_object_ancestors(S_pre, [n_root])
$property_release_nodes(pobjectprops_parent.SLOTS) = [HCELL n_left, HCELL n_right]
$node_children(S_pre, HOBJECT n_parent) = [HCELL n_left, HCELL n_right]
$node_children(S_pre, HCELL n_left) = [HOBJECT n_old] /\ $node_children(S_pre, HCELL n_right) = [HOBJECT n_old]
$weakref_get(S_pre, n_weak_parent) = POBJECT n_parent /\ $weakref_get(S_pre, n_weak_old) = POBJECT n_old /\ $weakref_get(S_pre, n_weak_new) = POBJECT n_new
S_pre.GC.ACTIVE = eps /\ S_pre.GC.PLAN = eps /\ S_pre.GC.WORKER = eps
$object_table_at(S_pre.OBJECTTABLES, n_parent) = eps /\ ~$weakmap_key_waiting(S_pre, n_parent)
~(n_left <- S_pre.LITERALREFRETAINED) /\ ~(n_left <- S_pre.LITERALREFDEBTS)
~(n_right <- S_pre.LITERALREFRETAINED) /\ ~(n_right <- S_pre.LITERALREFDEBTS)
~$foreach_released_cell(S_pre, n_left) /\ ~$foreach_released_cell(S_pre, n_right)
$heap_count(HCELL n_left, S_pre.NATIVEEXCESS) = 0 /\ $heap_count(HCELL n_right, S_pre.NATIVEEXCESS) = 0
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HARRAY n_root) = 1 /\ $heap_owners(H_pre, HOBJECT n_parent) = 2
$heap_owners(H_pre, HOBJECT n_old) = 3 /\ $heap_owners(H_pre, HOBJECT n_new) = 1
$heap_owners(H_pre, HCELL n_left) = 3 /\ $heap_owners(H_pre, HCELL n_right) = 2
$heap_valid(H_pre) /\ $call_descriptors_valid(S_pre)
$error_handler_eligible(S_pre, 8) /\ S_pre.SOURCEPENDING = eps
""".strip().splitlines()

SELF = r"""
S_self = $nrpr_seek(S_self_initial, 9, 5000)[.COMPLETION = NORMAL]
$nrpr_ready(S_self, 9)
S_self.TODO = (CALL_SEND pcalltarget_self eps 0 eps (porigin_self_call) z_self) :: ptask_self_tail*
S_self.RESULT = KNOWN (PARRAY n_self_root)
S_self.ARRAYS[n_self_root].ITEMS = [ENTRY (KSTRING ($ptascii("root"))) (DIRECT (POBJECT n_self_object))]
$lookup(S_self.ENV, $ptascii("root")) = (n_self_cell)
S_self.STORE[n_self_cell] = DEFINED (POBJECT n_self_object)
$call_reference_operand_valid(S_self, REFERENCE n_self_cell)
$objectprops_record_at(S_self.OBJECTPROPS, n_self_object) = (pobjectprops_self)
pobjectprops_self.SLOTS = [{DECL eps, NAME ($ptascii("self")), STATE (PROP_VALUE (ALIAS n_self_cell))}]
$node_children(S_self, HOBJECT n_self_object) = [HCELL n_self_cell]
$node_children(S_self, HCELL n_self_cell) = [HOBJECT n_self_object]
$objectprops_valid(S_self, [pobjectprops_self])
$positional_reference_notice_source(S_self, pcalltarget_self, 0, (porigin_self_call))
H_self = $heap_graph(S_self)
$heap_owners(H_self, HOBJECT n_self_object) = 2 /\ $heap_owners(H_self, HCELL n_self_cell) = 2
$heap_valid(H_self) /\ $call_descriptors_valid(S_self)
""".strip().splitlines()

ANCESTOR = r"""
S_ancestor = $nrpr_seek(S_ancestor_initial, 10, 5000)[.COMPLETION = NORMAL]
$nrpr_ready(S_ancestor, 10)
S_ancestor.TODO = (CALL_SEND pcalltarget_ancestor eps 0 eps (porigin_ancestor_call) z_ancestor) :: ptask_ancestor_tail*
S_ancestor.RESULT = KNOWN (PARRAY n_ancestor_root)
S_ancestor.ARRAYS[n_ancestor_root].ITEMS = [ENTRY (KSTRING ($ptascii("root"))) (DIRECT (POBJECT n_ancestor_object))]
$lookup(S_ancestor.ENV, $ptascii("root")) = (n_ancestor_cell)
S_ancestor.STORE[n_ancestor_cell] = DEFINED (POBJECT n_ancestor_object)
$call_reference_operand_valid(S_ancestor, REFERENCE n_ancestor_cell)
$objectprops_record_at(S_ancestor.OBJECTPROPS, n_ancestor_object) = (pobjectprops_ancestor)
pobjectprops_ancestor.SLOTS = [{DECL eps, NAME ($ptascii("next")), STATE (PROP_VALUE (DIRECT (POBJECT n_middle)))}]
$objectprops_record_at(S_ancestor.OBJECTPROPS, n_middle) = (pobjectprops_middle)
pobjectprops_middle.SLOTS = [{DECL eps, NAME ($ptascii("back")), STATE (PROP_VALUE (ALIAS n_ancestor_cell))}]
$node_children(S_ancestor, HOBJECT n_ancestor_object) = [HOBJECT n_middle]
$node_children(S_ancestor, HOBJECT n_middle) = [HCELL n_ancestor_cell]
$node_children(S_ancestor, HCELL n_ancestor_cell) = [HOBJECT n_ancestor_object]
$objectprops_valid(S_ancestor, [pobjectprops_ancestor, pobjectprops_middle])
$positional_reference_notice_source(S_ancestor, pcalltarget_ancestor, 0, (porigin_ancestor_call))
H_ancestor = $heap_graph(S_ancestor)
$heap_owners(H_ancestor, HOBJECT n_ancestor_object) = 2 /\ $heap_owners(H_ancestor, HOBJECT n_middle) = 2
$heap_owners(H_ancestor, HCELL n_ancestor_cell) = 2
$heap_valid(H_ancestor) /\ $call_descriptors_valid(S_ancestor)
""".strip().splitlines()

FRONT = r"""
~$named_reference_notice_object_slots(S_pre, pobjectprops_parent.SLOTS)
~$named_reference_notice_object(S_pre, POBJECT n_parent)
~$named_reference_notice_array(S_pre, PARRAY n_root) /\ ~$named_reference_notice_pending(S_pre)
S_scalar = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_parent, [ppropertyslot_one[.STATE = PROP_VALUE (DIRECT pvalue_original)], ppropertyslot_two[.STATE = PROP_VALUE (DIRECT pvalue_original)]])]
$named_reference_notice_object(S_scalar, POBJECT n_parent) /\ $named_reference_notice_pending(S_scalar)
H_scalar = $heap_graph(S_scalar)
$heap_owners(H_scalar, HCELL n_left) = 2 /\ $heap_owners(H_scalar, HCELL n_right) = 1
$heap_owners(H_scalar, HOBJECT n_old) = 3 /\ $heap_owners(H_scalar, HOBJECT n_new) = 1
$heap_valid(H_scalar) /\ $call_descriptors_valid(S_scalar)
S_fenced = $drive(S_pre, 1)
S_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
S_fenced.EVENTS = S_pre.EVENTS /\ S_fenced.STORE = S_pre.STORE ++ [DEFINED (PARRAY n_root)]
~$named_reference_notice_object(S_self, POBJECT n_self_object) /\ ~$positional_reference_notice_pending(S_self)
S_self_fenced = $drive(S_self, 1)
S_self_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
S_self_fenced.EVENTS = S_self.EVENTS
~$named_reference_notice_object(S_ancestor, POBJECT n_ancestor_object) /\ ~$positional_reference_notice_pending(S_ancestor)
S_ancestor_fenced = $drive(S_ancestor, 1)
S_ancestor_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
S_ancestor_fenced.EVENTS = S_ancestor.EVENTS
""".strip().splitlines()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-provenance', required=True, type=Path, action='append')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    assert args.front
    provenance = [path.resolve() for path in args.native_provenance]
    natives = [json.loads(path.read_bytes()) for path in provenance]
    cases = json.loads(CATALOGUE.read_bytes())
    records = {row['id']: row for row in natives}
    assert len(records) == len(natives) == len(cases) == 3
    sources = {i: Path(records[row['id']]['command'][-1]) for i, row in enumerate(cases)}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    for i, row in enumerate(cases):
        native, source = records[row['id']], sources[i]
        assert native['mode'] == 'native-only' and native['passed'] and native['inputs_stable'] and native['head_stable']
        assert source.read_bytes() == row['source'].encode() and sha(source) == native['source_sha256'] == row['source_sha256']
        assert native['runtime_sha256'] == native['runtime_sha256_after'] == sha(types.PHP)
        assert native['profile'] == json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
        assert source.with_name('native.stdout').read_bytes() == native['stdout'].encode() == row['native_stdout'].encode()
        assert source.with_name('native.stderr').read_bytes() == native['stderr'].encode() == row['native_stderr'].encode()
        assert native['exit'] == row['native_exit'] == 0 and not native['timeout'] and not native['group_after']
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    fixtures = {}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for i, source in sources.items():
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] and checked['fixture']
            fixtures[i] = checked['fixture']
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    def initial(name, i):
        return name + ' = $php_run(' + fixtures[i] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(sources[i])).decode()) + ')'
    reached = [initial('S_initial', 0)] + RETURN + COMMON + [initial('S_self_initial', 1)] + SELF + [initial('S_ancestor_initial', 2)] + ANCESTOR
    derived = FRONT
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + line + '\n' for line in reached + derived))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, fixture, Path(__file__), CATALOGUE, *provenance]
    paths += [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py')]
    for source in sources.values():
        paths += [source, source.with_name('native.stdout'), source.with_name('native.stderr')]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable
        and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable,
        'fixture_sha256': sha(fixture), 'part': 'stdclass-alias-object-field-front' if args.front else 'stdclass-alias-object-field-notice', 'conditions': len(reached) + len(derived),
        'reached_conditions': len(reached), 'derived_conditions': len(derived),
        'heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached),
        'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('stdclass-alias-object-field', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
