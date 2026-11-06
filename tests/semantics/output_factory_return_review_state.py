#!/usr/bin/env python3
"""Fresh factory results cross real return owners before native throw/report."""
import argparse,base64,json,os,re,tempfile,time
from pathlib import Path
from recorded_worker import Worker
import output_deprecation_warning_review_state as runner
import output_factory_return_sources as sources
import output_object_conversion_review_sources as support
ROOT=support.ROOT
PREFIX=r'''
dec $fr_phase(pstate, nat) : bool
def $fr_phase(S, 0) = true
  -- if S.TODO = (ORDINARY_CTOR_RECEIVE pordinaryinternal) :: ptask_tail*
  -- if pordinaryinternal.INDEX = 3 /\ pordinaryinternal.CALL.BASE = "Exception"
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = pcallcontext.FUNCTION /\ pcallcontext.ARGC = 0
def $fr_phase(S, 1) = true
  -- if S.TODO = [RETURN_UNWIND (KNOWN (POBJECT n)) (porigin)]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = pcallcontext.FUNCTION /\ pcallcontext.ARGC = 0
  -- if S.OBJECTS[n] = THROWABLE pthrowable
def $fr_phase(S, 2) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_tail*
  -- if S.RESULT = KNOWN (POBJECT n)
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n_object pcallcontext.FUNCTION
def $fr_phase(S, 3) = true
  -- if S.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (OUTPUT_FINAL_OBJECT_CV pobobjectreturn) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $fr_phase(S, 4) = true
  -- if S.TODO = [OUTPUT_FINAL_DEACTIVATE pobdeactivate]
  -- if pobdeactivate.INDEX = 0

def $fr_phase(S, 5) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n_object pcallcontext.FUNCTION
def $fr_phase(S, 6) = true
  -- if S.TODO = [RETURN_UNWIND (KNOWN pvalue) porigin?]
  -- if $string_bytes(pvalue) = ($ptascii("H"))
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = pcallcontext.FUNCTION
def $fr_phase(S, 7) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_tail*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("H"))
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n_object pcallcontext.FUNCTION
def $fr_phase(S, 8) = true
  -- if S.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (DESTRUCTOR_C_RETURN pdestructorcall) :: (DESTRUCTOR_RESULT pdestructorcall) :: (OUTPUT_FINAL_OBJECT_LOCAL_THROW pobobjectreturn pdestructorcall pobobjectsource eps) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps

def $fr_phase(S, n) = false -- otherwise
dec $fr_seek(pstate, nat, nat) : pstate
def $fr_seek(S, n_phase, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $fr_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $fr_phase(S, n_phase)
def $fr_seek(S, n_phase, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$fr_phase(S, n_phase)
def $fr_seek(S, n_phase, n) = $fr_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$fr_phase(S, n_phase) /\ $(n > 0)
'''
def public(s):
 return f'$call_descriptors_valid({s}) /\\ $heap_valid($heap_graph({s})) /\\ $output_state_valid({s}) /\\ $destruction_state_valid({s})'
