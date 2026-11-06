#!/usr/bin/env python3
"""Source-reached helper CV publication, exceptional restores and clearing."""
import argparse,base64,json,os,re,tempfile,time
from pathlib import Path
from recorded_worker import Worker
import output_factory_helper_cv_sources as sources
import output_factory_cv_review_state as shared
import output_deprecation_warning_review_state as runner
import output_object_conversion_review_sources as support

ROOT=support.ROOT
public=shared.public
seek=shared.seek
step=shared.step
PREFIX=shared.previous.PREFIX+r'''
dec $ccv_phase(pstate, nat) : bool
def $ccv_phase(S, 0) = true
  -- if S.TODO = (WRITE_NAME preqbytes z) :: ptask_tail*
  -- if S.RESULT = KNOWN (POBJECT n)
  -- if S.OBJECTS[n] = THROWABLE pthrowable
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = pcallcontext.FUNCTION
def $ccv_phase(S, 1) = true
  -- if S.TODO = DISCARD :: ptask_tail*
  -- if S.RESULT = KNOWN PNULL
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = pcallcontext.FUNCTION
def $ccv_phase(S, 2) = true
  -- if S.TODO = (EVAL (NExprVariable phpType32 metadata)) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = pcallcontext.FUNCTION
def $ccv_phase(S, 3) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = pcallcontext.FUNCTION
def $ccv_phase(S, 4) = true
  -- if S.TODO = [THROW_SEARCH n]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = pcallcontext.FUNCTION
def $ccv_phase(S, 5) = true
  -- if S.TODO = (WRITE_NAME preqbytes z) :: ptask_tail*
  -- if S.RESULT = KNOWN (POBJECT n)
  -- if S.OBJECTS[n] = THROWABLE pthrowable
def $ccv_phase(S, 6) = true
  -- if S.TODO = DISCARD :: ptask_tail*
  -- if S.RESULT = KNOWN PNULL
def $ccv_phase(S, 7) = true
  -- if S.TODO = (WRITE_NAME preqbytes z) :: ptask_tail*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("H"))
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = pcallcontext.FUNCTION
def $ccv_phase(S, 8) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = pcallcontext.FUNCTION
def $ccv_phase(S, 9) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
def $ccv_phase(S, 10) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_tail*
def $ccv_phase(S, n) = false -- otherwise
dec $ccv_seek(pstate, nat, nat) : pstate
def $ccv_seek(S, n_phase, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $ccv_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $ccv_phase(S, n_phase)
def $ccv_seek(S, n_phase, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$ccv_phase(S, n_phase)
def $ccv_seek(S, n_phase, n) = $ccv_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$ccv_phase(S, n_phase) /\ $(n > 0)
dec $ccv_writes(pstate, nat) : pstate*
def $ccv_writes(S, 0) = eps
def $ccv_writes(S, n) = [S_write, S_written, S_discard, S_dropped] ++ $ccv_writes(S_dropped, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if S_write_found = $ccv_seek(S, 0, 1024)
  -- if S_write_found.COMPLETION = NORMAL \/ S_write_found.COMPLETION = BUDGET
  -- if S_write = S_write_found[.COMPLETION = NORMAL]
  -- if S_written_found = $drive_steps(S_write, 1)
  -- if S_written_found.COMPLETION = BUDGET
  -- if S_written = S_written_found[.COMPLETION = NORMAL]
  -- if S_discard_found = $ccv_seek(S_written, 1, 64)
  -- if S_discard_found.COMPLETION = NORMAL \/ S_discard_found.COMPLETION = BUDGET
  -- if S_discard = S_discard_found[.COMPLETION = NORMAL]
  -- if S_dropped_found = $drive_steps(S_discard, 1)
  -- if S_dropped_found.COMPLETION = BUDGET
  -- if S_dropped = S_dropped_found[.COMPLETION = NORMAL]
'''
CONTROLS={'sibling':sources.SIBLING,'rebind':sources.REBIND,'catch':sources.CATCH,
 'cleanup':sources.CLEANUP,'recipient-byref':sources.RECIPIENT_BYREF,
 'recursive':sources.RECURSIVE,'override':sources.OVERRIDE,'native-local':sources.NATIVE_LOCAL}

def initial(program,path):
 return ['S_initial = $php_file_run('+program+', 0, '+runner.bytes_expr(os.fsencode(path))+', '+runner.bytes_expr(os.fsencode(path.parent))+')']

