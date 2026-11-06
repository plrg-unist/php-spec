#!/usr/bin/env python3
"""Real residual Parent RC, shared Child edges, GC closure and STORE order."""
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc69_peer_shared_property_rc.php').read_text()
STAGE = (
    'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: '
    '(ENUM_IS_CALLABLE_OUTPUT penumqueryoutput) :: ptask_after_output* '
    '-- if pdestructionoperation.SOURCE = ENUM_IS_CALLABLE_CLEAR penumqueryoutput '
    '-- if penumqueryoutput.OLD = HOBJECT n_old '
    '-- if S.STORE[penumqueryoutput.CELL] = DEFINED (POBJECT n_parent) '
    '-- if $object_name(S, n_parent) = $ptascii("GC69ParentPeer")')

DECLARATIONS = r'''syntax pgc69stage = RECOVER | DROP | TRACE | CHILD | PARENT
dec $gc69_at(pstate, pgc69stage, nat, nat) : bool
def $gc69_at(S, RECOVER, n_parent, n_child) = true
  -- if $lookup(S.ENV, $ptascii("recovered")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (POBJECT n_parent)
  -- if $heap_owners($heap_graph(S), HOBJECT n_parent) = 1
def $gc69_at(S, DROP, n_parent, n_child) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*
  -- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_parent)) :: pdestructionjob_tail*
  -- if $heap_owners($heap_graph(S), HOBJECT n_parent) = 1
def $gc69_at(S, TRACE, n_parent, n_child) = true
  -- if S.TODO = (GC_TRACE pgccall) :: ptask_tail*
def $gc69_at(S, CHILD, n_parent, n_child) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.STORE /\ pdestructorcall.OBJECT = n_child
def $gc69_at(S, PARENT, n_parent, n_child) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.STORE /\ pdestructorcall.OBJECT = n_parent
def $gc69_at(S, pgc69stage, n_parent, n_child) = false -- otherwise
dec $gc69_seek(pstate, pgc69stage, nat, nat, nat) : pstate
def $gc69_seek(S, pgc69stage, n_parent, n_child, n) = S
  -- if $gc69_at(S, pgc69stage, n_parent, n_child)
def $gc69_seek(S, pgc69stage, n_parent, n_child, n) = $gc69_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pgc69stage, n_parent, n_child, $nabs($(n - 1)))
  -- if ~$gc69_at(S, pgc69stage, n_parent, n_child) -- if $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $gc69_seek(S, pgc69stage, n_parent, n_child, 0) = S
  -- if ~$gc69_at(S, pgc69stage, n_parent, n_child)
def $gc69_seek(S, pgc69stage, n_parent, n_child, n) = S
  -- if ~$gc69_at(S, pgc69stage, n_parent, n_child)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $gc69_output(pevent*) : preqbytes
def $gc69_output(eps) = eps
def $gc69_output((OUTPUT preqbytes) :: pevent_tail*) = preqbytes ++ $gc69_output(pevent_tail*)
'''
recorded = review.recorded


def recorded_fixture(command, directory, stem, environment, seconds):
    fixture = Path(command[-1])
    fixture.write_text(DECLARATIONS + fixture.read_text())
    return recorded(command, directory, stem, environment, seconds)


review.recorded = recorded_fixture


def seek(before, after, stage):
    return [f'{after}_paused = $gc69_seek({before}, {stage}, n_parent, n_child, 4000)',
            f'{after}_paused.COMPLETION = BUDGET',
            f'{after} = {after}_paused[.COMPLETION = NORMAL]']


def counts(state, parent_physical, parent_native, child_physical):
    return [f'$heap_owners($heap_graph({state}), HOBJECT n_parent) = {parent_physical}',
            f'$native_rc({state}, HOBJECT n_parent) = {parent_native}',
            f'$heap_owners($heap_graph({state}), HOBJECT n_child) = {child_physical}',
            f'$native_rc({state}, HOBJECT n_child) = {child_physical}',
            f'$heap_count(HOBJECT n_child, {state}.NATIVEEXCESS) = 0']


def valid(state):
    return [f'$heap_valid($heap_graph({state}))', f'$native_excess_valid({state})',
            f'$destruction_state_valid({state})', f'$call_descriptors_valid({state})']


def fields(state):
    return [f'$objectprops_at({state}.OBJECTPROPS, n_parent) = ([ppropertyslot_left, ppropertyslot_marker, ppropertyslot_right])',
            f'$node_children({state}, HOBJECT n_parent) = [HOBJECT n_child, HOBJECT n_child]']


def budget(state):
    return [f'$drive_steps({state}, 0) = {state}[.COMPLETION = BUDGET]',
            f'$drive_steps({state}, 2) = $drive_steps($drive_steps({state}, 1)[.COMPLETION = NORMAL], 1)']


