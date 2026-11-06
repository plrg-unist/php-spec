#!/usr/bin/env python3
"""Actual query overwrite, weak recovery, native RC and collector lifetime."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc68_query_lost_rc.php').read_text()
STAGE = (
    'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: '
    '(ENUM_IS_CALLABLE_OUTPUT penumqueryoutput) :: ptask_after_output* '
    '-- if pdestructionoperation.SOURCE = ENUM_IS_CALLABLE_CLEAR penumqueryoutput '
    '-- if penumqueryoutput.OLD = HOBJECT n_old '
    '-- if S.STORE[penumqueryoutput.CELL] = DEFINED (POBJECT n_child) '
    '-- if n_child =/= n_old')

DECLARATIONS = r'''syntax pgc68stage = GET | DROP | TRACE | STORE
dec $gc68_at(pstate, pgc68stage, nat) : bool
def $gc68_at(S, GET, n_child) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET
  -- if pconfigcall.OWNER = (n_watch)
  -- if $weakref_get(S, n_watch) = POBJECT n_child
def $gc68_at(S, DROP, n_child) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*
  -- if pdestructionrelease.JOBS = pdestructionjob :: pdestructionjob_tail*
  -- if $destruction_job_node(pdestructionjob) = (HOBJECT n_child)
def $gc68_at(S, TRACE, n_child) = true
  -- if S.TODO = (GC_TRACE pgccall) :: ptask_tail*
def $gc68_at(S, STORE, n_child) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.STORE /\ pdestructorcall.OBJECT = n_child
def $gc68_at(S, pgc68stage, n_child) = false -- otherwise
dec $gc68_seek(pstate, pgc68stage, nat, nat) : pstate
def $gc68_seek(S, pgc68stage, n_child, n) = S
  -- if $gc68_at(S, pgc68stage, n_child)
def $gc68_seek(S, pgc68stage, n_child, n) = $gc68_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pgc68stage, n_child, $nabs($(n - 1)))
  -- if ~$gc68_at(S, pgc68stage, n_child) -- if $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $gc68_seek(S, pgc68stage, n_child, 0) = S
  -- if ~$gc68_at(S, pgc68stage, n_child)
def $gc68_seek(S, pgc68stage, n_child, n) = S
  -- if ~$gc68_at(S, pgc68stage, n_child)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $gc68_output(pevent*) : preqbytes
def $gc68_output(eps) = eps
def $gc68_output((OUTPUT preqbytes) :: pevent_tail*) = preqbytes ++ $gc68_output(pevent_tail*)
'''
recorded = review.recorded


def recorded_fixture(command, directory, stem, environment, seconds):
    fixture = Path(command[-1])
    fixture.write_text(DECLARATIONS + fixture.read_text())
    return recorded(command, directory, stem, environment, seconds)


review.recorded = recorded_fixture


def seek(before, after, stage):
    return [f'{after}_paused = $gc68_seek({before}, {stage}, n_child, 4000)',
            f'{after}_paused.COMPLETION = BUDGET',
            f'{after} = {after}_paused[.COMPLETION = NORMAL]']


def valid(state):
    return [f'$heap_valid($heap_graph({state}))', f'$native_excess_valid({state})',
            f'$destruction_state_valid({state})', f'$call_descriptors_valid({state})']


def counts(state, physical, native):
    return [f'$heap_owners($heap_graph({state}), HOBJECT n_child) = {physical}',
            f'$native_rc({state}, HOBJECT n_child) = {native}']


def budget(state):
    return [f'$drive_steps({state}, 0) = {state}[.COMPLETION = BUDGET]',
            f'$drive_steps({state}, 2) = $drive_steps($drive_steps({state}, 1)[.COMPLETION = NORMAL], 1)']


CHECKS = [
    '$initial_state(NORMAL).NATIVEEXCESS = eps',
    'S.NATIVEEXCESS = eps', 'S.CURRENT = eps', 'S.FRAMES = eps',
    '$destructor_operation_valid(S, pdestructionoperation)',
    '$object_name(S, n_child) = $ptascii("LostRcChild")',
    '~(n_child <- S.DESTRUCTION.CALLED)',
    'n_old <- S.DESTRUCTION.CALLED', '~((HOBJECT n_old) <- S.ALLOCATIONS)',
    '$lookup(S.ENV, $ptascii("name")) = (penumqueryoutput.CELL)',
    'penumqueryoutput.CELL <- S.REFCELLS',
    '$heap_owners($heap_graph(S), HCELL penumqueryoutput.CELL) = 2',
    '$node_children(S, HCELL penumqueryoutput.CELL) = [HOBJECT n_child]',
    '$lookup(S.ENV, $ptascii("watch")) = (n_watch_cell)',
    'S.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
    '$weakref_get(S, n_watch) = POBJECT n_child',
    *counts('S', 1, 1), *valid('S'),
    '$gc68_output(S.EVENTS) = $ptascii("O|")',
    'PhpStep: S ~> S_raw',
    'S_raw.STORE[penumqueryoutput.CELL] = DEFINED (PSTRING penumqueryoutput.NAME)',
    'S_raw.NATIVEEXCESS = [HOBJECT n_child]',
    'S_raw.TODO = ptask_after_output*',
    'S_raw.DESTRUCTION.RELEASES = eps', 'S_raw.DESTRUCTION.OPERATIONS = eps',
    'S_raw.EVENTS = S.EVENTS', 'S_raw.ALLOCATIONS = S.ALLOCATIONS',
    *counts('S_raw', 0, 1), '$weakref_get(S_raw, n_watch) = POBJECT n_child',
    # Reconstruct only the immediate commit argument from its actual successor.
    'S_emit = S_raw[.STORE = S.STORE][.NATIVEEXCESS = eps][.TODO = (ENUM_IS_CALLABLE_OUTPUT penumqueryoutput) :: ptask_after_output*]',
    '$enum_is_callable_output_excess_ready(S_emit, penumqueryoutput)',
    '$enum_is_callable_output_commit(S_emit, penumqueryoutput) = S_raw',
    '~((HOBJECT n_child) <- $eager_slots(S_emit, S_raw))',
    'S_called = S_emit[.DESTRUCTION.CALLED = S_emit.DESTRUCTION.CALLED ++ [n_child]]',
    '$heap_graph(S_called) = $heap_graph(S_emit)',
    '~$enum_is_callable_output_excess_ready(S_called, penumqueryoutput)',
    '$enum_is_callable_output_commit(S_called, penumqueryoutput).COMPLETION = UNSUPPORTED "is_callable output rebound to owning value or new type source"',
    'n_extra_cell = |S_emit.STORE|',
    'S_extra = S_emit[.STORE = S_emit.STORE ++ [DEFINED (POBJECT n_child)]][.ENV = S_emit.ENV ++ [BIND $ptascii("gc68_external") n_extra_cell]][.ALLOCATIONS = S_emit.ALLOCATIONS ++ [HCELL n_extra_cell]]',
    '$heap_valid($heap_graph(S_extra))', *counts('S_extra', 2, 2),
    '~$enum_is_callable_output_excess_ready(S_extra, penumqueryoutput)',
    'penumqueryoutput_wrong = penumqueryoutput[.CELL = n_extra_cell]',
    'S_wrong_cell = S_extra[.STORE[penumqueryoutput.CELL] = DEFINED PNULL][.ENV = $unbind(S_extra.ENV, $ptascii("name")) ++ [BIND $ptascii("name") n_extra_cell]][.REFCELLS = S_extra.REFCELLS ++ [n_extra_cell]][.TODO = (ENUM_IS_CALLABLE_OUTPUT penumqueryoutput_wrong) :: ptask_after_output*]',
    '$heap_valid($heap_graph(S_wrong_cell))', *counts('S_wrong_cell', 1, 1),
    '~$enum_is_callable_output_excess_ready(S_wrong_cell, penumqueryoutput_wrong)',
    'S_quiet = S_emit[.STORE[penumqueryoutput.CELL] = DEFINED PNULL]',
    '$enum_is_callable_output_ready(S_quiet, penumqueryoutput)',
    '~$enum_is_callable_output_excess_ready(S_quiet, penumqueryoutput)',
    '$enum_is_callable_output_commit(S_quiet, penumqueryoutput).NATIVEEXCESS = eps',
    'n_array = |S_emit.ARRAYS|',
    'S_array = S_emit[.STORE[penumqueryoutput.CELL] = DEFINED (PARRAY n_array)][.ARRAYS = S_emit.ARRAYS ++ [$array_empty()]][.ALLOCATIONS = S_emit.ALLOCATIONS ++ [HARRAY n_array]]',
    '$heap_valid($heap_graph(S_array))',
    '~$enum_is_callable_output_excess_ready(S_array, penumqueryoutput)',
    '$enum_is_callable_output_commit(S_array, penumqueryoutput).COMPLETION = UNSUPPORTED "is_callable output rebound to owning value or new type source"',
    # A pending THROW head is outside the new normal-head arm, even when the
    # machine completion is NORMAL. No PHP throw agreement is claimed here.
    'S_throw_head = S_emit[.TODO = (THROW_SEARCH n_child) :: (ENUM_IS_CALLABLE_OUTPUT penumqueryoutput) :: ptask_after_output*]',
    '~$enum_is_callable_output_excess_ready(S_throw_head, penumqueryoutput)',
    '$enum_is_callable_output_commit(S_throw_head, penumqueryoutput).NATIVEEXCESS = eps',
    '$native_decrements(S, S_raw, [HOBJECT n_child]) = eps',
    '$native_decrements(S, S_raw, [HOBJECT n_child, HOBJECT n_child]) = [HOBJECT n_child]',
    '$native_decrements(S_raw, S_raw, [HOBJECT n_child]) = [HOBJECT n_child]',
    'S_twice = S_raw[.NATIVEEXCESS = [HOBJECT n_child, HOBJECT n_child]]',
    '$heap_graph(S_twice) = $heap_graph(S_raw)', *counts('S_twice', 0, 2),
    '$native_excess_valid(S_twice)',
    '$native_decrements(S_raw, S_twice, [HOBJECT n_child, HOBJECT n_child]) = [HOBJECT n_child]',
    '$heap_prune_native($heap_graph(S_raw), S_raw.NATIVEEXCESS).NODES = S_raw.ALLOCATIONS',
    '~((HOBJECT n_child) <- $heap_prune($heap_graph(S_raw)).NODES)',
    *budget('S'),
    'S_next = $drive_steps(S, 1)', 'S_next.COMPLETION = BUDGET',
    'S_after = S_next[.COMPLETION = NORMAL]',
    'S_after.NATIVEEXCESS = S_raw.NATIVEEXCESS', *counts('S_after', 0, 1),
    'S_after.DESTRUCTION.RELEASES = eps', *valid('S_after'),
    *seek('S_after', 'S_get', 'GET'),
    'S_get.TODO = (CONFIG_INVOKE pconfigcall_get) :: ptask_get_tail*',
    'pconfigcall_get.OWNER = (n_watch)', *counts('S_get', 0, 1),
    'PhpStep: S_get ~> S_get_raw',
    'S_get_raw.RESULT = KNOWN (POBJECT n_child)', *counts('S_get_raw', 1, 2),
    'S_get_raw.NATIVEEXCESS = S_get.NATIVEEXCESS',
    # Heap counterstate: redistribute that real recovered result to two aliases
    # of one cell, then remove their names. No extra PHP/native case is implied.
    'n_recovered_cell = |S_get_raw.STORE|',
    'S_alias = S_get_raw[.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.STORE = S_get_raw.STORE ++ [DEFINED (POBJECT n_child)]][.ENV = S_get_raw.ENV ++ [BIND $ptascii("gc68_alias_a") n_recovered_cell, BIND $ptascii("gc68_alias_b") n_recovered_cell]][.REFCELLS = S_get_raw.REFCELLS ++ [n_recovered_cell]][.ALLOCATIONS = S_get_raw.ALLOCATIONS ++ [HCELL n_recovered_cell]]',
    '$heap_valid($heap_graph(S_alias))',
    '$heap_owners($heap_graph(S_alias), HCELL n_recovered_cell) = 2',
    *counts('S_alias', 1, 2),
    'S_alias.NATIVEEXCESS = S_get_raw.NATIVEEXCESS',
    'S_one_alias = S_alias[.ENV = $unbind(S_alias.ENV, $ptascii("gc68_alias_a"))]',
    '$heap_owners($heap_graph(S_one_alias), HCELL n_recovered_cell) = 1',
    *counts('S_one_alias', 1, 2),
    'S_no_alias = S_one_alias[.ENV = $unbind(S_one_alias.ENV, $ptascii("gc68_alias_b"))]',
    'H_no_alias = $heap_prune_native($heap_graph(S_no_alias), S_no_alias.NATIVEEXCESS)',
    '~((HCELL n_recovered_cell) <- H_no_alias.NODES)',
    '(HOBJECT n_child) <- H_no_alias.NODES',
    '$heap_owners(H_no_alias, HOBJECT n_child) = 0',
    '$heap_native_rc(H_no_alias, S_no_alias.NATIVEEXCESS, HOBJECT n_child) = 1',
    'S_get_next = $drive_steps(S_get, 1)',
    *seek('S_get_next', 'S_drop', 'DROP'),
    'S_drop.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_drop) :: ptask_drop_tail*',
    'pdestructionrelease_drop.JOBS = (DESTRUCTION_TEMP (HOBJECT n_child)) :: pdestructionjob_drop_tail*',
    *counts('S_drop', 1, 2), *valid('S_drop'),
    'PhpStep: S_drop ~> S_drop_raw', *counts('S_drop_raw', 0, 1),
    'S_drop_raw.NATIVEEXCESS = S_drop.NATIVEEXCESS',
    'S_drop_raw.DESTRUCTION.CALLED = S_drop.DESTRUCTION.CALLED',
    '$weakref_get(S_drop_raw, n_watch) = POBJECT n_child',
    '$native_decrements(S_drop, S_drop_raw, [HOBJECT n_child]) = [HOBJECT n_child]',
    *budget('S_drop'),
    *seek('S_drop', 'S_trace', 'TRACE'),
    'S_trace.TODO = (GC_TRACE pgccall) :: ptask_trace_tail*',
    *counts('S_trace', 0, 1), *valid('S_trace'),
    '$heap_count(HOBJECT n_child, $gc_nodes(S_trace.GC.BUFFER)) = 1',
    '(HOBJECT n_child) <- $gc_white($gc_graph(S_trace), $gc_eligible_nodes(S_trace.GC.BUFFER))',
    '~((HOBJECT n_child) <- $gc_native_white($gc_graph(S_trace), S_trace.NATIVEEXCESS, $gc_eligible_nodes(S_trace.GC.BUFFER)))',
    'pgcplan = $gc_plan(S_trace, pgccall)',
    'pgcplan.GRAPH = $gc_graph(S_trace)', 'pgcplan.EXCESS = [HOBJECT n_child]',
    'pgcplan.DTORS = eps', 'pgcplan.FREESET = eps',
    'PhpStep: S_trace ~> S_plan',
    'S_plan.TODO = (GC_DTORS pgcplan) :: ptask_trace_tail*',
    'S_plan.GC.PLAN = (pgcplan)', '$gc_plan_valid(S_plan, pgcplan)',
    'pgcplan_wrong = pgcplan[.EXCESS = eps]',
    'S_wrong_plan = S_plan[.GC.PLAN = (pgcplan_wrong)][.TODO = (GC_DTORS pgcplan_wrong) :: ptask_trace_tail*]',
    '$heap_graph(S_wrong_plan) = $heap_graph(S_plan)',
    '~$gc_plan_valid(S_wrong_plan, pgcplan_wrong)',
    '~$gc_snapshot_valid($gc_call_scope(S_wrong_plan, pgccall), pgcplan_wrong)',
    'pgcplan_twice = pgcplan[.EXCESS = [HOBJECT n_child, HOBJECT n_child]]',
    'S_twice_plan = S_plan[.GC.PLAN = (pgcplan_twice)][.TODO = (GC_DTORS pgcplan_twice) :: ptask_trace_tail*]',
    '~$gc_plan_valid(S_twice_plan, pgcplan_twice)', *budget('S_trace'),
    *seek('S_plan', 'S_store', 'STORE'),
    'S_store.TODO = (DESTRUCTOR_ENTER pdestructorcall_store) :: ptask_store_tail*',
    'pdestructorcall_store.STORE', 'pdestructorcall_store.OBJECT = n_child',
    'S_store.NATIVEEXCESS = [HOBJECT n_child]', *counts('S_store', 2, 3),
    *valid('S_store'),
    '$gc68_output(S_store.EVENTS) = $ptascii("O|N|1|lostRcTarget|1|U|1|G|0|1|E|S|1|")',
    'S_done = $drive_steps(S_store, 4000)', 'S_done.COMPLETION = NORMAL',
    'S_done.TODO = eps', 'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE',
    'n_child <- S_done.DESTRUCTION.CALLED',
    'S_done.NATIVEEXCESS = [HOBJECT n_child]', *counts('S_done', 0, 1),
    '$gc68_output(S_done.EVENTS) = $ptascii("O|N|1|lostRcTarget|1|U|1|G|0|1|E|S|1|D|")',
    'S_bad = S_done[.NATIVEEXCESS = [HOBJECT n_old]]',
    '~$native_excess_valid(S_bad)',
    '$prune_allocations(S_bad).COMPLETION = UNSUPPORTED "unallocated unmatched native RC"',
    # The existing STORE_DONE abstraction has no forced free_obj transition.
    # Exercise its real retirement helper as a countercontrol, not a source step.
    'S_retire_input = S_done[.NATIVEEXCESS = [HOBJECT n_child, HOBJECT n_child]][.ALLOCATIONS = $destruction_node_delete(S_done.ALLOCATIONS, HOBJECT n_child)]',
    'S_retired = $gc_store_retire(S_retire_input, HOBJECT n_child)',
    'S_retired.NATIVEEXCESS = eps', '$native_excess_valid(S_retired)',
    '$native_rc(S_retired, HOBJECT n_child) = 0',
]

review.CASES = {'query-native-excess-lifetime': {
    'source': SOURCE, 'stage': STAGE, 'checks': CHECKS,
}}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=360) else 1)
