"""Check magic ??= read release, receiver re-fetch, cached RHS and abrupt writes."""
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
syntax pcastage = CA_PREP | CA_ISSET | CA_READ bool | CA_GET | CA_DECIDE | CA_RHS porigin | CA_WRITE | CA_RECEIVE porigin | CA_SET_RETURN | CA_SET_THROW | CA_THROW_DISCARD | CA_SET_RESULT | CA_DELIVERY | CA_DTOR nat | CA_CATCH
dec $ca_output(pevent*) : ptbytes
def $ca_output(eps) = eps
def $ca_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $ca_output(pevent*)
dec $ca_stage(pstate,pcastage) : bool
def $ca_stage(S,CA_PREP) = true
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $property_coalesce_assign_plan(S[.COMPLETION = NORMAL]) =/= eps
def $ca_stage(S,CA_ISSET) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_COALESCE_TARGET ppropertycoalesce false
  -- if S.TODO = (RETURN_UNWIND (KNOWN (PBOOL b)) porigin?) :: ptask_tail*
def $ca_stage(S,CA_READ b_get) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce b_get) :: ptask_tail*
def $ca_stage(S,CA_GET) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_COALESCE_TARGET ppropertycoalesce true
  -- if S.TODO = (RETURN_UNWIND (KNOWN pvalue) porigin?) :: ptask_tail*
def $ca_stage(S,CA_DECIDE) = true
  -- if S.TODO = (PROPERTY_COALESCE_ASSIGN_VALUE porigin pbase n_owner pcallcontext?) :: ptask_tail*
def $ca_stage(S,CA_RHS porigin) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.FUNCTION = porigin
  -- if S.TODO = (RETURN_UNWIND (KNOWN (PINT 7)) porigin_return?) :: ptask_tail*
def $ca_stage(S,CA_WRITE) = true
  -- if S.TODO = (COALESCE_ASSIGN_WRITE pbase false z) :: ptask_tail*
def $ca_stage(S,CA_RECEIVE porigin) = true
  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: ptask_tail*
def $ca_stage(S,CA_SET_RETURN) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_MAGIC_SET_TARGET ppropertymagicset
  -- if S.TODO = (RETURN_UNWIND (KNOWN PNULL) porigin?) :: ptask_tail*
