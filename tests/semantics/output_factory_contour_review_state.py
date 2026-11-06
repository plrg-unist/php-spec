#!/usr/bin/env python3
"""Same fresh result crosses actual by-value factory return-frame contours."""
import argparse,base64,json,os,re,tempfile,time
from pathlib import Path
from recorded_worker import Worker
import output_factory_return_review_state as previous
import output_factory_contour_sources as sources
import output_deprecation_warning_review_state as runner
import output_object_conversion_review_sources as support
ROOT=support.ROOT
PREFIX=previous.PREFIX+r'''
dec $fc_return(pstate) : bool
def $fc_return(S) = true
  -- if S.TODO = [RETURN_UNWIND (KNOWN (POBJECT n)) (porigin)]
  -- if S.OBJECTS[n] = THROWABLE pthrowable
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = pcallcontext.FUNCTION /\ pcallcontext.ARGC = 0
def $fc_return(S) = false -- otherwise
dec $fc_seek_return(pstate, nat) : pstate
def $fc_seek_return(S, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $fc_seek_return(S, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $fc_return(S)
def $fc_seek_return(S, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$fc_return(S)
def $fc_seek_return(S, n) = $fc_seek_return($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$fc_return(S) /\ $(n > 0)
dec $fc_walk(pstate, nat, nat) : pstate*
def $fc_walk(S, n_exception, 0) = [S_ready]
  -- if S_ready_found = $fr_seek(S, 2, 512)
  -- if S_ready_found.COMPLETION = NORMAL \/ S_ready_found.COMPLETION = BUDGET
  -- if S_ready = S_ready_found[.COMPLETION = NORMAL]
def $fc_walk(S, n_exception, n) = [S_return, S_one] ++ $fc_walk(S_one, n_exception, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if S_return_found = $fc_seek_return(S, 512)
  -- if S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET
  -- if S_return = S_return_found[.COMPLETION = NORMAL]
  -- if S_return.TODO = [RETURN_UNWIND (KNOWN (POBJECT n_exception)) (porigin_return)]
  -- if S_one_found = $drive_steps(S_return, 1)
  -- if S_one_found.COMPLETION = BUDGET
  -- if S_one = S_one_found[.COMPLETION = NORMAL]
'''
public=previous.public
def birth(program,path):
 return [
  'S_initial = $php_file_run('+program+', 0, '+runner.bytes_expr(os.fsencode(path))+', '+runner.bytes_expr(os.fsencode(path.parent))+')',
  'S_ctor_found = $fr_seek(S_initial, 0, 1024)',r'S_ctor_found.COMPLETION = NORMAL \/ S_ctor_found.COMPLETION = BUDGET',
  'S_ctor = S_ctor_found[.COMPLETION = NORMAL]',
  'S_ctor.TODO = (ORDINARY_CTOR_RECEIVE pordinaryinternal) :: ptask_ctor*',
  'pctorcall = pordinaryinternal.CALL','n_exception = pctorcall.RECEIVER',
  'pordinaryinternal.VALUES = [pvalue_message, PINT z_code, PNULL]',
  '$ob_object_call_context(S_ctor) = ((S_native, pfunction_leaf, pobsourcecontour))',
  'S_native.CURRENT = (pcallcontext_native)',
  'pcallcontext_native.TARGET = METHOD_TARGET n_object pcallcontext_native.FUNCTION',
  '$function_at($all_functions(S_ctor), pcallcontext_native.FUNCTION) = (pfunction_native)',
  'S_born_found = $drive_steps(S_ctor, 1)','S_born_found.COMPLETION = BUDGET',
  'S_born = S_born_found[.COMPLETION = NORMAL]',
  '$ob_object_native_source(S_born) = (OBJECT_FACTORY_NEW pobfactoryreturn)',
 ]