def primary(program,path):
 b=initial(program,path)+[
  '[S_write, S_written, S_discard, S_dropped] = $ccv_writes(S_initial, 1)',
  'S_write.TODO = (WRITE_NAME preqbytes_name z_write) :: ptask_write*',
  'S_write.RESULT = KNOWN (POBJECT n_exception)',
  'S_write.CURRENT = (pcallcontext_helper)',
  'pcallcontext_helper.TARGET = pcallcontext_helper.FUNCTION',
  '$function_at($all_functions(S_write),pcallcontext_helper.FUNCTION) = (pfunction_helper)',
  '$ob_object_source_active($ob_object_native_source(S_write)) = (OBJECT_CV_RETURN pobcvreturn)',
  '$lookup(S_written.ENV,preqbytes_name) = (n_cell)',
  '$ob_object_cv_lookup_at($ob_object_cv_associations($ob_object_native_source(S_written)),1,preqbytes_name) = (pobcvassoc)']
 b += seek('S_throw','S_dropped',3,128)+[
  'S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_throw*',
  'S_throw.RESULT = VARIABLE preqbytes_name z_read']
 b += step('S_pending','S_throw')+['S_pending.TODO = (THROW_SEARCH n_exception) :: ptask_throw*']
 b += seek('S_leave','S_pending',4,128)+[
  'S_leave.TODO = [THROW_SEARCH n_exception]',
  'S_leave.FRAMES = pframe_call :: pframe_tail*',
  'pframe_call.CONTEXT = (pcallcontext_native)',
  'pcallcontext_native.TARGET = METHOD_TARGET n_object pcallcontext_native.FUNCTION',
  '$function_at($all_functions(S_leave),pcallcontext_native.FUNCTION) = (pfunction_native)']
 b += step('S_restored','S_leave')+[
  'S_expected = $ob_object_call_capture(S_leave[.FRAMES = pframe_tail*],(OBJECT_CV_THROW pobcvassoc porigin_throw 1))']
 c=[('completed factory receipt stops its normal cursor at helper FRAME1',r'pobcvreturn.FRAME = 1 /\ $ob_object_cv_end(pobcvreturn) = 1 /\ |pobcvreturn.CONTOUR.CALLS| = 2 /\ pobcvreturn.CONTOUR.CURSOR = 1 /\ pobcvreturn.FUNCTION =/= pfunction_helper.ORIGIN /\ pobcvreturn.BIRTH.OBJECT = n_exception /\ $ob_object_ctor_fact_live(S_write,pobcvreturn.BIRTH)'),
  ('actual write commits the same result to private helper cell F1',r'pobcvassoc.FACTORY = pobcvreturn /\ pobcvassoc.NAME = preqbytes_name /\ pobcvassoc.CELL = n_cell /\ S_written.RESULT = KNOWN PNULL /\ S_written.STORE[n_cell] = DEFINED (POBJECT n_exception) /\ $heap_count(HCELL n_cell,$machine_roots(S_written)) = 1 /\ $heap_owners($heap_graph(S_written),HOBJECT n_exception) = 1 /\ $ob_object_cv_lookup($ob_object_cv_associations($ob_object_native_source(S_written)),preqbytes_name) = eps'),
  ('NULL discard retains indirect F1 and the scoped helper association',r'S_dropped.RESULT = KNOWN PNULL /\ $heap_count(HOBJECT n_exception,$machine_roots(S_dropped)) = 0 /\ $heap_owners($heap_graph(S_dropped),HOBJECT n_exception) = 1 /\ $ob_object_cv_lookup_at($ob_object_cv_associations($ob_object_native_source(S_dropped)),1,preqbytes_name) = (pobcvassoc)'),
  ('genuine delayed VARIABLE operand is unchanged by zero budget',r'S_throw.RESULT = VARIABLE preqbytes_name z_read /\ $heap_owners($heap_graph(S_throw),HOBJECT n_exception) = 1 /\ $drive_steps(S_throw,0) = S_throw[.COMPLETION = BUDGET]'),
  ('one real THROW publishes helper pending F2 without native report authority',r'S_pending.RESULT = KNOWN PNULL /\ $ob_object_source_active($ob_object_native_source(S_pending)) = (OBJECT_CV_THROW pobcvassoc porigin_throw 0) /\ $ob_object_cv_pending(S_pending) /\ $ob_object_source_thrown($ob_object_native_source(S_pending)) = eps /\ $heap_owners($heap_graph(S_pending),HOBJECT n_exception) = 2 /\ $heap_count(HOBJECT n_object,$machine_roots(S_pending)) = 2'),
  ('one exact VM pop advances only the exceptional cursor and restores native caller',r'S_restored.CURRENT = pframe_call.CONTEXT /\ S_restored.FRAMES = S_expected.FRAMES /\ S_restored.ORIGIN = pframe_call.ORIGIN /\ S_restored.CONSTCONTEXT = pframe_call.CONSTCONTEXT /\ S_leave.CURRENT = (pcallcontext_helper) /\ $ob_object_source_active($ob_object_native_source(S_restored)) = (OBJECT_CV_THROW pobcvassoc porigin_throw 1) /\ pobcvassoc.FACTORY.CONTOUR.CURSOR = 1 /\ $ob_object_source_thrown($ob_object_native_source(S_restored)) = ((pobcvreturn.RETURN,pobcvreturn.BIRTH))'),
  ('real helper CV release leaves pending F1 and keeps native T2 and creation fields',r'S_restored.DESTRUCTION.FRAMES = eps /\ ~((HCELL n_cell) <- S_restored.ALLOCATIONS) /\ $heap_owners($heap_graph(S_restored),HOBJECT n_exception) = 1 /\ $heap_count(HOBJECT n_object,$machine_roots(S_restored)) = 2 /\ S_restored.CVS = pfunction_native.CVS /\ $throwable_field(S_restored,n_exception,"line") = PINT 13 /\ $throwable_field(S_restored,n_exception,"previous") = PNULL /\ S_restored.EVENTS = [OUTPUT ([80])]'),
  ('pivotal written pending and restored states remain publicly valid',' /\\ '.join(public(s) for s in ('S_written','S_pending','S_restored')))]
 return b,c