def pipeline(fixture,path):
 return [
 'S_initial = $php_file_run('+fixture+', 0, '+runner.bytes_expr(os.fsencode(path))+', '+runner.bytes_expr(os.fsencode(path.parent))+')',
 'S_ctor_found = $fr_seek(S_initial, 0, 1024)',r'S_ctor_found.COMPLETION = NORMAL \/ S_ctor_found.COMPLETION = BUDGET',
 'S_ctor = S_ctor_found[.COMPLETION = NORMAL]',
 'S_ctor.TODO = (ORDINARY_CTOR_RECEIVE pordinaryinternal) :: ptask_ctor*',
 'pctorcall = pordinaryinternal.CALL','pctorcall_source = pordinaryinternal.SOURCE',
 'pordinaryinternal.VALUES = [pvalue_message, PINT z_code, PNULL]',
 'n_exception = pctorcall.RECEIVER',
 'S_ctor.CURRENT = (pcallcontext_make)',
 '$function_at(S_ctor.FUNCTIONS, pcallcontext_make.FUNCTION) = (pfunction_make)',
 'S_ctor.FRAMES = pframe_call :: pframe_native_tail*',
 'pframe_call.CONTEXT = (pcallcontext_native)',
 'pcallcontext_native.TARGET = METHOD_TARGET n_object pcallcontext_native.FUNCTION',
 '$function_at($all_functions(S_ctor), pcallcontext_native.FUNCTION) = (pfunction_native)',
 'S_born_found = $drive_steps(S_ctor, 1)','S_born_found.COMPLETION = BUDGET',
 'S_born = S_born_found[.COMPLETION = NORMAL]',
 '$ob_object_native_source(S_born) = (OBJECT_FACTORY_NEW pobfactoryreturn)',
 'S_return_found = $fr_seek(S_born, 1, 512)',r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
 'S_return = S_return_found[.COMPLETION = NORMAL]',
 'S_return.TODO = [RETURN_UNWIND (KNOWN (POBJECT n_exception)) (porigin_return)]',
 'S_one_found = $drive_steps(S_return, 1)','S_one_found.COMPLETION = BUDGET',
 'S_one = S_one_found[.COMPLETION = NORMAL]',
 '$ob_object_native_source(S_one) = (OBJECT_FACTORY_RETURNED pobfactoryreturn)',
 'S_ready_found = $fr_seek(S_one, 2, 512)',r'S_ready_found.COMPLETION = NORMAL \/ S_ready_found.COMPLETION = BUDGET',
 'S_ready = S_ready_found[.COMPLETION = NORMAL]',
 'S_ready.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_ready*',
 'S_active_found = $drive_steps(S_ready, 1)','S_active_found.COMPLETION = BUDGET',
 'S_active = S_active_found[.COMPLETION = NORMAL]',
 'S_active.TODO = (THROW_SEARCH n_exception) :: ptask_active*',
 '$ob_object_native_source(S_active) = (OBJECT_FACTORY_THROW pobfactoryreturn)',
 ]
