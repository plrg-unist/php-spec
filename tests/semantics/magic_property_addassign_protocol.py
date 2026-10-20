"""Check post-RHS magic += selection, separate handler holds and protected result cleanup."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()

PREFIX = r'''
syntax pmastage = MA_PREP | MA_RHS porigin | MA_APPLY | MA_GET_RETURN | MA_GET_THROW | MA_GET_RESULT | MA_GET_COPY | MA_VALUE | MA_RECEIVE porigin | MA_SET_RETURN | MA_SET_THROW | MA_SET_RESULT | MA_DELIVERY | MA_FINISH | MA_GET_DISCARD | MA_SET_DISCARD | MA_OUTER_DISCARD | MA_FINISH_DISCARD | MA_DTOR nat | MA_CATCH | MA_OUTPUT ptbytes
dec $ma_output(pevent*) : ptbytes
def $ma_output(eps) = eps
def $ma_output((OUTPUT ptbytes) :: pevent_tail*) = ptbytes ++ $ma_output(pevent_tail*)
dec $ma_stage(pstate,pmastage) : bool
def $ma_stage(S,MA_PREP) = true
  -- if S.TODO = (COMPOUND_PREP ADD expression_target expression_rhs z) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $ma_stage(S,MA_RHS porigin) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.FUNCTION = porigin
  -- if S.TODO = (RETURN_UNWIND (KNOWN (PINT 2)) porigin_return?) :: ptask_tail*
def $ma_stage(S,MA_APPLY) = true
  -- if S.TODO = (COMPOUND_APPLY ADD pbase false z) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $ma_stage(S,MA_GET_RETURN) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_GET_TARGET n porigin
  -- if S.TODO = (RETURN_UNWIND (KNOWN (PINT 5)) porigin_return?) :: ptask_tail*
def $ma_stage(S,MA_GET_THROW) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_GET_TARGET n porigin
  -- if S.TODO = (THROW_VALUE porigin_throw z) :: ptask_tail*
def $ma_stage(S,MA_GET_RESULT) = true
  -- if S.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $ma_stage(S,MA_GET_COPY) = true
  -- if S.TODO = (PROPERTY_GET_COPY ppropertyget (KNOWN (PINT 5))) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $ma_stage(S,MA_VALUE) = true
  -- if S.TODO = (PROPERTY_MAGIC_ADD_VALUE ppropertymagicadd) :: ptask_tail*
def $ma_stage(S,MA_RECEIVE porigin) = true
  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: ptask_tail*
def $ma_stage(S,MA_SET_RETURN) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_MAGIC_SET_TARGET ppropertymagicset
  -- if S.TODO = (RETURN_UNWIND (KNOWN PNULL) porigin_return?) :: ptask_tail*
def $ma_stage(S,MA_SET_THROW) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_MAGIC_SET_TARGET ppropertymagicset
  -- if S.TODO = (THROW_VALUE porigin_throw z) :: ptask_tail*
def $ma_stage(S,MA_SET_RESULT) = true
  -- if S.TODO = (PROPERTY_MAGIC_SET_RESULT ppropertymagicset) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $ma_stage(S,MA_DELIVERY) = true
  -- if S.TODO = (PROPERTY_MAGIC_SET_DELIVERY ppropertymagicset) :: ptask_tail*
def $ma_stage(S,MA_FINISH) = true
  -- if S.TODO = (PROPERTY_MAGIC_ADD_FINISH ppropertymagicadd i_left i_sum) :: ptask_tail*
def $ma_stage(S,MA_GET_DISCARD) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $ma_stage(S,MA_SET_DISCARD) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_MAGIC_SET_RESULT ppropertymagicset) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $ma_stage(S,MA_OUTER_DISCARD) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_MAGIC_ADD_VALUE ppropertymagicadd) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $ma_stage(S,MA_FINISH_DISCARD) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_MAGIC_ADD_FINISH ppropertymagicadd 5 7) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $ma_stage(S,MA_DTOR n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $ma_stage(S,MA_CATCH) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask_tail*
  -- if S.CURRENT = eps
def $ma_stage(S,MA_OUTPUT ptbytes) = ($ma_output(S.EVENTS) = ptbytes)
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $ma_stage(S,pmastage) = false -- otherwise
dec $ma_seek(pstate,pmastage,nat) : pstate
def $ma_seek(S,pmastage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $ma_stage(S,pmastage) \/ n = 0
def $ma_seek(S,pmastage,n) = $ma_seek($drive_steps(S[.COMPLETION = NORMAL],1),pmastage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$ma_stage(S,pmastage) /\ $(n > 0)
def $ma_seek(S,pmastage,n) = $ma_seek($drive_steps(S,1),pmastage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $ma_seek(S,pmastage,n) = S -- otherwise
dec $ma_after(pstate,pstate) : pstate
def $ma_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $ma_guard(pstate) : bool
def $ma_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $object_tables_valid(S) /\ $gc_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
dec $ma_in_get(pstate,nat) : bool
def $ma_in_get(S,n) = ($property_get_guard_tasks(S.TODO,n,$ptascii("value")) \/ $property_get_guard_frames(S.FRAMES,n,$ptascii("value")) \/ $property_empty_get_active(S,n,$ptascii("value")))
dec $ma_in_set(pstate,nat) : bool
def $ma_in_set(S,n) = $property_magic_set_guard(S,S.CURRENT,S.FRAMES,n,$ptascii("value"))
'''

def lines(text): return [line for line in text.strip().splitlines() if line]
def reach(name, previous, stage):
    return [f'{name}_found = $ma_seek({previous},{stage},2000)',
            fr'{name}_found.COMPLETION = NORMAL \/ {name}_found.COMPLETION = BUDGET',
            f'{name} = {name}_found[.COMPLETION = NORMAL]', f'$ma_stage({name},{stage})']

FRONT = lines(r'''
S_front.TODO = (COMPOUND_PREP ADD expression_target expression_rhs z_assign) :: ptask_tail*
S_front.ORIGIN = (porigin_parent)
pbase_pending = S_front.BASE
pbase_pending = BASE_PROPERTY_PENDING (BASE_VALUE (VARIABLE ptbytes_cv z_cv)) (KNOWN (PSTRING ptbytes_name)) z_receiver
ptbytes_cv = $ptascii("child") /\ ptbytes_name = $ptascii("value")
$base_nodes(pbase_pending) = eps
$property_magic_add_source(S_front,porigin_parent)
$lookup(S_front.ENV,ptbytes_cv) = (n_child_cell)
S_front.STORE[n_child_cell] = DEFINED (POBJECT n_old)
$lookup(S_front.ENV,$ptascii("rhs")) = (n_rhs_cell)
$lookup(S_front.ENV,$ptascii("result")) = (n_result_cell)
S_front.STORE[n_result_cell] = DEFINED (PINT 42)
porigin_parent = PORIGIN n_unit pcpath_parent
$code_at(S_front.CODE,n_unit) = (pcode)
$code_name(pcode.NAMES,pcpath_parent ++ [PCFIELD 1]) = ((preqbytes_rhs,preqbytes_fallback?))
$call_target(S_front,preqbytes_rhs,preqbytes_fallback?) = (pfunction_rhs)
~pfunction_rhs.SIGNATURE.BYREF /\ pfunction_rhs.SIGNATURE.PARAMETERS = eps
$heap_owners($heap_graph(S_front),HOBJECT n_old) = 1
$ma_output(S_front.EVENTS) = ptbytes_prefix
$ma_guard(S_front)
''')
RHS = lines(r'''
S_rhs.CURRENT = (pcallcontext_rhs)
pcallcontext_rhs.FUNCTION = pfunction_rhs.ORIGIN /\ pcallcontext_rhs.RECEIVER = eps
S_rhs.TODO = (RETURN_UNWIND (KNOWN (PINT 2)) porigin_rhs_return?) :: ptask_rhs_return*
S_rhs.FRAMES = [pframe_rhs]
pframe_rhs.TODO = (ORIGIN_RETURN (porigin_parent)) :: (COMPOUND_APPLY ADD pbase_pending false z_assign) :: ptask_tail*
S_rhs_saved = $constant_frame_view(S_rhs,pframe_rhs,eps)
$property_magic_add_source(S_rhs_saved,porigin_parent)
$base_nodes(pbase_pending) = eps
S_rhs.STORE[n_result_cell] = DEFINED (PINT 42)
$ma_output(S_rhs.EVENTS) = ptbytes_rhs
$ma_guard(S_rhs)
''')
APPLY = lines(r'''
S_apply.TODO = (COMPOUND_APPLY ADD pbase_pending false z_assign) :: ptask_tail*
S_apply.ORIGIN = (porigin_parent) /\ S_apply.RESULT = KNOWN (PINT 2)
$property_magic_add_plan($hold_task_inputs(S_apply),pbase_pending,S_apply.RESULT,z_assign) = (ppropertymagicadd)
ppropertymagicadd.SITE = porigin_parent /\ ppropertymagicadd.LINE = z_assign /\ ppropertymagicadd.RHS = 2
ppropertymagicadd.CALLER = eps /\ ppropertymagicadd.OWNER = 0 /\ ppropertymagicadd.TAIL = ptask_tail*
ppropertyget = ppropertymagicadd.GET
ppropertyget.OBJECT = n_selected /\ ppropertyget.NAME = ptbytes_name
$property_get_source(S_apply,ppropertyget) /\ $property_get_history(S_apply,ppropertyget)
$property_magic_add_history(S_apply,ppropertymagicadd)
$property_get_method(S_apply,n_selected) = (pmethoddesc_get)
$property_magic_set_method(S_apply,n_selected) = (pmethoddesc_set)
pmethoddesc_get.OWNER = pmethoddesc_set.OWNER /\ pmethoddesc_get.OWNER =/= ppropertyget.CLASS
$property_effective_desc(S_apply,n_selected,ptbytes_name) = (ppropertydesc)
ppropertydesc.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))] /\ ppropertydesc.VISIBILITY = PROPERTY_PRIVATE
$objectprops_at(S_apply.OBJECTPROPS,n_selected) = (ppropertyslot_before_all*)
$property_slot_at(ppropertyslot_before_all*,ppropertydesc.KEY) = (ppropertyslot_before)
ppropertyslot_before.STATE = PROP_VALUE (DIRECT (PINT 5))
$ma_guard(S_apply)
PhpStep: S_apply ~> S_call_raw
S_call = $ma_after(S_apply,S_call_raw)
S_call.TODO = (CALL_ARGS (PROPERTY_GET_TARGET n_selected ppropertyget.METHOD) eps 1 ([KNOWN (PSTRING ptbytes_name)]) (ppropertyget.SITE) ppropertyget.LINE) :: (PROPERTY_GET_RESULT ppropertyget) :: (ORIGIN_RETURN (porigin_parent)) :: (PROPERTY_MAGIC_ADD_VALUE ppropertymagicadd) :: ptask_tail*
$property_get_capture(S_call,ppropertyget) /\ $property_get_pending_call(S_call,PROPERTY_GET_TARGET n_selected ppropertyget.METHOD,ppropertyget.SITE)
$target_nodes(PROPERTY_GET_TARGET n_selected ppropertyget.METHOD) = eps
$task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT n_selected]
$task_nodes(PROPERTY_MAGIC_ADD_VALUE ppropertymagicadd) = [HOBJECT n_selected]
$heap_owners($heap_graph(S_call),HOBJECT n_selected) = $(n_external + 3)
$ma_guard(S_call)
''')
GET = lines(r'''
S_get.CURRENT = (pcallcontext_get)
pcallcontext_get.TARGET = PROPERTY_GET_TARGET n_selected ppropertyget.METHOD
pcallcontext_get.LEXICAL_CLASS = (pmethoddesc_get.OWNER) /\ pcallcontext_get.CALLED_CLASS = (ppropertyget.CLASS)
$call_receiver_roots(pcallcontext_get) = eps
$property_get_entered(S_get,S_get.CURRENT,S_get.FRAMES,pcallcontext_get.TARGET,ppropertyget.SITE)
S_get.STORE[n_child_cell] = DEFINED PNULL
S_get.FRAMES = [pframe_get]
pframe_get.TODO = (PROPERTY_GET_RESULT ppropertyget) :: (ORIGIN_RETURN (porigin_parent)) :: (PROPERTY_MAGIC_ADD_VALUE ppropertymagicadd) :: ptask_tail*
S_get_saved = $constant_frame_view(S_get,pframe_get,eps)
~$property_get_capture(S_get_saved,ppropertyget)
$property_get_valid(S_get_saved,ppropertyget,true)
$heap_owners($heap_graph(S_get),HOBJECT n_selected) = $(n_external + 2)
$ma_in_get(S_get,n_selected) /\ ~$ma_in_set(S_get,n_selected) /\ $ma_guard(S_get)
$ma_output(S_get.EVENTS) = ptbytes_get
''')
VALUE = lines(r'''
S_value.TODO = (PROPERTY_MAGIC_ADD_VALUE ppropertymagicadd) :: ptask_tail*
S_value.ORIGIN = (porigin_parent) /\ S_value.RESULT = KNOWN (PINT 5)
$property_magic_add_valid(S_value,ppropertymagicadd,PROPERTY_MAGIC_ADD_VALUE ppropertymagicadd)
$heap_owners($heap_graph(S_value),HOBJECT n_selected) = $(n_external + 1)
S_value.STORE[n_child_cell] = DEFINED PNULL
~$ma_in_get(S_value,n_selected) /\ ~$ma_in_set(S_value,n_selected) /\ $ma_guard(S_value)
$property_magic_add_set_plan(S_value) = (ppropertymagicset)
ppropertymagicset.OBJECT = n_selected /\ ppropertymagicset.METHOD = pmethoddesc_set.FUNCTION.ORIGIN
ppropertymagicset.INPUT = 7 /\ ppropertymagicset.RHS = KNOWN (PINT 7) /\ ppropertymagicset.CELL = eps
ppropertymagicset.TAIL = (PROPERTY_MAGIC_ADD_FINISH ppropertymagicadd 5 7) :: ptask_tail*
$property_magic_add_set(S_value,ppropertymagicset)
PhpStep: S_value ~> S_set_call_raw
S_set_call = $ma_after(S_value,S_set_call_raw)
$property_magic_set_capture(S_set_call,ppropertymagicset) /\ $property_magic_set_pending_call(S_set_call,ppropertymagicset)
S_set_call.STORE[n_child_cell] = DEFINED PNULL
$task_nodes(PROPERTY_MAGIC_SET_RESULT ppropertymagicset) = [HOBJECT n_selected]
$task_nodes(PROPERTY_MAGIC_ADD_FINISH ppropertymagicadd 5 7) = [HOBJECT n_selected]
$heap_owners($heap_graph(S_set_call),HOBJECT n_selected) = $(n_external + 2)
$ma_guard(S_set_call)
''')
RECEIVE = lines(r'''
S_receive.TODO = (TYPE_RECEIVE ppropertymagicset.METHOD 0) :: ptask_receive_tail*
S_receive.CURRENT = (pcallcontext_receive)
pcallcontext_receive.TARGET = PROPERTY_MAGIC_SET_TARGET ppropertymagicset
pcallcontext_receive.LEXICAL_CLASS = (pmethoddesc_set.OWNER) /\ pcallcontext_receive.CALLED_CLASS = (ppropertyget.CLASS)
$target_function(S_receive,pcallcontext_receive.TARGET) = (pmethoddesc_set.FUNCTION)
$receiving_function(S_receive,ppropertymagicset.METHOD) = (pmethoddesc_set.FUNCTION)
$call_receiver_roots(pcallcontext_receive) = eps
$lookup(S_receive.ENV,$ptascii("incoming")) = (n_incoming)
S_receive.STORE[n_incoming] = DEFINED (PINT 7)
$heap_owners($heap_graph(S_receive),HOBJECT n_selected) = $(n_external + 2)
$ma_guard(S_receive)
''')
SET = lines(r'''
S_set.CURRENT = (pcallcontext_set)
pcallcontext_set.TARGET = PROPERTY_MAGIC_SET_TARGET ppropertymagicset
S_set.STORE[n_child_cell] = DEFINED PNULL
$property_magic_set_entered(S_set,S_set.CURRENT,S_set.FRAMES,ppropertymagicset)
S_set.FRAMES = [pframe_set]
S_set_saved = $constant_frame_view(S_set,pframe_set,eps)
$property_magic_set_capture(S_set_saved,ppropertymagicset)
S_set_scope = $constant_frame_scope(S_set,pframe_set,eps)
$lookup(S_set_scope.ENV,ptbytes_cv) = (n_child_cell)
S_set_saved.STORE[n_child_cell] = DEFINED PNULL
$heap_owners($heap_graph(S_set),HOBJECT n_selected) = $(n_external + 2)
~$ma_in_get(S_set,n_selected) /\ $ma_in_set(S_set,n_selected) /\ $ma_guard(S_set)
$ma_output(S_set.EVENTS) = ptbytes_set
''')
NORMAL = lines(r'''
$objectprops_at(S_set.OBJECTPROPS,n_selected) = (ppropertyslot_after_all*)
$property_slot_at(ppropertyslot_after_all*,ppropertydesc.KEY) = (ppropertyslot_after)
ppropertyslot_after.STATE = PROP_VALUE (DIRECT (PINT 7))
S_setresult.TODO = (PROPERTY_MAGIC_SET_RESULT ppropertymagicset) :: ppropertymagicset.TAIL
$property_magic_set_valid(S_setresult,ppropertymagicset)
S_setresult.RESULT = KNOWN PNULL
$heap_owners($heap_graph(S_setresult),HOBJECT n_selected) = $(n_external + 2)
PhpStep: S_setresult ~> S_delivery_raw
S_delivery_pending = $ma_after(S_setresult,S_delivery_raw)
S_delivery_found = $ma_seek(S_delivery_pending,MA_DELIVERY,2000)
S_delivery_found.COMPLETION = NORMAL \/ S_delivery_found.COMPLETION = BUDGET
S_delivery = S_delivery_found[.COMPLETION = NORMAL]
$ma_stage(S_delivery,MA_DELIVERY)
S_delivery.TODO = (PROPERTY_MAGIC_SET_DELIVERY ppropertymagicset) :: ppropertymagicset.TAIL
$heap_owners($heap_graph(S_delivery),HOBJECT n_selected) = $(n_external + 1)
~$ma_in_set(S_delivery,n_selected) /\ $ma_guard(S_delivery)
PhpStep: S_delivery ~> S_finish_raw
S_finish = $ma_after(S_delivery,S_finish_raw)
S_finish.TODO = (PROPERTY_MAGIC_ADD_FINISH ppropertymagicadd 5 7) :: ptask_tail*
S_finish.RESULT = KNOWN (PINT 7)
$property_magic_add_valid(S_finish,ppropertymagicadd,PROPERTY_MAGIC_ADD_FINISH ppropertymagicadd 5 7)
$heap_owners($heap_graph(S_finish),HOBJECT n_selected) = $(n_external + 1)
~$ma_in_get(S_finish,n_selected) /\ ~$ma_in_set(S_finish,n_selected) /\ $ma_guard(S_finish)
S_finish.STORE[n_result_cell] = DEFINED (PINT 42)
PhpStep: S_finish ~> S_release_raw
S_releasing = $ma_after(S_finish,S_release_raw)
''')
CHILD = lines(r'''
S_child.CURRENT = (pcallcontext_child)
$destructor_context_call(pcallcontext_child,S_child.CURRENT,S_child.FRAMES) = (pdestructorcall_child)
pdestructorcall_child.OBJECT = n_selected
pdestructorcall_child.OPERATION = (pdestructionoperation_child)
pdestructionoperation_child.BASE = BASE_VALUE (KNOWN PNULL)
S_child.STORE[n_result_cell] = DEFINED (PINT 42)
~$ma_in_get(S_child,n_selected) /\ ~$ma_in_set(S_child,n_selected) /\ $ma_guard(S_child)
''')
CATCH = lines(r'''
S_catch.TODO = (CATCH_BIND porigin_catch n_index n_caught) :: ptask_catch_tail*
n_caught = n_error
S_catch.STORE[n_result_cell] = DEFINED (PINT 42)
S_catch.STORE[n_rhs_cell] = DEFINED (PINT 99)
~(HOBJECT n_selected <- S_catch.ALLOCATIONS)
S_catch.OBJECTS[n_caught] = THROWABLE pthrowable_caught
pthrowable_caught.KIND = "Exception"
$ma_output(S_catch.EVENTS) = ptbytes_catch
$ma_guard(S_catch)
''')
FINISH = lines(r'''
S_final = $drive_steps(S_end[.COMPLETION = NORMAL],2000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps
$ma_output(S_final.EVENTS) = ptbytes_final
S_final.STORE[n_result_cell] = DEFINED (PINT i_result)
~(HOBJECT n_old <- S_final.ALLOCATIONS) /\ ~(HOBJECT n_selected <- S_final.ALLOCATIONS)
$ma_guard(S_final)
S_zero = $drive_steps(S_front,0)
S_zero.COMPLETION = BUDGET /\ S_zero.EVENTS = S_front.EVENTS
S_zero.STORE = S_front.STORE /\ S_zero.ALLOCATIONS = S_front.ALLOCATIONS
S_resumed = $drive_steps(S_zero[.COMPLETION = NORMAL],2000)
S_resumed.COMPLETION = NORMAL /\ $ma_output(S_resumed.EVENTS) = ptbytes_final
S_resumed.STORE = S_final.STORE /\ S_resumed.ALLOCATIONS = S_final.ALLOCATIONS
''')
DERIVED = lines(r'''
$property_magic_add_plan($hold_task_inputs(S_apply),pbase_pending,S_apply.RESULT,$(z_assign + 1)) = eps
pbase_bad = BASE_PROPERTY_PENDING (BASE_VALUE (VARIABLE ptbytes_cv $(z_cv + 1))) (KNOWN (PSTRING ptbytes_name)) z_receiver
$property_magic_add_plan($hold_task_inputs(S_apply),pbase_bad,S_apply.RESULT,z_assign) = eps
S_wrong_name = S_apply[.CODE = $compilation_code_replace(S_apply.CODE,pcode[.NAMES = [CODENAME (pcpath_parent ++ [PCFIELD 1]) ($ptascii("missing115")) eps]])]
~$property_magic_add_source(S_wrong_name,porigin_parent)
$property_magic_add_plan($hold_task_inputs(S_wrong_name),pbase_pending,S_wrong_name.RESULT,z_assign) = eps
~$property_magic_add_history(S_apply,ppropertymagicadd[.GET = ppropertyget[.LINE = $(ppropertyget.LINE + 1)]])
~$property_magic_add_history(S_apply,ppropertymagicadd[.SET = ppropertyget.METHOD])
~$property_magic_add_history(S_apply,ppropertymagicadd[.OWNER = 1])
~$property_magic_add_sum(ppropertymagicadd,9223372036854775807,9223372036854775809)
~$property_magic_add_sum(ppropertymagicadd,5,8)
ppropertymagicset_bad = ppropertymagicset[.INPUT = 8]
~$property_magic_add_set(S_value,ppropertymagicset_bad)
~$property_magic_set_source(S_value,ppropertymagicset_bad)
S_raw_get = S_getresult[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING $ptascii("5tail"))]
$property_get_verify(S_raw_get,ppropertyget,S_raw_get.RESULT) = S_raw_get
S_raw_value = S_value[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING $ptascii("5tail"))]
$property_magic_add_set_plan(S_raw_value) = eps
PhpStep: S_raw_value ~> S_raw_refused
S_raw_refused.COMPLETION = UNSUPPORTED "magic compound getter result or integer sum"
S_raw_refused.EVENTS = S_raw_value.EVENTS /\ S_raw_refused.STORE = S_raw_value.STORE /\ S_raw_refused.ALLOCATIONS = S_raw_value.ALLOCATIONS
''')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', action='append', choices=('retarget','sole','set-throw','get-throw'))
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_property_addassign_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile and data['native_observations_accepted']
    assert [case['id'] for case in data['cases']] == ['retarget','sole','set-throw','get-throw']
    selected = data['cases']
    if args.case:
        assert len(args.case) == len(set(args.case))
        selected = [case for case in selected if case['id'] in args.case]
        assert len(selected) == len(args.case)
    php, adapter, bridge, worker, runner, compiler = (ROOT / name for name in [
        '.tools/php/bin/php','_build/default/adapter/main.exe','.tools/php-file.so',
        'frontend/worker.php','tests/semantics/_build/default/numeric_runner.exe','.tools/spectec/bin/p4spectec'])
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    assert sha(compiler) == '26d77fb9bfae2b2868e137a94051f55f9b607660c340e9b22ae8300fb0d8ce88'
    assert sha(runner) == 'b57a2ed7daf86de23993a29d079083377cfef6da133739a164dbfdb9f11fd7a0'
    manifest = ROOT / 'spec/semantics/modules.json'
    modules = [ROOT / name for name in json.loads(manifest.read_bytes())]
    watched = [Path(__file__),Path(recorder.__file__),catalogue,profile_file,php,adapter,bridge,worker,runner,compiler,
        manifest,*modules,*(HERE / case['source_file'] for case in data['cases']),
        *(ROOT / name for name in ['spec/schema.json','spec/php.watsup','spec/nodes.json','frontend/target.php',
            'frontend/wire.php','frontend/wire.py','tests/semantics/recorded_worker.py','tests/semantics/static_types.py'])]
    revision,status = git('rev-parse','HEAD'),git('status','--short')
    assert revision == args.revision and not status,(revision,status)
    before = {str(path):sha(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='magic-property-addassign-protocol-',dir=ROOT / '.tools'))
    print(out,flush=True)
    report = {'revision':revision,'inputs':before,'profile':profile,'module_count':len(modules),
        'mode':'SL','cache':False,'det':True,'records':[],'fixtures':[],'selection':[case['id'] for case in selected],
        'application_invocations':0,'application_evaluations':0,'source_agreements':0,
        'premises':0,'reached_premises':0,'derived_premises':0,'cap_seconds':90,
        'environment':{'LC_ALL':'C','TZ':'UTC','PHP_SPEC_SCRIPT_ENCODING':'absent','jobs':1},'passed':False}
    try:
        flags = [part for key,value in profile.items() for part in ('-d',key + '=' + value)]
        for case in selected:
            name = case['id']
            source = HERE / case['source_file']
            assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256']
            native_stderr = base64.b64decode(case['stderr_template_base64']).replace(b'{FILE}',case['original_source'].encode())
            native_tuple = base64.b64decode(case['stdout_base64']) + b'\0' + native_stderr + b'\0' + str(case['exit_status']).encode()
            assert hashlib.sha256(native_tuple).hexdigest() == case['native_raw_sha256']
            directory = out / name
            directory.mkdir()
            frontend = Worker([str(php),'-n',*flags,'-d','extension=' + str(bridge),str(worker)],directory / 'frontend')
            adapter_worker = None
            try:
                parsed = frontend.request({'op':'parse','source':base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted'],parsed
                adapter_worker = Worker([str(adapter),str(ROOT)],directory / 'adapter')
                checked = adapter_worker.request({'op':'check','ast':parsed['ast'],'fixture':True})
                assert checked['ok'] and checked['ast'] == parsed['ast']
            finally:
                if adapter_worker:
                    adapter_worker.close()
                frontend.close()
            output = base64.b64decode(case['stdout_base64']).decode()
            prefix = {'retarget':'N:','sole':'O:','set-throw':'X:','get-throw':'G:'}[name]
            rhs_output = prefix + ('R|D1/5|r|' if name == 'retarget' else 'R|r|')
            get_output = rhs_output + ('G2|' if name == 'retarget' else 'G1|') + 'MagicAddParent115|MagicAddChild115|' + ('' if name == 'get-throw' else 'g|')
            set_output = get_output + ('S2/7|' if name == 'retarget' else 'S1/7|') + ('' if name == 'set-throw' else 's|')
            setup = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                'ptbytes_prefix = $ptascii(' + json.dumps(prefix) + ')',
                'ptbytes_rhs = $ptascii(' + json.dumps(rhs_output) + ')',
                'ptbytes_get = $ptascii(' + json.dumps(get_output) + ')',
                'ptbytes_set = $ptascii(' + json.dumps(set_output) + ')',
                'ptbytes_catch = $ptascii(' + json.dumps(output.split('C|')[0] if 'C|' in output else '') + ')',
                'ptbytes_final = $ptascii(' + json.dumps(output) + ')',
                'n_external = ' + ('1' if name == 'retarget' else '0'),
                'i_result = ' + ('42' if name in ('set-throw','get-throw') else '7')]
            reached = setup + reach('S_front','S_initial','MA_PREP') + FRONT
            if name in ('set-throw','get-throw'):
                reached += ['$lookup(S_front.ENV,$ptascii("error")) = (n_error_cell)',
                    'S_front.STORE[n_error_cell] = DEFINED (POBJECT n_error)']
            if name == 'retarget':
                reached += ['$lookup(S_front.ENV,$ptascii("replacement")) = (n_replacement_cell)',
                    'S_front.STORE[n_replacement_cell] = DEFINED (POBJECT n_selected)', 'n_selected =/= n_old']
            else:
                reached += ['n_selected = n_old']
            reached += reach('S_rhs','S_front','MA_RHS pfunction_rhs.ORIGIN') + RHS
            if name == 'retarget':
                reached += ['~(HOBJECT n_old <- S_rhs.ALLOCATIONS)',
                    'S_rhs.STORE[n_child_cell] = DEFINED (POBJECT n_selected)',
                    'S_rhs.STORE[n_rhs_cell] = DEFINED (PINT 100)',
                    '$heap_owners($heap_graph(S_rhs),HOBJECT n_selected) = 2']
            else:
                reached += ['S_rhs.STORE[n_child_cell] = DEFINED (POBJECT n_selected)',
                    'S_rhs.STORE[n_rhs_cell] = DEFINED (PINT 55)',
                    '$heap_owners($heap_graph(S_rhs),HOBJECT n_selected) = 1']
            reached += reach('S_apply','S_rhs','MA_APPLY') + APPLY
            reached += reach('S_get','S_call','MA_GET_THROW' if name == 'get-throw' else 'MA_GET_RETURN') + GET
            if name == 'get-throw':
                reached += ['S_get.TODO = (THROW_VALUE porigin_get_throw z_get_throw) :: ptask_get_throw*',
                    'S_get_error = $resolve_at(S_get,S_get.RESULT,z_get_throw)',
                    'S_get_error.COMPLETION = NORMAL', 'S_get_error.RESULT = KNOWN (POBJECT n_error)']
                reached += reach('S_outer_discard','S_get','MA_OUTER_DISCARD') + [
                    'S_outer_discard.TODO = (THROW_SEARCH n_error) :: (PROPERTY_MAGIC_ADD_VALUE ppropertymagicadd) :: ptask_tail*',
                    '$property_magic_add_valid(S_outer_discard,ppropertymagicadd,PROPERTY_MAGIC_ADD_VALUE ppropertymagicadd)',
                    '$heap_owners($heap_graph(S_outer_discard),HOBJECT n_selected) = 1',
                    r'~$ma_in_get(S_outer_discard,n_selected) /\ ~$ma_in_set(S_outer_discard,n_selected) /\ $ma_guard(S_outer_discard)',
                    'PhpStep: S_outer_discard ~> S_outer_drop_raw',
                    'S_outer_drop_raw.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
                    '$heap_owners($heap_graph(S_outer_drop_raw),HOBJECT n_selected) = 0',
                    'S_throw_releasing = $ma_after(S_outer_discard,S_outer_drop_raw)']
            else:
                reached += reach('S_getresult','S_get','MA_GET_RESULT') + [
                    'S_getresult.TODO = (PROPERTY_GET_RESULT ppropertyget) :: (ORIGIN_RETURN (porigin_parent)) :: (PROPERTY_MAGIC_ADD_VALUE ppropertymagicadd) :: ptask_tail*',
                    'S_getresult.RESULT = KNOWN (PINT 5)',
                    r'ppropertyget.DECL = eps /\ ppropertymagicadd.PROPERTY = ppropertydesc.ORIGIN',
                    '$property_get_verify(S_getresult,ppropertyget,S_getresult.RESULT) = S_getresult',
                    'PhpStep: S_getresult ~> S_copy_raw',
                    'S_copy_raw.TODO = (PROPERTY_GET_COPY ppropertyget (KNOWN (PINT 5))) :: (ORIGIN_RETURN (porigin_parent)) :: (PROPERTY_MAGIC_ADD_VALUE ppropertymagicadd) :: ptask_tail*',
                    'S_copy_pending = $ma_after(S_getresult,S_copy_raw)',
                    *reach('S_copy','S_copy_pending','MA_GET_COPY'),
                    'S_copy.TODO = S_copy_raw.TODO',
                    '$heap_owners($heap_graph(S_copy),HOBJECT n_selected) = $(n_external + 1)',
                    r'~$ma_in_get(S_copy,n_selected) /\ $ma_guard(S_copy)']
                reached += reach('S_value','S_copy','MA_VALUE') + VALUE
                reached += reach('S_receive','S_set_call','MA_RECEIVE ppropertymagicset.METHOD') + RECEIVE
                reached += reach('S_set','S_receive','MA_SET_THROW' if name == 'set-throw' else 'MA_SET_RETURN') + SET
                if name == 'set-throw':
                    reached += ['S_set.TODO = (THROW_VALUE porigin_set_throw z_set_throw) :: ptask_set_throw*',
                        'S_set_error = $resolve_at(S_set,S_set.RESULT,z_set_throw)',
                        'S_set_error.COMPLETION = NORMAL', 'S_set_error.RESULT = KNOWN (POBJECT n_error)']
                    reached += reach('S_discard','S_set','MA_SET_DISCARD') + [
                        'S_discard.TODO = (THROW_SEARCH n_error) :: (PROPERTY_MAGIC_SET_RESULT ppropertymagicset) :: (PROPERTY_MAGIC_ADD_FINISH ppropertymagicadd 5 7) :: ptask_tail*',
                        r'$property_magic_set_valid(S_discard,ppropertymagicset) /\ $ma_guard(S_discard)',
                        'PhpStep: S_discard ~> S_inner_drop_raw',
                        'S_inner_releasing = $ma_after(S_discard,S_inner_drop_raw)',
                        *reach('S_inner_drop','S_inner_releasing','MA_FINISH_DISCARD'),
                        'S_inner_drop.TODO = (THROW_SEARCH n_error) :: (PROPERTY_MAGIC_ADD_FINISH ppropertymagicadd 5 7) :: ptask_tail*',
                        'S_inner_drop.RESULT = KNOWN PNULL',
                        '$heap_owners($heap_graph(S_inner_drop),HOBJECT n_selected) = 1',
                        r'$property_magic_add_sum(ppropertymagicadd,5,7) /\ $ma_guard(S_inner_drop)',
                        'PhpStep: S_inner_drop ~> S_outer_drop_raw',
                        'S_outer_drop_raw.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
                        '$heap_owners($heap_graph(S_outer_drop_raw),HOBJECT n_selected) = 0',
                        'S_throw_releasing = $ma_after(S_inner_drop,S_outer_drop_raw)']
                else:
                    reached += reach('S_setresult','S_set','MA_SET_RESULT') + NORMAL
                    if name == 'retarget':
                        reached += ['$heap_owners($heap_graph(S_release_raw),HOBJECT n_selected) = 1',
                            'S_release_raw.RESULT = KNOWN (PINT 7)',
                            'S_release_raw.TODO = ptask_tail*']
                        reached += reach('S_a','S_releasing','MA_OUTPUT ($ptascii(' + json.dumps(set_output + 'A|7/100|') + '))')
                        reached += ['S_a.STORE[n_result_cell] = DEFINED (PINT 7)',
                            'S_a.STORE[n_rhs_cell] = DEFINED (PINT 100)',
                            '$heap_owners($heap_graph(S_a),HOBJECT n_selected) = 1', '$ma_guard(S_a)', 'S_end = S_a']
                    else:
                        reached += ['$heap_owners($heap_graph(S_release_raw),HOBJECT n_selected) = 0']
                        reached += reach('S_child','S_releasing','MA_DTOR n_selected') + CHILD + [
                            'pdestructionoperation_child.SOURCE = PROPERTY_MAGIC_ADD_FINISH ppropertymagicadd 5 7',
                            r'pdestructionoperation_child.VALUE = KNOWN (PINT 7) /\ pdestructionoperation_child.PENDING = eps',
                            '$ma_output(S_child.EVENTS) = ptbytes_set', 'S_end = S_child']
            if name in ('get-throw','set-throw'):
                reached += reach('S_child','S_throw_releasing','MA_DTOR n_selected') + CHILD + [
                    'pdestructionoperation_child.SOURCE = THROW_SEARCH n_error',
                    r'pdestructionoperation_child.VALUE = KNOWN PNULL /\ pdestructionoperation_child.PENDING = (n_error)',
                    '$ma_output(S_child.EVENTS) = ' + ('ptbytes_get' if name == 'get-throw' else 'ptbytes_set')]
                reached += reach('S_catch','S_child','MA_CATCH') + CATCH + ['S_end = S_catch']
            reached += FINISH + [f'z_assign = {case["assignment_line"]}']
            derived = DERIVED if name == 'retarget' else []
            content = PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
            for condition in reached + derived:
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $main() = false -- otherwise\n'
            fixture = directory / 'property-addassign.watsup'
            fixture.write_text(content)
            row = {'id':name,'path':str(fixture),'sha256':sha(fixture),'reached_premises':len(reached),
                'derived_premises':len(derived),'premises':len(reached) + len(derived)}
            report['fixtures'].append(row)
            for key in ('premises','reached_premises','derived_premises'):
                report[key] += row[key]
        report.update(prepared=True,passed=True)
        if not args.prepare_only:
            for fixture in report['fixtures']:
                directory = Path(fixture['path']).parent
                process = recorder.recorded([str(compiler),'algo',*map(str,modules),fixture['path']],directory / 'compiler',90)
                passed = process['exit'] == 0 and not process['timeout'] and not process['interruption'] and not process['group_after'] and not (directory / 'compiler.stderr').read_bytes() and b'\ndef $main : bool =\n' in (directory / 'compiler.stdout').read_bytes()
                report['records'].append({'id':fixture['id'] + '-algorithmic-compilation','process':process,'passed':passed,'application_evaluations':0})
                report['passed'] = passed
                assert passed
                report['application_invocations'] += 1
                process = recorder.recorded([str(runner),'--sl',*map(str,modules),fixture['path']],directory / 'state',90)
                output = (directory / 'state.stdout').read_bytes()
                evaluated = process['exit'] == 0 and output in (b'true\n',b'false\n')
                report['application_evaluations'] += int(evaluated)
                passed = evaluated and not process['timeout'] and not process['interruption'] and not process['group_after'] and not (directory / 'state.stderr').read_bytes() and output == b'true\n'
                report['records'].append({'id':fixture['id'] + '-strict-SL-application','process':process,'passed':passed})
                report['passed'] = passed
                assert passed
    finally:
        report.update(inputs_stable=before == {str(path):sha(path) for path in watched},
            fixtures_stable=all(row['sha256'] == sha(Path(row['path'])) for row in report['fixtures']),
            head_stable=revision == git('rev-parse','HEAD'),status_stable=status == git('status','--short'))
        if not args.prepare_only:
            report['passed'] = (report['passed'] and len(report['records']) == 2 * len(selected)
                and all(row['passed'] for row in report['records'])
                and report['application_invocations'] == len(selected)
                and report['application_evaluations'] == len(selected))
        report['passed'] = report['passed'] and all(report[key] for key in ('inputs_stable','fixtures_stable','head_stable','status_stable'))
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report,indent=2) + '\n')
        print(json.dumps({key:report[key] for key in ('passed','application_evaluations','premises','reached_premises','derived_premises','inputs_stable','head_stable','status_stable')}),flush=True)
    assert report['passed']

if __name__ == '__main__':
    main()