def report_assertions(program,path):
 b,_=primary(program,path)
 b += seek('S_exit','S_restored',3,helper='fr')+[
  'S_exit.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (OUTPUT_FINAL_OBJECT_CV pobobjectreturn) :: ptask_exit*']
 b += step('S_report','S_exit')+['S_report.TODO = [OUTPUT_FINAL_PENDING pobdeactivate n_exception true]']
 b += seek('S_retired','S_report',4,helper='fr')+[
  'S_retired.DESTRUCTION.ABANDONED = [pdestructioncleanup]',
  'pobcvassoc_wrongnormal = pobcvassoc[.FACTORY = pobcvassoc.FACTORY[.CONTOUR = pobcvassoc.FACTORY.CONTOUR[.CURSOR = 2]]]']
 c=[('only original native C0 reports with pending1 and cast2 after helper retirement',r'$ob_object_final_cv_ready(S_exit,pobobjectreturn,pdestructionframe,n_exception) /\ pdestructionframe.FUNCTION = pfunction_native.ORIGIN /\ pdestructionframe.FUNCTION =/= pfunction_helper.ORIGIN /\ pdestructionframe.FUNCTION =/= pobcvreturn.FUNCTION /\ S_exit.CURRENT = eps /\ S_exit.FRAMES = eps /\ ~((HCELL n_cell) <- S_exit.ALLOCATIONS) /\ $heap_owners($heap_graph(S_exit),HOBJECT n_exception) = 1 /\ $heap_count(HOBJECT n_object,$machine_roots(S_exit)) = 2 /\ '+public('S_exit')),
  ('fatal bytes keep actual creation line and complete make/fail/internal trace','S_report.EVENTS = [OUTPUT ([80]), STDERR '+runner.bytes_expr(shared.fatal(path,13,[(10,'make'),(6,'fail')]))+r'] /\ S_report.EXITSTATUS = 255 /\ $throwable_field(S_report,n_exception,"previous") = PNULL'),
  ('retired nonowning receipt validates with no Exception root and real cast2',r'~((HOBJECT n_exception) <- S_retired.ALLOCATIONS) /\ $heap_count(HOBJECT n_exception,$machine_roots(S_retired)) = 0 /\ $heap_count(HOBJECT n_object,$machine_roots(S_retired)) = 2 /\ $eager_cleanup_valid(S_retired,pdestructioncleanup) /\ $task_nodes(pdestructioncleanup.SOURCE) = eps /\ '+public('S_retired')),
  ('partial skipped and wrong-normal cursors cannot grant native report authority',r'$ob_object_source_thrown((OBJECT_CV_THROW pobcvassoc porigin_throw 0)) = eps /\ $ob_object_source_thrown((OBJECT_CV_THROW pobcvassoc porigin_throw 2)) = eps /\ $ob_object_source_thrown((OBJECT_CV_THROW pobcvassoc_wrongnormal porigin_throw 1)) = eps /\ $ob_object_source_thrown(pobobjectreturn.SOURCE) = ((pobcvreturn.RETURN,pobcvreturn.BIRTH))')]
 return b,c

