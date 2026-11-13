#!/usr/bin/env python3
"""Ground shared physical child edges, current REQUEST alias leaves, COW and retirement."""
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
CATALOGUE = Path(__file__).with_name('request_string_array_leaf_reference_notice_review_cases.json')

PREFIX = r"""
dec $nrpr_output(pevent*) : ptbytes
def $nrpr_output(eps) = eps
def $nrpr_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $nrpr_output(pevent*)
dec $nrpr_ready(pstate, nat) : bool
def $nrpr_ready(S, 0) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("ReviewNotice41\\Primary\\make")
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;")
def $nrpr_ready(S, 1) = true
  -- if S.TODO = (NAMED_SEND pcalltarget phpType7* n pnamedargs porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("ReviewNotice41\\Primary\\take")
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;")
def $nrpr_ready(S, 2) = true
  -- if S.TODO = (NAMED_ARGS pcalltarget eps 2 pnamedargs porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;H:1;")
def $nrpr_ready(S, 3) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;H:1;F:4:17:23;R:1Y:17:2Z:2Z:X7:2Z:2Z:1:31:31;")
def $nrpr_ready(S, 4) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;H:1;F:4:17:23;R:1Y:17:2Z:2Z:X7:2Z:2Z:1:31:31;D;")
def $nrpr_ready(S, 5) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;H:1;F:4:17:23;R:1Y:17:2Z:2Z:X7:2Z:2Z:1:31:31;D;P;")
def $nrpr_ready(S, 6) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;H:1;F:4:17:23;R:1Y:17:2Z:2Z:X7:2Z:2Z:1:31:31;D;P;O;")
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
S_return = $nrpr_seek(S_initial, 0, 3000)[.COMPLETION = NORMAL]
$nrpr_ready(S_return, 0)
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
S_return.CURRENT = (pcallcontext_return)
$function_at($all_functions(S_return), pcallcontext_return.FUNCTION) = (pfunction_producer)
pfunction_producer.NAME = $ptascii("ReviewNotice41\\Primary\\make")
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
$lookup(psymboltable_caller.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(psymboltable_caller.ENV, $ptascii("snapshot")) = (n_snapshot)
$lookup(psymboltable_caller.ENV, $ptascii("outside")) = (n_outside)
n_snapshot =/= n_leaf /\ n_outside =/= n_leaf /\ n_outside =/= n_snapshot
~(n_snapshot <- S_return.REFCELLS) /\ ~(n_outside <- S_return.REFCELLS)
S_return.STORE[n_leaf] = DEFINED pvalue_original
S_return.STORE[n_snapshot] = DEFINED pvalue_original
pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))
$string_carrier_valid(S_return, pvalue_original)
S_return.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("a"))) (DIRECT (PARRAY n_child)), ENTRY (KSTRING ($ptascii("b"))) (DIRECT (PARRAY n_child))]
S_return.ARRAYS[n_child].ITEMS = [ENTRY (KSTRING ($ptascii("direct"))) (DIRECT pvalue_original), ENTRY (KSTRING ($ptascii("alias"))) (ALIAS n_leaf)]
S_return.STORE[n_outside] = DEFINED (PARRAY n_child)
S_return.PARAMETERBACKINGS = eps /\ S_return.PROPREFS = eps /\ S_return.REFCOERCIONS = eps
$typed_conversion_at(S_return, pfunction_producer.SIGNATURE.RETURNS, PARRAY n_root, true) = TYPEVALUE (PARRAY n_root)
S_checked = $typed_return_value(S_return, z_return)
S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN (PARRAY n_root)
S_checked.STORE = S_return.STORE /\ S_checked.ARRAYS = S_return.ARRAYS /\ S_checked.STRINGDATA = S_return.STRINGDATA
S_checked.PARAMETERBACKINGS = S_return.PARAMETERBACKINGS /\ S_checked.PROPREFS = S_return.PROPREFS /\ S_checked.REFCOERCIONS = S_return.REFCOERCIONS
S_checked.ALLOCATIONS = S_return.ALLOCATIONS
S_after_return = $drive(S_return, 1)[.COMPLETION = NORMAL]
S_after_return.TODO = (RETURN_UNWIND (KNOWN (PARRAY n_root)) porigin_return?) :: ptask_return_tail*
$task_nodes(RETURN_UNWIND (KNOWN (PARRAY n_root)) porigin_return?) = [HARRAY n_root]
H_return = $heap_graph(S_after_return)
$heap_owners(H_return, HARRAY n_child) = 3 /\ $heap_owners(H_return, HCELL n_leaf) = 2
$heap_owners(H_return, HCELL n_formal) = 1 /\ $heap_owners(H_return, HCELL n_source_return) = 3
$heap_valid(H_return) /\ $call_descriptors_valid(S_after_return)
""".strip().splitlines()

