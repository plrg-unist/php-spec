"""Check terminal empty's captured isset/get calls, integer truth and cleanup."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import error_handler_run as recorder
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()

PREFIX = r'''
dec $me_replace(pcoccurrence*,pcpath,pcnode) : pcoccurrence*
def $me_replace(eps,pcpath,pcnode) = eps
def $me_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath pcnode) :: pcoccurrence*
def $me_replace((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath_other pcnode_old) :: $me_replace(pcoccurrence*,pcpath,pcnode)
  -- if pcpath_other =/= pcpath
syntax pemptytest = ME_PREP | ME_ISSET ptbytes | ME_RESULT ptbytes bool | ME_THROW bool
dec $me_stage(pstate,pemptytest) : bool
def $me_stage(S,ME_PREP) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_PREP (NIdentifier (BYTES text) metadata) 23) :: ptask*
  -- if $base64(text) = $ptascii("skip")
def $me_stage(S,ME_ISSET ptbytes) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (ISSET_RESULT true z) :: ptask*
  -- if S.BASE = BASE_PROPERTY (POBJECT n) ptbytes
def $me_stage(S,ME_RESULT ptbytes b) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty b) :: ptask*
  -- if ppropertyempty.NAME = ptbytes
def $me_stage(S,ME_THROW b) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (THROW_SEARCH n) :: (PROPERTY_EMPTY_RESULT ppropertyempty b) :: ptask*
def $me_stage(S,pemptytest) = false -- otherwise
dec $me_seek(pstate,pemptytest,nat) : pstate
def $me_seek(S,pemptytest,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $me_stage(S,pemptytest) \/ n = 0
def $me_seek(S,pemptytest,n) = $me_seek($drive_steps(S[.COMPLETION = NORMAL],1),pemptytest,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$me_stage(S,pemptytest) /\ $(n > 0)
def $me_seek(S,pemptytest,n) = $me_seek($drive_steps(S,1),pemptytest,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $me_seek(S,pemptytest,n) = S -- otherwise
dec $me_after(pstate,pstate) : pstate
def $me_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $me_guard(pstate) : bool
def $me_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
dec $me_output(pevent*) : ptbytes
def $me_output(eps) = eps
def $me_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $me_output(pevent*)
'''

BODY = r'''
$me_stage(S,ME_ISSET ($ptascii("ready")))
$lookup(S.ENV,$ptascii("child")) = (n_child_cell)
S.STORE[n_child_cell] = DEFINED (POBJECT n_child)
$class_named(S.CLASSNAMES,$ptlc($ptascii("MagicEmptyParent83"))) = (porigin_parent)
$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)
$class_named(S.CLASSNAMES,$ptlc($ptascii("MagicEmptyChild83"))) = (porigin_child)
S.OBJECTS[n_child] = INSTANCE porigin_child
$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_parent)
$objectprops_at(S.OBJECTPROPS,n_child) = (ppropertyslot_initial*)
ppropertydesc_zero = pclassdesc_parent.PROPERTIES[1]
ppropertydesc_ready = pclassdesc_parent.PROPERTIES[3]
ppropertydesc_pending = pclassdesc_parent.PROPERTIES[4]
$property_slot_at(ppropertyslot_initial*,ppropertydesc_ready.KEY) = (ppropertyslot_ready)
$property_slot_at(ppropertyslot_initial*,ppropertydesc_pending.KEY) = (ppropertyslot_pending)
ppropertyslot_ready.STATE = PROP_VALUE (DIRECT (PINT 0)) /\ ppropertyslot_pending.STATE = PROP_INITIAL
~$property_empty_pending(S) /\ ~$property_isset_pending(S) /\ $property_empty_plan(S) = eps
S.TODO = (ISSET_RESULT true 22) :: ptask_ready_tail*
$me_guard(S)
PhpStep: S ~> S_ready_raw
S_ready = $me_after(S,S_ready_raw)
S_ready.RESULT = KNOWN (PBOOL true) /\ S_ready.TODO = ptask_ready_tail* /\ S_ready.EVENTS = S.EVENTS /\ S_ready.OBJECTPROPS = S.OBJECTPROPS
S_pending_found = $me_seek(S_ready,ME_ISSET ($ptascii("pending")),1000)
S_pending_found.COMPLETION = NORMAL \/ S_pending_found.COMPLETION = BUDGET
S_pending = S_pending_found[.COMPLETION = NORMAL]
$me_stage(S_pending,ME_ISSET ($ptascii("pending")))
~$property_empty_pending(S_pending) /\ ~$property_isset_pending(S_pending)
PhpStep: S_pending ~> S_pending_raw
S_pending_done = $me_after(S_pending,S_pending_raw)
S_pending_done.RESULT = KNOWN (PBOOL true) /\ S_pending_done.EVENTS = S_pending.EVENTS
S_prep_found = $me_seek(S_pending_done,ME_PREP,1000)
S_prep_found.COMPLETION = NORMAL \/ S_prep_found.COMPLETION = BUDGET
S_prep = S_prep_found[.COMPLETION = NORMAL]
$me_stage(S_prep,ME_PREP) /\ $property_empty_prepare(S_prep) /\ ~$property_get_pending(S_prep)
S_prep.TODO = (PROPERTY_PREP phpType20_prep 23) :: (ORIGIN_RETURN (porigin_skip)) :: (ISSET_RESULT true 23) :: ptask_skip_tail*
$property_empty_source(S_prep,porigin_skip,$ptascii("skip"),23)
S_skip_found = $me_seek(S_prep,ME_ISSET ($ptascii("skip")),1000)
S_skip_found.COMPLETION = NORMAL \/ S_skip_found.COMPLETION = BUDGET
S_skip = S_skip_found[.COMPLETION = NORMAL]
$me_stage(S_skip,ME_ISSET ($ptascii("skip")))
$me_output(S_skip.EVENTS) = $ptascii("P:T/T|S:")
$property_empty_pending(S_skip) /\ $property_isset_pending(S_skip) /\ $property_isset_plan(S_skip) = eps
$property_empty_plan(S_skip) = (ppropertyempty_skip)
ppropertyempty_skip.SITE = porigin_skip /\ ppropertyempty_skip.NAME = $ptascii("skip") /\ ppropertyempty_skip.LINE = 23 /\ ppropertyempty_skip.OBJECT = n_child /\ ppropertyempty_skip.CLASS = porigin_child
$property_empty_function(S_skip,ppropertyempty_skip,false) = (pfunction_isset)
$property_empty_function(S_skip,ppropertyempty_skip,true) = (pfunction_get)
ppropertyempty_skip.ISSET = pfunction_isset.ORIGIN /\ ppropertyempty_skip.GET = pfunction_get.ORIGIN
porigin_isset = pfunction_isset.ORIGIN
porigin_get = pfunction_get.ORIGIN
$property_empty_method(S_skip,n_child,false) = (pmethoddesc_isset)
$property_empty_method(S_skip,n_child,true) = (pmethoddesc_get)
pmethoddesc_isset.OWNER = porigin_parent /\ pmethoddesc_get.OWNER = porigin_parent
pfunction_get.ORIGIN = PORIGIN n_source pcpath_get
$source_unit(S_skip.SOURCES,n_source) = (pcunit_source)
S_skip.SOURCES = [pcunit_source]
$origin_node(S_skip.SOURCES,pfunction_get.ORIGIN) = (NStmtClassMethod phpType14_get phpType24_get phpType4_get phpType11_get phpType16_get phpType18_get (SEQUENCE statement_get*) metadata_get)
$property_magic_method_source(S_skip,pmethoddesc_isset,"__isset") /\ $property_empty_get_source(S_skip,pmethoddesc_get)
$property_empty_valid(S_skip,ppropertyempty_skip) /\ $property_empty_capture(S_skip,ppropertyempty_skip) /\ ~$property_empty_guard(S_skip,n_child,$ptascii("skip"))
PhpStep: S_skip ~> S_isset_call_raw
S_isset_call = $me_after(S_skip,S_isset_call_raw)
S_isset_call.TODO = (CALL_ARGS (PROPERTY_EMPTY_TARGET ppropertyempty_skip false) eps 1 ([KNOWN (PSTRING ($ptascii("skip")))]) (porigin_skip) 23) :: (PROPERTY_EMPTY_RESULT ppropertyempty_skip false) :: ptask_skip_tail*
$property_empty_pending_call(S_isset_call,ppropertyempty_skip,false) /\ $me_guard(S_isset_call)
$task_nodes(PROPERTY_EMPTY_RESULT ppropertyempty_skip false) = [HOBJECT n_child] /\ $target_nodes(PROPERTY_EMPTY_TARGET ppropertyempty_skip false) = eps
$heap_owners($heap_graph(S_skip),HOBJECT n_child) = $heap_owners($heap_graph(S_isset_call),HOBJECT n_child)
PhpStep: S_isset_call ~> S_isset_entered_raw
S_isset_entered = $me_after(S_isset_call,S_isset_entered_raw)
S_isset_entered.CURRENT = (pcallcontext_isset)
pcallcontext_isset.TARGET = PROPERTY_EMPTY_TARGET ppropertyempty_skip false /\ pcallcontext_isset.RECEIVER = (n_child) /\ pcallcontext_isset.LEXICAL_CLASS = (porigin_parent) /\ pcallcontext_isset.CALLED_CLASS = (porigin_child)
S_isset_entered.FRAMES = [pframe_isset]
$property_empty_context(S_isset_entered,pcallcontext_isset) /\ $property_empty_frame(S_isset_entered,pcallcontext_isset,pframe_isset,ppropertyempty_skip,false)
$property_empty_guard(S_isset_entered,n_child,$ptascii("skip")) /\ ~$property_empty_get_active(S_isset_entered,n_child,$ptascii("skip"))
$call_receiver_roots(pcallcontext_isset) = eps /\ $me_guard(S_isset_entered)
S_false_found = $me_seek(S_isset_entered,ME_RESULT ($ptascii("skip")) false,1000)
S_false_found.COMPLETION = NORMAL \/ S_false_found.COMPLETION = BUDGET
S_false = S_false_found[.COMPLETION = NORMAL]
$me_stage(S_false,ME_RESULT ($ptascii("skip")) false)
S_false.RESULT = KNOWN (PBOOL false) /\ S_false.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty_skip false) :: ptask_skip_tail* /\ S_false.FRAMES = eps
$me_output(S_false.EVENTS) = $ptascii("P:T/T|S:I:skip/MagicEmptyParent83/MagicEmptyChild83/MagicEmptyParent83::__isset|")
n_false_owners = $heap_owners($heap_graph(S_false),HOBJECT n_child)
PhpStep: S_false ~> S_false_raw
S_false_done = $me_after(S_false,S_false_raw)
S_false_done.RESULT = KNOWN (PBOOL true) /\ S_false_done.TODO = ptask_skip_tail* /\ S_false_done.EVENTS = S_false.EVENTS
n_false_owners = $($heap_owners($heap_graph(S_false_done),HOBJECT n_child) + 1)
S_zero_found = $me_seek(S_false_done,ME_ISSET ($ptascii("zero")),1000)
S_zero_found.COMPLETION = NORMAL \/ S_zero_found.COMPLETION = BUDGET
S_zero = S_zero_found[.COMPLETION = NORMAL]
$me_stage(S_zero,ME_ISSET ($ptascii("zero")))
$property_empty_plan(S_zero) = (ppropertyempty_zero)
ppropertyempty_zero.PROPERTY = ppropertydesc_zero.ORIGIN /\ ppropertyempty_zero.OBJECT = n_child /\ ppropertyempty_zero.GET = pfunction_get.ORIGIN
S_true_found = $me_seek(S_zero,ME_RESULT ($ptascii("zero")) false,1000)
S_true_found.COMPLETION = NORMAL \/ S_true_found.COMPLETION = BUDGET
S_true = S_true_found[.COMPLETION = NORMAL]
$me_stage(S_true,ME_RESULT ($ptascii("zero")) false)
S_true.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty_zero false) :: ptask_zero_tail*
S_true.RESULT = KNOWN (PBOOL true)
$property_empty_valid(S_true,ppropertyempty_zero) /\ $me_guard(S_true)
PhpStep: S_true ~> S_get_call_raw
S_get_call = $me_after(S_true,S_get_call_raw)
S_get_call.TODO = (CALL_ARGS (PROPERTY_EMPTY_TARGET ppropertyempty_zero true) eps 1 ([KNOWN (PSTRING ($ptascii("zero")))]) (ppropertyempty_zero.SITE) 24) :: (PROPERTY_EMPTY_RESULT ppropertyempty_zero true) :: ptask_zero_tail*
S_get_call.RESULT = KNOWN PNULL /\ S_get_call.EVENTS = S_true.EVENTS
$property_empty_pending_call(S_get_call,ppropertyempty_zero,true) /\ $me_guard(S_get_call)
$heap_owners($heap_graph(S_get_call),HOBJECT n_child) = $heap_owners($heap_graph(S_true),HOBJECT n_child)
PhpStep: S_get_call ~> S_get_entered_raw
S_get_entered = $me_after(S_get_call,S_get_entered_raw)
S_get_entered.CURRENT = (pcallcontext_get)
pcallcontext_get.TARGET = PROPERTY_EMPTY_TARGET ppropertyempty_zero true /\ pcallcontext_get.FUNCTION = pfunction_get.ORIGIN /\ pcallcontext_get.RECEIVER = (n_child) /\ pcallcontext_get.LEXICAL_CLASS = (porigin_parent) /\ pcallcontext_get.CALLED_CLASS = (porigin_child)
$property_empty_context(S_get_entered,pcallcontext_get) /\ $property_empty_guard(S_get_entered,n_child,$ptascii("zero")) /\ $property_empty_get_active(S_get_entered,n_child,$ptascii("zero"))
~$property_empty_get_active(S_get_entered,n_child,$ptascii("full")) /\ $call_receiver_roots(pcallcontext_get) = eps /\ $me_guard(S_get_entered)
S_zero_result_found = $me_seek(S_get_entered,ME_RESULT ($ptascii("zero")) true,1000)
S_zero_result_found.COMPLETION = NORMAL \/ S_zero_result_found.COMPLETION = BUDGET
S_zero_result = S_zero_result_found[.COMPLETION = NORMAL]
$me_stage(S_zero_result,ME_RESULT ($ptascii("zero")) true)
S_zero_result.RESULT = KNOWN (PINT 0) /\ S_zero_result.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty_zero true) :: ptask_zero_tail* /\ S_zero_result.FRAMES = eps
n_zero_owners = $heap_owners($heap_graph(S_zero_result),HOBJECT n_child)
PhpStep: S_zero_result ~> S_zero_raw
S_zero_done = $me_after(S_zero_result,S_zero_raw)
S_zero_done.RESULT = KNOWN (PBOOL true) /\ S_zero_done.TODO = ptask_zero_tail* /\ S_zero_done.EVENTS = S_zero_result.EVENTS
n_zero_owners = $($heap_owners($heap_graph(S_zero_done),HOBJECT n_child) + 1)
S_full_found = $me_seek(S_zero_done,ME_RESULT ($ptascii("full")) true,1000)
S_full_found.COMPLETION = NORMAL \/ S_full_found.COMPLETION = BUDGET
S_full = S_full_found[.COMPLETION = NORMAL]
$me_stage(S_full,ME_RESULT ($ptascii("full")) true)
S_full.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty_full true) :: ptask_full_tail*
S_full.RESULT = KNOWN (PINT 13)
PhpStep: S_full ~> S_full_raw
S_full_done = $me_after(S_full,S_full_raw)
S_full_done.RESULT = KNOWN (PBOOL false) /\ S_full_done.TODO = ptask_full_tail* /\ S_full_done.EVENTS = S_full.EVENTS
S_final = $drive_steps(S_full_done,10000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps
$me_output(S_final.EVENTS) = $ptascii("P:T/T|S:I:skip/MagicEmptyParent83/MagicEmptyChild83/MagicEmptyParent83::__isset|T|Z:I:zero/MagicEmptyParent83/MagicEmptyChild83/MagicEmptyParent83::__isset|G:zero/MagicEmptyParent83/MagicEmptyChild83/MagicEmptyParent83::__get|T|F:I:full/MagicEmptyParent83/MagicEmptyChild83/MagicEmptyParent83::__isset|G:full/MagicEmptyParent83/MagicEmptyChild83/MagicEmptyParent83::__get|F|R:ONLY|")
S_final.OBJECTPROPS = S.OBJECTPROPS /\ $me_guard(S_final)
S_budget = $drive_steps(S_get_call,0)
S_budget.COMPLETION = BUDGET /\ S_budget.TODO = S_get_call.TODO /\ S_budget.OBJECTPROPS = S_get_call.OBJECTPROPS
$drive_steps(S_budget[.COMPLETION = NORMAL],10000) = S_final
'''.strip().splitlines()

DERIVED = r'''
S_wrong_prep = S_prep[.TODO = (PROPERTY_PREP phpType20_prep 23) :: ptask_skip_tail*]
~$property_empty_prepare(S_wrong_prep) /\ $property_get_pending(S_wrong_prep)
S_wrong_mode = S_prep[.TODO = (PROPERTY_PREP phpType20_prep 23) :: (ORIGIN_RETURN (porigin_skip)) :: (ISSET_RESULT false 23) :: ptask_skip_tail*]
~$property_empty_prepare(S_wrong_mode) /\ $property_get_pending(S_wrong_mode)
~$property_empty_source(S_skip,porigin_skip,$ptascii("zero"),23) /\ ~$property_empty_source(S_skip,porigin_skip,$ptascii("skip"),24)
porigin_ready = ppropertydesc_ready.ORIGIN
~$property_empty_valid(S_skip,ppropertyempty_skip[.PROPERTY = porigin_ready])
~$property_empty_valid(S_skip,ppropertyempty_skip[.GET = porigin_isset])
S_source_missing = S_skip[.SOURCES = ([pcunit_source[.OCCURRENCES = $me_replace(pcunit_source.OCCURRENCES,pcpath_get,NStmtNop metadata_get)]])]
~$property_empty_get_source(S_source_missing,pmethoddesc_get) /\ $property_empty_function(S_source_missing,ppropertyempty_skip,true) = eps
$property_empty_pending(S_source_missing) /\ $property_empty_plan(S_source_missing) = eps
PhpStep: S_source_missing ~> S_source_done
S_source_done.COMPLETION = UNSUPPORTED "magic empty source, methods, or recursive access"
S_no_result = S_get_call[.TODO = (CALL_ARGS (PROPERTY_EMPTY_TARGET ppropertyempty_zero true) eps 1 ([KNOWN (PSTRING ($ptascii("zero")))]) (ppropertyempty_zero.SITE) 24) :: ptask_zero_tail*]
~$property_empty_pending_call(S_no_result,ppropertyempty_zero,true)
S_wrong_arg = S_get_call[.TODO = (CALL_ARGS (PROPERTY_EMPTY_TARGET ppropertyempty_zero true) eps 1 ([KNOWN (PSTRING ($ptascii("full")))]) (ppropertyempty_zero.SITE) 24) :: (PROPERTY_EMPTY_RESULT ppropertyempty_zero true) :: ptask_zero_tail*]
~$property_empty_pending_call(S_wrong_arg,ppropertyempty_zero,true)
S_direct = S_get_entered[.CURRENT = (pcallcontext_get[.TARGET = METHOD_TARGET n_child porigin_get])]
~$property_empty_guard(S_direct,n_child,$ptascii("zero")) /\ ~$property_empty_get_active(S_direct,n_child,$ptascii("zero"))
~$property_empty_active(S_get_entered,S_get_entered.CURRENT,eps,n_child,$ptascii("zero"),true)
S_private_active = S_get_entered[.TODO = [(ISSET_RESULT true 24)]][.ORIGIN = (ppropertyempty_zero.SITE)][.BASE = BASE_PROPERTY (POBJECT n_child) ($ptascii("zero"))][.RESULT = KNOWN PNULL]
$property_empty_guard(S_private_active,n_child,$ptascii("zero")) /\ $property_resolve(S_private_active,n_child,$ptascii("zero")) = PROPERTY_ACCESS ppropertydesc_zero.KEY
~$property_isset_needed(S_private_active,n_child,$ptascii("zero")) /\ ~$property_empty_pending(S_private_active) /\ $property_empty_plan(S_private_active) = eps
PhpStep: S_private_active ~> S_private_raw
S_private_done = $me_after(S_private_active,S_private_raw)
S_private_done.RESULT = KNOWN (PBOOL false) /\ S_private_done.TODO = eps /\ S_private_done.EVENTS = S_private_active.EVENTS
S_nonint = S_zero_result[.RESULT = KNOWN (PFLOAT 0)]
PhpStep: S_nonint ~> S_nonint_done
S_nonint_done.COMPLETION = UNSUPPORTED "magic empty getter result type" /\ S_nonint_done.TODO = S_nonint.TODO /\ S_nonint_done.EVENTS = S_nonint.EVENTS
S_rebound_raw = S_true[.STORE[n_child_cell] = DEFINED PNULL]
S_rebound = $me_after(S_true,S_rebound_raw)
$property_empty_valid(S_rebound,ppropertyempty_zero) /\ ~$property_empty_capture(S_rebound,ppropertyempty_zero) /\ $me_guard(S_rebound)
PhpStep: S_rebound ~> S_rebound_call_raw
S_rebound_call = $me_after(S_rebound,S_rebound_call_raw)
$property_empty_pending_call(S_rebound_call,ppropertyempty_zero,true) /\ S_rebound_call.TODO = S_get_call.TODO
S_rebound_found = $me_seek(S_rebound_call,ME_RESULT ($ptascii("zero")) true,1000)
S_rebound_found.COMPLETION = NORMAL \/ S_rebound_found.COMPLETION = BUDGET
S_rebound_result = S_rebound_found[.COMPLETION = NORMAL]
$me_stage(S_rebound_result,ME_RESULT ($ptascii("zero")) true) /\ S_rebound_result.RESULT = KNOWN (PINT 0)
S_rebound_result.STORE[n_child_cell] = DEFINED PNULL /\ $property_empty_valid(S_rebound_result,ppropertyempty_zero) /\ $me_guard(S_rebound_result)
'''.strip().splitlines()

for label, state, record, getter in [('isset', 'S_isset_entered', 'ppropertyempty_skip', 'false'),
                                     ('get', 'S_get_entered', 'ppropertyempty_zero', 'true')]:
    DERIVED += [
        f'S_abrupt_{label} = $throwable_materialize($throw_scalar({state},"Error",$ptascii("cleanup"),13))',
        f'S_abrupt_{label}.COMPLETION = THROWING n_throw_{label}',
        f'S_throw_found_{label} = $me_seek(S_abrupt_{label},ME_THROW {getter},1000)',
        f'S_throw_found_{label}.COMPLETION = NORMAL \\/ S_throw_found_{label}.COMPLETION = BUDGET',
        f'S_throw_{label} = S_throw_found_{label}[.COMPLETION = NORMAL]',
        f'$me_stage(S_throw_{label},ME_THROW {getter})',
        f'S_throw_{label}.TODO = (THROW_SEARCH n_throw_{label}) :: (PROPERTY_EMPTY_RESULT {record} {getter}) :: ptask_throw_{label}*',
        f'S_throw_{label}.CURRENT = eps /\\ S_throw_{label}.FRAMES = eps',
        f'$property_empty_throw_tail(S_throw_{label},{record},{getter}) /\\ $call_task_valid(S_throw_{label},PROPERTY_EMPTY_RESULT {record} {getter}) /\\ $me_guard(S_throw_{label})',
        f'n_throw_owners_{label} = $heap_owners($heap_graph(S_throw_{label}),HOBJECT n_child)',
        f'PhpStep: S_throw_{label} ~> S_discard_raw_{label}',
        f'S_discard_{label} = $me_after(S_throw_{label},S_discard_raw_{label})',
        f'S_discard_{label}.TODO = (THROW_SEARCH n_throw_{label}) :: ptask_throw_{label}* /\\ S_discard_{label}.EVENTS = S_throw_{label}.EVENTS',
        f'n_throw_owners_{label} = $($heap_owners($heap_graph(S_discard_{label}),HOBJECT n_child) + 1)',
        f'~$property_empty_throw_tail(S_discard_{label},{record},{getter}) /\\ $me_guard(S_discard_{label})',
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_empty_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file, source = HERE / 'profile.json', HERE / 'magic-empty.php'
    profile = json.loads(profile_file.read_bytes())
    case = data['cases'][0]
    assert data['native_profile'] == profile
    assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256']
    php, adapter, bridge, worker, runner, compiler = (ROOT / name for name in [
        '.tools/php/bin/php', '_build/default/adapter/main.exe', '.tools/php-file.so',
        'frontend/worker.php', 'tests/semantics/_build/default/numeric_runner.exe', '.tools/spectec/bin/p4spectec'])
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    assert sha(compiler) == '26d77fb9bfae2b2868e137a94051f55f9b607660c340e9b22ae8300fb0d8ce88'
    assert sha(runner) == 'b57a2ed7daf86de23993a29d079083377cfef6da133739a164dbfdb9f11fd7a0'
    manifest = ROOT / 'spec/semantics/modules.json'
    modules = [ROOT / name for name in json.loads(manifest.read_bytes())]
    watched = [Path(__file__), Path(recorder.__file__), catalogue, source, profile_file, php,
               adapter, bridge, worker, runner, compiler, manifest, *modules, ROOT / 'spec/schema.json',
               ROOT / 'spec/php.watsup', ROOT / 'spec/nodes.json', ROOT / 'frontend/target.php',
               ROOT / 'frontend/wire.php', ROOT / 'frontend/wire.py', HERE / 'recorded_worker.py', HERE / 'static_types.py']
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    assert revision == args.revision and not status, (revision, status)
    before = {str(path): sha(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='magic-empty-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    report = {'revision': revision, 'inputs': before, 'profile': profile, 'module_count': len(modules),
              'mode': 'SL', 'cache': False, 'det': True, 'records': [],
              'application_invocations': 0, 'application_evaluations': 0, 'source_agreements': 0,
              'derived_premises': len(DERIVED), 'reached_premises': 5 + len(BODY), 'premises': 5 + len(BODY) + len(DERIVED),
              'cap_seconds': 90, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'jobs': 1}, 'passed': False}
    fixture = None
    try:
        flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
        frontend = Worker([str(php), '-n', *flags, '-d', 'extension=' + str(bridge), str(worker)], out / 'frontend')
        adapter_worker = None
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'], parsed
            adapter_worker = Worker([str(adapter), str(ROOT)], out / 'adapter')
            checked = adapter_worker.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] and checked['ast'] == parsed['ast']
        finally:
            if adapter_worker:
                adapter_worker.close()
            frontend.close()
        setup = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                 r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                 'S_found = $me_seek(S_initial,ME_ISSET ($ptascii("ready")),1000)',
                 r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                 'S = S_found[.COMPLETION = NORMAL]']
        content = PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
        for condition in setup + BODY + DERIVED:
            content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
        content += 'def $main() = false -- otherwise\n'
        fixture = out / 'hook.watsup'
        fixture.write_text(content)
        report.update(fixture=str(fixture), fixture_sha256=sha(fixture), prepared=True, passed=True)
        if not args.prepare_only:
            process = recorder.recorded([str(compiler), 'algo', *map(str, modules), str(fixture)], out / 'compiler', 90)
            passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and not (out / 'compiler.stderr').read_bytes() and b'\ndef $main : bool =\n' in (out / 'compiler.stdout').read_bytes()
            report['records'].append({'id': 'algorithmic-compilation', 'process': process, 'passed': passed, 'application_evaluations': 0})
            report['passed'] = passed
            assert passed
            report['application_invocations'] = 1
            process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'state', 90)
            output = (out / 'state.stdout').read_bytes()
            evaluated = process['exit'] == 0 and output in (b'true\n', b'false\n')
            report['application_evaluations'] = int(evaluated)
            passed = evaluated and not process['timeout'] and not process['group_after'] and not (out / 'state.stderr').read_bytes() and output == b'true\n'
            report['records'].append({'id': 'strict-SL-application', 'process': process, 'passed': passed})
            report['passed'] = passed
    finally:
        report.update(inputs_stable=before == {str(path): sha(path) for path in watched},
                      fixture_stable=fixture is None or report['fixture_sha256'] == sha(fixture),
                      head_stable=revision == git('rev-parse', 'HEAD'), status_stable=status == git('status', '--short'))
        report['passed'] = report['passed'] and all(report[key] for key in ('inputs_stable', 'fixture_stable', 'head_stable', 'status_stable'))
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({key: report[key] for key in ('passed', 'application_evaluations', 'derived_premises', 'reached_premises', 'inputs_stable', 'head_stable', 'status_stable')}), flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