def refusals(program,path):
 b,_=primary(program,path)
 b += ['PhpStep: S_throw ~> S_php',
  'S_after_throw = $throwable_transition(S_throw,S_php)',
  'pobcvassoc_frame0 = pobcvassoc[.FACTORY = pobcvassoc.FACTORY[.FRAME = 0]]',
  'pobcvassoc_frame2 = pobcvassoc[.FACTORY = pobcvassoc.FACTORY[.FRAME = 2]]',
  'pobcvassoc_normal = pobcvassoc[.FACTORY = pobcvassoc.FACTORY[.CONTOUR = pobcvassoc.FACTORY.CONTOUR[.CURSOR = 2]]]',
  'pobcvassoc_cell = pobcvassoc[.CELL = 999999]',
  'pobcvassoc_name = pobcvassoc[.NAME = $ptascii("foreign")]',
  'S_owned = S_throw[.TODO = S_throw.TODO ++ [THROW_SEARCH n_exception]]',
  'S_after_owned = S_after_throw[.TODO = S_after_throw.TODO ++ [THROW_SEARCH n_exception]]',
  'S_owned_read = $resolve_at(S_owned,S_owned.RESULT,z_throw)',
  'S_raw_restore = $restore_frame_raw(S_leave)',
  'S_hook = $destructor_frame_restore(S_leave,S_raw_restore)',
  'S_no_pop = S_raw_restore[.FRAMES = S_leave.FRAMES]',
  'S_skip_pop = S_raw_restore[.FRAMES = eps]',
  'S_wrong_current = S_raw_restore[.CURRENT = S_leave.CURRENT]',
  'S_wrong_pending = S_leave[.TODO = [THROW_SEARCH n_object]]']
 c=[('actual throw capture requires exact recipient FRAME and normal end',r'$ob_object_cv_throw(S_throw,S_after_throw,pobcvassoc,porigin_throw) /\ ~$ob_object_cv_throw(S_throw,S_after_throw,pobcvassoc_frame0,porigin_throw) /\ ~$ob_object_cv_throw(S_throw,S_after_throw,pobcvassoc_frame2,porigin_throw) /\ ~$ob_object_cv_throw(S_throw,S_after_throw,pobcvassoc_normal,porigin_throw)'),
  ('actual delayed read requires matching name cell and pending identity',r'~$ob_object_cv_throw(S_throw,S_after_throw,pobcvassoc_cell,porigin_throw) /\ ~$ob_object_cv_throw(S_throw,S_after_throw,pobcvassoc_name,porigin_throw) /\ ~$ob_object_cv_throw(S_throw,S_after_throw[.COMPLETION = THROWING n_object],pobcvassoc,porigin_throw)'),
  ('owned current tail refuses despite intact recipient cell and resolved transition',r'$tasks_nodes(S_owned.TODO) =/= eps /\ $ob_object_cv_recipient(S_owned) =/= eps /\ $ob_object_cv_cell(S_owned,pobcvassoc) /\ S_after_owned = S_owned_read[.COMPLETION = THROWING n_exception][.TODO = ptask_throw* ++ [THROW_SEARCH n_exception]] /\ ~$ob_object_cv_throw(S_owned,S_after_owned,pobcvassoc,porigin_throw)'),
  ('only exact real one-tail same-pending restoration can advance cursor',r'$ob_object_source_active($ob_object_native_source(S_hook)) = (OBJECT_CV_THROW pobcvassoc porigin_throw 1) /\ $destructor_frame_restore(S_leave,S_no_pop) = S_no_pop /\ $destructor_frame_restore(S_leave,S_skip_pop) = S_skip_pop /\ $destructor_frame_restore(S_leave,S_wrong_current) = S_wrong_current /\ $destructor_frame_restore(S_wrong_pending,S_raw_restore) = S_raw_restore')]
 return b,c

def writing(start,tag,frame):
 b=seek('S_write'+tag,start,5,1024)+[
  f'S_write{tag}.TODO = (WRITE_NAME preqbytes_name{tag} z_write{tag}) :: ptask_write{tag}*',
  f'S_write{tag}.RESULT = KNOWN (POBJECT n_exception{tag})',
  f'$ob_object_source_active($ob_object_native_source(S_write{tag})) = (OBJECT_CV_RETURN pobcvreturn{tag})']
 b += step('S_written'+tag,'S_write'+tag)+[
  f'$lookup(S_written{tag}.ENV,preqbytes_name{tag}) = (n_cell{tag})',
  f'$ob_object_cv_lookup_at($ob_object_cv_associations($ob_object_native_source(S_written{tag})),{frame},preqbytes_name{tag}) = (pobcvassoc{tag})']
 return b+seek('S_discard'+tag,'S_written'+tag,6,64)+step('S_dropped'+tag,'S_discard'+tag)

def throwing(start,tag,phase=3):
 return seek('S_throw'+tag,start,phase,128)+[
  f'S_throw{tag}.TODO = (THROW_VALUE porigin_throw{tag} z_throw{tag}) :: ptask_throw{tag}*',
  f'S_throw{tag}.RESULT = VARIABLE preqbytes_name{tag} z_read{tag}',
 ]+step('S_pending'+tag,'S_throw'+tag)+[
  f'S_pending{tag}.TODO = (THROW_SEARCH n_exception{tag}) :: ptask_throw{tag}*']

