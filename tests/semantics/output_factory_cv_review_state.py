#!/usr/bin/env python3
"""Actual CV publication, selected throw, clearing and native output receipts."""
import argparse,base64,json,os,re,tempfile,time
from pathlib import Path
from recorded_worker import Worker
import output_factory_cv_sources as sources
import output_factory_return_review_state as previous
import output_deprecation_warning_review_state as runner
import output_object_conversion_review_sources as support

ROOT=support.ROOT
PREFIX=previous.PREFIX+r'''
dec $ccv_phase(pstate, nat) : bool
def $ccv_phase(S, 0) = true
  -- if S.TODO = (WRITE_NAME preqbytes z) :: ptask_tail*
  -- if S.RESULT = KNOWN (POBJECT n)
  -- if S.OBJECTS[n] = THROWABLE pthrowable
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n_object pcallcontext.FUNCTION
def $ccv_phase(S, 1) = true
  -- if S.TODO = DISCARD :: ptask_tail*
  -- if S.RESULT = KNOWN PNULL
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n_object pcallcontext.FUNCTION
def $ccv_phase(S, 2) = true
  -- if S.TODO = (EVAL (NExprVariable phpType32 metadata)) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n_object pcallcontext.FUNCTION
def $ccv_phase(S, 3) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n_object pcallcontext.FUNCTION
def $ccv_phase(S, 4) = true
  -- if S.TODO = (WRITE_NAME preqbytes z) :: ptask_tail*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("H"))
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n_object pcallcontext.FUNCTION
def $ccv_phase(S, 5) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
def $ccv_phase(S, 6) = true
  -- if $ob_object_source_active($ob_object_native_source(S)) = (OBJECT_CALL_NEW porigin pobctorbirth pobsourcecontour)
def $ccv_phase(S, 7) = true
  -- if $ob_object_source_active($ob_object_native_source(S)) = (OBJECT_CALL_THROW porigin pobctorbirth pobsourcecontour)
def $ccv_phase(S, 8) = true
  -- if $ob_object_source_active($ob_object_native_source(S)) = (OBJECT_CALL_UNWIND porigin pobctorbirth pobsourcecontour)
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
public=previous.public
CONTROLS={
 'cleanup':sources.CLEANUP,'rebind':sources.REBIND,'catch':sources.CATCH,
 'sibling-rebind':sources.CASES['factory-two-cvs'].replace(b'        throw $first;',b"        $first = 'H';\n        throw $later;"),
 'native-local':b"""<?php
echo 'P';
class T {
    function __toString() { $local = new T; throw new Exception('E'); }
    function __destruct() { $e = bridge(); throw $e; }
}
function bridge() { return make(); }
function make() { $message = 'F'; return new Exception($message); }
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
""",
 'legacy-helper-catch':sources.CASES['factory-cv'].replace(b'        throw $e;',b'        try { fail(); } catch (Exception $caught) {}\n        throw $e;').replace(b'function make()',b"function fail() { $message = 'X'; throw new Exception($message); }\nfunction make()"),
}

def seek(state,start,phase,limit=512,helper='ccv'):
 return [f'{state}_found = ${helper}_seek({start}, {phase}, {limit})',
  f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
  f'{state} = {state}_found[.COMPLETION = NORMAL]']

def step(state,start):
 return [f'{state}_found = $drive_steps({start}, 1)',f'{state}_found.COMPLETION = BUDGET',f'{state} = {state}_found[.COMPLETION = NORMAL]']

def written(program,path,writes):
 b=['S_initial = $php_file_run('+program+', 0, '+runner.bytes_expr(os.fsencode(path))+', '+runner.bytes_expr(os.fsencode(path.parent))+')']
 states=[f'S_{phase}_{i}' for i in range(writes) for phase in ('write','written','discard','dropped')]
 b += ['['+', '.join(states)+f'] = $ccv_writes(S_initial, {writes})']
 for i in range(writes):
  b += [f'S_write_{i}.TODO = (WRITE_NAME preqbytes_name_{i} z_write_{i}) :: ptask_write_{i}*',
   f'S_write_{i}.RESULT = KNOWN (POBJECT n_exception_{i})',
   f'$ob_object_source_active($ob_object_native_source(S_write_{i})) = (OBJECT_CV_RETURN pobcvreturn_{i})',
   f'$lookup(S_written_{i}.ENV, preqbytes_name_{i}) = (n_cell_{i})',
   f'$ob_object_cv_lookup($ob_object_cv_associations($ob_object_native_source(S_written_{i})), preqbytes_name_{i}) = (pobcvassoc_{i})']
 b += [f'S_written_{writes-1}.CURRENT = (pcallcontext_native)',
  'pcallcontext_native.TARGET = METHOD_TARGET n_object pcallcontext_native.FUNCTION',
  f'$function_at($all_functions(S_written_{writes-1}), pcallcontext_native.FUNCTION) = (pfunction_native)']
 return b

def throwing(start,suffix=''):
 t='S_throw'+suffix;p='S_pending'+suffix
 return seek(t,start,3,128)+[
  f'{t}.TODO = (THROW_VALUE porigin_throw{suffix} z_throw{suffix}) :: ptask_throw{suffix}*',
  f'{t}.RESULT = VARIABLE preqbytes_read{suffix} z_read{suffix}',
  f'$lookup({t}.ENV, preqbytes_read{suffix}) = (n_cell_read{suffix})',
  f'{t}.STORE[n_cell_read{suffix}] = DEFINED (POBJECT n_selected{suffix})',
  f'$ob_object_cv_lookup($ob_object_cv_associations($ob_object_native_source({t})), preqbytes_read{suffix}) = (pobcvassoc_selected{suffix})',
 ]+step(p,t)+[f'{p}.TODO = (THROW_SEARCH n_selected{suffix}) :: ptask_throw{suffix}*']

def flow(program,path,writes=1):
 b=written(program,path,writes)+throwing(f'S_dropped_{writes-1}')
 c=[]
 for i in range(writes):
  c += [(f'factory {i} reaches its real assignment with immutable birth and exhausted contour',f'pobcvreturn_{i}.BIRTH.OBJECT = n_exception_{i} /\\ pobcvreturn_{i}.CONTOUR.CALLS =/= eps /\\ pobcvreturn_{i}.CONTOUR.CURSOR = |pobcvreturn_{i}.CONTOUR.CALLS| /\\ $ob_object_ctor_fact_live(S_write_{i}, pobcvreturn_{i}.BIRTH)'),
   (f'write {i} moves the actual result to its private compiled CV cell',f'pobcvassoc_{i}.FACTORY = pobcvreturn_{i} /\\ pobcvassoc_{i}.NAME = preqbytes_name_{i} /\\ pobcvassoc_{i}.CELL = n_cell_{i} /\\ S_written_{i}.RESULT = KNOWN PNULL /\\ S_written_{i}.STORE[n_cell_{i}] = DEFINED (POBJECT n_exception_{i}) /\\ $heap_count(HCELL n_cell_{i}, $machine_roots(S_written_{i})) = 1 /\\ $heap_owners($heap_graph(S_written_{i}), HOBJECT n_exception_{i}) = 1'),
   (f'discard {i} retains the cell-owned result without a direct RESULT root',f'S_dropped_{i}.RESULT = KNOWN PNULL /\\ $ob_object_cv_lookup($ob_object_cv_associations($ob_object_native_source(S_dropped_{i})), preqbytes_name_{i}) = (pobcvassoc_{i}) /\\ $heap_count(HOBJECT n_exception_{i}, $machine_roots(S_dropped_{i})) = 0 /\\ $heap_owners($heap_graph(S_dropped_{i}), HOBJECT n_exception_{i}) = 1 /\\ $ob_object_source_pending($ob_object_native_source(S_dropped_{i})) = eps')]
 c += [('actual selected VARIABLE read remains cell-owned across zero budget',r'preqbytes_read = preqbytes_name_0 /\ n_selected = n_exception_0 /\ $heap_count(HOBJECT n_selected, $machine_roots(S_throw)) = 0 /\ $heap_owners($heap_graph(S_throw), HOBJECT n_selected) = 1 /\ $drive_steps(S_throw, 0) = S_throw[.COMPLETION = BUDGET]'),
  ('one charged THROW spends only the selected row and publishes F2 with T2',r'S_pending.RESULT = KNOWN PNULL /\ $ob_object_source_active($ob_object_native_source(S_pending)) = (OBJECT_CV_THROW pobcvassoc_selected porigin_throw) /\ $ob_object_cv_lookup($ob_object_cv_associations($ob_object_native_source(S_pending)), preqbytes_read) = eps /\ $ob_object_source_pending($ob_object_native_source(S_pending)) = ((pobcvassoc_selected.FACTORY.RETURN,n_selected)) /\ $heap_owners($heap_graph(S_pending), HOBJECT n_selected) = 2 /\ $heap_count(HOBJECT n_object, $machine_roots(S_pending)) = 2'),
  ('selected constructor fields and creation trace survive storage and actual throw',f'$throwable_field(S_pending,n_selected,"line") = PINT {11 if writes==1 else 15} /\\ $throwable_field(S_pending,n_selected,"previous") = PNULL /\\ $throwable_field(S_pending,n_selected,"trace") = $throwable_field(S_write_0,n_selected,"trace")'),
  ('published discarded and pending states remain publicly valid',' /\\ '.join(public(s) for s in [f'S_written_{i}' for i in range(writes)]+[f'S_dropped_{i}' for i in range(writes)]+['S_pending']))]
 if writes==2:
  c += [('two fresh same-factory results coexist and the later certificate survives the earlier throw',r'n_exception_0 =/= n_exception_1 /\ n_cell_0 =/= n_cell_1 /\ pobcvreturn_0.FUNCTION = pobcvreturn_1.FUNCTION /\ $ob_object_cv_associations($ob_object_native_source(S_throw)) = [pobcvassoc_1,pobcvassoc_0] /\ $ob_object_cv_associations($ob_object_native_source(S_pending)) = [pobcvassoc_1] /\ $heap_owners($heap_graph(S_pending), HOBJECT n_exception_1) = 1')]
 return b,c

def refusals(program,path,writes=1):
 b,_=flow(program,path,writes)
 b += ['PhpStep: S_write_0 ~> S_raw_write','PhpStep: S_throw ~> S_php',
  'S_after_throw = $throwable_transition(S_throw, S_php)',
  'S_no_issued = $ob_object_call_capture(S_write_0, eps)',
  'S_no_row = $ob_object_call_capture(S_throw, eps)',
  'S_after_no_row = $ob_object_call_capture(S_after_throw, eps)',
  'pobcvassoc_cell = pobcvassoc_selected[.CELL = 999999]',
  'pobcvassoc_name = pobcvassoc_selected[.NAME = $ptascii("foreign")]',
  'pobcvassoc_birth = pobcvassoc_selected[.FACTORY = pobcvassoc_selected.FACTORY[.BIRTH = pobcvassoc_selected.FACTORY.BIRTH[.OBJECT = n_object]]]',
  'S_wrong_receiver = S_throw[.CURRENT = (pcallcontext_native[.RECEIVER = (n_selected)])]',
  'S_wrong_result = S_throw[.RESULT = KNOWN (POBJECT n_selected)]']
 c=[('missing actual issued fact and selected stored row cannot mint authority',r'$ob_object_cv_committed(S_no_issued, S_raw_write) = eps /\ $source_exception_transition(S_no_row, S_after_no_row) = S_after_no_row'),
  ('actual observer requires the selected cell name receiver and delayed operand',r'$ob_object_cv_throw(S_throw,S_after_throw,pobcvassoc_selected,porigin_throw) /\ ~$ob_object_cv_throw(S_throw,S_after_throw,pobcvassoc_cell,porigin_throw) /\ ~$ob_object_cv_throw(S_throw,S_after_throw,pobcvassoc_name,porigin_throw) /\ ~$ob_object_cv_throw(S_wrong_receiver,S_after_throw,pobcvassoc_selected,porigin_throw) /\ ~$ob_object_cv_throw(S_wrong_result,S_after_throw,pobcvassoc_selected,porigin_throw)'),
  ('altered birth and pending identity refuse pure capture without executing forged states',r'~$ob_object_cv_throw(S_throw,S_after_throw,pobcvassoc_birth,porigin_throw) /\ ~$ob_object_cv_throw(S_throw,S_after_throw[.COMPLETION = THROWING n_object],pobcvassoc_selected,porigin_throw)'),
  ('canonical maps reject nested wrappers and do not infer a missing row',r'$ob_object_cv_pack(([pobcvassoc_selected]), (OBJECT_CV_DATA eps eps)) = eps /\ $ob_object_cv_pack(eps,(OBJECT_CV_THROW pobcvassoc_selected porigin_throw)) = (OBJECT_CV_THROW pobcvassoc_selected porigin_throw) /\ $ob_object_cv_lookup(eps,preqbytes_read) = eps /\ $ob_object_source_pending((OBJECT_CV_DATA ([pobcvassoc_selected]) (OBJECT_CV_DATA eps (OBJECT_CV_THROW pobcvassoc_selected porigin_throw)))) = eps')]
 return b,c

def fatal(path,line,frames):
 trace=''.join(f'#{i} {path}({call}): {name}()\n' for i,(call,name) in enumerate(frames))
 return (f'Fatal error: Uncaught Exception: E in {path}:{line}\nStack trace:\n'+trace+f'#{len(frames)} [internal function]: T->__toString()\n#{len(frames)+1} {{main}}\n  thrown in {path} on line {line}\n').encode()

def report_assertions(program,path,writes=1):
 b,_=flow(program,path,writes)
 b += seek('S_exit','S_pending',3,helper='fr')+[
  'S_exit.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (OUTPUT_FINAL_OBJECT_CV pobobjectreturn) :: ptask_exit*']
 b += step('S_report','S_exit')+['S_report.TODO = [OUTPUT_FINAL_PENDING pobdeactivate n_selected true]']
 b += seek('S_retired','S_report',4,helper='fr')+[
  'S_retired.DESTRUCTION.ABANDONED = [pdestructioncleanup]',
  'pobobjectreturn_uncommitted = pobobjectreturn[.SOURCE = (OBJECT_CV_RETURN pobcvreturn_0)]',
  'pobcvassoc_partial = pobcvassoc_selected[.FACTORY = pobcvassoc_selected.FACTORY[.CONTOUR = pobcvassoc_selected.FACTORY.CONTOUR[.CURSOR = 0]]]',
  'pobobjectreturn_partial = pobobjectreturn[.SOURCE = (OBJECT_CV_THROW pobcvassoc_partial porigin_throw)]',
  'pobcvassoc_wrong = pobcvassoc_selected[.FACTORY = pobcvassoc_selected.FACTORY[.ASSIGN = pobcvassoc_selected.FACTORY.RETURN]]',
  'pobobjectreturn_wrong = pobobjectreturn[.SOURCE = (OBJECT_CV_THROW pobcvassoc_wrong porigin_throw)]']
 for kind in ('uncommitted','partial','wrong'):
  b += [f'pdestructioncleanup_{kind} = pdestructioncleanup[.SOURCE = OUTPUT_FINAL_OBJECT_THROW pobobjectreturn_{kind} pobdeactivate pobcvassoc_selected.FACTORY.RETURN n_selected]',
   f'S_{kind}_receipt = S_retired[.DESTRUCTION.ABANDONED = [pdestructioncleanup_{kind}]]']
 expected=fatal(path,11,[(5,'make')]) if writes==1 else fatal(path,15,[(11,'make'),(5,'bridge')])
 c=[('actual native C0 alone reports after CV release with pending F1 and cast T2',r'$ob_object_final_cv_ready(S_exit,pobobjectreturn,pdestructionframe,n_selected) /\ pdestructionframe.FUNCTION = pfunction_native.ORIGIN /\ pdestructionframe.FUNCTION =/= pobcvreturn_0.FUNCTION /\ S_exit.CURRENT = eps /\ S_exit.FRAMES = eps /\ $ob_object_cv_associations(pobobjectreturn.SOURCE) = eps /\ ~((HCELL n_cell_0) <- S_exit.ALLOCATIONS) /\ $heap_owners($heap_graph(S_exit),HOBJECT n_selected) = 1 /\ $heap_count(HOBJECT n_object,$machine_roots(S_exit)) = 2 /\ '+public('S_exit')),
  ('creation line and complete saved factory trace determine the fatal bytes','S_report.EVENTS = [OUTPUT ([80]), STDERR '+runner.bytes_expr(expected)+r'] /\ $throwable_field(S_report,n_selected,"previous") = PNULL /\ S_report.EXITSTATUS = 255'),
  ('retired snapshot receipt preserves source authority without F ownership',r'~((HOBJECT n_selected) <- S_retired.ALLOCATIONS) /\ $heap_count(HOBJECT n_selected,$machine_roots(S_retired)) = 0 /\ $heap_count(HOBJECT n_object,$machine_roots(S_retired)) = 2 /\ $eager_cleanup_valid(S_retired,pdestructioncleanup) /\ $task_nodes(pdestructioncleanup.SOURCE) = eps /\ '+public('S_retired')),
  ('uncommitted partial and wrong-source receipts refuse report authority',' /\\ '.join(f'~$eager_cleanup_valid(S_{kind}_receipt,pdestructioncleanup_{kind})' for kind in ('uncommitted','partial','wrong')))]
 return b,c

def rebind_assertions(program,path,writes=1):
 b=written(program,path,writes)+seek('S_rebind',f'S_dropped_{writes-1}',4)+[
  'S_rebind.TODO = (WRITE_NAME preqbytes_name_0 z_rebind) :: ptask_rebind*',
  'PhpStep: S_rebind ~> S_rebind_raw',
  'S_observed = $source_exception_transition(S_rebind,S_rebind_raw)']
 b += step('S_rebound','S_rebind')
 c=[('actual H write removes only the selected association before physical F retirement',r'$ob_object_cv_lookup($ob_object_cv_associations($ob_object_native_source(S_observed)),preqbytes_name_0) = eps /\ (HOBJECT n_exception_0) <- S_observed.ALLOCATIONS /\ $heap_owners($heap_graph(S_observed),HOBJECT n_exception_0) = 0 /\ ~((HOBJECT n_exception_0) <- S_rebound.ALLOCATIONS) /\ '+public('S_rebound'))]
 if writes==1:
  b += seek('S_scalar','S_rebound',3,128)
  c += [('invalid scalar throw is not executed and cannot recover retired provenance',r'$ob_object_native_source(S_scalar) = eps /\ $heap_count(HOBJECT n_exception_0,$machine_roots(S_scalar)) = 0 /\ S_scalar.EVENTS = [OUTPUT ([80])] /\ '+public('S_scalar'))]
 else:
  b += throwing('S_rebound')
  c += [('rebinding first leaves the later real cell and certificate usable',r'$ob_object_cv_associations($ob_object_native_source(S_rebound)) = [pobcvassoc_1] /\ $ob_object_cv_cell(S_rebound,pobcvassoc_1) /\ n_selected = n_exception_1 /\ pobcvassoc_selected = pobcvassoc_1 /\ $ob_object_source_active($ob_object_native_source(S_pending)) = (OBJECT_CV_THROW pobcvassoc_1 porigin_throw) /\ $heap_owners($heap_graph(S_pending),HOBJECT n_exception_1) = 2 /\ '+public('S_pending'))]
 return b,c

def protocol_assertions(program,path,writes=1):
 b,c=flow(program,path,writes)
 prefix=len(b)
 for fn in (refusals,report_assertions):
  bindings,checks=fn(program,path,writes)
  assert bindings[:prefix]==b[:prefix]
  b+=bindings[prefix:];c+=checks
 return b,c

def catch_assertions(program,path,writes=2):
 b=written(program,path,2)+throwing('S_dropped_1')
 b += seek('S_catch','S_pending',5,helper='fr')+[
  'S_catch.TODO = (CATCH_BIND porigin_try n_index n_exception_0) :: ptask_catch*']
 b += throwing('S_catch','_later')
 c=[('first actual throw spends its fact while later remains live',r'n_selected = n_exception_0 /\ $ob_object_cv_associations($ob_object_native_source(S_pending)) = [pobcvassoc_1] /\ $ob_object_source_active($ob_object_native_source(S_pending)) = (OBJECT_CV_THROW pobcvassoc_0 porigin_throw)'),
  ('genuine catch clears active history and preserves only the later cell association',r'$ob_object_source_active($ob_object_native_source(S_catch)) = eps /\ $ob_object_cv_associations($ob_object_native_source(S_catch)) = [pobcvassoc_1] /\ $ob_object_cv_cell(S_catch,pobcvassoc_1) /\ $ob_object_ctor_fact_live(S_catch,pobcvreturn_0.BIRTH) /\ $ob_object_cv_lookup($ob_object_cv_associations($ob_object_native_source(S_catch)),preqbytes_name_0) = eps /\ '+public('S_catch')),
  ('subsequent genuine later-CV throw uses its own surviving certificate',r'n_selected_later = n_exception_1 /\ pobcvassoc_selected_later = pobcvassoc_1 /\ $ob_object_source_active($ob_object_native_source(S_pending_later)) = (OBJECT_CV_THROW pobcvassoc_1 porigin_throw_later) /\ $ob_object_cv_associations($ob_object_native_source(S_pending_later)) = eps /\ $heap_owners($heap_graph(S_pending_later),HOBJECT n_exception_1) = 2 /\ '+public('S_pending_later'))]
 return b,c

def cleanup_assertions(program,path,writes=1):
 b=written(program,path,1)+throwing('S_dropped_0')
 b += seek('S_D','S_pending',5)+[
  'S_D.TODO = (DESTRUCTOR_ENTER pdestructorcall_D) :: ptask_D*']
 b += seek('S_exit','S_D',3,helper='fr')+[
  'S_exit.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (OUTPUT_FINAL_OBJECT_CV pobobjectreturn) :: ptask_exit*']
 b += step('S_report','S_exit')
 c=[('selected e-CV releases before the later D destructor while C guards remain',r'$heap_owners($heap_graph(S_pending),HOBJECT n_selected) = 2 /\ $heap_owners($heap_graph(S_D),HOBJECT n_selected) = 1 /\ ~((HCELL n_cell_0) <- S_D.ALLOCATIONS) /\ $heap_count(HOBJECT n_object,$machine_roots(S_D)) = 2 /\ S_D.EVENTS = [OUTPUT ([80])] /\ '+public('S_D')),
  ('D warning occurs before native C0 with only pending F1 and native T2',r'S_exit.EVENTS = [OUTPUT ([80]), WARNING ($ptascii("missing")) 3] /\ $ob_object_final_cv_ready(S_exit,pobobjectreturn,pdestructionframe,n_selected) /\ $heap_owners($heap_graph(S_exit),HOBJECT n_selected) = 1 /\ $heap_count(HOBJECT n_object,$machine_roots(S_exit)) = 2 /\ '+public('S_exit')),
  ('the same warning precedes fatal bytes from the saved creation trace','S_report.EVENTS = [OUTPUT ([80]), WARNING ($ptascii("missing")) 3, STDERR '+runner.bytes_expr(fatal(path,13,[(6,'make')]))+']')]
 return b,c

def native_local_assertions(program,path,writes=1):
 b=written(program,path,1)+throwing('S_dropped_0')+[
  '$ob_object_final_local_context(S_pending) = ((pobobjectreturn,pdestructorcall,pobobjectsource?,ptask_native*))',
  'pdestructorcall.FRAME = (pdestructionframe_outer)',
  'pdestructionframe_outer.PENDING = (n_old)']
 b += seek('S_exit','S_pending',8,helper='fr')+[
  'S_exit.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: ptask_exit*']
 owners=lambda s:f'$heap_count(HOBJECT pobobjectreturn.OBJECT,$machine_roots({s})) = 2 /\\ $heap_count(HOBJECT pdestructorcall.OBJECT,$machine_roots({s})) = 2 /\\ $heap_count(HOBJECT n_old,$machine_roots({s})) = 1'
 c=[('local CV write and actual throw preserve distinct old E and both real C pairs',r'n_selected = n_exception_0 /\ n_selected =/= n_old /\ $ob_object_source_active(pobobjectsource?) = (OBJECT_CV_THROW pobcvassoc_0 porigin_throw) /\ $heap_owners($heap_graph(S_pending),HOBJECT n_selected) = 2 /\ $throwable_field(S_pending,n_selected,"previous") = PNULL /\ '+owners('S_pending')+' /\\ '+public('S_written_0')+' /\\ '+public('S_pending')),
  ('actual local C0 follows CV release and retains only pending F1',r'$ob_object_final_local_ready(S_exit,pobobjectreturn,pdestructorcall,pobcvreturn_0.RETURN,n_selected,pdestructionframe,ptask_exit*) /\ pdestructionframe.FUNCTION = pfunction_native.ORIGIN /\ pdestructionframe.FUNCTION =/= pobcvreturn_0.FUNCTION /\ S_exit.CURRENT = eps /\ S_exit.FRAMES = eps /\ ~((HCELL n_cell_0) <- S_exit.ALLOCATIONS) /\ $heap_owners($heap_graph(S_exit),HOBJECT n_selected) = 1 /\ '+owners('S_exit')+' /\\ '+public('S_exit'))]
 return b,c

def legacy_assertions(program,path,writes=1):
 b=written(program,path,1)
 b += seek('S_legacy_new','S_dropped_0',6)+seek('S_legacy_throw','S_legacy_new',7)+seek('S_legacy_unwind','S_legacy_throw',8)
 b += seek('S_catch','S_legacy_unwind',5,helper='fr')+[
  'S_catch.TODO = (CATCH_BIND porigin_try n_index n_legacy) :: ptask_catch*']
 b += throwing('S_catch')
 c=[('stored result survives genuine wrapped old helper NEW THROW and UNWIND', ' /\\ '.join(f'$ob_object_cv_associations($ob_object_native_source({s})) = [pobcvassoc_0] /\\ $heap_owners($heap_graph({s}),HOBJECT n_exception_0) = 1' for s in ('S_legacy_new','S_legacy_throw','S_legacy_unwind'))),
  ('actual native catch clears old helper history and preserves the stored e cell',r'n_legacy =/= n_exception_0 /\ $ob_object_source_active($ob_object_native_source(S_catch)) = eps /\ $ob_object_cv_associations($ob_object_native_source(S_catch)) = [pobcvassoc_0] /\ $ob_object_cv_cell(S_catch,pobcvassoc_0) /\ '+public('S_catch')),
  ('subsequent actual e throw uses its original factory association',r'n_selected = n_exception_0 /\ pobcvassoc_selected = pobcvassoc_0 /\ $ob_object_source_active($ob_object_native_source(S_pending)) = (OBJECT_CV_THROW pobcvassoc_0 porigin_throw) /\ $heap_owners($heap_graph(S_pending),HOBJECT n_selected) = 2 /\ '+public('S_pending'))]
 return b,c

def render(bindings,checks):
 return PREFIX+'\ndec $main() : bool*\ndef $main() = ['+', '.join('('+expr+')' for _,expr in checks)+']\n'+''.join(('  -- ' if item.startswith('PhpStep:') else '  -- if ')+item+'\n' for item in bindings)

def fingerprint():
 paths=('spec/semantics/30-storage.watsup','spec/semantics/40-control.watsup','spec/semantics/152-throwable-runtime.watsup','spec/semantics/456-output-object-returns.watsup','spec/semantics/80-call-control.watsup','spec/semantics/161-throwable-constructors.watsup','spec/semantics/257-request-destructors.watsup','spec/semantics/270-eager-destructors.watsup','spec/semantics/modules.json','tests/semantics/output_factory_cv_sources.py','tests/semantics/output_factory_cv_review_state.py','tests/semantics/output_factory_return_review_state.py','tests/semantics/_build/default/numeric_runner.exe','_build/default/adapter/main.exe','.tools/php/bin/php')
 return {name:support.common.sha(ROOT/name) for name in paths}

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--output',type=Path);parser.add_argument('--native-root',type=Path)
 parser.add_argument('--checked-root',type=Path,help='reuse the existing baseline-02/control-preparation-01 checked packets')
 parser.add_argument('--select',choices=(*sources.CASES,'all'),default='all')
 parser.add_argument('--stage',choices=('flow','refusals','report','protocol',*CONTROLS),default='flow')
 parser.add_argument('--prepare-only',action='store_true');args=parser.parse_args()
 out=args.output or Path(tempfile.mkdtemp(prefix='factory-cv-review-'));out.mkdir(parents=True,exist_ok=True)
 report={'revision':support.subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD']).decode().strip(),'before':fingerprint(),'records':[],'passed':False,'native_agreement_credit':0,'cap_seconds':300,'stage':args.stage}
 try:
  modules=json.loads((ROOT/'spec/semantics/modules.json').read_text())
  originals=args.stage in ('flow','refusals','report','protocol')
  chosen=list(sources.CASES.items()) if originals else [(args.stage,CONTROLS[args.stage])]
  for index,(name,source) in enumerate(chosen,1):
   if originals and args.select not in ('all',name):continue
   directory=out/name;directory.mkdir()
   cached=args.checked_root/('baseline-02' if originals else 'control-preparation-01')/name if args.checked_root else None
   path=args.native_root/f'native-0{index}'/'source.php' if originals and args.native_root else (cached/'source.php' if cached and not originals else directory/'source.php')
   if (originals and args.native_root) or (cached and not originals):assert path.read_bytes()==source
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
   writes=2 if name in ('factory-two-cvs','catch','sibling-rebind') else 1
   fn={'flow':flow,'refusals':refusals,'report':report_assertions,'protocol':protocol_assertions,'cleanup':cleanup_assertions,'rebind':rebind_assertions,'catch':catch_assertions,'sibling-rebind':rebind_assertions,'native-local':native_local_assertions,'legacy-helper-catch':legacy_assertions}[args.stage]
   bindings,checks=fn(checked['fixture'],path,writes);fixture=directory/'state.watsup';fixture.write_text(render(bindings,checks))
   record={'case':name,'checks':[name for name,_ in checks],'fixture_sha256':support.common.sha(fixture),'passed':False};report['records'].append(record)
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