COMMON = r"""
S_pre = $nrpr_seek(S_after_return, 1, 3000)[.COMPLETION = NORMAL]
$nrpr_ready(S_pre, 1)
S_pre.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
pnamedargs.SLOTS = [NAMED_SENT (KNOWN (PINT 4))] /\ pnamedargs.NAMED = eps
$named_origin(S_pre, (porigin_call), 1) = (porigin_argument)
porigin_argument = PORIGIN n_unit pcpath_argument
$exit_fixed(S_pre, porigin_argument) = ((preqbytes, preqbytes_fallback?))
preqbytes = $ptascii("ReviewNotice41\\Primary\\make")
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
S_pre.STORE[n_source_cv] = DEFINED (PINT 31)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("snapshot")) = (n_snapshot)
$lookup(S_pre.ENV, $ptascii("outside")) = (n_outside)
S_pre.STORE[n_leaf] = DEFINED pvalue_original /\ S_pre.STORE[n_snapshot] = DEFINED pvalue_original
S_pre.STORE[n_outside] = DEFINED (PARRAY n_child)
S_pre.ARRAYS[n_root].ITEMS = S_return.ARRAYS[n_root].ITEMS
S_pre.ARRAYS[n_child].ITEMS = S_return.ARRAYS[n_child].ITEMS
$string_carrier_valid(S_pre, pvalue_original)
~$named_reference_notice_value(pvalue_original) /\ $named_reference_notice_root_value(S_pre, pvalue_original)
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HARRAY n_root) = 1 /\ $heap_owners(H_pre, HARRAY n_child) = 3
$heap_owners(H_pre, HCELL n_source_cv) = 2 /\ $heap_owners(H_pre, HCELL n_leaf) = 2
$heap_owners(H_pre, HCELL n_snapshot) = 1 /\ $heap_owners(H_pre, HCELL n_outside) = 1
$heap_valid(H_pre) /\ $call_descriptors_valid(S_pre)
$error_handler_eligible(S_pre, 8) /\ S_pre.SOURCEPENDING = eps
""".strip().splitlines()