def provenance(fixture,path,local):
 b=pipeline(fixture,path)+[
 'S_no_source = $ob_object_call_capture(S_born, eps)',
 'S_wrong_result = S_no_source[.RESULT = KNOWN (POBJECT n_object)]',
 'S_failed = S_no_source[.COMPLETION = THROWING n_exception]',
 'S_held = S_no_source[.HELD = [HOBJECT n_exception]]',
 'S_tasks = S_no_source[.TODO = S_no_source.TODO ++ [THROW_SEARCH n_exception]]',
 'pobfactoryreturn_function = pobfactoryreturn[.FUNCTION = pfunction_native.ORIGIN]',
 'pobfactoryreturn_return = pobfactoryreturn[.RETURN = pobfactoryreturn.THROW]',
 'pobfactoryreturn_throw = pobfactoryreturn[.THROW = pobfactoryreturn.RETURN]',
 'S_pre_hook = $ob_object_call_capture(S_one, (OBJECT_FACTORY_NEW pobfactoryreturn))',
 'S_bad_marker = S_return[.TODO = [RETURN_UNWIND (KNOWN (POBJECT n_exception)) (pobfactoryreturn.THROW)]]',
 'S_no_pop = S_pre_hook[.FRAMES = S_return.FRAMES]',
 'S_no_carrier = S_pre_hook[.RESULT = KNOWN PNULL][.DESTRUCTION.FRAMES = eps]',
 'S_budget = $drive_steps(S_return, 0)',
 ]
 if local:
  b += ['S_one.DESTRUCTION.FRAMES = pdestructionframe :: pdestructionframe_tail*']
 carrier=(r'S_one.RESULT = KNOWN PNULL /\ pdestructionframe.VALUE = KNOWN (POBJECT n_exception) /\ pdestructionframe.PENDING = eps /\ pdestructionframe.FUNCTION = pfunction_make.ORIGIN /\ $ob_object_factory_value_frames(S_one.DESTRUCTION.FRAMES, pobfactoryreturn)' if local else r'S_one.RESULT = KNOWN (POBJECT n_exception) /\ S_one.DESTRUCTION.FRAMES = eps')
 checks=[
 ('selected completed constructor issues one normalized nonowning birth',r'pctorcall.MODE = CTOR_NEW /\ pctorcall_source.MODE = CTOR_NEW /\ pctorcall_source.RECEIVER = n_exception /\ pobfactoryreturn.BIRTH.OBJECT = n_exception /\ pobfactoryreturn.BIRTH.SITE = pctorcall.SITE /\ $string_bytes(pvalue_message) = (pobfactoryreturn.BIRTH.MESSAGE) /\ pobfactoryreturn.BIRTH.CODE = z_code /\ pobfactoryreturn.BIRTH.LINE = pctorcall.LINE /\ $ob_object_ctor_fact_live(S_born, pobfactoryreturn.BIRTH) /\ $heap_count(HOBJECT n_exception, $machine_roots(S_born)) = 1'),
 ('producer return and native throw remain separately selected own-code sites',r'pobfactoryreturn.FUNCTION = pfunction_make.ORIGIN /\ pobfactoryreturn.RETURN = porigin_return /\ pobfactoryreturn.THROW = porigin_throw /\ porigin_return =/= porigin_throw /\ $ob_object_factory_function(S_born, pfunction_native, pobfactoryreturn) = (pfunction_make) /\ ~pfunction_make.SIGNATURE.BYREF /\ pfunction_make.SIGNATURE.PARAMETERS = eps'),
 ('issuer cannot mint from other modes failed result or owned continuation',r'$ctor_completed(S_no_source, pctorcall, pvalue_message, PINT z_code, PNULL) = S_born /\ $ctor_completed(S_no_source, pctorcall[.MODE = CTOR_METHOD], pvalue_message, PINT z_code, PNULL) = S_no_source /\ $ctor_completed(S_no_source, pctorcall[.MODE = CTOR_CAPTURE 0], pvalue_message, PINT z_code, PNULL) = S_no_source /\ $ctor_completed(S_wrong_result, pctorcall, pvalue_message, PINT z_code, PNULL) = S_wrong_result /\ $ctor_completed(S_failed, pctorcall, pvalue_message, PINT z_code, PNULL) = S_failed /\ $ctor_completed(S_held, pctorcall, pvalue_message, PINT z_code, PNULL) = S_held /\ $ctor_completed(S_tasks, pctorcall, pvalue_message, PINT z_code, PNULL) = S_tasks'),
 ('altered producer return and throw cannot validate the factory source',r'$ob_object_factory_function(S_born, pfunction_native, pobfactoryreturn_function) = eps /\ $ob_object_factory_function(S_born, pfunction_native, pobfactoryreturn_return) = eps /\ $ob_object_factory_function(S_born, pfunction_native, pobfactoryreturn_throw) = eps'),
 ('actual marker and exact one-pop carrier are necessary for returned handoff',r'$source_exception_transition(S_return, S_pre_hook) = S_one /\ $source_exception_transition(S_bad_marker, S_pre_hook) = S_pre_hook /\ $source_exception_transition(S_return, S_no_pop) = S_no_pop /\ $source_exception_transition(S_return, S_no_carrier) = S_no_carrier'),
 ('real return carrier preserves the one returned object',carrier+r' /\ $heap_count(HOBJECT n_exception, $machine_roots(S_return)) = 1 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_one)) = 1 /\ S_one.CURRENT = pframe_call.CONTEXT /\ |S_one.FRAMES| = $(|S_return.FRAMES| - 1)'),
 ('constructed and returned phases cannot report or capture early',r'$ob_object_source_pending((OBJECT_FACTORY_NEW pobfactoryreturn)) = eps /\ $ob_object_source_thrown((OBJECT_FACTORY_NEW pobfactoryreturn)) = eps /\ $ob_object_source_pending((OBJECT_FACTORY_RETURNED pobfactoryreturn)) = eps /\ $ob_object_source_thrown((OBJECT_FACTORY_RETURNED pobfactoryreturn)) = eps /\ $ob_object_factory_capture(S_ready, pfunction_native, (OBJECT_FACTORY_NEW pobfactoryreturn), porigin_throw, n_exception) = eps /\ $ob_object_factory_capture(S_one, pfunction_native, (OBJECT_FACTORY_RETURNED pobfactoryreturn), porigin_throw, n_exception) = eps'),
 ('only published matching native result becomes pending without a new root',r'S_ready.RESULT = KNOWN (POBJECT n_exception) /\ ~$ob_object_factory_value_frames(S_ready.DESTRUCTION.FRAMES, pobfactoryreturn) /\ $ob_object_factory_capture(S_ready, pfunction_native, (OBJECT_FACTORY_RETURNED pobfactoryreturn), porigin_throw, n_exception) = (OBJECT_FACTORY_THROW pobfactoryreturn) /\ $ob_object_source_pending($ob_object_native_source(S_active)) = ((porigin_return,n_exception)) /\ $heap_count(HOBJECT n_exception, $machine_roots(S_active)) = 1 /\ $heap_count(HOBJECT n_object, $machine_roots(S_active)) = 2'),
 ('zero budget preserves actual return owner and metadata',r'S_budget.COMPLETION = BUDGET /\ S_budget.TODO = S_return.TODO /\ S_budget.CURRENT = S_return.CURRENT /\ S_budget.FRAMES = S_return.FRAMES /\ S_budget.GC = S_return.GC /\ S_budget.EVENTS = S_return.EVENTS /\ S_budget.ALLOCATIONS = S_return.ALLOCATIONS'),
 ('issued handoff and pending states retain public invariants',public('S_born')+' /\\ '+public('S_one')+' /\\ '+public('S_active')),
 ]
 return b,checks