def restoring(start,tag):
 return seek('S_leave'+tag,start,4,128)+[
  f'S_leave{tag}.TODO = [THROW_SEARCH n_exception{tag}]',
  f'S_leave{tag}.FRAMES = pframe_call{tag} :: pframe_tail{tag}*',
 ]+step('S_restored'+tag,'S_leave'+tag)

def sibling_assertions(program,path):
 b=initial(program,path)+writing('S_initial','_native',0)+writing('S_dropped_native','_helper',1)
 b += throwing('S_dropped_helper','_helper')+restoring('S_pending_helper','_helper')
 b += seek('S_catch','S_restored_helper',5,helper='fr')+[
  'S_catch.TODO = (CATCH_BIND porigin_try n_index n_exception_helper) :: ptask_catch*']
 b += throwing('S_catch','_native',10)
 c=[('native and helper same-name CVs retain separate real cells and frame-scoped receipts',r'preqbytes_name_native = preqbytes_name_helper /\ n_cell_native =/= n_cell_helper /\ n_exception_native =/= n_exception_helper /\ pobcvreturn_native.FRAME = 0 /\ pobcvreturn_helper.FRAME = 1 /\ $ob_object_cv_lookup_at($ob_object_cv_associations($ob_object_native_source(S_dropped_helper)),0,preqbytes_name_native) = (pobcvassoc_native) /\ $ob_object_cv_lookup_at($ob_object_cv_associations($ob_object_native_source(S_dropped_helper)),1,preqbytes_name_helper) = (pobcvassoc_helper)'),
  ('actual helper pop and native catch preserve only the native row',r'S_restored_helper.CURRENT = pframe_call_helper.CONTEXT /\ $ob_object_source_active($ob_object_native_source(S_restored_helper)) = (OBJECT_CV_THROW pobcvassoc_helper porigin_throw_helper 1) /\ ~((HCELL n_cell_helper) <- S_restored_helper.ALLOCATIONS) /\ $ob_object_source_active($ob_object_native_source(S_catch)) = eps /\ $ob_object_cv_associations($ob_object_native_source(S_catch)) = [pobcvassoc_native] /\ $ob_object_cv_cell(S_catch,pobcvassoc_native) /\ '+public('S_catch')),
  ('later native throw selects its own surviving receipt',r'$ob_object_source_active($ob_object_native_source(S_pending_native)) = (OBJECT_CV_THROW pobcvassoc_native porigin_throw_native 0) /\ $heap_owners($heap_graph(S_pending_native),HOBJECT n_exception_native) = 2 /\ '+public('S_pending_native'))]
 return b,c

def rebind_assertions(program,path):
 b=initial(program,path)+writing('S_initial','_native',0)+writing('S_dropped_native','_helper',1)
 b += seek('S_rebind','S_dropped_helper',7)+[
  'S_rebind.TODO = (WRITE_NAME preqbytes_name_helper z_rebind) :: ptask_rebind*',
  'PhpStep: S_rebind ~> S_rebind_raw',
  'S_observed = $source_exception_transition(S_rebind,S_rebind_raw)']
 b += step('S_rebound','S_rebind')+seek('S_H','S_rebound',6,helper='fr')+[
  'S_H.FRAMES = pframe_H :: pframe_H_tail*',
  'pframe_H.CONTEXT = (pcallcontext_native)',
  'pcallcontext_native.TARGET = METHOD_TARGET n_object pcallcontext_native.FUNCTION']+step('S_H_restored','S_H')
 c=[('real helper H write removes its row before F retirement and keeps native sibling',r'$ob_object_cv_associations($ob_object_native_source(S_observed)) = [pobcvassoc_native] /\ (HOBJECT n_exception_helper) <- S_observed.ALLOCATIONS /\ $heap_owners($heap_graph(S_observed),HOBJECT n_exception_helper) = 0 /\ ~((HOBJECT n_exception_helper) <- S_rebound.ALLOCATIONS) /\ $heap_owners($heap_graph(S_rebound),HOBJECT n_exception_native) = 1'),
  ('actual normal H restoration preserves the native row without helper provenance',r'S_H_restored.CURRENT = pframe_H.CONTEXT /\ $ob_object_source_active($ob_object_native_source(S_H_restored)) = eps /\ $ob_object_cv_associations($ob_object_native_source(S_H_restored)) = [pobcvassoc_native] /\ ~((HCELL n_cell_helper) <- S_H_restored.ALLOCATIONS) /\ $ob_object_cv_cell(S_H_restored,pobcvassoc_native) /\ $heap_count(HOBJECT n_object,$machine_roots(S_H_restored)) = 2 /\ '+public('S_H_restored'))]
 return b,c