def pipeline(program,path,edges,active=True):
 b=birth(program,path)
 states=[s for i in range(edges) for s in (f'S_return_{i}',f'S_one_{i}')]+['S_ready']
 b += ['['+', '.join(states)+f'] = $fc_walk(S_born, n_exception, {edges})']
 for i in range(edges):
  b += [f'S_return_{i}.TODO = [RETURN_UNWIND (KNOWN (POBJECT n_exception)) (porigin_return_{i})]',
   f'S_return_{i}.CURRENT = (pcallcontext_{i})',
   f'$function_at(S_return_{i}.FUNCTIONS, pcallcontext_{i}.FUNCTION) = (pfunction_{i})',
   f'S_return_{i}.FRAMES = pframe_{i} :: pframe_tail_{i}*',
   f'pobfactoryreturn_{i} = pobfactoryreturn[.CONTOUR = pobfactoryreturn.CONTOUR[.CURSOR = {i}]]',
   f'pobfactoryreturn_after_{i} = pobfactoryreturn[.CONTOUR = pobfactoryreturn.CONTOUR[.CURSOR = {i+1}]]']
 b += [f'pobfactoryreturn_final = pobfactoryreturn_after_{edges-1}',
  'S_ready.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_ready*']
 if active:
  b += ['S_active_found = $drive_steps(S_ready, 1)','S_active_found.COMPLETION = BUDGET',
   'S_active = S_active_found[.COMPLETION = NORMAL]',
   'S_active.TODO = (THROW_SEARCH n_exception) :: ptask_active*']
 return b