def fatal(path,local):
 line,call=(15,9) if local else (11,6)
 return (f'Fatal error: Uncaught Exception: E in {path}:{line}\nStack trace:\n#0 {path}({call}): make()\n#1 [internal function]: T->__toString()\n#2 {{main}}\n  thrown in {path} on line {line}\n').encode()
def report_assertions(fixture,path,local):
 b=pipeline(fixture,path)+[
 'S_exit_found = $fr_seek(S_active, 3, 512)',r'S_exit_found.COMPLETION = NORMAL \/ S_exit_found.COMPLETION = BUDGET',
 'S_exit = S_exit_found[.COMPLETION = NORMAL]',
 'S_exit.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (OUTPUT_FINAL_OBJECT_CV pobobjectreturn) :: ptask_tail*',
 'S_report_found = $drive_steps(S_exit, 1)','S_report_found.COMPLETION = BUDGET',
 'S_report = S_report_found[.COMPLETION = NORMAL]',
 'S_report.TODO = [OUTPUT_FINAL_PENDING pobdeactivate n_exception true]',
 'S_retired_found = $fr_seek(S_report, 4, 512)',r'S_retired_found.COMPLETION = NORMAL \/ S_retired_found.COMPLETION = BUDGET',
 'S_retired = S_retired_found[.COMPLETION = NORMAL]',
 'S_retired.DESTRUCTION.ABANDONED = [pdestructioncleanup]',
 'pobfactoryreturn_wrong = pobfactoryreturn[.RETURN = pobfactoryreturn.THROW]',
 'pobobjectreturn_new = pobobjectreturn[.SOURCE = (OBJECT_FACTORY_NEW pobfactoryreturn)]',
 'pobobjectreturn_returned = pobobjectreturn[.SOURCE = (OBJECT_FACTORY_RETURNED pobfactoryreturn)]',
 'pobobjectreturn_wrong = pobobjectreturn[.SOURCE = (OBJECT_FACTORY_THROW pobfactoryreturn_wrong)]',
 'pdestructioncleanup_new = pdestructioncleanup[.SOURCE = OUTPUT_FINAL_OBJECT_THROW pobobjectreturn_new pobdeactivate pobfactoryreturn.RETURN n_exception]',
 'pdestructioncleanup_returned = pdestructioncleanup[.SOURCE = OUTPUT_FINAL_OBJECT_THROW pobobjectreturn_returned pobdeactivate pobfactoryreturn.RETURN n_exception]',
 'pdestructioncleanup_wrong = pdestructioncleanup[.SOURCE = OUTPUT_FINAL_OBJECT_THROW pobobjectreturn_wrong pobdeactivate pobfactoryreturn.RETURN n_exception]',
 'S_new = S_retired[.DESTRUCTION.ABANDONED = [pdestructioncleanup_new]]',
 'S_returned = S_retired[.DESTRUCTION.ABANDONED = [pdestructioncleanup_returned]]',
 'S_wrong = S_retired[.DESTRUCTION.ABANDONED = [pdestructioncleanup_wrong]]',
 ]
 events='[OUTPUT ([80])'+(', WARNING ($ptascii("missing")) 4' if local else '')+', STDERR '+runner.bytes_expr(fatal(path,local))+']'
 c=[
 ('only original native frame reports after full return-slot consumption',r'$ob_object_final_cv_ready(S_exit, pobobjectreturn, pdestructionframe, n_exception) /\ pdestructionframe.FUNCTION = pfunction_native.ORIGIN /\ pdestructionframe.FUNCTION =/= pfunction_make.ORIGIN /\ S_exit.CURRENT = eps /\ S_exit.FRAMES = eps /\ S_exit.ORIGIN = eps /\ ~$ob_object_factory_value_frames(S_exit.DESTRUCTION.FRAMES, pobfactoryreturn)'),
 ('creation line and retained factory trace survive later native throw', 'S_report.EVENTS = '+events+r' /\ S_report.EXITSTATUS = 255 /\ $throwable_field(S_report, n_exception, "previous") = PNULL /\ $heap_count(HOBJECT n_exception, $machine_roots(S_report)) = 1 /\ $heap_count(HOBJECT n_object, $machine_roots(S_report)) = 2'),
 ('retired report uses immutable birth without acquiring an owner',r'~((HOBJECT n_exception) <- S_retired.ALLOCATIONS) /\ $heap_count(HOBJECT n_exception, $machine_roots(S_retired)) = 0 /\ $heap_count(HOBJECT n_object, $machine_roots(S_retired)) = 2 /\ $eager_cleanup_valid(S_retired, pdestructioncleanup) /\ $task_nodes(pdestructioncleanup.SOURCE) = eps'),
 ('retired receipts refuse prethrow phases and wrong producer source',r'~$eager_cleanup_valid(S_new, pdestructioncleanup_new) /\ ~$eager_cleanup_valid(S_returned, pdestructioncleanup_returned) /\ ~$eager_cleanup_valid(S_wrong, pdestructioncleanup_wrong)'),
 ]
 return b,c