def normal_assertions(program,path,override=False):
 b=initial(program,path)+writing('S_initial','_helper',1)+throwing('S_dropped_helper','_helper')
 if not override:
  b += seek('S_catch','S_pending_helper',8)+[
   'S_catch.TODO = (CATCH_BIND porigin_try n_index n_exception_helper) :: ptask_catch*']
 b += seek('S_H','S_pending_helper' if override else 'S_catch',6,helper='fr')+[
  'S_H.FRAMES = pframe_H :: pframe_H_tail*',
  'pframe_H.CONTEXT = (pcallcontext_native)',
  'pcallcontext_native.TARGET = METHOD_TARGET n_object pcallcontext_native.FUNCTION']+step('S_H_restored','S_H')
 c=[('normal H departure clears the selected active fact without reviving spent CV rows',r'$ob_object_cv_normal_active(S_H) = eps /\ $ob_object_cv_associations($ob_object_native_source(S_H)) = eps /\ $ob_object_source_active($ob_object_native_source(S_H_restored)) = eps /\ $ob_object_cv_associations($ob_object_native_source(S_H_restored)) = eps'),
  ('real H restore retires helper cells and F while preserving native cast owners',r'S_H_restored.CURRENT = pframe_H.CONTEXT /\ ~((HCELL n_cell_helper) <- S_H_restored.ALLOCATIONS) /\ ~((HOBJECT n_exception_helper) <- S_H_restored.ALLOCATIONS) /\ $heap_count(HOBJECT n_object,$machine_roots(S_H_restored)) = 2 /\ '+public('S_H_restored'))]
 if not override:
  c.insert(0,('genuine helper catch clears active provenance before normal restoration',r'$ob_object_source_active($ob_object_native_source(S_catch)) = eps /\ $ob_object_cv_associations($ob_object_native_source(S_catch)) = eps /\ '+public('S_catch')))
 else:
  c.insert(0,('finally override clears actual active provenance before H return while F remains cell-owned',r'$ob_object_source_active($ob_object_native_source(S_H)) = eps /\ $heap_count(HOBJECT n_exception_helper,$machine_roots(S_H)) = 0 /\ $heap_owners($heap_graph(S_H),HOBJECT n_exception_helper) = 1'))
 return b,c

def recursive_assertions(program,path):
 b=initial(program,path)+writing('S_initial','_outer',1)+writing('S_dropped_outer','_child',2)
 b += ['S_write_outer.CURRENT = (pcallcontext_outer)','S_write_child.CURRENT = (pcallcontext_child)']
 b += throwing('S_dropped_child','_child')+restoring('S_pending_child','_child')
 b += seek('S_catch','S_restored_child',8)+[
  'S_catch.TODO = (CATCH_BIND porigin_try n_index n_exception_child) :: ptask_catch*']
 b += throwing('S_catch','_outer')
 c=[('recursive equal-function equal-name activations keep FRAME1 and FRAME2 cells distinct',r'preqbytes_name_outer = preqbytes_name_child /\ n_cell_outer =/= n_cell_child /\ n_exception_outer =/= n_exception_child /\ pobcvreturn_outer.FRAME = 1 /\ pobcvreturn_child.FRAME = 2 /\ pcallcontext_outer.FUNCTION = pcallcontext_child.FUNCTION /\ $ob_object_cv_associations($ob_object_native_source(S_dropped_child)) = [pobcvassoc_child,pobcvassoc_outer]'),
  ('real child pop and parent catch preserve only the outer activation row',r'S_restored_child.CURRENT = pframe_call_child.CONTEXT /\ $ob_object_source_active($ob_object_native_source(S_restored_child)) = (OBJECT_CV_THROW pobcvassoc_child porigin_throw_child 1) /\ $ob_object_source_thrown($ob_object_native_source(S_restored_child)) = eps /\ pobcvassoc_child.FACTORY.CONTOUR.CURSOR = 1 /\ $heap_owners($heap_graph(S_restored_child),HOBJECT n_exception_outer) = 1 /\ ~((HCELL n_cell_child) <- S_restored_child.ALLOCATIONS) /\ $ob_object_source_active($ob_object_native_source(S_catch)) = eps /\ $ob_object_cv_associations($ob_object_native_source(S_catch)) = [pobcvassoc_outer] /\ $ob_object_cv_cell(S_catch,pobcvassoc_outer)'),
  ('later outer throw spends the surviving parent certificate',r'$ob_object_source_active($ob_object_native_source(S_pending_outer)) = (OBJECT_CV_THROW pobcvassoc_outer porigin_throw_outer 0) /\ $heap_owners($heap_graph(S_pending_outer),HOBJECT n_exception_outer) = 2 /\ '+public('S_pending_outer'))]
 return b,c