CHECKS = [
    'S.NATIVEEXCESS = eps', '$destructor_operation_valid(S, pdestructionoperation)',
    '$objectprops_at(S.OBJECTPROPS, n_parent) = ([ppropertyslot_left, ppropertyslot_marker, ppropertyslot_right])',
    'ppropertyslot_left.STATE = PROP_VALUE (DIRECT (POBJECT n_child))',
    'ppropertyslot_right.STATE = PROP_VALUE (DIRECT (POBJECT n_child))',
    'ppropertyslot_marker.STATE = PROP_VALUE (DIRECT (PINT 17))',
    'S.OBJECTS[n_parent] = INSTANCE porigin_parent',
    '$class_at(S.CLASSES, porigin_parent) = (pclassdesc_parent)',
    '$enum_is_callable_output_excess_fields(S, n_parent, pclassdesc_parent.PROPERTIES)',
    '$enum_is_callable_output_excess_child(S, n_child)',
    '$lookup(S.ENV, $ptascii("parentWatch")) = (n_parent_watch_cell)',
    'S.STORE[n_parent_watch_cell] = DEFINED (POBJECT n_parent_watch)',
    '$lookup(S.ENV, $ptascii("childWatch")) = (n_child_watch_cell)',
    'S.STORE[n_child_watch_cell] = DEFINED (POBJECT n_child_watch)',
    *counts('S', 1, 1, 2), *fields('S'), *valid('S'),
    '$gc69_output(S.EVENTS) = $ptascii("O|")',
    'PhpStep: S ~> S_raw',
    'S_raw.NATIVEEXCESS = [HOBJECT n_parent]',
    'S_raw.TODO = ptask_after_output*',
    'S_raw.DESTRUCTION.RELEASES = eps', 'S_raw.DESTRUCTION.OPERATIONS = eps',
    'S_raw.EVENTS = S.EVENTS', 'S_raw.ALLOCATIONS = S.ALLOCATIONS',
    *counts('S_raw', 0, 1, 2), *fields('S_raw'),
    '$weakref_get(S_raw, n_parent_watch) = POBJECT n_parent',
    '$weakref_get(S_raw, n_child_watch) = POBJECT n_child',
    'S_twice = S_raw[.NATIVEEXCESS = [HOBJECT n_parent, HOBJECT n_parent]]',
    '$heap_graph(S_twice) = $heap_graph(S_raw)', *counts('S_twice', 0, 2, 2),
    # A helper-only commit argument keeps the actual CALL/CELL receipt. These
    # counterstates reject data outside the newly admitted DIRECT field layer.
    'S_emit = S_raw[.STORE = S.STORE][.NATIVEEXCESS = eps][.TODO = (ENUM_IS_CALLABLE_OUTPUT penumqueryoutput) :: ptask_after_output*]',
    '$enum_is_callable_output_excess_ready(S_emit, penumqueryoutput)',
    '$enum_is_callable_output_commit(S_emit, penumqueryoutput) = S_raw',
    'S_wrong_order = S_emit[.OBJECTPROPS = $objectprops_set(S_emit.OBJECTPROPS, n_parent, [ppropertyslot_right, ppropertyslot_marker, ppropertyslot_left])]',
    '$heap_graph(S_wrong_order) = $heap_graph(S_emit)',
    '~$enum_is_callable_output_excess_fields(S_wrong_order, n_parent, pclassdesc_parent.PROPERTIES)',
    '~$enum_is_callable_output_excess_ready(S_wrong_order, penumqueryoutput)',
    'n_ref = |S_emit.STORE|',
    'S_alias = S_emit[.STORE = S_emit.STORE ++ [DEFINED (POBJECT n_child)]][.REFCELLS = S_emit.REFCELLS ++ [n_ref]][.ALLOCATIONS = S_emit.ALLOCATIONS ++ [HCELL n_ref]][.OBJECTPROPS = $objectprops_set(S_emit.OBJECTPROPS, n_parent, [ppropertyslot_left[.STATE = PROP_VALUE (ALIAS n_ref)], ppropertyslot_marker, ppropertyslot_right])]',
    '$heap_valid($heap_graph(S_alias))', *counts('S_alias', 1, 1, 2),
    '~$enum_is_callable_output_excess_fields(S_alias, n_parent, pclassdesc_parent.PROPERTIES)',
    '~$enum_is_callable_output_excess_ready(S_alias, penumqueryoutput)',
    'n_array = |S_emit.ARRAYS|',
    'S_array = S_emit[.ARRAYS = S_emit.ARRAYS ++ [$array_empty()]][.ALLOCATIONS = S_emit.ALLOCATIONS ++ [HARRAY n_array]][.OBJECTPROPS = $objectprops_set(S_emit.OBJECTPROPS, n_parent, [ppropertyslot_left[.STATE = PROP_VALUE (DIRECT (PARRAY n_array))], ppropertyslot_marker, ppropertyslot_right])]',
    '$heap_valid($heap_graph(S_array))',
    '~$enum_is_callable_output_excess_ready(S_array, penumqueryoutput)',
    'S_child_credit = S_emit[.NATIVEEXCESS = [HOBJECT n_child]]',
    '$heap_graph(S_child_credit) = $heap_graph(S_emit)',
    '~$enum_is_callable_output_excess_child(S_child_credit, n_child)',
    '~$enum_is_callable_output_excess_ready(S_child_credit, penumqueryoutput)',
    'S_deep = S_emit[.OBJECTPROPS = $objectprops_set(S_emit.OBJECTPROPS, n_child, [{DECL eps, NAME $ptascii("deeper"), STATE PROP_VALUE (DIRECT (POBJECT n_parent_watch))}])]',
    '$heap_valid($heap_graph(S_deep))',
    '~$enum_is_callable_output_excess_child(S_deep, n_child)',
    '~$enum_is_callable_output_excess_ready(S_deep, penumqueryoutput)',
    *budget('S'),
    'S_after = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
    *seek('S_after', 'S_recovered', 'RECOVER'),
    *counts('S_recovered', 1, 2, 2), *fields('S_recovered'), *valid('S_recovered'),
    *seek('S_recovered', 'S_drop', 'DROP'),
    *counts('S_drop', 1, 2, 2), *valid('S_drop'),
    'PhpStep: S_drop ~> S_drop_raw', *counts('S_drop_raw', 0, 1, 2),
    'S_drop_raw.DESTRUCTION.CALLED = S_drop.DESTRUCTION.CALLED',
    *fields('S_drop_raw'), *budget('S_drop'),
    *seek('S_drop', 'S_trace', 'TRACE'),
    'S_trace.TODO = (GC_TRACE pgccall) :: ptask_trace_tail*',
    *counts('S_trace', 0, 1, 2), *fields('S_trace'), *valid('S_trace'),
    '$heap_count(HOBJECT n_parent, $gc_nodes(S_trace.GC.BUFFER)) = 1',
    '$heap_count(HOBJECT n_child, $gc_nodes(S_trace.GC.BUFFER)) = 1',
    'H_trace = $gc_graph(S_trace)',
    '(HOBJECT n_parent) <- $gc_white(H_trace, $gc_eligible_nodes(S_trace.GC.BUFFER))',
    '(HOBJECT n_child) <- $gc_white(H_trace, $gc_eligible_nodes(S_trace.GC.BUFFER))',
    '$gc_native_white(H_trace, S_trace.NATIVEEXCESS, $gc_eligible_nodes(S_trace.GC.BUFFER)) = eps',
    '$heap_count(HOBJECT n_child, H_trace.ROOTS) = 0',
    '$heap_count(HOBJECT n_parent, H_trace.ROOTS) = 0',
    'pgcplan = $gc_plan(S_trace, pgccall)', 'pgcplan.EXCESS = [HOBJECT n_parent]',
    'pgcplan.GRAPH = H_trace', 'pgcplan.DTORS = eps', 'pgcplan.FREESET = eps',
    'PhpStep: S_trace ~> S_plan',
    'S_plan.TODO = (GC_DTORS pgcplan) :: ptask_trace_tail*',
    '$gc_plan_valid(S_plan, pgcplan)', *budget('S_trace'),
    *seek('S_plan', 'S_child', 'CHILD'),
    'S_child.TODO = (DESTRUCTOR_ENTER pdestructorcall_child) :: ptask_child_tail*',
    'pdestructorcall_child.STORE', 'pdestructorcall_child.OBJECT = n_child',
    'n_child <- S_child.DESTRUCTION.CALLED', '~(n_parent <- S_child.DESTRUCTION.CALLED)',
    *counts('S_child', 0, 1, 4), *fields('S_child'), *valid('S_child'),
    '$instance_storage_for(S_child, n_parent) = eps',
    '$weakref_get(S_child, n_parent_watch) = POBJECT n_parent',
    *seek('S_child', 'S_parent', 'PARENT'),
    'S_parent.TODO = (DESTRUCTOR_ENTER pdestructorcall_parent) :: ptask_parent_tail*',
    'pdestructorcall_parent.STORE', 'pdestructorcall_parent.OBJECT = n_parent',
    'n_child <- S_parent.DESTRUCTION.CALLED', 'n_parent <- S_parent.DESTRUCTION.CALLED',
    *counts('S_parent', 2, 3, 2), *fields('S_parent'), *valid('S_parent'),
    '$instance_storage_for(S_parent, n_parent) = eps',
    '$instance_storage_for(S_parent, n_child) = eps',
    '$weakref_get(S_parent, n_child_watch) = POBJECT n_child',
    '$gc69_output(S_parent.EVENTS) = $ptascii("O|N|1|gc69TargetPeer|1|1|R|1|1|U|1|1|G|0|1|1|E|S|1|1|C|1|")',
    'S_done = $drive_steps(S_parent, 4000)', 'S_done.COMPLETION = NORMAL',
    'S_done.TODO = eps', 'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE',
    'S_done.NATIVEEXCESS = [HOBJECT n_parent]', *counts('S_done', 0, 1, 2),
    *fields('S_done'),
    '$gc69_output(S_done.EVENTS) = $ptascii("O|N|1|gc69TargetPeer|1|1|R|1|1|U|1|1|G|0|1|1|E|S|1|1|C|1|P|1|1|1|")',
]

review.CASES = {'residual-parent-shared-child-closure': {
    'source': SOURCE, 'stage': STAGE, 'checks': CHECKS,
}}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=360) else 1)