CATCH=sources.CASES['factory-result'].replace(b'        throw make();',b"        try { throw make(); } catch (Exception $e) { return 'H'; }")
SITES=sources.CASES['factory-result'].replace(b'        throw make();',b"        try { throw make(); } catch (Exception $e) { $old = $e; }\n        throw make();")
NATIVE_LOCAL=b"""<?php
echo 'P';
class T {
    function __toString() { $local = new T; throw new Exception('E'); }
    function __destruct() { throw make(); }
}
function make() { $message = 'F'; return new Exception($message); }
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
"""
def override_assertions(fixture,path,local=False):
 all_bindings=pipeline(fixture,path)
 b=all_bindings[:all_bindings.index('S_return_found = $fr_seek(S_born, 1, 512)')]+[
 'S_override_found = $fr_seek(S_born, 6, 512)',r'S_override_found.COMPLETION = NORMAL \/ S_override_found.COMPLETION = BUDGET',
 'S_override = S_override_found[.COMPLETION = NORMAL]',
 'S_override.TODO = [RETURN_UNWIND (KNOWN pvalue_h) porigin_override?]',
 'S_handoff_found = $drive_steps(S_override, 1)','S_handoff_found.COMPLETION = BUDGET',
 'S_handoff = S_handoff_found[.COMPLETION = NORMAL]',
 'S_scalar_found = $fr_seek(S_handoff, 7, 512)',r'S_scalar_found.COMPLETION = NORMAL \/ S_scalar_found.COMPLETION = BUDGET',
 'S_scalar = S_scalar_found[.COMPLETION = NORMAL]',
 'S_scalar.TODO = (THROW_VALUE porigin_scalar z_scalar) :: ptask_scalar*',
 ]
 c=[
 ('actual fresh factory birth exists before finally overrides its return',r'pobfactoryreturn.BIRTH.OBJECT = n_exception /\ $ob_object_ctor_fact_live(S_born, pobfactoryreturn.BIRTH) /\ $heap_count(HOBJECT n_exception, $machine_roots(S_born)) = 1'),
 ('real finally H consumes F and clears borrowed source before GC',r'$string_bytes(pvalue_h) = ($ptascii("H")) /\ ~((HOBJECT n_exception) <- S_override.ALLOCATIONS) /\ $heap_count(HOBJECT n_exception, $machine_roots(S_override)) = 0 /\ $ob_object_native_source(S_override) = eps /\ $heap_count(HOBJECT n_object, $machine_roots(S_override)) = 2 /\ '+public('S_override')),
 ('normal return publishes H without recovering the retired F certificate',r'S_handoff.CURRENT = pframe_call.CONTEXT /\ $ob_object_native_source(S_handoff) = eps /\ $heap_count(HOBJECT n_exception, $machine_roots(S_handoff)) = 0 /\ $heap_count(HOBJECT n_object, $machine_roots(S_handoff)) = 2 /\ '+public('S_handoff')),
 ('native scalar throw frontier has no stale factory authority',r'$ob_object_native_source(S_scalar) = eps /\ $ob_object_factory_capture(S_scalar, pfunction_native, eps, porigin_scalar, n_exception) = eps /\ S_scalar.EVENTS = [OUTPUT ([80])] /\ '+public('S_scalar')),
 ]
 return b,c