def provenance(program,path,edges):
 b=pipeline(program,path,edges)+[
  'S_no_source = $ob_object_call_capture(S_born, eps)',
  'S_owned = S_no_source[.HELD = [HOBJECT n_exception]]',
  'S_tasks = S_no_source[.TODO = S_no_source.TODO ++ [THROW_SEARCH n_exception]]',
  'pobfactoryreturn_skip = pobfactoryreturn[.CONTOUR = pobfactoryreturn.CONTOUR[.CURSOR = 1]]',
  'pobfactoryreturn_exhausted = pobfactoryreturn[.CONTOUR = pobfactoryreturn.CONTOUR[.CURSOR = |pobfactoryreturn.CONTOUR.CALLS|]]',
  'pobfactoryreturn_bad = pobfactoryreturn[.FUNCTION = pfunction_native.ORIGIN]',
  'pobsourcecontour_bad = pobfactoryreturn.CONTOUR[.NATIVE = pfunction_leaf.ORIGIN]',
  'pobfactoryreturn_native = pobfactoryreturn[.CONTOUR = pobsourcecontour_bad]',
  'pobsourcecall_bad = pobfactoryreturn.CONTOUR.CALLS[0][.SITE = pobfactoryreturn.RETURN]',
  'pobfactoryreturn_site = pobfactoryreturn[.CONTOUR = pobfactoryreturn.CONTOUR[.CALLS = pobsourcecall_bad :: pobfactoryreturn.CONTOUR.CALLS[1:$nabs($(|pobfactoryreturn.CONTOUR.CALLS| - 1))]]]',
  'S_bad_name = S_return_0[.CURRENT = (pcallcontext_0[.NAME = $ptascii("foreign")])]',
  'S_bad_cvs = S_return_0[.CVS = eps]',
  'pframe_0.CONTEXT = (pcallcontext_caller)',
  'pframe_0.LOCALS = (psymboltable_caller)',
  'S_bad_middle_name = S_return_0[.FRAMES = pframe_0[.CONTEXT = (pcallcontext_caller[.NAME = $ptascii("foreign")])] :: pframe_tail_0*]',
  'S_bad_middle_cvs = S_return_0[.FRAMES = pframe_0[.LOCALS = (psymboltable_caller[.CVS = [$ptascii("foreign")]])] :: pframe_tail_0*]',
  'S_owned_caller = S_return_0[.FRAMES = pframe_0[.HELD = [HOBJECT n_exception]] :: pframe_tail_0*]',
  'S_pre_hook = $ob_object_call_capture(S_one_0, (OBJECT_FACTORY_NEW pobfactoryreturn))',
  'S_skipped_post = $ob_object_call_capture(S_one_0, (OBJECT_FACTORY_RETURNED pobfactoryreturn_exhausted))',
  'S_no_pop = S_pre_hook[.FRAMES = S_return_0.FRAMES]',
  'S_no_carrier = S_pre_hook[.RESULT = KNOWN PNULL][.DESTRUCTION.FRAMES = eps]',
  'S_bad_marker = S_return_0[.TODO = [RETURN_UNWIND (KNOWN (POBJECT n_exception)) (pobfactoryreturn.THROW)]]',
  'S_budget = $drive_steps(S_return_0, 0)',
 ]
 c=[
  ('completed leaf NEW retains selected normalized birth and immutable full contour',f'pobfactoryreturn.CONTOUR = pobsourcecontour /\\ |pobsourcecontour.CALLS| = {edges} /\\ pobfactoryreturn.CONTOUR.CURSOR = 0 /\\ pobfactoryreturn.FUNCTION = pfunction_leaf.ORIGIN /\\ pobfactoryreturn.BIRTH.OBJECT = pctorcall.RECEIVER /\\ $ob_object_ctor_fact_live(S_born, pobfactoryreturn.BIRTH) /\\ $ob_object_factory_function(S_born, pfunction_native, pobfactoryreturn) = (pfunction_leaf)'),
  ('current birth owner bounds remain enforced',r'$ctor_completed(S_no_source, pctorcall, pvalue_message, PINT z_code, PNULL) = S_born /\ $ctor_completed(S_owned, pctorcall, pvalue_message, PINT z_code, PNULL) = S_owned /\ $ctor_completed(S_tasks, pctorcall, pvalue_message, PINT z_code, PNULL) = S_tasks'),
 ]
 for i in range(edges):
  before='OBJECT_FACTORY_NEW' if i==0 else 'OBJECT_FACTORY_RETURNED'
  c += [(f'edge {i} consumes its own marker and exactly one real frame while F has one owner',
   f'$ob_object_native_source(S_return_{i}) = ({before} pobfactoryreturn_{i}) /\\ $ob_object_factory_return_origin(S_return_{i}, pobfactoryreturn_{i}) = (porigin_return_{i}) /\\ $ob_object_native_source(S_one_{i}) = (OBJECT_FACTORY_RETURNED pobfactoryreturn_after_{i}) /\\ S_one_{i}.FRAMES = $ob_object_call_capture_frames(S_one_{i}, pframe_tail_{i}*, (OBJECT_FACTORY_RETURNED pobfactoryreturn_after_{i})) /\\ S_one_{i}.CURRENT = pframe_{i}.CONTEXT /\\ S_one_{i}.ORIGIN = pframe_{i}.ORIGIN /\\ S_one_{i}.CONSTCONTEXT = pframe_{i}.CONSTCONTEXT /\\ |S_one_{i}.FRAMES| = $(|S_return_{i}.FRAMES| - 1) /\\ $ob_object_factory_carrier(S_one_{i}, pfunction_{i}, pobfactoryreturn_{i}) /\\ $heap_count(HOBJECT n_exception, $machine_roots(S_return_{i})) = 1 /\\ $heap_count(HOBJECT n_exception, $machine_roots(S_one_{i})) = 1 /\\ $heap_count(HOBJECT n_object, $machine_roots(S_one_{i})) = 2')]
 c += [
  ('cursor skip altered leaf NAME CVS and saved owned continuation refuse active authority',r'$ob_object_factory_current(S_return_0, pobfactoryreturn_skip) = eps /\ $ob_object_factory_current(S_return_0, pobfactoryreturn_exhausted) = eps /\ $ob_object_factory_function(S_born, pfunction_native, pobfactoryreturn_bad) = eps /\ $ob_object_factory_current(S_bad_name, pobfactoryreturn) = eps /\ $ob_object_factory_current(S_bad_cvs, pobfactoryreturn) = eps /\ $ob_object_factory_current(S_owned_caller, pobfactoryreturn) = eps'),
  ('immutable selected native and intermediate edge reject foreign names locals and call sites',r'$ob_object_factory_function(S_born, pfunction_native, pobfactoryreturn_native) = eps /\ $ob_object_factory_function(S_born, pfunction_native, pobfactoryreturn_site) = eps /\ $ob_object_factory_current(S_bad_middle_name, pobfactoryreturn) = eps /\ $ob_object_factory_current(S_bad_middle_cvs, pobfactoryreturn) = eps'),
  ('handoff cannot consume a wrong marker omit the frame pop lose the carrier or skip a position',r'$source_exception_transition(S_return_0, S_pre_hook) = S_one_0 /\ $source_exception_transition(S_return_0, S_skipped_post) = S_skipped_post /\ $source_exception_transition(S_bad_marker, S_pre_hook) = S_pre_hook /\ $source_exception_transition(S_return_0, S_no_pop) = S_no_pop /\ $source_exception_transition(S_return_0, S_no_carrier) = S_no_carrier'),
  ('partial returned and constructed records cannot become pending or report',r'$ob_object_source_pending((OBJECT_FACTORY_NEW pobfactoryreturn)) = eps /\ $ob_object_source_thrown((OBJECT_FACTORY_RETURNED pobfactoryreturn_after_0)) = eps /\ $ob_object_source_pending((OBJECT_FACTORY_THROW pobfactoryreturn_after_0)) = eps /\ $ob_object_factory_capture(S_ready, pfunction_native, (OBJECT_FACTORY_RETURNED pobfactoryreturn_after_0), porigin_throw, n_exception) = eps /\ $ob_object_factory_capture(S_ready, pfunction_native, (OBJECT_FACTORY_NEW pobfactoryreturn), porigin_throw, n_exception) = eps'),
  ('only exhausted contour and matching published native result can throw',r'pobfactoryreturn_final.CONTOUR.CURSOR = |pobfactoryreturn_final.CONTOUR.CALLS| /\ S_ready.RESULT = KNOWN (POBJECT n_exception) /\ ~$ob_object_factory_value_frames(S_ready.DESTRUCTION.FRAMES, pobfactoryreturn_final) /\ $ob_object_factory_capture(S_ready, pfunction_native, (OBJECT_FACTORY_RETURNED pobfactoryreturn_final), porigin_throw, n_exception) = (OBJECT_FACTORY_THROW pobfactoryreturn_final) /\ $ob_object_factory_capture(S_ready[.RESULT = KNOWN (POBJECT n_object)], pfunction_native, (OBJECT_FACTORY_RETURNED pobfactoryreturn_final), porigin_throw, n_exception) = eps /\ $ob_object_native_source(S_active) = (OBJECT_FACTORY_THROW pobfactoryreturn_final) /\ $heap_count(HOBJECT n_exception, $machine_roots(S_active)) = 1 /\ $heap_count(HOBJECT n_object, $machine_roots(S_active)) = 2'),
  ('zero budget preserves return owner metadata and events',r'S_budget.COMPLETION = BUDGET /\ S_budget.TODO = S_return_0.TODO /\ S_budget.CURRENT = S_return_0.CURRENT /\ S_budget.FRAMES = S_return_0.FRAMES /\ S_budget.ALLOCATIONS = S_return_0.ALLOCATIONS /\ S_budget.GC = S_return_0.GC /\ S_budget.EVENTS = S_return_0.EVENTS'),
  ('actual produced returned and pending states are publicly valid',public('S_born')+' /\\ '+public('S_ready')+' /\\ '+public('S_active')),
 ]
 if edges==3:
  c += [('recursive equal contexts consume positions rather than origin identities',r'S_return_0.CURRENT = S_one_0.CURRENT /\ pcallcontext_0.FUNCTION = pcallcontext_1.FUNCTION /\ pframe_0.ORIGIN = pframe_1.ORIGIN /\ pobfactoryreturn_after_0.CONTOUR.CURSOR = 1 /\ pobfactoryreturn_after_1.CONTOUR.CURSOR = 2 /\ |S_one_0.FRAMES| = $(|S_return_0.FRAMES| - 1) /\ |S_one_1.FRAMES| = $(|S_return_1.FRAMES| - 1)')]
 return b,c