PRIVATE = r"""
$named_reference_notice_array(S_pre, PARRAY n_root)
$named_reference_notice_operand(S_pre, KNOWN (PARRAY n_root))
$named_reference_notice_pending(S_pre)
n_private = |S_pre.STORE|
n_private =/= n_source_cv /\ n_private =/= n_leaf /\ n_private =/= n_formal /\ n_private =/= n_snapshot /\ n_private =/= n_outside
S_notice = $drive(S_pre, 1)[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_notice*
perrorcall.RESUME = NAMED_ARGS pcalltarget eps 2 pnamedargs_after (porigin_call) z_call
pnamedargs_after.SLOTS = [NAMED_SENT (KNOWN (PINT 4)), NAMED_SENT (REFERENCE n_private)]
S_notice.STORE[n_private] = DEFINED (PARRAY n_root)
n_private <- S_notice.REFCELLS /\ (HCELL n_private) <- S_notice.ALLOCATIONS
$named_reference_notice_operand(S_notice, REFERENCE n_private)
$task_nodes(perrorcall.RESUME) = [HCELL n_private]
$node_children(S_notice, HCELL n_private) = [HARRAY n_root]
S_notice.ARRAYS = S_pre.ARRAYS /\ S_notice.STRINGDATA = S_pre.STRINGDATA
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1 /\ $heap_owners(H_notice, HARRAY n_root) = 1
$heap_owners(H_notice, HARRAY n_child) = 3 /\ $heap_owners(H_notice, HCELL n_leaf) = 2
$heap_valid(H_notice) /\ $error_call_valid(S_notice, perrorcall)
S_resume = $nrpr_seek(S_notice, 2, 4000)[.COMPLETION = NORMAL]
$nrpr_ready(S_resume, 2)
S_resume.TODO = perrorcall.RESUME :: ptask_resume*
S_resume.STORE[n_private] = DEFINED (PARRAY n_root)
S_resume.STORE[n_source_cv] = DEFINED (PINT 31) /\ S_resume.STORE[n_snapshot] = DEFINED pvalue_original
S_resume.STORE[n_leaf] = DEFINED pvalue_current
pvalue_current = PSTRING_CARRIER (REQUEST_STRING n_current_string) ($ptascii("23"))
n_current_string =/= n_string /\ $string_carrier_valid(S_resume, pvalue_current)
S_resume.STORE[n_outside] = DEFINED (PARRAY n_outside_child)
n_outside_child =/= n_child /\ n_outside_child =/= n_root
S_resume.ARRAYS[n_outside_child].ITEMS = [ENTRY (KSTRING ($ptascii("direct"))) (DIRECT (PSTRING ($ptascii("X7")))), ENTRY (KSTRING ($ptascii("alias"))) (ALIAS n_leaf)]
S_resume.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_resume.ARRAYS[n_child].ITEMS = S_pre.ARRAYS[n_child].ITEMS
$named_reference_notice_array(S_resume, PARRAY n_root)
$named_reference_notice_operand(S_resume, REFERENCE n_private)
$error_call_valid(S_resume, perrorcall)
H_resume = $heap_graph(S_resume)
$heap_owners(H_resume, HARRAY n_root) = 1 /\ $heap_owners(H_resume, HARRAY n_child) = 2
$heap_owners(H_resume, HARRAY n_outside_child) = 1 /\ $heap_owners(H_resume, HCELL n_leaf) = 3
$heap_valid(H_resume) /\ $call_descriptors_valid(S_resume)
S_written = $nrpr_seek(S_resume, 3, 8000)[.COMPLETION = NORMAL]
$nrpr_ready(S_written, 3)
$lookup(S_written.ENV, $ptascii("r")) = (n_private)
S_written.STORE[n_private] = DEFINED (PARRAY n_root)
S_written.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("a"))) (DIRECT (PARRAY n_private_child)), ENTRY (KSTRING ($ptascii("b"))) (DIRECT (PARRAY n_child))]
n_private_child =/= n_child /\ n_private_child =/= n_outside_child /\ n_private_child =/= n_root
S_written.ARRAYS[n_private_child].ITEMS = [ENTRY (KSTRING ($ptascii("direct"))) (DIRECT (PSTRING ($ptascii("1Y")))), ENTRY (KSTRING ($ptascii("alias"))) (ALIAS n_leaf)]
S_written.ARRAYS[n_child].ITEMS = S_pre.ARRAYS[n_child].ITEMS
S_written.ARRAYS[n_outside_child].ITEMS = S_resume.ARRAYS[n_outside_child].ITEMS
S_written.STORE[n_leaf] = DEFINED (PSTRING ($ptascii("2Z")))
S_written.STORE[n_snapshot] = DEFINED pvalue_original
$string_carrier_valid(S_written, pvalue_original) /\ $string_carrier_valid(S_written, pvalue_current)
H_written = $heap_graph(S_written)
$heap_owners(H_written, HCELL n_private) = 1 /\ $heap_owners(H_written, HARRAY n_root) = 1
$heap_owners(H_written, HARRAY n_child) = 1 /\ $heap_owners(H_written, HARRAY n_private_child) = 1 /\ $heap_owners(H_written, HARRAY n_outside_child) = 1
$heap_owners(H_written, HCELL n_leaf) = 4
$heap_valid(H_written) /\ $call_descriptors_valid(S_written)
S_deleted = $nrpr_seek(S_written, 4, 3000)[.COMPLETION = NORMAL]
$nrpr_ready(S_deleted, 4)
S_deleted.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("a"))) (DIRECT (PARRAY n_private_child))]
~((HARRAY n_child) <- S_deleted.ALLOCATIONS)
H_deleted = $heap_graph(S_deleted)
$heap_owners(H_deleted, HARRAY n_child) = 0 /\ $heap_owners(H_deleted, HCELL n_leaf) = 3
$heap_owners(H_deleted, HARRAY n_private_child) = 1 /\ $heap_owners(H_deleted, HARRAY n_outside_child) = 1
$heap_valid(H_deleted) /\ $call_descriptors_valid(S_deleted)
S_replaced = $nrpr_seek(S_deleted, 5, 3000)[.COMPLETION = NORMAL]
$nrpr_ready(S_replaced, 5)
S_replaced.STORE[n_private] = DEFINED (PINT 37)
~((HARRAY n_root) <- S_replaced.ALLOCATIONS) /\ ~((HARRAY n_private_child) <- S_replaced.ALLOCATIONS)
H_replaced = $heap_graph(S_replaced)
$heap_owners(H_replaced, HCELL n_private) = 1 /\ $heap_owners(H_replaced, HCELL n_leaf) = 2
$heap_owners(H_replaced, HARRAY n_outside_child) = 1
$node_children(S_replaced, HCELL n_private) = eps /\ $heap_valid(H_replaced)
S_outside = $nrpr_seek(S_replaced, 6, 3000)[.COMPLETION = NORMAL]
$nrpr_ready(S_outside, 6)
~((HCELL n_outside) <- S_outside.ALLOCATIONS) /\ ~((HARRAY n_outside_child) <- S_outside.ALLOCATIONS)
H_outside = $heap_graph(S_outside)
$heap_owners(H_outside, HCELL n_leaf) = 1 /\ $heap_valid(H_outside)
S_full = $drive(S_outside, 10000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
~((HCELL n_leaf) <- S_full.ALLOCATIONS)
S_full.STORE[n_private] = DEFINED (PINT 37) /\ S_full.STORE[n_source_cv] = DEFINED (PINT 31) /\ S_full.STORE[n_snapshot] = DEFINED pvalue_original
$node_children(S_full, HCELL n_private) = eps /\ $string_carrier_valid(S_full, pvalue_original)
S_full.PARAMETERBACKINGS = eps /\ S_full.PROPREFS = eps /\ S_full.REFCOERCIONS = eps
$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)
""".strip().splitlines()