def catch_assertions(fixture,path,local=False):
 b=pipeline(fixture,path)+[
 'S_catch_found = $fr_seek(S_active, 5, 512)',r'S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET',
 'S_catch = S_catch_found[.COMPLETION = NORMAL]',
 'S_catch.TODO = (CATCH_BIND porigin_try n_index n_exception) :: ptask_catch*',
 ]
 c=[
 ('factory result becomes pending only at the actual native throw',r'$ob_object_source_pending($ob_object_native_source(S_active)) = ((pobfactoryreturn.RETURN,n_exception)) /\ S_ready.CURRENT = S_active.CURRENT /\ $heap_count(HOBJECT n_exception, $machine_roots(S_active)) = 1'),
 ('actual native catch clears metadata while caught F remains owned',r'$ob_object_native_source(S_catch) = eps /\ $task_nodes(CATCH_BIND porigin_try n_index n_exception) = [HOBJECT n_exception] /\ $heap_count(HOBJECT n_exception, $machine_roots(S_catch)) = 1 /\ $heap_count(HOBJECT n_object, $machine_roots(S_catch)) = 2 /\ S_catch.EVENTS = [OUTPUT ([80])]'),
 ('caught budget state retains public invariants',public('S_catch')),
 ]
 return b,c
def sites_assertions(fixture,path,local=False):
 b=pipeline(fixture,path)+[
 'S_catch_found = $fr_seek(S_active, 5, 512)',r'S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET',
 'S_catch = S_catch_found[.COMPLETION = NORMAL]',
 'S_second_ctor_found = $fr_seek(S_catch, 0, 512)',r'S_second_ctor_found.COMPLETION = NORMAL \/ S_second_ctor_found.COMPLETION = BUDGET',
 'S_second_ctor = S_second_ctor_found[.COMPLETION = NORMAL]',
 'S_second_ctor.TODO = (ORDINARY_CTOR_RECEIVE pordinaryinternal_second) :: ptask_ctor_second*',
 'pctorcall_second = pordinaryinternal_second.CALL',
 'pordinaryinternal_second.VALUES = [pvalue_message_second, PINT z_code_second, PNULL]',
 'n_second = pctorcall_second.RECEIVER',
 'S_second_born_found = $drive_steps(S_second_ctor, 1)','S_second_born_found.COMPLETION = BUDGET',
 'S_second_born = S_second_born_found[.COMPLETION = NORMAL]',
 '$ob_object_native_source(S_second_born) = (OBJECT_FACTORY_NEW pobfactoryreturn_second)',
 'pobfactoryreturn_foreign = pobfactoryreturn_second[.THROW = pobfactoryreturn.THROW]',
 'S_second_no_source = $ob_object_call_capture(S_second_born, eps)',
 'S_second_no_source.FRAMES = pframe_second :: pframe_second_tail*',
 'pframe_second.TODO = (ORIGIN_RETURN (pobfactoryreturn_second.THROW)) :: (THROW_VALUE pobfactoryreturn_second.THROW z_second_throw) :: ptask_second_native*',
 'S_foreign_consumer = S_second_no_source[.FRAMES = pframe_second[.TODO = (ORIGIN_RETURN (pobfactoryreturn.THROW)) :: (THROW_VALUE pobfactoryreturn.THROW z_throw) :: ptask_second_native*] :: pframe_second_tail*]',
 'S_second_ready_found = $fr_seek(S_second_born, 2, 512)',r'S_second_ready_found.COMPLETION = NORMAL \/ S_second_ready_found.COMPLETION = BUDGET',
 'S_second_ready = S_second_ready_found[.COMPLETION = NORMAL]',
 'S_second_ready.TODO = (THROW_VALUE porigin_second z_second) :: ptask_second*',
 'S_old_result = S_second_ready[.RESULT = KNOWN (POBJECT n_exception)]',
 ]
 c=[
 ('two actual factory calls retain distinct fresh results and distinct native consumers',r'n_second =/= n_exception /\ pobfactoryreturn_second.THROW =/= pobfactoryreturn.THROW /\ pobfactoryreturn_second.RETURN = pobfactoryreturn.RETURN /\ (HOBJECT n_exception) <- S_second_ready.ALLOCATIONS /\ $heap_owners($heap_graph(S_second_ready), HOBJECT n_exception) = 2 /\ $heap_count(HOBJECT n_second, $machine_roots(S_second_ready)) = 1'),
 ('foreign valid consumer selects same factory but cannot authenticate actual call edge',r'$ob_object_factory_function(S_second_born, pfunction_native, pobfactoryreturn_foreign) = (pfunction_make) /\ $ob_object_factory_current(S_second_born, pobfactoryreturn_foreign) = eps'),
 ('issuer rejects coherently retargeted saved consumer while current callsite stays real',r'$ctor_completed(S_second_no_source, pctorcall_second, pvalue_message_second, PINT z_code_second, PNULL) = S_second_born /\ $ctor_completed(S_foreign_consumer, pctorcall_second, pvalue_message_second, PINT z_code_second, PNULL) = S_foreign_consumer'),
 ('live older Throwable cannot replace the newly returned result',r'$ob_object_factory_capture(S_second_ready, pfunction_native, (OBJECT_FACTORY_RETURNED pobfactoryreturn_second), porigin_second, n_exception) = eps /\ $ob_object_factory_capture(S_old_result, pfunction_native, (OBJECT_FACTORY_RETURNED pobfactoryreturn_second), porigin_second, n_second) = eps'),
 ('second source-reached native throw frontier is publicly valid',public('S_second_ready')),
 ]
 return b,c