def fatal(path,edges):
 line,message=(14,'E') if edges==2 else (13,'R')
 frames=[(10,'make'),(6,'bridge')] if edges==2 else [(11,'recur'),(11,'recur'),(6,'recur')]
 trace=''.join(f'#{i} {path}({call}): {name}()\n' for i,(call,name) in enumerate(frames))
 return (f'Fatal error: Uncaught Exception: {message} in {path}:{line}\nStack trace:\n'+trace+f'#{len(frames)} [internal function]: T->__toString()\n#{len(frames)+1} {{main}}\n  thrown in {path} on line {line}\n').encode()
def report_assertions(program,path,edges):
 b=pipeline(program,path,edges)+[
  'S_exit_found = $fr_seek(S_active, 3, 512)',r'S_exit_found.COMPLETION = NORMAL \/ S_exit_found.COMPLETION = BUDGET',
  'S_exit = S_exit_found[.COMPLETION = NORMAL]',
  'S_exit.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (OUTPUT_FINAL_OBJECT_CV pobobjectreturn) :: ptask_tail*',
  'S_report_found = $drive_steps(S_exit, 1)','S_report_found.COMPLETION = BUDGET',
  'S_report = S_report_found[.COMPLETION = NORMAL]',
  'S_report.TODO = [OUTPUT_FINAL_PENDING pobdeactivate n_exception true]',
  'S_retired_found = $fr_seek(S_report, 4, 512)',r'S_retired_found.COMPLETION = NORMAL \/ S_retired_found.COMPLETION = BUDGET',
  'S_retired = S_retired_found[.COMPLETION = NORMAL]',
  'S_retired.DESTRUCTION.ABANDONED = [pdestructioncleanup]',
  'pobobjectreturn_returned = pobobjectreturn[.SOURCE = (OBJECT_FACTORY_RETURNED pobfactoryreturn_final)]',
  'pobobjectreturn_partial = pobobjectreturn[.SOURCE = (OBJECT_FACTORY_THROW pobfactoryreturn_after_0)]',
  'pdestructioncleanup_returned = pdestructioncleanup[.SOURCE = OUTPUT_FINAL_OBJECT_THROW pobobjectreturn_returned pobdeactivate pobfactoryreturn.RETURN n_exception]',
  'pdestructioncleanup_partial = pdestructioncleanup[.SOURCE = OUTPUT_FINAL_OBJECT_THROW pobobjectreturn_partial pobdeactivate pobfactoryreturn.RETURN n_exception]',
  'S_returned_receipt = S_retired[.DESTRUCTION.ABANDONED = [pdestructioncleanup_returned]]',
  'S_partial_receipt = S_retired[.DESTRUCTION.ABANDONED = [pdestructioncleanup_partial]]',
 ]
 c=[
  ('only original native C0 reports after every factory VALUE carrier has left',r'$ob_object_final_cv_ready(S_exit, pobobjectreturn, pdestructionframe, n_exception) /\ pdestructionframe.FUNCTION = pfunction_native.ORIGIN /\ pdestructionframe.FUNCTION =/= pfunction_leaf.ORIGIN /\ S_exit.CURRENT = eps /\ S_exit.FRAMES = eps /\ S_exit.ORIGIN = eps /\ ~$ob_object_factory_value_frames(S_exit.DESTRUCTION.FRAMES, pobfactoryreturn_final) /\ $heap_count(HOBJECT n_object, $machine_roots(S_exit)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_exit)) = 1'),
  ('fatal rendering preserves leaf creation line and complete original return contour',r'S_report.EVENTS = [OUTPUT ([80]), STDERR '+runner.bytes_expr(fatal(path,edges))+r'] /\ $throwable_field(S_report, n_exception, "previous") = PNULL /\ $heap_count(HOBJECT n_object, $machine_roots(S_report)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_report)) = 1'),
  ('retired receipt retains normalized source fact without becoming an object owner',r'~((HOBJECT n_exception) <- S_retired.ALLOCATIONS) /\ $heap_count(HOBJECT n_exception, $machine_roots(S_retired)) = 0 /\ $heap_count(HOBJECT n_object, $machine_roots(S_retired)) = 2 /\ $eager_cleanup_valid(S_retired, pdestructioncleanup) /\ '+public('S_retired')),
  ('returned phase and partial contour cannot impersonate the completed report receipt',r'~$eager_cleanup_valid(S_returned_receipt, pdestructioncleanup_returned) /\ ~$eager_cleanup_valid(S_partial_receipt, pdestructioncleanup_partial)'),
 ]
 return b,c