CONTROLS = r"""
$named_reference_notice_array(S_return, PARRAY n_root)
$named_reference_notice_entries(S_notice, [ENTRY (KINT 0) (DIRECT pvalue_original)])
$named_reference_notice_entries(S_notice, [ENTRY (KINT 0) (ALIAS n_leaf)])
pvalue_bad_id = PSTRING_CARRIER (REQUEST_STRING (|S_notice.STRINGDATA|)) ($ptascii("17"))
pvalue_bad_bytes = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("18"))
S_bad_alias_id = S_notice[.STORE[n_leaf] = DEFINED pvalue_bad_id]
S_bad_alias_bytes = S_notice[.STORE[n_leaf] = DEFINED pvalue_bad_bytes]
~$named_reference_notice_array(S_bad_alias_id, PARRAY n_root)
~$named_reference_notice_array(S_bad_alias_bytes, PARRAY n_root)
S_bad_direct = S_notice[.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_bad_id)]]
~$named_reference_notice_array(S_bad_direct, PARRAY n_root)
S_raw_direct = S_notice[.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING ($ptascii("17"))))]]
~$named_reference_notice_array(S_raw_direct, PARRAY n_root)
S_raw_alias = S_notice[.STORE[n_leaf] = DEFINED (PSTRING ($ptascii("17")))]
~$named_reference_notice_array(S_raw_alias, PARRAY n_root)
S_nul = S_notice[.STRINGDATA = S_notice.STRINGDATA ++ [[0]]]
pvalue_nul = PSTRING_CARRIER (REQUEST_STRING (|S_notice.STRINGDATA|)) ([0])
$string_carrier_valid(S_nul, pvalue_nul)
~$named_reference_notice_array(S_nul[.STORE[n_leaf] = DEFINED pvalue_nul], PARRAY n_root)
~$named_reference_notice_array(S_nul[.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_nul)]], PARRAY n_root)
S_propref = S_notice[.PROPREFS = [{CELL n_leaf, SOURCES eps}]]
~$named_reference_notice_array(S_propref, PARRAY n_root)
S_coercion = S_notice[.REFCOERCIONS = [{CELL n_leaf, SITE pfunction_producer.ORIGIN, LINE 0, VALUE eps}]]
~$named_reference_notice_array(S_coercion, PARRAY n_root)
S_backed = S_notice[.PARAMETERBACKINGS = [{FUNCTION pfunction_producer.ORIGIN, INDEX 0, CELL n_leaf, LINE 0, VALUE eps}]]
~$named_reference_notice_array(S_backed, PARRAY n_root)
~$named_reference_notice_array(S_notice[.REFCELLS = [n_private]], PARRAY n_root)
~$named_reference_notice_array(S_notice[.LITERALREFDEBTS = [n_leaf]], PARRAY n_root)
~$named_reference_notice_array(S_notice[.LITERALARRAYDEBTS = [n_child]], PARRAY n_root)
~$named_reference_notice_array(S_notice[.NATIVEEXCESS = [HCELL n_leaf]], PARRAY n_root)
~$named_reference_notice_array(S_notice[.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_root))]], PARRAY n_root)
~$named_reference_notice_object_slots([{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT pvalue_original))}])
~$named_reference_notice_array(S_written, PARRAY n_root)
~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])
~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_notice
$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_notice, 2)
S_zero_deleted = $drive(S_deleted, 0)
S_zero_deleted.COMPLETION = BUDGET /\ S_zero_deleted[.COMPLETION = NORMAL] = S_deleted
$drive($drive(S_zero_deleted[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_deleted, 2)
""".strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-provenance', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    provenance = args.native_provenance.resolve()
    native = json.loads(provenance.read_bytes())
    source = Path(native['command'][-1])
    row, = json.loads(CATALOGUE.read_bytes())
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-only' and native['passed'] and native['inputs_stable']
    assert native['id'] == row['id'] and source.read_bytes() == row['source'].encode()
    assert sha(source) == native['source_sha256'] == row['source_sha256']
    assert native['runtime_sha256'] == native['runtime_sha256_after'] == sha(types.PHP)
    assert native['profile'] == json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert source.with_name('native.stdout').read_bytes() == native['stdout'].encode() == row['native_stdout'].encode()
    assert source.with_name('native.stderr').read_bytes() == native['stderr'].encode() == row['native_stderr'].encode()
    assert native['exit'] == row['native_exit'] == 0 and not native['timeout'] and not native['group_after']
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] and checked['fixture']
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
    reached = [initial] + RETURN + COMMON
    if args.front:
        derived = [
            '~$named_reference_notice_array(S_pre, PARRAY n_root)',
            '~$named_reference_notice_operand(S_pre, KNOWN (PARRAY n_root))',
            '~$named_reference_notice_pending(S_pre)',
            'S_fenced = $drive(S_pre, 1)',
            'S_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"',
            'S_fenced.EVENTS = S_pre.EVENTS',
            'S_fenced.STORE = S_pre.STORE ++ [DEFINED (PARRAY n_root)]',
            'S_fenced.STORE[n_source_cv] = DEFINED (PINT 31) /\\ S_fenced.ARRAYS = S_pre.ARRAYS',
        ]
    else:
        reached += PRIVATE
        reached.append('$nrpr_output(S_full.EVENTS) = $ptascii(' + json.dumps(row['native_stdout']) + ')')
        derived = CONTROLS
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + line + '\n' for line in reached + derived))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, fixture, source, provenance, source.with_name('native.stdout'), source.with_name('native.stderr'), Path(__file__), CATALOGUE]
    paths += [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py')]
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
        'source_sha256': sha(source), 'fixture_sha256': sha(fixture), 'part': 'request-string-array-leaf-front' if args.front else 'request-string-array-leaf-notice', 'conditions': len(reached) + len(derived),
        'reached_conditions': len(reached), 'derived_conditions': len(derived),
        'heap_bindings': len({line.split(' = ', 1)[0] for line in reached if line.startswith('H_') and ' = $heap_graph(' in line}),
        'executed_heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached),
        'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('request-string-array-leaf', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