def native_local_assertions(fixture,path,local=False):
 b=pipeline(fixture,path)+[
 '$ob_object_final_local_context(S_active) = ((pobobjectreturn, pdestructorcall, pobobjectsource?, ptask_native*))',
 'pdestructorcall.FRAME = (pdestructionframe_outer)',
 'pdestructionframe_outer.PENDING = (n_old)',
 'S_exit_found = $fr_seek(S_active, 8, 512)',r'S_exit_found.COMPLETION = NORMAL \/ S_exit_found.COMPLETION = BUDGET',
 'S_exit = S_exit_found[.COMPLETION = NORMAL]',
 'S_exit.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: ptask_return*',
 ]
 owners=lambda s:f'$heap_count(HOBJECT pobobjectreturn.OBJECT, $machine_roots({s})) = 2 /\\ $heap_count(HOBJECT pdestructorcall.OBJECT, $machine_roots({s})) = 2 /\\ $heap_count(HOBJECT n_old, $machine_roots({s})) = 1 /\\ $heap_count(HOBJECT n_exception, $machine_roots({s})) = 1'
 c=[
 ('native destructor gets same factory result through real returned owner',r'$ob_object_native_source(S_one) = (OBJECT_FACTORY_RETURNED pobfactoryreturn) /\ $ob_object_source_pending($ob_object_native_source(S_one)) = eps /\ $heap_count(HOBJECT n_exception, $machine_roots(S_one)) = 1 /\ S_ready.RESULT = KNOWN (POBJECT n_exception) /\ ~$ob_object_factory_value_frames(S_ready.DESTRUCTION.FRAMES, pobfactoryreturn)'),
 ('actual local native throw retains outer cast saved E and selected destructor guards',r'pdestructorcall.OBJECT = n_object /\ n_exception =/= n_old /\ $ob_object_source_pending(pobobjectsource?) = ((pobfactoryreturn.RETURN,n_exception)) /\ $throwable_field(S_active, n_exception, "previous") = PNULL /\ '+owners('S_active')),
 ('factory native-destructor pending state is publicly valid',public('S_active')),
 ('only genuine destructor C0 is ready to report factory-created F',r'$ob_object_final_local_ready(S_exit, pobobjectreturn, pdestructorcall, pobfactoryreturn.RETURN, n_exception, pdestructionframe, ptask_return*) /\ pdestructionframe.FUNCTION = pfunction_native.ORIGIN /\ pdestructionframe.FUNCTION =/= pfunction_make.ORIGIN /\ S_exit.CURRENT = eps /\ S_exit.FRAMES = eps /\ '+owners('S_exit')),
 ('native destructor C0 keeps full public ownership',public('S_exit')),
 ]
 return b,c