def cleanup_assertions(program,path,edges=2):
 b=pipeline(program,path,2)+[
  'S_one_1.DESTRUCTION.FRAMES = pdestructionframe_bridge :: pdestructionframe_tail*',
  'pdestructionframe_duplicate = pdestructionframe_bridge',
  'S_duplicate = S_one_1[.DESTRUCTION.FRAMES = [pdestructionframe_bridge, pdestructionframe_duplicate]]',
  'S_early_result = S_one_1[.RESULT = KNOWN (POBJECT n_exception)]',
  'S_bad_ready = S_ready[.DESTRUCTION.FRAMES = [pdestructionframe_bridge]]',
 ]
 c=[
  ('intermediate bridge has partial returned provenance before its own return',r'$ob_object_native_source(S_return_1) = (OBJECT_FACTORY_RETURNED pobfactoryreturn_after_0) /\ pobfactoryreturn_after_0.CONTOUR.CURSOR = 1 /\ $(pobfactoryreturn_after_0.CONTOUR.CURSOR < |pobfactoryreturn_after_0.CONTOUR.CALLS|) /\ $heap_count(HOBJECT n_exception, $machine_roots(S_return_1)) = 1'),
  ('real intermediate cleanup carries F under departed bridge FUNCTION',r'S_one_1.RESULT = KNOWN PNULL /\ pdestructionframe_bridge.VALUE = KNOWN (POBJECT n_exception) /\ pdestructionframe_bridge.PENDING = eps /\ pdestructionframe_bridge.FUNCTION = pfunction_1.ORIGIN /\ pdestructionframe_bridge.FUNCTION =/= pfunction_leaf.ORIGIN /\ $ob_object_factory_carrier(S_one_1, pfunction_1, pobfactoryreturn_after_0) /\ $heap_count(HOBJECT n_exception, $machine_roots(S_one_1)) = 1 /\ '+public('S_one_1')),
  ('wrong departed FUNCTION duplicate VALUE and simultaneous RESULT refuse carrier proof',r'~$ob_object_factory_carrier(S_one_1, pfunction_leaf, pobfactoryreturn_after_0) /\ ~$ob_object_factory_carrier(S_duplicate, pfunction_1, pobfactoryreturn_after_0) /\ ~$ob_object_factory_carrier(S_early_result, pfunction_1, pobfactoryreturn_after_0)'),
  ('all-contour residual VALUE prevents final native capture',r'$ob_object_factory_value_frames(S_bad_ready.DESTRUCTION.FRAMES, pobfactoryreturn_final) /\ $ob_object_factory_capture(S_bad_ready, pfunction_native, (OBJECT_FACTORY_RETURNED pobfactoryreturn_final), porigin_throw, n_exception) = eps'),
  ('intermediate destructor warning precedes same-result publication and actual throw',r'S_ready.EVENTS = [OUTPUT ([80]), WARNING ($ptascii("missing")) 3] /\ S_ready.RESULT = KNOWN (POBJECT n_exception) /\ S_ready.DESTRUCTION.FRAMES = eps /\ $heap_count(HOBJECT n_exception, $machine_roots(S_ready)) = 1 /\ $ob_object_native_source(S_active) = (OBJECT_FACTORY_THROW pobfactoryreturn_final) /\ '+public('S_active')),
 ]
 return b,c