def cleanup_assertions(program,path):
 b,_=primary(program,path)
 b += seek('S_D','S_restored',9)+[
  'S_D.TODO = (DESTRUCTOR_ENTER pdestructorcall_D) :: ptask_D*',
  'S_D.DESTRUCTION.FRAMES = pdestructionframe_helper :: pdestructionframe_tail*']
 b += seek('S_exit','S_D',3,helper='fr')+[
  'S_exit.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (OUTPUT_FINAL_OBJECT_CV pobobjectreturn) :: ptask_exit*']
 c=[('helper e cell releases before later D while CURRENT is already native',r'S_D.CURRENT = pframe_call.CONTEXT /\ pdestructionframe_helper.FUNCTION = pfunction_helper.ORIGIN /\ pdestructionframe_helper.FUNCTION =/= pfunction_native.ORIGIN /\ ~((HCELL n_cell) <- S_D.ALLOCATIONS) /\ $heap_owners($heap_graph(S_D),HOBJECT n_exception) = 1 /\ $heap_count(HOBJECT n_object,$machine_roots(S_D)) = 2 /\ S_D.EVENTS = [OUTPUT ([80])]'),
  ('Warning3 precedes original native C0 without early cast release',r'S_exit.EVENTS = [OUTPUT ([80]), WARNING ($ptascii("missing")) 3] /\ $ob_object_final_cv_ready(S_exit,pobobjectreturn,pdestructionframe,n_exception) /\ pdestructionframe.FUNCTION = pfunction_native.ORIGIN /\ $heap_owners($heap_graph(S_exit),HOBJECT n_exception) = 1 /\ $heap_count(HOBJECT n_object,$machine_roots(S_exit)) = 2 /\ '+public('S_exit'))]
 return b,c

def byref_assertions(program,path):
 b,_=primary(program,path)
 c=[('byref-declared recipient throws through actual exceptional restore without normal byref return',r'pfunction_helper.SIGNATURE.BYREF /\ $ob_object_source_active($ob_object_native_source(S_pending)) = (OBJECT_CV_THROW pobcvassoc porigin_throw 0) /\ S_restored.CURRENT = pframe_call.CONTEXT /\ $ob_object_source_active($ob_object_native_source(S_restored)) = (OBJECT_CV_THROW pobcvassoc porigin_throw 1) /\ pobcvassoc.FACTORY.CONTOUR.CURSOR = $ob_object_cv_end(pobcvassoc.FACTORY)'),
  ('byref declaration adds no result wrapper or owner to the pending native handoff',r'S_restored.RESULT = KNOWN PNULL /\ ~((HCELL n_cell) <- S_restored.ALLOCATIONS) /\ $heap_owners($heap_graph(S_restored),HOBJECT n_exception) = 1 /\ $heap_count(HOBJECT n_object,$machine_roots(S_restored)) = 2 /\ '+public('S_restored'))]
 return b,c

def native_local_assertions(program,path):
 b,_=primary(program,path)
 b += ['$ob_object_final_local_context(S_restored) = ((pobobjectreturn,pdestructorcall,pobobjectsource?,ptask_native*))',
  'pdestructorcall.FRAME = (pdestructionframe_outer)',
  'pdestructionframe_outer.PENDING = (n_old)']
 b += seek('S_exit','S_restored',8,helper='fr')+[
  'S_exit.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: ptask_exit*']
 owners=lambda s:f'$heap_count(HOBJECT pobobjectreturn.OBJECT,$machine_roots({s})) = 2 /\\ $heap_count(HOBJECT pdestructorcall.OBJECT,$machine_roots({s})) = 2 /\\ $heap_count(HOBJECT n_old,$machine_roots({s})) = 1 /\\ $heap_owners($heap_graph({s}),HOBJECT n_exception) = 1'
 c=[('helper pop restores local native consumer with old E and both real C pairs',r'S_restored.CURRENT = pframe_call.CONTEXT /\ $ob_object_source_active(pobobjectsource?) = (OBJECT_CV_THROW pobcvassoc porigin_throw 1) /\ n_exception =/= n_old /\ ~((HCELL n_cell) <- S_restored.ALLOCATIONS) /\ '+owners('S_restored')+' /\\ '+public('S_restored')),
  ('actual local C0 preserves pending F1 old E1 outer T2 and local T2',r'$ob_object_final_local_ready(S_exit,pobobjectreturn,pdestructorcall,pobcvreturn.RETURN,n_exception,pdestructionframe,ptask_exit*) /\ pdestructionframe.FUNCTION = pfunction_native.ORIGIN /\ pdestructionframe.FUNCTION =/= pfunction_helper.ORIGIN /\ $throwable_field(S_exit,n_exception,"previous") = PNULL /\ '+owners('S_exit')+' /\\ '+public('S_exit'))]
 return b,c