def $ca_stage(S,CA_SET_THROW) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_MAGIC_SET_TARGET ppropertymagicset
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_tail*
def $ca_stage(S,CA_THROW_DISCARD) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_MAGIC_SET_RESULT ppropertymagicset) :: ptask_tail*
def $ca_stage(S,CA_SET_RESULT) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_MAGIC_SET_RESULT ppropertymagicset) :: ptask_tail*
def $ca_stage(S,CA_DELIVERY) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_MAGIC_SET_DELIVERY ppropertymagicset) :: ptask_tail*
def $ca_stage(S,CA_DTOR n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $ca_stage(S,CA_CATCH) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask_tail*
def $ca_stage(S,pcastage) = false -- otherwise
dec $ca_seek(pstate,pcastage,nat) : pstate
def $ca_seek(S,pcastage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $ca_stage(S,pcastage) \/ n = 0
def $ca_seek(S,pcastage,n) = $ca_seek($drive_steps(S[.COMPLETION = NORMAL],1),pcastage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$ca_stage(S,pcastage) /\ $(n > 0)
def $ca_seek(S,pcastage,n) = $ca_seek($drive_steps(S,1),pcastage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $ca_seek(S,pcastage,n) = S -- otherwise
dec $ca_after(pstate,pstate) : pstate
def $ca_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $ca_guard(pstate) : bool
def $ca_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $object_tables_valid(S) /\ $gc_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
dec $ca_in_isset(pstate,nat) : bool
def $ca_in_isset(S,n) = $property_isset_guard(S,S.CURRENT,S.FRAMES,n,$ptascii("value"))
dec $ca_in_get(pstate,nat) : bool
def $ca_in_get(S,n) = ($property_get_guard_tasks(S.TODO,n,$ptascii("value")) \/ $property_get_guard_frames(S.FRAMES,n,$ptascii("value")) \/ $property_empty_get_active(S,n,$ptascii("value")))
'''

def lines(text): return [line for line in text.strip().splitlines() if line]
def reach(name, previous, stage):
    return [f'{name}_found = $ca_seek({previous},{stage},2000)',
            fr'{name}_found.COMPLETION = NORMAL \/ {name}_found.COMPLETION = BUDGET',
            f'{name} = {name}_found[.COMPLETION = NORMAL]', f'$ca_stage({name},{stage})']

COMMON = lines(r'''
S_front.TODO = (COALESCE_ASSIGN_PREP expression_target expression_rhs z_assign) :: ptask_tail*
S_front.ORIGIN = (porigin_parent)
S_front.CURRENT = eps /\ S_front.FRAMES = eps
pbase_pending = S_front.BASE
pbase_pending = BASE_PROPERTY_PENDING (BASE_VALUE (VARIABLE ptbytes_cv z_cv)) (KNOWN (PSTRING ptbytes_name)) z_receiver
ptbytes_cv = $ptascii("child") /\ ptbytes_name = $ptascii("value")
$base_nodes(pbase_pending) = eps
$property_coalesce_assign_source(S_front,porigin_parent) /\ $property_coalesce_assign_base(S_front,porigin_parent,pbase_pending)
$lookup(S_front.ENV,$ptascii("child")) = (n_child_cell)
S_front.STORE[n_child_cell] = DEFINED (POBJECT n_old)
$lookup(S_front.ENV,$ptascii("error")) = (n_error_cell)
S_front.STORE[n_error_cell] = DEFINED (POBJECT n_error)
$lookup(S_front.ENV,$ptascii("result")) = (n_result_cell)
S_front.STORE[n_result_cell] = DEFINED (PINT 42)
$property_coalesce_assign_plan(S_front) = (ppropertycoalesce)
ppropertycoalesce.OBJECT = n_old /\ ppropertycoalesce.CALLER = eps /\ ppropertycoalesce.OWNER = 0
$origin_child((porigin_parent),[PCFIELD 0]) = (ppropertycoalesce.SITE)
ppropertycoalesce.TAIL = (ORIGIN_RETURN (porigin_parent)) :: (PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase_pending 0 eps) :: ptask_tail*
$task_nodes(PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase_pending 0 eps) = eps
$property_magic_coalesce_assign_pending(S_front)
$property_isset_method(S_front,n_old) = (pmethoddesc_isset)
$property_get_method(S_front,n_old) = (pmethoddesc_get)
$property_magic_set_method(S_front,n_old) = (pmethoddesc_set)
pmethoddesc_set.OWNER = pmethoddesc_isset.OWNER /\ pmethoddesc_get.OWNER = pmethoddesc_isset.OWNER
pmethoddesc_isset.OWNER =/= ppropertycoalesce.CLASS
$property_magic_method_source(S_front,pmethoddesc_isset,"__isset") /\ $property_empty_get_source(S_front,pmethoddesc_get) /\ $property_magic_set_method_source(S_front,pmethoddesc_set)
$property_effective_desc(S_front,n_old,$ptascii("value")) = (ppropertydesc)
ppropertydesc.VISIBILITY = PROPERTY_PRIVATE
porigin_parent = PORIGIN n_unit pcpath_parent
$code_at(S_front.CODE,n_unit) = (pcode)
$code_name(pcode.NAMES,pcpath_parent ++ [PCFIELD 1]) = ((preqbytes_rhs,preqbytes_fallback?))
$call_target(S_front,preqbytes_rhs,preqbytes_fallback?) = (pfunction_rhs)
~pfunction_rhs.SIGNATURE.BYREF /\ pfunction_rhs.SIGNATURE.PARAMETERS = eps
$ca_output(S_front.EVENTS) = ptbytes_prefix
$heap_owners($heap_graph(S_front),HOBJECT n_old) = 1
~$ca_in_isset(S_front,n_old) /\ ~$ca_in_get(S_front,n_old) /\ $ca_guard(S_front)
PhpStep: S_front ~> S_call_raw
S_call = $ca_after(S_front,S_call_raw)
$property_coalesce_capture(S_call,ppropertycoalesce) /\ $property_coalesce_pending_call(S_call,ppropertycoalesce,false)
$target_nodes(PROPERTY_COALESCE_TARGET ppropertycoalesce false) = eps
$task_nodes(PROPERTY_COALESCE_RESULT ppropertycoalesce false) = [HOBJECT n_old]
$heap_owners($heap_graph(S_call),HOBJECT n_old) = 2 /\ $ca_guard(S_call)
''')
ISSET = lines(r'''
S_isset.CURRENT = (pcallcontext_isset)
pcallcontext_isset.TARGET = PROPERTY_COALESCE_TARGET ppropertycoalesce false
pcallcontext_isset.LEXICAL_CLASS = (pmethoddesc_isset.OWNER) /\ pcallcontext_isset.CALLED_CLASS = (ppropertycoalesce.CLASS)
S_isset.TODO = (RETURN_UNWIND (KNOWN (PBOOL b_isset)) porigin_isset_return?) :: ptask_isset_return*
$property_coalesce_entered(S_isset,S_isset.CURRENT,S_isset.FRAMES,ppropertycoalesce,false)
$call_receiver_roots(pcallcontext_isset) = eps
S_isset.STORE[n_child_cell] = DEFINED (POBJECT n_old)
$heap_owners($heap_graph(S_isset),HOBJECT n_old) = 2
$ca_output(S_isset.EVENTS) = ptbytes_prefix ++ $ptascii("I1|")
$ca_in_isset(S_isset,n_old) /\ ~$ca_in_get(S_isset,n_old) /\ $ca_guard(S_isset)
''')
ISSET_RESULT = lines(r'''
S_isresult.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce false) :: ppropertycoalesce.TAIL
S_isresult.RESULT = KNOWN (PBOOL b_isset)
$property_coalesce_valid(S_isresult,ppropertycoalesce) /\ $property_coalesce_capture(S_isresult,ppropertycoalesce)
$heap_owners($heap_graph(S_isresult),HOBJECT n_old) = 2
~$ca_in_isset(S_isresult,n_old) /\ ~$ca_in_get(S_isresult,n_old) /\ $ca_guard(S_isresult)
''')
GET_CALL = lines(r'''
PhpStep: S_isresult ~> S_get_call_raw
S_get_call = $ca_after(S_isresult,S_get_call_raw)
$property_coalesce_pending_call(S_get_call,ppropertycoalesce,true)
''')
GET = lines(r'''
S_get.CURRENT = (pcallcontext_get)
pcallcontext_get.TARGET = PROPERTY_COALESCE_TARGET ppropertycoalesce true
pcallcontext_get.LEXICAL_CLASS = (pmethoddesc_get.OWNER) /\ pcallcontext_get.CALLED_CLASS = (ppropertycoalesce.CLASS)
S_get.TODO = (RETURN_UNWIND (KNOWN pvalue_read) porigin_get_return?) :: ptask_get_return*
$property_coalesce_entered(S_get,S_get.CURRENT,S_get.FRAMES,ppropertycoalesce,true)
$call_receiver_roots(pcallcontext_get) = eps
~$ca_in_isset(S_get,n_old) /\ $ca_in_get(S_get,n_old) /\ $ca_guard(S_get)
$ca_output(S_get.EVENTS) = ptbytes_prefix ++ $ptascii("I1|G1|")
''')
GET_RESULT = lines(r'''
S_getresult.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: ppropertycoalesce.TAIL
S_getresult.RESULT = KNOWN pvalue_read
$property_coalesce_valid(S_getresult,ppropertycoalesce)
~$ca_in_isset(S_getresult,n_old) /\ ~$ca_in_get(S_getresult,n_old) /\ $ca_guard(S_getresult)
S_before_release = S_getresult
b_get = true
''')
RELEASE = lines(r'''
PhpStep: S_before_release ~> S_release_raw
S_release_raw.TODO = (ORIGIN_RETURN (porigin_parent)) :: (PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase_pending 0 eps) :: ptask_tail*
S_release_raw.RESULT = KNOWN pvalue_read /\ S_release_raw.BASE = BASE_VALUE (KNOWN PNULL)
S_releasing = $ca_after(S_before_release,S_release_raw)
''')
DECISION = lines(r'''
S_decide.TODO = (PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase_pending 0 eps) :: ptask_tail*
S_decide.ORIGIN = (porigin_parent)
S_decide.RESULT = KNOWN pvalue_read /\ S_decide.BASE = BASE_VALUE (KNOWN PNULL)
$property_coalesce_assign_value_valid(S_decide,porigin_parent,pbase_pending,0,eps)
$call_task_valid(S_decide,PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase_pending 0 eps)
~$ca_in_isset(S_decide,n_old) /\ ~$ca_in_get(S_decide,n_old) /\ $ca_guard(S_decide)
''')
RHS = lines(r'''
S_rhs.CURRENT = (pcallcontext_rhs)
pcallcontext_rhs.FUNCTION = pfunction_rhs.ORIGIN
pcallcontext_rhs.RECEIVER = eps /\ pcallcontext_rhs.INSTANCE = eps
S_rhs.TODO = (RETURN_UNWIND (KNOWN (PINT 7)) porigin_rhs_return?) :: ptask_rhs_return*
S_rhs.STORE[n_result_cell] = DEFINED (PINT 42)
S_rhs.FRAMES = pframe_rhs :: eps
S_rhs_saved = $constant_frame_view(S_rhs,pframe_rhs,eps)
$property_coalesce_assign_source(S_rhs_saved,porigin_parent) /\ $property_coalesce_assign_base(S_rhs_saved,porigin_parent,pbase_pending)
$base_nodes(pbase_pending) = eps
~$ca_in_isset(S_rhs,n_old) /\ ~$ca_in_get(S_rhs,n_old) /\ $ca_guard(S_rhs)
''')
WRITE = lines(r'''
S_write.TODO = (COALESCE_ASSIGN_WRITE pbase_pending false z_assign) :: ptask_tail*
S_write.RESULT = KNOWN (PINT 7)
$property_magic_coalesce_write_pending(S_write)
$property_magic_coalesce_set_plan(S_write) = (ppropertymagicset)
ppropertymagicset.SITE = porigin_parent /\ ppropertymagicset.OBJECT = n_set
ppropertymagicset.RHS = KNOWN (PINT 7) /\ ppropertymagicset.CELL = eps /\ ppropertymagicset.INPUT = 7
ppropertymagicset.CALLER = eps /\ ppropertymagicset.OWNER = 0 /\ ppropertymagicset.TAIL = ptask_tail*
ppropertymagicset.CLASS = ppropertycoalesce.CLASS /\ ppropertymagicset.PROPERTY = ppropertycoalesce.PROPERTY
$property_magic_set_rhs_source(S_write,ppropertymagicset) /\ $ca_guard(S_write)
PhpStep: S_write ~> S_set_call_raw
S_set_call = $ca_after(S_write,S_set_call_raw)
$property_magic_set_capture(S_set_call,ppropertymagicset) /\ $property_magic_set_pending_call(S_set_call,ppropertymagicset)
$task_nodes(PROPERTY_MAGIC_SET_RESULT ppropertymagicset) = [HOBJECT n_set]
''')
RECEIVE = lines(r'''
S_receive.TODO = (TYPE_RECEIVE ppropertymagicset.METHOD 0) :: ptask_receive_tail*
S_receive.CURRENT = (pcallcontext_receive)
pcallcontext_receive.TARGET = PROPERTY_MAGIC_SET_TARGET ppropertymagicset
pcallcontext_receive.LEXICAL_CLASS = (pmethoddesc_set.OWNER) /\ pcallcontext_receive.CALLED_CLASS = (ppropertymagicset.CLASS)
$target_function(S_receive,pcallcontext_receive.TARGET) = (pmethoddesc_set.FUNCTION)
$receiving_function(S_receive,ppropertymagicset.METHOD) = (pmethoddesc_set.FUNCTION)
$call_receiver_roots(pcallcontext_receive) = eps
$lookup(S_receive.ENV,$ptascii("incoming")) = (n_incoming)
S_receive.STORE[n_incoming] = DEFINED (PINT 7)
$ca_guard(S_receive)
''')
SET_STABLE = lines(r'''
S_set.CURRENT = (pcallcontext_set)
pcallcontext_set.TARGET = PROPERTY_MAGIC_SET_TARGET ppropertymagicset
S_set.STORE[n_child_cell] = DEFINED PNULL
$lookup(S_front.ENV,$ptascii("rhs")) = (n_rhs_cell)
S_set.STORE[n_rhs_cell] = DEFINED (PINT 99)
S_set.STORE[n_incoming] = DEFINED (PINT 7)
$property_magic_set_entered(S_set,S_set.CURRENT,S_set.FRAMES,ppropertymagicset)
$property_magic_set_guard(S_set,S_set.CURRENT,S_set.FRAMES,n_set,$ptascii("value"))
S_set.FRAMES = pframe_set :: eps
S_set_saved = $constant_frame_view(S_set,pframe_set,eps)
$property_magic_set_valid(S_set_saved,ppropertymagicset) /\ ~$property_magic_set_capture(S_set_saved,ppropertymagicset)
~$ca_in_isset(S_set,n_set) /\ ~$ca_in_get(S_set,n_set) /\ $ca_guard(S_set)
$ca_output(S_set.EVENTS) = ptbytes_set
''')
RETARGET_SET = lines(r'''
S_set.TODO = (RETURN_UNWIND (KNOWN PNULL) porigin_set_return?) :: ptask_set_return*
$heap_owners($heap_graph(S_set),HOBJECT n_set) = 2
$objectprops_at(S_set.OBJECTPROPS,n_set) = (ppropertyslot_set*)
$property_slot_at(ppropertyslot_set*,ppropertydesc.KEY) = (ppropertyslot_written)
ppropertyslot_written.STATE = PROP_VALUE (DIRECT (PINT 7))
''')
SET_RESULT = lines(r'''
S_setresult.TODO = (PROPERTY_MAGIC_SET_RESULT ppropertymagicset) :: ptask_tail*
$property_magic_set_valid(S_setresult,ppropertymagicset) /\ ~$property_magic_set_capture(S_setresult,ppropertymagicset)
~$property_magic_set_guard(S_setresult,S_setresult.CURRENT,S_setresult.FRAMES,n_set,$ptascii("value"))
$ca_guard(S_setresult)
''')
DELIVERY = lines(r'''
S_delivery.TODO = (PROPERTY_MAGIC_SET_DELIVERY ppropertymagicset) :: ptask_tail*
$property_magic_set_delivery_valid(S_delivery,ppropertymagicset) /\ $property_magic_set_rhs(S_delivery,ppropertymagicset) = (7)
$task_nodes(PROPERTY_MAGIC_SET_DELIVERY ppropertymagicset) = eps
$heap_owners($heap_graph(S_delivery),HOBJECT n_set) = 1
S_delivery.STORE[n_rhs_cell] = DEFINED (PINT 99)
$ca_guard(S_delivery)
PhpStep: S_delivery ~> S_delivered_raw
S_delivered_raw.TODO = ptask_tail* /\ S_delivered_raw.RESULT = KNOWN (PINT 7)
S_end = $ca_after(S_delivery,S_delivered_raw)
''')
ZERO_CHILD = lines(r'''
S_child.CURRENT = (pcallcontext_child)
$destructor_context_call(pcallcontext_child,S_child.CURRENT,S_child.FRAMES) = (pdestructorcall_child)
pdestructorcall_child.OPERATION = (pdestructionoperation_child)
pdestructionoperation_child.SOURCE = PROPERTY_COALESCE_RESULT ppropertycoalesce true
pdestructionoperation_child.VALUE = KNOWN (PINT 0)
pdestructionoperation_child.BASE = BASE_VALUE (KNOWN PNULL)
pdestructionoperation_child.PENDING = eps
$ca_output(S_child.EVENTS) = $ptascii("Z:I1|G1|")
~$ca_in_isset(S_child,n_old) /\ ~$ca_in_get(S_child,n_old) /\ $ca_guard(S_child)
''')
ZERO_END = lines(r'''
~(HOBJECT n_old <- S_decide.ALLOCATIONS)
S_decide.STORE[n_child_cell] = DEFINED PNULL
$ca_output(S_decide.EVENTS) = $ptascii("Z:I1|G1|D1|")
PhpStep: S_decide ~> S_present_raw
S_present_raw.TODO = ptask_tail* /\ S_present_raw.RESULT = KNOWN (PINT 0)
S_end = $ca_after(S_decide,S_present_raw)
''')
NULL_WRITE = lines(r'''
S_write.TODO = (COALESCE_ASSIGN_WRITE pbase_pending false z_assign) :: ptask_tail*
S_write.RESULT = KNOWN (PINT 7)
S_write.STORE[n_child_cell] = DEFINED PNULL
~$property_magic_coalesce_write_pending(S_write) /\ $property_magic_coalesce_set_plan(S_write) = eps
$property_coalesce_assign_base(S_write,porigin_parent,pbase_pending) /\ $ca_guard(S_write)
''')
CATCH = lines(r'''
S_catch.TODO = (CATCH_BIND porigin_catch n_catch_index n_caught) :: ptask_catch_tail*
S_catch.STORE[n_result_cell] = DEFINED (PINT 42)
S_catch.STORE[n_child_cell] = DEFINED PNULL
~(HOBJECT n_old <- S_catch.ALLOCATIONS)
S_catch.OBJECTS[n_caught] = THROWABLE pthrowable_caught
$throwable_previous_id(S_catch,n_caught) = eps
~$ca_in_isset(S_catch,n_old) /\ ~$ca_in_get(S_catch,n_old) /\ $ca_guard(S_catch)
S_end = S_catch
''')
SET_THROW = lines(r'''
S_set.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_throw_tail*
$heap_owners($heap_graph(S_set),HOBJECT n_set) = 1
S_error_read = $resolve_at(S_set,S_set.RESULT,z_throw)
S_error_read.COMPLETION = NORMAL
S_error_read.RESULT = KNOWN (POBJECT n_error)
''')
THROW_DISCARD = lines(r'''
S_discard.TODO = (THROW_SEARCH n_error) :: (PROPERTY_MAGIC_SET_RESULT ppropertymagicset) :: ptask_tail*
$property_magic_set_valid(S_discard,ppropertymagicset) /\ ~$property_magic_set_capture(S_discard,ppropertymagicset)
~$property_magic_set_guard(S_discard,S_discard.CURRENT,S_discard.FRAMES,n_set,$ptascii("value"))
$ca_guard(S_discard)
PhpStep: S_discard ~> S_discard_raw
S_discard_raw.TODO = (THROW_SEARCH n_error) :: ptask_tail*
S_discard_raw.RESULT = KNOWN PNULL /\ S_discard_raw.BASE = BASE_VALUE (KNOWN PNULL)
$heap_owners($heap_graph(S_discard_raw),HOBJECT n_old) = 0
S_throw_releasing = $ca_after(S_discard,S_discard_raw)
''')
THROW_CHILD = lines(r'''
S_child.CURRENT = (pcallcontext_child)
$destructor_context_call(pcallcontext_child,S_child.CURRENT,S_child.FRAMES) = (pdestructorcall_child)
pdestructorcall_child.OPERATION = (pdestructionoperation_child)
pdestructionoperation_child.SOURCE = THROW_SEARCH n_error
pdestructionoperation_child.PENDING = (n_error)
pdestructionoperation_child.VALUE = KNOWN PNULL /\ pdestructionoperation_child.BASE = BASE_VALUE (KNOWN PNULL)
S_child.STORE[n_result_cell] = DEFINED (PINT 42)
$ca_output(S_child.EVENTS) = ptbytes_set
~$property_magic_set_guard(S_child,S_child.CURRENT,S_child.FRAMES,n_set,$ptascii("value"))
~$ca_in_isset(S_child,n_old) /\ ~$ca_in_get(S_child,n_old) /\ $ca_guard(S_child)
''')
FINISH = lines(r'''
S_final = $drive_steps(S_end,10000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps
$ca_output(S_final.EVENTS) = ptbytes_final
S_final.STORE[n_result_cell] = DEFINED (PINT i_result)
~(HOBJECT n_old <- S_final.ALLOCATIONS) /\ $ca_guard(S_final)
S_budget = $drive_steps(S_front,0)
S_budget = S_front[.COMPLETION = BUDGET]
$drive_steps(S_budget[.COMPLETION = NORMAL],10000) = S_final
''')
DERIVED = lines(r'''
~$property_coalesce_assign_value_valid(S_decide,porigin_parent,pbase_pending,1,eps)
~$property_coalesce_assign_value_valid(S_decide,porigin_parent,pbase_pending,0,(pcallcontext_isset))
pbase_wrong_line = BASE_PROPERTY_PENDING (BASE_VALUE (VARIABLE ptbytes_cv $(z_cv + 1))) (KNOWN (PSTRING ptbytes_name)) z_receiver
~$property_coalesce_assign_base(S_decide,porigin_parent,pbase_wrong_line)
S_wrong_origin = S_front[.ORIGIN = eps]
$property_coalesce_assign_plan(S_wrong_origin) = eps
ppropertycoalesce_wrong_line = ppropertycoalesce[.LINE = $(ppropertycoalesce.LINE + 1)]
~$property_coalesce_source(S_call,ppropertycoalesce_wrong_line)
S_wrong_name = S_front[.CODE = $compilation_code_replace(S_front.CODE,pcode[.NAMES = [CODENAME (pcpath_parent ++ [PCFIELD 1]) ($ptascii("absent111")) eps]])]
~$property_coalesce_assign_source(S_wrong_name,porigin_parent)
$property_magic_coalesce_assign_pending(S_wrong_name) /\ $property_coalesce_assign_plan(S_wrong_name) = eps
PhpStep: S_wrong_name ~> S_refused
S_refused.COMPLETION = UNSUPPORTED "magic coalesce assignment source or methods"
S_refused.EVENTS = S_wrong_name.EVENTS /\ S_refused.STORE = S_wrong_name.STORE /\ S_refused.ALLOCATIONS = S_wrong_name.ALLOCATIONS
''')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', action='append', choices=('retarget', 'zero', 'null-write', 'set-throw'))
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_coalesce_assignment_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile and data['native_observations_accepted']
    assert [case['id'] for case in data['cases']] == ['retarget', 'zero', 'null-write', 'set-throw']
    selected = data['cases']
    if args.case:
        assert len(args.case) == len(set(args.case))
        selected = [case for case in selected if case['id'] in args.case]
        assert len(selected) == len(args.case)
    php, adapter, bridge, worker, runner, compiler = (ROOT / name for name in [
        '.tools/php/bin/php', '_build/default/adapter/main.exe', '.tools/php-file.so',
        'frontend/worker.php', 'tests/semantics/_build/default/numeric_runner.exe', '.tools/spectec/bin/p4spectec'])
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    assert sha(compiler) == '26d77fb9bfae2b2868e137a94051f55f9b607660c340e9b22ae8300fb0d8ce88'
    assert sha(runner) == 'b57a2ed7daf86de23993a29d079083377cfef6da133739a164dbfdb9f11fd7a0'
    manifest = ROOT / 'spec/semantics/modules.json'
    modules = [ROOT / name for name in json.loads(manifest.read_bytes())]
    watched = [Path(__file__), Path(recorder.__file__), catalogue, profile_file, php, adapter, bridge, worker, runner, compiler,
               manifest, *modules, *(HERE / case['source_file'] for case in data['cases']),
               *(ROOT / name for name in ['spec/schema.json', 'spec/php.watsup', 'spec/nodes.json', 'frontend/target.php',
                    'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py'])]
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    assert revision == args.revision and not status, (revision, status)
    before = {str(path): sha(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='magic-coalesce-assignment-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    report = {'revision': revision, 'inputs': before, 'profile': profile, 'module_count': len(modules),
              'mode': 'SL', 'cache': False, 'det': True, 'records': [], 'fixtures': [], 'selection': [case['id'] for case in selected],
              'application_invocations': 0, 'application_evaluations': 0, 'source_agreements': 0,
              'premises': 0, 'reached_premises': 0, 'derived_premises': 0,
              'cap_seconds': 90, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent', 'jobs': 1}, 'passed': False}
    try:
        flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
        for case in selected:
            name = case['id']
            source = HERE / case['source_file']
            assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256']
            native_stderr = base64.b64decode(case['stderr_template_base64']).replace(b'{FILE}', case['original_source'].encode())
            native_tuple = base64.b64decode(case['stdout_base64']) + b'\0' + native_stderr + b'\0' + str(case['exit_status']).encode()
            assert hashlib.sha256(native_tuple).hexdigest() == case['native_raw_sha256']
            directory = out / name
            directory.mkdir()
            frontend = Worker([str(php), '-n', *flags, '-d', 'extension=' + str(bridge), str(worker)], directory / 'frontend')
            adapter_worker = None
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted'], parsed
                adapter_worker = Worker([str(adapter), str(ROOT)], directory / 'adapter')
                checked = adapter_worker.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                assert checked['ok'] and checked['ast'] == parsed['ast']
            finally:
                if adapter_worker:
                    adapter_worker.close()
                frontend.close()
            output = base64.b64decode(case['stdout_base64']).decode()
            before_output = {'retarget':'N:', 'zero':'Z:', 'null-write':'E:', 'set-throw':'X:'}[name]
            setup = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'ptbytes_prefix = $ptascii(' + json.dumps(before_output) + ')',
                     'ptbytes_final = $ptascii(' + json.dumps(output) + ')',
                     'b_isset = ' + ('true' if name in ('zero', 'null-write') else 'false'),
                     'pvalue_read = ' + ('PINT 0' if name == 'zero' else 'PNULL'),
                     'i_result = ' + ('0' if name == 'zero' else '7' if name == 'retarget' else '42')]
            reached = setup + reach('S_front', 'S_initial', 'CA_PREP') + COMMON
            reached += reach('S_isset', 'S_call', 'CA_ISSET') + ISSET
            reached += reach('S_isresult', 'S_isset', 'CA_READ false') + ISSET_RESULT
            if name in ('zero', 'null-write'):
                reached += GET_CALL + reach('S_get', 'S_get_call', 'CA_GET') + GET
                reached += ['S_get.STORE[n_child_cell] = DEFINED ' + ('PNULL' if name == 'zero' else '(POBJECT n_old)'),
                            '$heap_owners($heap_graph(S_get),HOBJECT n_old) = ' + ('1' if name == 'zero' else '2')]
                reached += reach('S_getresult', 'S_get', 'CA_READ true') + GET_RESULT
            else:
                reached += ['S_before_release = S_isresult', 'b_get = false']
            reached += RELEASE
            if name == 'zero':
                reached += ['$heap_owners($heap_graph(S_release_raw),HOBJECT n_old) = 0']
                reached += reach('S_child', 'S_releasing', 'CA_DTOR n_old') + ZERO_CHILD
                reached += reach('S_decide', 'S_child', 'CA_DECIDE') + DECISION + ZERO_END
            else:
                reached += reach('S_decide', 'S_releasing', 'CA_DECIDE') + DECISION
                reached += ['S_decide.STORE[n_child_cell] = DEFINED (POBJECT n_old)',
                            '$heap_owners($heap_graph(S_decide),HOBJECT n_old) = 1']
                if name == 'retarget':
                    reached += ['$lookup(S_front.ENV,$ptascii("replacement")) = (n_replacement_cell)',
                                'S_front.STORE[n_replacement_cell] = DEFINED (POBJECT n_new)', 'n_new =/= n_old']
                reached += reach('S_rhs', 'S_decide', 'CA_RHS pfunction_rhs.ORIGIN') + RHS
                if name in ('retarget', 'null-write'):
                    reached += ['~(HOBJECT n_old <- S_rhs.ALLOCATIONS)',
                                '$ca_output(S_rhs.EVENTS) = ptbytes_prefix ++ $ptascii(' + json.dumps('I1|R|D1|r|' if name == 'retarget' else 'I1|G1|R|D1|r|') + ')',
                                'S_rhs.STORE[n_child_cell] = DEFINED ' + ('(POBJECT n_new)' if name == 'retarget' else 'PNULL')]
                else:
                    reached += ['S_rhs.STORE[n_child_cell] = DEFINED (POBJECT n_old)',
                                '$ca_output(S_rhs.EVENTS) = $ptascii("X:I1|R|")']
                reached += reach('S_write', 'S_rhs', 'CA_WRITE')
                if name == 'null-write':
                    reached += NULL_WRITE + reach('S_catch', 'S_write', 'CA_CATCH') + CATCH
                    reached += ['n_caught =/= n_error', 'pthrowable_caught.KIND = "Error"',
                                '$string_bytes($throwable_field(S_catch,n_caught,"message")) = ($ptascii("Attempt to assign property ") ++ [34] ++ $ptascii("value") ++ [34] ++ $ptascii(" on null"))',
                                '$ca_output(S_catch.EVENTS) = $ptascii("E:I1|G1|R|D1|r|")']
                else:
                    reached += ['n_set = ' + ('n_new' if name == 'retarget' else 'n_old')] + WRITE
                    reached += reach('S_receive', 'S_set_call', 'CA_RECEIVE ppropertymagicset.METHOD') + RECEIVE
                    reached += ['ptbytes_set = $ptascii(' + json.dumps('N:I1|R|D1|r|S2:7|' if name == 'retarget' else 'X:I1|R|S1:7|') + ')']
                    reached += reach('S_set', 'S_receive', 'CA_SET_RETURN' if name == 'retarget' else 'CA_SET_THROW') + SET_STABLE
                    if name == 'retarget':
                        reached += RETARGET_SET
                        reached += reach('S_setresult', 'S_set', 'CA_SET_RESULT') + SET_RESULT
                        reached += reach('S_delivery', 'S_setresult', 'CA_DELIVERY') + DELIVERY
                    else:
                        reached += SET_THROW + reach('S_discard', 'S_set', 'CA_THROW_DISCARD') + THROW_DISCARD
                        reached += reach('S_child', 'S_throw_releasing', 'CA_DTOR n_old') + THROW_CHILD
                        reached += reach('S_catch', 'S_child', 'CA_CATCH') + CATCH
                        reached += ['n_caught = n_error', 'pthrowable_caught.KIND = "Exception"',
                                    '$ca_output(S_catch.EVENTS) = $ptascii("X:I1|R|S1:7|D1|")']
            reached += FINISH + [f'z_assign = {case["assignment_line"]}']
            if name == 'retarget':
                reached += ['~(HOBJECT n_new <- S_final.ALLOCATIONS)']
            derived = DERIVED if name == 'retarget' else []
            content = PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
            for condition in reached + derived:
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $main() = false -- otherwise\n'
            fixture = directory / 'coalesce-assignment.watsup'
            fixture.write_text(content)
            row = {'id': name, 'path': str(fixture), 'sha256': sha(fixture), 'reached_premises': len(reached), 'derived_premises': len(derived), 'premises': len(reached) + len(derived)}
            report['fixtures'].append(row)
            for key in ('premises', 'reached_premises', 'derived_premises'):
                report[key] += row[key]
        report.update(prepared=True, passed=True)
        if not args.prepare_only:
            for fixture in report['fixtures']:
                directory = Path(fixture['path']).parent
                process = recorder.recorded([str(compiler), 'algo', *map(str, modules), fixture['path']], directory / 'compiler', 90)
                passed = process['exit'] == 0 and not process['timeout'] and not process['interruption'] and not process['group_after'] and not (directory / 'compiler.stderr').read_bytes() and b'\ndef $main : bool =\n' in (directory / 'compiler.stdout').read_bytes()
                report['records'].append({'id': fixture['id'] + '-algorithmic-compilation', 'process': process, 'passed': passed, 'application_evaluations': 0})
                report['passed'] = passed
                assert passed
                report['application_invocations'] += 1
                process = recorder.recorded([str(runner), '--sl', *map(str, modules), fixture['path']], directory / 'state', 90)
                output = (directory / 'state.stdout').read_bytes()
                evaluated = process['exit'] == 0 and output in (b'true\n', b'false\n')
                report['application_evaluations'] += int(evaluated)
                passed = evaluated and not process['timeout'] and not process['interruption'] and not process['group_after'] and not (directory / 'state.stderr').read_bytes() and output == b'true\n'
                report['records'].append({'id': fixture['id'] + '-strict-SL-application', 'process': process, 'passed': passed})
                report['passed'] = passed
                assert passed
    finally:
        report.update(inputs_stable=before == {str(path): sha(path) for path in watched},
                      fixtures_stable=all(row['sha256'] == sha(Path(row['path'])) for row in report['fixtures']),
                      head_stable=revision == git('rev-parse', 'HEAD'), status_stable=status == git('status', '--short'))
        report['passed'] = report['passed'] and all(report[key] for key in ('inputs_stable', 'fixtures_stable', 'head_stable', 'status_stable'))
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({key: report[key] for key in ('passed', 'application_evaluations', 'premises', 'reached_premises', 'derived_premises', 'inputs_stable', 'head_stable', 'status_stable')}), flush=True)
    assert report['passed']

if __name__ == '__main__':
    main()