def override_assertions(program,path,edges=2):
 b=birth(program,path)+[
  'S_leaf_found = $fc_seek_return(S_born, 512)',r'S_leaf_found.COMPLETION = NORMAL \/ S_leaf_found.COMPLETION = BUDGET',
  'S_leaf = S_leaf_found[.COMPLETION = NORMAL]',
  'S_first_found = $drive_steps(S_leaf, 1)','S_first_found.COMPLETION = BUDGET',
  'S_first = S_first_found[.COMPLETION = NORMAL]',
  '$ob_object_native_source(S_first) = (OBJECT_FACTORY_RETURNED pobfactoryreturn_partial)',
  'S_override_found = $fr_seek(S_first, 6, 512)',r'S_override_found.COMPLETION = NORMAL \/ S_override_found.COMPLETION = BUDGET',
  'S_override = S_override_found[.COMPLETION = NORMAL]',
  'S_override.TODO = [RETURN_UNWIND (KNOWN pvalue_h) porigin_override?]',
  'S_override.FRAMES = pframe_bridge :: pframe_tail*',
  'S_handoff_found = $drive_steps(S_override, 1)','S_handoff_found.COMPLETION = BUDGET',
  'S_handoff = S_handoff_found[.COMPLETION = NORMAL]',
  'S_scalar_found = $fr_seek(S_handoff, 7, 512)',r'S_scalar_found.COMPLETION = NORMAL \/ S_scalar_found.COMPLETION = BUDGET',
  'S_scalar = S_scalar_found[.COMPLETION = NORMAL]',
  'S_scalar.TODO = (THROW_VALUE porigin_scalar z_scalar) :: ptask_scalar*',
 ]
 c=[
  ('actual leaf return hands F to intermediate bridge with unexhausted RETURNED cursor',r'pobfactoryreturn_partial.CONTOUR.CURSOR = 1 /\ |pobfactoryreturn_partial.CONTOUR.CALLS| = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_first)) = 1 /\ $ob_object_source_pending($ob_object_native_source(S_first)) = eps'),
  ('intermediate finally override consumes F and clears partial receipt before retirement',r'$string_bytes(pvalue_h) = ($ptascii("H")) /\ ~((HOBJECT n_exception) <- S_override.ALLOCATIONS) /\ $heap_count(HOBJECT n_exception, $machine_roots(S_override)) = 0 /\ $ob_object_native_source(S_override) = eps /\ '+public('S_override')),
  ('actual normal bridge return restores native context without stale F authority',r'S_handoff.CURRENT = pframe_bridge.CONTEXT /\ S_handoff.ORIGIN = pframe_bridge.ORIGIN /\ S_handoff.FRAMES = pframe_tail* /\ $ob_object_native_source(S_handoff) = eps /\ $heap_count(HOBJECT n_exception, $machine_roots(S_handoff)) = 0 /\ $heap_count(HOBJECT n_object, $machine_roots(S_handoff)) = 2 /\ '+public('S_handoff')),
  ('later scalar throw frontier retains H and cannot recover retired factory certificate',r'S_scalar.EVENTS = [OUTPUT ([80])] /\ $ob_object_native_source(S_scalar) = eps /\ $ob_object_factory_capture(S_scalar, pfunction_native, eps, porigin_scalar, n_exception) = eps /\ '+public('S_scalar')),
 ]
 return b,c