def render(bindings,checks):
 return PREFIX+'\ndec $main() : bool*\ndef $main() = ['+', '.join('('+x+')' for _,x in checks)+']\n'+''.join('  -- if '+x+'\n' for x in bindings)
def fingerprint():
 return {p:support.common.sha(ROOT/p) for p in ('spec/semantics/30-storage.watsup','spec/semantics/456-output-object-returns.watsup','spec/semantics/257-request-destructors.watsup','spec/semantics/modules.json','tests/semantics/output_factory_return_sources.py','tests/semantics/output_factory_return_review_state.py','tests/semantics/_build/default/numeric_runner.exe','_build/default/adapter/main.exe','.tools/php/bin/php')}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);p.add_argument('--stage',choices=('provenance','report','override','catch','sites','native_local'),default='provenance');p.add_argument('--native-root',type=Path);p.add_argument('--select',choices=('minimal','local','all'),default='all');args=p.parse_args()
 out=args.output or Path(tempfile.mkdtemp(prefix='factory-return-review-'));out.mkdir(parents=True,exist_ok=True)
 report={'revision':support.subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD']).decode().strip(),'before':fingerprint(),'records':[],'passed':False,'native_agreement_credit':0,'cap_seconds':300,'stage':args.stage};directory=out
 try:
  modules=json.loads((ROOT/'spec/semantics/modules.json').read_text())
  if args.stage in ('provenance','report'):
   chosen=[(index,name,source,bool(index),True) for index,(name,source) in enumerate(sources.CASES.items())]
  else:
   name,source={'override':('producer-finally-override',sources.OVERRIDE),'catch':('native-caller-catch',CATCH),'sites':('two-valid-native-sites',SITES),'native_local':('native-destructor-factory',NATIVE_LOCAL)}[args.stage]
   chosen=[(0,name,source,args.stage=='native_local',False)]
  for index,name,source,local,frozen_case in chosen:
   short='local' if local else 'minimal'
   if args.select not in ('all',short):continue
   directory=out/short;directory.mkdir();frozen=args.native_root is not None and frozen_case;path=args.native_root/f'native-0{index+1}'/'source.php' if frozen else directory/'source.php'
   if frozen:assert path.read_bytes()==source
   else:path.write_bytes(source)
   worker=Worker([str(ROOT/'.tools/php/bin/php'),'-n','-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],directory/'frontend')
   try:parsed=worker.request({'op':'parse','source':base64.b64encode(source).decode()})
   finally:worker.close()
   adapter=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],directory/'adapter')
   try:checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
   finally:adapter.close()
   fn={'provenance':provenance,'report':report_assertions,'override':override_assertions,'catch':catch_assertions,'sites':sites_assertions,'native_local':native_local_assertions}[args.stage];bindings,checks=fn(checked['fixture'],path,local);fixture=directory/'state.watsup';fixture.write_text(render(bindings,checks))
   rec={'case':name,'checks':[x for x,_ in checks],'fixture_sha256':support.common.sha(fixture),'passed':False};report['records'].append(rec);start=time.monotonic()
   result=support.common.run([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),'--sl',*[str(ROOT/x) for x in modules],str(fixture)],directory,'state',300)
   rec['seconds']=round(time.monotonic()-start,3);values=re.findall(rb'\b(?:true|false)\b',result.stdout);rec.update(exit=result.returncode,results=[x==b'true' for x in values])
   assert not re.sub(rb'true|false|[\[\](),;\s]',b'',result.stdout),(result.stdout,result.stderr)
   assert result.returncode==0 and not result.stderr and values==[b'true']*len(checks),(result.returncode,result.stderr.decode(errors='replace'),rec['results'])
   rec['passed']=True;print(short,True,rec['seconds'],flush=True)
  assert report['records'],'no fixture selected';report['passed']=True
 except BaseException as e:
  report['failure']={'type':type(e).__name__,'message':str(e)};raise
 finally:
  report['after']=fingerprint();report['stable']=report['before']==report['after'];report['passed']=report['passed'] and report['stable'];(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json',report['passed'],flush=True)
if __name__=='__main__':main()
