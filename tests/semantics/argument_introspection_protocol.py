#!/usr/bin/env python3
"""Source-reached live argument views, own sends and continuation authenticity."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile

from recorded_worker import Worker
from throwable_protocol import PREFIX
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SAVED = '''
dec $saved_arginfo_head(ptask) : bool
def $saved_arginfo_head(ARGINFO_SEND pargcall) = true
def $saved_arginfo_head(ptask) = false -- otherwise
dec $saved_arginfo(ptask*) : pargcall?
def $saved_arginfo(eps) = eps
def $saved_arginfo((ARGINFO_SEND pargcall) :: ptask_tail*) = (pargcall)
def $saved_arginfo(ptask :: ptask_tail*) = $saved_arginfo(ptask_tail*)
  -- if ~$saved_arginfo_head(ptask)
dec $saved_arginfo_stage(pstate) : bool
def $saved_arginfo_stage(S) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if $saved_arginfo(pframe.TODO) = (pargcall)
def $saved_arginfo_stage(S) = false -- otherwise
dec $saved_argref_head(ptask) : bool
def $saved_argref_head(ARGINFO_REF_CAPTURE pargref n poperand*) = true
def $saved_argref_head(ARGINFO_REF_VALUES pargref n poperand*) = true
def $saved_argref_head(ARGINFO_REF_ERROR pargref poperand*) = true
def $saved_argref_head(ptask) = false -- otherwise
dec $saved_argref(ptask*) : pargref?
def $saved_argref(eps) = eps
def $saved_argref((ARGINFO_REF_CAPTURE pargref n poperand*) :: ptask_tail*) = (pargref)
def $saved_argref((ARGINFO_REF_VALUES pargref n poperand*) :: ptask_tail*) = (pargref)
def $saved_argref((ARGINFO_REF_ERROR pargref poperand*) :: ptask_tail*) = (pargref)
def $saved_argref(ptask :: ptask_tail*) = $saved_argref(ptask_tail*)
  -- if ~$saved_argref_head(ptask)
dec $saved_argref_stage(pstate) : bool
def $saved_argref_stage(S) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if $saved_argref(pframe.TODO) = (pargref)
def $saved_argref_stage(S) = false -- otherwise
dec $saved_argref_capture(ptask) : bool
def $saved_argref_capture(ARGINFO_REF_CAPTURE pargref n poperand*) = true
def $saved_argref_capture(ptask) = false -- otherwise
dec $saved_argref_prefix(ptask*) : poperand*
def $saved_argref_prefix(eps) = eps
def $saved_argref_prefix((ARGINFO_REF_CAPTURE pargref n poperand*) :: ptask_tail*) = poperand*
def $saved_argref_prefix(ptask :: ptask_tail*) = $saved_argref_prefix(ptask_tail*)
  -- if ~$saved_argref_capture(ptask)
'''
COMMON = [
    '$arginfo_kind(pargcall.KIND)',
    '$call_descriptors_valid(S)',
    '$heap_valid($heap_graph(S))',
    '~$arginfo_call_valid(S, pargcall[.SITE = PORIGIN 999 eps])',
    '~$arginfo_call_valid(S, pargcall[.LINE = 999])',
    '~$arginfo_call_valid(S, pargcall[.KIND = INTRINSIC_EXIT])',
    '~$arginfo_call_valid(S, pargcall[.OWNER = (999)])',
    '~$arginfo_call_valid(S, pargcall[.SELECTION = (999)])',
    'S_done = $drive(S, 1000)',
    'S_done.COMPLETION = NORMAL',
    'S_done.TODO = eps',
    'S_done.FRAMES = eps',
    '$heap_valid($heap_graph(S_done))',
    'S_done = $drive(S_initial[.COMPLETION = NORMAL], 1000)',
]
CASES = [
    ('args-selection', b'<?php function f($a){echo func_get_arg(0);}f(7);',
     'S.TODO = (ARGINFO_ARGS pargcall) :: ptask*', [
         '$call_task_valid(S, ARGINFO_ARGS pargcall)',
         'pargcall.INDEX = 0', 'pargcall.SENT = eps',
         '$task_nodes(ARGINFO_ARGS pargcall) = eps',
         '~$call_task_valid(S, ARGINFO_ARGS pargcall[.INDEX = 1])',
         '~$call_task_valid(S, ARGINFO_ARGS pargcall[.NAMED = true])']),
    ('send-cv-provenance', b'<?php function f($a){$p="0";echo func_get_arg($p);}f(7);',
     'S.TODO = (ARGINFO_SEND pargcall) :: ptask*', [
         '$call_task_valid(S, ARGINFO_SEND pargcall)',
         '$arginfo_result_valid(S)',
         '~$arginfo_result_valid(S[.RESULT = KNOWN PNULL])',
         '~$call_task_valid(S, ARGINFO_SEND pargcall[.INDEX = 1])',
         '~$call_task_valid(S, ARGINFO_SEND pargcall[.SENT = [NAMED_SENT (KNOWN PNULL)]])']),
    ('unpack-cv-provenance', b'<?php function f($a){$p=[0];echo func_get_arg(...$p);}f(7);',
     'S.TODO = (ARGINFO_UNPACK_PREP pargcall) :: ptask*', [
         '$call_task_valid(S, ARGINFO_UNPACK_PREP pargcall)',
         '$arginfo_result_valid(S)',
         '~$arginfo_result_valid(S[.RESULT = KNOWN PNULL])',
         '~$call_task_valid(S, ARGINFO_UNPACK_PREP pargcall[.INDEX = 1])']),
    ('unpack-owned-prefix', b'<?php function f($a){echo func_get_arg(...["position"=>0]);}f(7);',
     'S.TODO = (ARGINFO_UNPACK_NEXT pargcall poperand n_cursor) :: ptask*', [
         'poperand = KNOWN (PARRAY n_array)',
         '$call_task_valid(S, ARGINFO_UNPACK_NEXT pargcall poperand n_cursor)',
         '(HARRAY n_array) <- $task_nodes(ARGINFO_UNPACK_NEXT pargcall poperand n_cursor)',
         '$($heap_owners($heap_graph(S), HARRAY n_array) > 0)',
         '~$call_task_valid(S, ARGINFO_UNPACK_NEXT pargcall poperand 999)',
         '~$call_task_valid(S, ARGINFO_UNPACK_NEXT pargcall (KNOWN (PARRAY 999)) n_cursor)',
         '~$call_task_valid(S[.ALLOCATIONS = eps], ARGINFO_UNPACK_NEXT pargcall poperand n_cursor)',
         '$arginfo_unpack_prefix(S, pargcall, [ENTRY (KSTRING $ptascii("wrong")) (DIRECT (PINT 0))]) = eps']),
    ('invoke-live-reference', b'<?php function f(&$a){echo func_get_arg(0);}$x=7;f($x);',
     'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask*', [
         '$call_task_valid(S, ARGINFO_INVOKE pargcall)',
         'S.CURRENT = (pcallcontext)', 'pcallcontext.ARGC = 1',
         '$lookup(S.ENV, $ptascii("a")) = (n_cell)',
         '$arginfo_values(S, pcallcontext) = [PINT 7]',
         '$task_nodes(ARGINFO_INVOKE pargcall) = eps',
         'S_live = S[.STORE = $set_cell(S.STORE, n_cell, DEFINED (PINT 9))]',
         '$call_descriptors_valid(S_live)',
         '$arginfo_values(S_live, pcallcontext) = [PINT 9]',
         'S_read = $arginfo_receive(S_live, pargcall)', 'S_read.RESULT = KNOWN (PINT 9)',
         'S_unset = S[.STORE = $set_cell(S.STORE, n_cell, UNDEFINED)]',
         '$arginfo_values(S_unset, pcallcontext) = [PNULL]',
         '$arginfo_receive(S_unset, pargcall).EVENTS = S.EVENTS',
         '~$call_descriptors_valid(S[.CURRENT = (pcallcontext[.NAME = $ptascii("forged")])])',
         '~$call_descriptors_valid(S[.CURRENT = (pcallcontext[.PARAMS = eps])])',
         '~$call_descriptors_valid(S[.CURRENT = (pcallcontext[.ARGC = 999])])',
         '~$call_descriptors_valid(S[.CURRENT = (pcallcontext[.EXTRA = [KNOWN PNULL]])])',
         '~$call_task_valid(S, ARGINFO_INVOKE pargcall[.SENT = eps])']),
    ('fresh-array-child-owners', b'<?php function f($a){$r=func_get_args();echo $r[0][0];}$a=[7];f($a);',
     'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask*', [
         'pargcall.KIND = INTRINSIC_FUNC_GET_ARGS', 'S.CURRENT = (pcallcontext)',
         '$arginfo_values(S, pcallcontext) = [PARRAY n_old]',
         '$task_nodes(ARGINFO_INVOKE pargcall) = eps',
         'S_result = $arginfo_receive(S, pargcall)',
         'S_result.RESULT = KNOWN (PARRAY n_new)', 'n_new = |S.ARRAYS|', 'n_new =/= n_old',
         'S_result.ARRAYS[n_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_old))]',
         '$($heap_owners($heap_graph(S_result), HARRAY n_old) = $heap_owners($heap_graph(S), HARRAY n_old) + 1)',
         '$heap_valid($heap_graph(S_result))']),
    ('dynamic-selection-receipt', b'<?php function f($a){$g="func_get_arg";try{$g(0);}catch(Error $e){echo 1;}}f(7);',
     'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask*', [
         'pargcall.SELECTION = (n_nonce)', 'S.SELECTEDCALLS[n_nonce] = pselectedcall',
         '$selected_entry_valid(S, pselectedcall)', '$arginfo_dynamic(S, pargcall)',
         '~$arginfo_global(S, pargcall)',
         '~$arginfo_selected_valid(S, pargcall[.KIND = INTRINSIC_FUNC_GET_ARGS])',
         '~$selected_entry_source_valid(S, pselectedcall[.LOOKUP = $ptascii("func_get_args")])',
         '~$selected_entry_source_valid(S, pselectedcall[.ORIGINAL = $ptascii("wrong")])',
         '~$selected_entry_active_valid(S, pselectedcall[.DEPTH = 999])',
         '~$call_descriptors_valid(S[.SELECTEDCALLS = [pselectedcall[.DEPTH = 999]]])']),
    ('captured-owner-root', b'<?php function kill(&$c){$c=null;return 0;}$c=func_get_arg(...);try{$c(kill($c));}catch(Error $e){echo 1;}',
     'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask*', [
         'pargcall.OWNER = (n_owner)',
         '$lookup(S.ENV, $ptascii("c")) = (n_cell)',
         'S.STORE[n_cell] = DEFINED PNULL',
         'S.OBJECTS[n_owner] = INTRINSICCLOSURE INTRINSIC_FUNC_GET_ARG',
         '(HOBJECT n_owner) <- $task_nodes(ARGINFO_INVOKE pargcall)',
         '$($heap_owners($heap_graph(S), HOBJECT n_owner) > 0)',
         '$arginfo_selected_valid(S, pargcall)',
         '~$arginfo_selected_valid(S, pargcall[.OWNER = eps])']),
    ('saved-callback-context', b'<?php function g($p){return $p;}function f($a){echo func_get_arg(g(0));}f(7);',
     '$saved_arginfo_stage(S)', [
         'S.FRAMES = pframe :: pframe_tail*',
         '$saved_arginfo(pframe.TODO) = (pargcall)',
         'S.CURRENT = (pcallcontext)', 'pcallcontext.NAME = $ptascii("g")',
         'pframe.CONTEXT = (pcallcontext_saved)', 'pcallcontext_saved.NAME = $ptascii("f")',
         '$call_frames_valid(S, S.FRAMES)',
         '~$call_current_valid(S[.CURRENT = (pcallcontext[.NAME = $ptascii("f")])])',
         '~$call_saved_context_valid(S, pframe[.CONTEXT = (pcallcontext_saved[.ARGC = 999])])',
         '~$call_saved_context_valid(S, pframe[.CONTEXT = (pcallcontext_saved[.PARAMS = eps])])',
         '~$call_tasks_valid(S[.ORIGIN = pframe.ORIGIN][.CURRENT = pframe.CONTEXT], [ARGINFO_SEND pargcall[.LINE = 999]])'],
     False),
    ('tmp-reference-preparation-argkey', b"<?php function f($a){try{take(func_get_args()[argkey(0)][second()]);}catch(Error $e){echo 1;}}function argkey($p){return $p;}function second(){echo 'S';return 0;}function take(&$x){echo 'bad';}f([7]);",
     'S.TODO = (ARGINFO_REF_PREP pargref) :: ptask*', [
         '$call_task_valid(S, ARGINFO_REF_PREP pargref)',
         '$task_nodes(ARGINFO_REF_PREP pargref) = eps',
         '~$call_task_valid(S, ARGINFO_REF_PREP pargref[.LINE = 999])',
         '~$call_task_valid(S, ARGINFO_REF_PREP pargref[.POSITION = 999])',
         '~$call_task_valid(S, ARGINFO_REF_PREP pargref[.CALLSITE = pargref.ARGUMENT])',
         '~$call_task_valid(S, ARGINFO_REF_PREP pargref[.ARGUMENT = pargref.DIMENSION])',
         '~$call_task_valid(S, ARGINFO_REF_PREP pargref[.DIMENSION = pargref.ARGUMENT])',
         'pargref.DIMENSION = PORIGIN n_unit pcpath',
         '$code_at(S.CODE, n_unit) = (pcode)', '$source_unit(S.SOURCES, n_unit) = (pcunit)',
         '$pparginfo_tmp(pcode, pcunit, pcpath ++ [PCFIELD 0])',
         '~$pparginfo_tmp(pcode[.NAMES = eps], pcunit, pcpath ++ [PCFIELD 0])',
         '~$pparginfo_tmp(pcode[.UNIT = 999], pcunit, pcpath ++ [PCFIELD 0])',
         '~$pparginfo_tmp(pcode, pcunit[.OCCURRENCES = eps], pcpath ++ [PCFIELD 0])'], 'ref'),
    ('tmp-producer-capture-argkey', b"<?php function f($a){try{take(func_get_args()[argkey(0)]);}catch(Error $e){echo 1;}}function argkey($p){return $p;}function take(&$x){echo 'bad';}f(7);",
     'S.TODO = (ARGINFO_REF_CAPTURE pargref 0 eps) :: ptask*', [
         '$call_task_valid(S, ARGINFO_REF_CAPTURE pargref 0 eps)', '$arginfo_result_valid(S)',
         'S.RESULT = KNOWN (PARRAY n_array)', '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
         '~$arginfo_result_valid(S[.RESULT = KNOWN PNULL])',
         '~$call_task_valid(S, ARGINFO_REF_CAPTURE pargref 1 eps)',
         '~$call_task_valid(S, ARGINFO_REF_CAPTURE pargref 0 ([KNOWN PNULL]))',
         '$task_nodes(ARGINFO_REF_CAPTURE pargref 0 eps) = eps'], 'ref'),
    ('tmp-reference-key-mutation-argkey', b"<?php function f($a){try{take(func_get_args()[argkey($a)][second()]);}catch(Error $e){echo 1;}}function argkey(&$p){$p=9;return 0;}function second(){echo 'S';return 0;}function take(&$x){echo 'bad';}f(7);",
     'S.TODO = (ARGINFO_REF_ERROR pargref poperand*) :: ptask*', [
         '$call_task_valid(S, ARGINFO_REF_ERROR pargref poperand*)', '$arginfo_result_valid(S)',
         'poperand* = [KNOWN (PARRAY n_array), KNOWN (PINT 0), KNOWN (PINT 0)]',
         'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
         '$lookup(S.ENV, $ptascii("a")) = (n_cell)', 'S.STORE[n_cell] = DEFINED (PINT 9)',
         '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
         '~$arginfo_result_valid(S[.TODO = (ARGINFO_REF_ERROR pargref ([KNOWN PNULL, KNOWN (PINT 0), KNOWN (PINT 0)])) :: ptask*])',
         '~$arginfo_result_valid(S[.ALLOCATIONS = eps])',
         '~$call_task_valid(S, ARGINFO_REF_ERROR pargref eps)',
         '~$call_task_valid(S, ARGINFO_REF_ERROR pargref[.LINE = 999] poperand*)'], 'ref'),
    ('tmp-reference-undefined-cv', b"<?php function f($a){try{take(func_get_args()[$missing][second()]);}catch(Error $e){echo 1;}}function second(){echo 'S';return 0;}function take(&$x){echo 'bad';}f(7);",
     'S.TODO = (ARGINFO_REF_ERROR pargref poperand*) :: ptask*', [
         '$call_task_valid(S, ARGINFO_REF_ERROR pargref poperand*)', '$arginfo_result_valid(S)',
         'poperand* = [KNOWN (PARRAY n_array), VARIABLE n_name* z_key, KNOWN (PINT 0)]',
         '~$call_task_valid(S, ARGINFO_REF_ERROR pargref ([KNOWN (PARRAY n_array), KNOWN PNULL, KNOWN (PINT 0)]))',
         '~$call_task_valid(S, ARGINFO_REF_ERROR pargref ([KNOWN (PARRAY n_array), VARIABLE $ptascii("wrong") z_key, KNOWN (PINT 0)]))',
         '~$call_task_valid(S, ARGINFO_REF_ERROR pargref ([KNOWN (PARRAY n_array), VARIABLE n_name* 999, KNOWN (PINT 0)]))'], 'ref'),
    ('tmp-reference-append', b"<?php function f($a){try{take(func_get_args()[][second()]);}catch(Error $e){echo 1;}}function second(){echo 'S';return 0;}function take(&$x){echo 'bad';}f(7);",
     'S.TODO = (ARGINFO_REF_ERROR pargref poperand*) :: ptask*', [
         '$call_task_valid(S, ARGINFO_REF_ERROR pargref poperand*)', '$arginfo_result_valid(S)',
         'poperand* = [KNOWN (PARRAY n_array), KNOWN (PINT 0)]',
         '~$arginfo_result_valid(S[.TODO = (ARGINFO_REF_ERROR pargref ([KNOWN PNULL, KNOWN (PINT 0)])) :: ptask*])',
         '~$call_task_valid(S, ARGINFO_REF_ERROR pargref ([KNOWN (PARRAY n_array)]))'], 'ref'),
    ('tmp-property-selector-owner', b"<?php class C{public $p=7;}class K{function __toString(){echo 'bad';return 'p';}}function f($a){try{take(func_get_args()[0]->{name()});}catch(Error $e){echo 1;}}function name(){return new K;}function take(&$x){echo 'bad';}f(new C);",
     'S.TODO = (ARGINFO_REF_ERROR pargref poperand*) :: ptask*', [
         '$call_task_valid(S, ARGINFO_REF_ERROR pargref poperand*)', '$arginfo_result_valid(S)',
         'poperand* = [KNOWN (PARRAY n_array), KNOWN (PINT 0), KNOWN (POBJECT n_object)]',
         '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
         '$heap_owners($heap_graph(S), HOBJECT n_object) = 1',
         '(HOBJECT n_object) <- $task_nodes(ARGINFO_REF_ERROR pargref poperand*)',
         '~$call_task_valid(S, ARGINFO_REF_ERROR pargref ([KNOWN (PARRAY n_array), KNOWN (PINT 0), KNOWN (POBJECT 999)]))'], 'ref'),
    ('tmp-reference-saved-key-argkey', b"<?php function f($a){try{take(func_get_args()[argkey(0)][second()]);}catch(Error $e){echo 1;}}function argkey($p){return $p;}function second(){echo 'S';return 0;}function take(&$x){echo 'bad';}f(7);",
     '$saved_argref_stage(S)', [
         'S.FRAMES = pframe :: pframe_tail*', '$saved_argref(pframe.TODO) = (pargref)',
         'S.CURRENT = (pcallcontext)', 'pcallcontext.NAME = $ptascii("argkey")',
         'pframe.CONTEXT = (pcallcontext_saved)', 'pcallcontext_saved.NAME = $ptascii("f")',
         '$saved_argref_prefix(pframe.TODO) = [KNOWN (PARRAY n_array)]',
         '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
         '$call_frames_valid(S, S.FRAMES)',
         '~$call_tasks_valid(S[.ORIGIN = (pargref.ARGUMENT)][.CURRENT = pframe.CONTEXT], [ARGINFO_REF_PREP pargref[.LINE = 999]])'], 'ref'),
    ('tmp-first-property-cv', b"<?php function f($a){try{take(func_get_args()->{$missing});}catch(Error $e){echo 1;}}function take(&$x){echo 'bad';}f(7);",
     'S.TODO = (ARGINFO_REF_ERROR pargref poperand*) :: ptask*', [
         '$call_task_valid(S, ARGINFO_REF_ERROR pargref poperand*)', '$arginfo_result_valid(S)',
         'pargref.DIMENSION = pargref.ARGUMENT',
         'poperand* = [KNOWN (PARRAY n_array), VARIABLE n_name* z_name]',
         '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
         '~$call_task_valid(S, ARGINFO_REF_ERROR pargref ([KNOWN (PARRAY n_array), KNOWN PNULL]))',
         '~$call_task_valid(S, ARGINFO_REF_ERROR pargref ([KNOWN (PARRAY n_array), VARIABLE n_name* 999]))',
         '~$arginfo_result_valid(S[.TODO = (ARGINFO_REF_ERROR pargref ([KNOWN PNULL, VARIABLE n_name* z_name])) :: ptask*])'], 'ref'),
    ('tmp-first-property-constant-selector', b"<?php function f($a){try{take(func_get_args()->{[]});}catch(Error $e){echo 1;}}function take(&$x){echo 'bad';}f(7);",
     'S.TODO = (ARGINFO_REF_ERROR pargref poperand*) :: ptask*', [
         '$call_task_valid(S, ARGINFO_REF_ERROR pargref poperand*)', '$arginfo_result_valid(S)',
         'pargref.DIMENSION = pargref.ARGUMENT', 'poperand* = [KNOWN (PARRAY n_array)]',
         '$origin_child((pargref.ARGUMENT), [PCFIELD 1]) = (porigin_name)',
         '$arginfo_constant_origin(S, porigin_name)',
         '~$arginfo_constant_origin(S[.CODE = eps], porigin_name)',
         '~$call_task_valid(S, ARGINFO_REF_ERROR pargref ([KNOWN (PARRAY n_array), KNOWN PNULL]))',
         '~$arginfo_result_valid(S[.TODO = (ARGINFO_REF_ERROR pargref ([KNOWN PNULL])) :: ptask*])'], 'ref'),
    ('tmp-initial-parser-literal-class', b"<?php function f($a){echo ('func_'.'num_args')();}f(7);",
     'S.TODO = (ARGINFO_ARGS pargcall) :: ptask*', [
         'pargcall.SITE = PORIGIN n_unit pcpath',
         '$code_at(S.CODE, n_unit) = (pcode)', '$source_unit(S.SOURCES, n_unit) = (pcunit)',
         '$pparginfo_tmp(pcode, pcunit, pcpath)',
         '$occurrence_node(pcunit.OCCURRENCES, pcpath) = (NExprFuncCall expression phpType6 metadata)',
         '$pparginfo_initial(expression)',
         '$ppcall_literal(expression) = ($ptascii("func_num_args"))',
         '~$pparginfo_tmp(pcode[.NAMES = eps], pcunit, pcpath)',
         '~$pparginfo_tmp(pcode, pcunit[.OCCURRENCES = eps], pcpath)',
         '~$pparginfo_tmp(pcode[.UNIT = 999], pcunit, pcpath)']),
    ('tmp-later-compiler-const-var-class', b"<?php function f($a){echo (__NAMESPACE__.'func_num_args')();}f(7);",
     'S.TODO = (ARGINFO_ARGS pargcall) :: ptask*', [
         'pargcall.SITE = PORIGIN n_unit pcpath',
         '$code_at(S.CODE, n_unit) = (pcode)', '$source_unit(S.SOURCES, n_unit) = (pcunit)',
         '$occurrence_node(pcunit.OCCURRENCES, pcpath) = (NExprFuncCall expression phpType6 metadata)',
         '~$pparginfo_initial(expression)',
         '$ppcall_literal(expression) = eps',
         '~$pparginfo_tmp(pcode, pcunit, pcpath)',
         '$ppunpack_class(pcode, pcunit, pcpath) = (UNPACK_VAR)',
         '$code_name(pcode.NAMES, pcpath) = (($ptascii("func_num_args"), eps))']),
    ('wrapper-preparation-source-leaf', b"<?php function f($a){try{take((@([$r]=func_get_args()))[argkey(0)]);}catch(Error $e){echo 1;}}function argkey($p){return $p;}function take(&$x){echo 'bad';}f(7);",
     'S.TODO = (ARGINFO_REF_PREP pargref) :: ptask*', [
         '$call_task_valid(S, ARGINFO_REF_PREP pargref)',
         '$task_nodes(ARGINFO_REF_PREP pargref) = eps',
         'pargref.DIMENSION = PORIGIN n_unit pcpath',
         '$code_at(S.CODE, n_unit) = (pcode)', '$source_unit(S.SOURCES, n_unit) = (pcunit)',
         '$pparginfo_tmp_leaf(pcode, pcunit, pcpath ++ [PCFIELD 0]) = (pcpath_api)',
         'pcpath_api =/= pcpath ++ [PCFIELD 0]', '$pparginfo_tmp(pcode, pcunit, pcpath_api)',
         '$ppunpack_class(pcode, pcunit, pcpath ++ [PCFIELD 0]) = (UNPACK_VALUE)',
         '~$pparginfo_tmp(pcode, pcunit, pcpath ++ [PCFIELD 0])',
         '$pparginfo_tmp_leaf(pcode[.NAMES = eps], pcunit, pcpath ++ [PCFIELD 0]) = eps',
         '$pparginfo_tmp_leaf(pcode[.EXPRESSIONS = eps], pcunit, pcpath ++ [PCFIELD 0]) = eps',
         '$pparginfo_tmp_leaf(pcode[.UNIT = 999], pcunit, pcpath ++ [PCFIELD 0]) = eps',
         '$pparginfo_tmp_leaf(pcode, pcunit[.OCCURRENCES = eps], pcpath ++ [PCFIELD 0]) = eps',
         '~$call_task_valid(S, ARGINFO_REF_PREP pargref[.DIMENSION = pargref.CALLSITE])'], 'ref'),
    ('wrapper-producer-single-owner', b"<?php function f($a){try{take((@([$r]=func_get_args()))[argkey(0)]);}catch(Error $e){echo 1;}}function argkey($p){return $p;}function take(&$x){echo 'bad';}f(7);",
     'S.TODO = (ARGINFO_REF_CAPTURE pargref 0 eps) :: ptask*', [
         '$call_task_valid(S, ARGINFO_REF_CAPTURE pargref 0 eps)', '$arginfo_result_valid(S)',
         'S.RESULT = KNOWN (PARRAY n_array)', '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
         '$lookup(S.ENV, $ptascii("r")) = (n_cell)', 'S.STORE[n_cell] = DEFINED (PINT 7)',
         '$task_nodes(ARGINFO_REF_CAPTURE pargref 0 eps) = eps',
         '~$arginfo_result_valid(S[.RESULT = KNOWN PNULL])',
         '~$arginfo_result_valid(S[.BASE = BASE_VALUE (KNOWN (PARRAY n_array))])',
         '~$call_task_valid(S, ARGINFO_REF_CAPTURE pargref 1 eps)'], 'ref'),
    ('wrapper-saved-key-context', b"<?php function f($a){try{take(([$r]=func_get_args())[argkey($a,0)]);}catch(Error $e){echo 1;}}function argkey(&$p,$extra){$p=9;return 0;}function take(&$x){echo 'bad';}f(7);",
     '$saved_argref_stage(S)', [
         'S.FRAMES = pframe :: pframe_tail*', '$saved_argref(pframe.TODO) = (pargref)',
         'S.CURRENT = (pcallcontext)', 'pcallcontext.NAME = $ptascii("argkey")', 'pcallcontext.ARGC = 2',
         'pframe.CONTEXT = (pcallcontext_saved)', 'pcallcontext_saved.NAME = $ptascii("f")', 'pcallcontext_saved.ARGC = 1',
         '$saved_argref_prefix(pframe.TODO) = [KNOWN (PARRAY n_array)]',
         'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
         '$heap_owners($heap_graph(S), HARRAY n_array) = 1', '$call_frames_valid(S, S.FRAMES)'], 'ref'),
    ('wrapper-terminal-live-mutation', b"<?php function f($a){try{take(([$r]=func_get_args())[argkey($a,0)]);}catch(Error $e){echo 1;}}function argkey(&$p,$extra){$p=9;return 0;}function take(&$x){echo 'bad';}f(7);",
     'S.TODO = (ARGINFO_REF_ERROR pargref poperand*) :: ptask*', [
         '$call_task_valid(S, ARGINFO_REF_ERROR pargref poperand*)', '$arginfo_result_valid(S)',
         'poperand* = [KNOWN (PARRAY n_array), KNOWN (PINT 0)]',
         'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
         '$lookup(S.ENV, $ptascii("a")) = (n_a)', 'S.STORE[n_a] = DEFINED (PINT 9)',
         '$lookup(S.ENV, $ptascii("r")) = (n_r)', 'S.STORE[n_r] = DEFINED (PINT 7)',
         '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
         '~$arginfo_result_valid(S[.TODO = (ARGINFO_REF_ERROR pargref ([KNOWN PNULL, KNOWN (PINT 0)])) :: ptask*])',
         '~$call_task_valid(S, ARGINFO_REF_ERROR pargref eps)',
         '~$call_task_valid(S, ARGINFO_REF_ERROR pargref[.LINE = 999] poperand*)'], 'ref'),
    ('language-list-call-private-cell', b"<?php function f(&$a){[&$r]=(__NAMESPACE__.'func_get_args')();$r=9;echo $a,$r;}$x=7;f($x);echo $x;",
     'S.TODO = (LIST_STORE expression (REFERENCE n_leaf) true z) :: ptask*', [
         '$call_reference_operand_valid(S, REFERENCE n_leaf)',
         'S.STORE[n_leaf] = DEFINED (PINT 7)', '$lookup(S.ENV, $ptascii("a")) = (n_a)', 'n_leaf =/= n_a',
         '(HCELL n_leaf) <- $task_nodes(LIST_STORE expression (REFERENCE n_leaf) true z)',
         '$heap_owners($heap_graph(S), HCELL n_leaf) = 1',
         '~$call_reference_operand_valid(S, REFERENCE 999)'], 'ref'),
    ('language-list-cv-alias-cell', b"<?php function f(&$a){$copy=func_get_args();[&$r]=$copy;$r=9;echo $a,$copy[0],$r;}$x=7;f($x);echo $x;",
     'S.TODO = (LIST_STORE expression (REFERENCE n_leaf) true z) :: ptask*', [
         '$call_reference_operand_valid(S, REFERENCE n_leaf)',
         'S.STORE[n_leaf] = DEFINED (PINT 7)', '$lookup(S.ENV, $ptascii("a")) = (n_a)', 'n_leaf =/= n_a',
         '$lookup(S.ENV, $ptascii("copy")) = (n_copy)', 'S.STORE[n_copy] = DEFINED (PARRAY n_array)',
         'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf)]',
         '(HCELL n_leaf) <- $task_nodes(LIST_STORE expression (REFERENCE n_leaf) true z)',
         '$heap_owners($heap_graph(S), HCELL n_leaf) = 2'], 'ref'),
    # The pinned optimized source has an engine fatal: this is chosen-language
    # state evidence only, never a native agreement.
    ('language-engine-defect-model-only', b"<?php function f($a){try{take(([&$r]=func_get_args()));}catch(Error $e){echo 'E';}echo $a,$r;}function take(&$x){echo 'T';$x=9;}f(7);",
     'S.TODO = (LIST_STORE expression (REFERENCE n_leaf) true z) :: ptask*', [
         '$call_reference_operand_valid(S, REFERENCE n_leaf)', 'S.STORE[n_leaf] = DEFINED (PINT 7)',
         '$lookup(S.ENV, $ptascii("a")) = (n_a)', 'n_leaf =/= n_a',
         '(HCELL n_leaf) <- $task_nodes(LIST_STORE expression (REFERENCE n_leaf) true z)',
         '$heap_owners($heap_graph(S), HCELL n_leaf) = 1'], 'ref'),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(match):
    out = Path(tempfile.mkdtemp(prefix='argument-introspection-protocol-', dir=ROOT / '.tools'))
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    before = types.syntax_validation.implementation_fingerprint()
    inputs = [*modules, ROOT / 'spec/semantics/modules.json', Path(__file__),
              ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
              ROOT / '_build/default/adapter/main.exe',
              ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in inputs}
    records=[]
    for case in CASES:
        name, source, stage, checks = case[:4]
        if match not in name:
            continue
        directory = out / name
        directory.mkdir()
        path = directory / 'source.php'
        path.write_bytes(source)
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                           'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], directory / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            assert parsed['accepted'], (name, parsed)
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], (name, checked)
        finally:
            frontend.close(); adapter.close()
        initial='$php_run('+checked['fixture']+', 0, '+json.dumps(base64.b64encode(str(path).encode()).decode())+')'
        conditions=['S_initial = '+initial, 'S = $seek(S_initial[.COMPLETION = NORMAL], 1000)[.COMPLETION = NORMAL]', stage]+checks
        if len(case) == 5 and case[4] == 'ref':
            conditions += [c for c in COMMON if 'pargcall' not in c]
        else:
            conditions += COMMON if len(case)==4 else [c for c in COMMON if 'arginfo_call_valid' not in c]
        fixture=directory/'protocol.watsup'
        prefix=PREFIX.replace('STAGE', stage)
        fixture.write_text(SAVED+prefix+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+condition+'\n' for condition in conditions))
        command=[str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),*map(str,modules),str(fixture)]
        (directory/'command.json').write_text(json.dumps(command)+'\n')
        result=subprocess.run(command,capture_output=True,timeout=90)
        (directory/'stdout').write_bytes(result.stdout); (directory/'stderr').write_bytes(result.stderr)
        passed=result.returncode==0 and result.stdout==b'true\n' and not result.stderr
        records.append({'name':name,'pass':passed,'exit_status':result.returncode,'assertions':len(conditions),'source_sha256':sha(path),'fixture_sha256':sha(fixture),'stdout_sha256':sha(directory/'stdout'),'stderr_sha256':sha(directory/'stderr')})
        print(name,passed,len(conditions),flush=True)
    assert before==types.syntax_validation.implementation_fingerprint()
    assert all(sha(ROOT/name)==digest for name,digest in hashes.items())
    report={'result':'pass' if records and all(row['pass'] for row in records) else 'fail','fingerprint':before,'inputs':hashes,'raw':str(out),'records':records}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(out,report['result'],flush=True)
    return report['result']=='pass'


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--match',default='');args=parser.parse_args()
    raise SystemExit(0 if main(args.match) else 1)