CATCH=sources.CASES['factory-contour-bridge'].replace(b'throw bridge();',b"try { throw bridge(); } catch (Exception $e) { return 'H'; }")
def catch_assertions(program,path,edges=2):
 b=pipeline(program,path,2)+[
  'S_catch_found = $fr_seek(S_active, 5, 512)',r'S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET',
  'S_catch = S_catch_found[.COMPLETION = NORMAL]',
  'S_catch.TODO = (CATCH_BIND porigin_try n_index n_exception) :: ptask_catch*',
 ]
 c=[
  ('all factory returns precede actual native throwing and catch',r'$ob_object_native_source(S_active) = (OBJECT_FACTORY_THROW pobfactoryreturn_final) /\ pobfactoryreturn_final.CONTOUR.CURSOR = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_active)) = 1'),
  ('native catch clears receipt while real catch task still owns F',r'$ob_object_native_source(S_catch) = eps /\ $task_nodes(CATCH_BIND porigin_try n_index n_exception) = [HOBJECT n_exception] /\ $heap_count(HOBJECT n_exception, $machine_roots(S_catch)) = 1 /\ $heap_count(HOBJECT n_object, $machine_roots(S_catch)) = 2 /\ S_catch.EVENTS = [OUTPUT ([80])] /\ '+public('S_catch')),
 ]
 return b,c
NATIVE_LOCAL=previous.NATIVE_LOCAL.replace(b'throw make();',b'throw bridge();').replace(b'function make()',b'function bridge() { return make(); }\nfunction make()')
def native_local_assertions(program,path,edges=2):
 b=pipeline(program,path,2)+[
  '$ob_object_final_local_context(S_active) = ((pobobjectreturn, pdestructorcall, pobobjectsource?, ptask_native*))',
  'pdestructorcall.FRAME = (pdestructionframe_outer)',
  'pdestructionframe_outer.PENDING = (n_old)',
  'S_exit_found = $fr_seek(S_active, 8, 512)',r'S_exit_found.COMPLETION = NORMAL \/ S_exit_found.COMPLETION = BUDGET',
  'S_exit = S_exit_found[.COMPLETION = NORMAL]',
  'S_exit.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: ptask_return*',
 ]
 owners=lambda s:f'$heap_count(HOBJECT pobobjectreturn.OBJECT, $machine_roots({s})) = 2 /\\ $heap_count(HOBJECT pdestructorcall.OBJECT, $machine_roots({s})) = 2 /\\ $heap_count(HOBJECT n_old, $machine_roots({s})) = 1 /\\ $heap_count(HOBJECT n_exception, $machine_roots({s})) = 1'
 c=[
  ('factory contour exhausts through two real returns before local native throw',r'$ob_object_native_source(S_one_0) = (OBJECT_FACTORY_RETURNED pobfactoryreturn_after_0) /\ $ob_object_native_source(S_one_1) = (OBJECT_FACTORY_RETURNED pobfactoryreturn_final) /\ pobfactoryreturn_after_0.CONTOUR.CURSOR = 1 /\ pobfactoryreturn_final.CONTOUR.CURSOR = 2 /\ S_ready.RESULT = KNOWN (POBJECT n_exception) /\ ~$ob_object_factory_value_frames(S_ready.DESTRUCTION.FRAMES, pobfactoryreturn_final)'),
  ('local factory pending preserves distinct old E outer cast and selected destructor guards',r'pdestructorcall.OBJECT = n_object /\ n_exception =/= n_old /\ $ob_object_source_pending(pobobjectsource?) = ((pobfactoryreturn.RETURN,n_exception)) /\ $throwable_field(S_active, n_exception, "previous") = PNULL /\ '+owners('S_active')),
  ('actual local native pending state is publicly valid',public('S_active')),
  ('report authority belongs to local destructor C0 after both forwarding frames leave',r'$ob_object_final_local_ready(S_exit, pobobjectreturn, pdestructorcall, pobfactoryreturn.RETURN, n_exception, pdestructionframe, ptask_return*) /\ pdestructionframe.FUNCTION = pfunction_native.ORIGIN /\ pdestructionframe.FUNCTION =/= pfunction_leaf.ORIGIN /\ pdestructionframe.FUNCTION =/= pfunction_1.ORIGIN /\ S_exit.CURRENT = eps /\ S_exit.FRAMES = eps /\ '+owners('S_exit')),
  ('native destructor C0 preserves complete public ownership',public('S_exit')),
 ]
 return b,c