def render(bindings,checks):
 return PREFIX+'\ndec $main() : bool*\ndef $main() = ['+', '.join('('+expr+')' for _,expr in checks)+']\n'+''.join(('  -- ' if item.startswith('PhpStep:') else '  -- if ')+item+'\n' for item in bindings)

def fingerprint():
 names=('spec/semantics/30-storage.watsup','spec/semantics/40-control.watsup','spec/semantics/456-output-object-returns.watsup','spec/semantics/modules.json','tests/semantics/output_factory_helper_cv_sources.py','tests/semantics/output_factory_helper_cv_review_state.py','tests/semantics/output_factory_cv_review_state.py','tests/semantics/output_factory_return_review_state.py','tests/semantics/_build/default/numeric_runner.exe','_build/default/adapter/main.exe','.tools/php/bin/php')
 return {name:support.common.sha(ROOT/name) for name in names}

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--output',type=Path);parser.add_argument('--native-root',type=Path)
 parser.add_argument('--checked-root',type=Path,help='reuse the frozen baseline-01 and control-preparation packets')
 parser.add_argument('--stage',choices=('primary','report','refusals',*CONTROLS),default='primary')
 parser.add_argument('--prepare-only',action='store_true');args=parser.parse_args()
 out=args.output or Path(tempfile.mkdtemp(prefix='helper-cv-review-'));out.mkdir(parents=True,exist_ok=True)
 report={'revision':support.subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD']).decode().strip(),'before':fingerprint(),'records':[],'passed':False,'native_agreement_credit':0,'cap_seconds':300,'stage':args.stage}
 try:
  modules=json.loads((ROOT/'spec/semantics/modules.json').read_text())
  original=args.stage in ('primary','report','refusals')
  chosen=list(sources.CASES.items()) if original else [(args.stage,CONTROLS[args.stage])]
  for name,source in chosen:
   directory=out/name;directory.mkdir()
   packet='baseline-01' if original else ('control-preparation-02' if name in ('recursive','override') else 'control-preparation-03' if name=='native-local' else 'control-preparation-01')
   cached=args.checked_root/packet/name if args.checked_root else None
   path=args.native_root/'native-01/source.php' if original and args.native_root else (cached/'source.php' if cached and not original else directory/'source.php')
   if (original and args.native_root) or (cached and not original):assert path.read_bytes()==source
   else:path.write_bytes(source)
   if cached:
    request=json.loads((cached/'frontend/0.request').read_text());assert base64.b64decode(request['source'])==source
    checked=json.loads((cached/'adapter/0.response').read_text())
   else:
    worker=Worker([str(ROOT/'.tools/php/bin/php'),'-n','-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],directory/'frontend')
    try:parsed=worker.request({'op':'parse','source':base64.b64encode(source).decode()})
    finally:worker.close()
    worker=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],directory/'adapter')
    try:checked=worker.request({'op':'check','ast':parsed['ast'],'fixture':True})
    finally:worker.close()
   fn={'primary':primary,'report':report_assertions,'refusals':refusals,'sibling':sibling_assertions,'rebind':rebind_assertions,'catch':normal_assertions,'override':lambda program,path:normal_assertions(program,path,True),'recursive':recursive_assertions,'cleanup':cleanup_assertions,'recipient-byref':byref_assertions,'native-local':native_local_assertions}[args.stage]
   bindings,checks=fn(checked['fixture'],path);fixture=directory/'state.watsup';fixture.write_text(render(bindings,checks))
   record={'case':name,'checks':[name for name,_ in checks],'fixture_sha256':support.common.sha(fixture),'source_sha256':support.common.sha(path),'passed':False};report['records'].append(record)
   if args.prepare_only:continue
   started=time.monotonic();result=support.common.run([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),'--sl',*[str(ROOT/m) for m in modules],str(fixture)],directory,'state',300)
   values=re.findall(rb'\b(?:true|false)\b',result.stdout);record.update(seconds=round(time.monotonic()-started,3),exit=result.returncode,results=[value==b'true' for value in values])
   assert not re.sub(rb'true|false|[\[\](),;\s]',b'',result.stdout),(result.stdout,result.stderr)
   assert result.returncode==0 and not result.stderr and values==[b'true']*len(checks),(result.returncode,result.stderr.decode(errors='replace'),record['results'])
   record['passed']=True;print(name,True,record['seconds'],flush=True)
  assert report['records'],'no fixture selected';report['passed']=not args.prepare_only
 except BaseException as error:
  report['failure']={'type':type(error).__name__,'message':str(error)};raise
 finally:
  report['after']=fingerprint();report['stable']=report['before']==report['after'];report['passed']=report['passed'] and report['stable'];(out/('preparation.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