def render(bindings,checks):
 return PREFIX+'\ndec $main() : bool*\ndef $main() = ['+', '.join('('+x+')' for _,x in checks)+']\n'+''.join('  -- if '+x+'\n' for x in bindings)
def fingerprint():
 return {p:support.common.sha(ROOT/p) for p in ('spec/semantics/30-storage.watsup','spec/semantics/456-output-object-returns.watsup','spec/semantics/257-request-destructors.watsup','spec/semantics/modules.json','tests/semantics/output_factory_contour_sources.py','tests/semantics/output_factory_contour_review_state.py','tests/semantics/output_factory_return_review_state.py','tests/semantics/_build/default/numeric_runner.exe','_build/default/adapter/main.exe','.tools/php/bin/php')}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);p.add_argument('--select',choices=('bridge','recursive','all'),default='all');p.add_argument('--stage',choices=('provenance','report','cleanup','override','catch','native_local'),default='provenance');p.add_argument('--native-root',type=Path);p.add_argument('--prepare-only',action='store_true');args=p.parse_args()
 out=args.output or Path(tempfile.mkdtemp(prefix='factory-contour-review-'));out.mkdir(parents=True,exist_ok=True)
 report={'revision':support.subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD']).decode().strip(),'before':fingerprint(),'records':[],'passed':False,'native_agreement_credit':0,'cap_seconds':300,'stage':args.stage}
 try:
  modules=json.loads((ROOT/'spec/semantics/modules.json').read_text())
  chosen=list(sources.CASES.items()) if args.stage in ('provenance','report') else [(args.stage,{'cleanup':sources.CLEANUP,'override':sources.OVERRIDE,'catch':CATCH,'native_local':NATIVE_LOCAL}[args.stage])]
  for index,(name,source) in enumerate(chosen):
   short=('bridge','recursive')[index]
   if args.select not in ('all',short):continue
   d=out/short;d.mkdir();frozen=args.native_root and args.stage in ('provenance','report');path=args.native_root/f'native-0{index+1}'/'source.php' if frozen else d/'source.php'
   if frozen:assert path.read_bytes()==source
   else:path.write_bytes(source)
   worker=Worker([str(ROOT/'.tools/php/bin/php'),'-n','-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],d/'frontend')
   try:parsed=worker.request({'op':'parse','source':base64.b64encode(source).decode()})
   finally:worker.close()
   adapter=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],d/'adapter')
   try:checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
   finally:adapter.close()
   fn={'provenance':provenance,'report':report_assertions,'cleanup':cleanup_assertions,'override':override_assertions,'catch':catch_assertions,'native_local':native_local_assertions}[args.stage]
   bindings,checks=fn(checked['fixture'],path,index+2);fixture=d/'state.watsup';fixture.write_text(render(bindings,checks))
   rec={'case':name,'checks':[x for x,_ in checks],'fixture_sha256':support.common.sha(fixture),'passed':False};report['records'].append(rec)
   if args.prepare_only:continue
   start=time.monotonic();result=support.common.run([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),'--sl',*[str(ROOT/x) for x in modules],str(fixture)],d,'state',300)
   values=re.findall(rb'\b(?:true|false)\b',result.stdout);rec.update(seconds=round(time.monotonic()-start,3),exit=result.returncode,results=[x==b'true' for x in values])
   assert not re.sub(rb'true|false|[\[\](),;\s]',b'',result.stdout),(result.stdout,result.stderr)
   assert result.returncode==0 and not result.stderr and values==[b'true']*len(checks),(result.returncode,result.stderr.decode(errors='replace'),rec['results'])
   rec['passed']=True;print(short,True,rec['seconds'],flush=True)
  assert report['records'],'no fixture selected';report['passed']=not args.prepare_only
 except BaseException as e:
  report['failure']={'type':type(e).__name__,'message':str(e)};raise
 finally:
  report['after']=fingerprint();report['stable']=report['before']==report['after'];report['passed']=report['passed'] and report['stable'];(out/('preparation.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
