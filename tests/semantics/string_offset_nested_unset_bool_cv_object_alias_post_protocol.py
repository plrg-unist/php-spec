#!/usr/bin/env python3
"""Source-reached object aliases preserve real cell and object owners."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_empty_array_post_protocol as raw
import string_offset_nested_unset_bool_cv_deep_array_post_protocol as prior
import string_offset_nested_unset_bool_cv_object_alias_post_cases as cases

INDEX = 0
PRELAW = False
BASE_CONDITIONS = prior.conditions
PREFIX = raw.PREFIX + r'''
dec $review_object_alias_at(pstate, nat*) : bool
def $review_object_alias_at(S, n_output*) = ($review_cv_outputs(S.EVENTS) = n_output* /\ $lookup(S.ENV, $ptascii("key")) = eps /\ $lookup(S.ENV, $ptascii("objectAlias")) =/= eps)
dec $review_object_alias_seek(pstate, nat*, nat) : pstate
def $review_object_alias_seek(S, n_output*, 0) = S
def $review_object_alias_seek(S, n_output*, n) = S
  -- if $(n > 0)
  -- if $review_object_alias_at(S, n_output*) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $review_object_alias_seek(S, n_output*, n) = $review_object_alias_seek($drive_steps($review_cv_running(S), 1), n_output*, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$review_object_alias_at(S, n_output*)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def front(program, path):
    raw.INDEX, raw.cases = INDEX, cases
    checks = raw.front(program, path)
    checks[checks.index('parray_key.ITEMS = eps')] = ('parray_key.ITEMS = '
        '[ENTRY (KINT 0) (DIRECT (PINT 7)), ENTRY (KINT 1) (DIRECT (PARRAY n_middle))]')
    checks[checks.index('$node_children(S_R, HARRAY n_array) = eps')] = '$node_children(S_R, HARRAY n_array) = [HARRAY n_middle]'
    checks += ['$(n_middle < |S_R.ARRAYS|)', 'n_middle =/= n_array',
        'S_R.ARRAYS[n_middle].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8)), ENTRY (KINT 1) (ALIAS n_owner), ENTRY (KINT 2) (ALIAS n_owner)]',
        '$node_children(S_R, HARRAY n_middle) = [HCELL n_owner, HCELL n_owner]',
        '$heap_member(HARRAY n_middle, $heap_prune(H_R).NODES)',
        '$heap_edge_owners(HARRAY n_middle, H_R.EDGES, [HARRAY n_array]) = 1',
        '$lookup(S_R.ENV, $ptascii("objectAlias")) = (n_owner)',
        '$(n_owner < |S_R.STORE|)', 'n_owner =/= n_key',
        'S_R.STORE[n_owner] = DEFINED (POBJECT n_object)',
        'n_owner <- S_R.REFCELLS', '$call_reference_operand_valid(S_R, REFERENCE n_owner)',
        '~$literal_reference_plain_cell(S_R, n_owner)',
        '~$string_read_array_string_cell(S_R, n_owner)',
        '$propref_at(S_R.PROPREFS, n_owner) = eps',
        '$reference_coercion_at(S_R.REFCOERCIONS, n_owner) = eps',
        '$parameter_backing_at(S_R.PARAMETERBACKINGS, n_owner) = eps',
        '$heap_member(HCELL n_owner, H_R.ROOTS)',
        '$heap_member(HCELL n_owner, $heap_prune(H_R).NODES)',
        '$heap_edge_owners(HCELL n_owner, H_R.EDGES, [HARRAY n_middle]) = 2',
        '$node_children(S_R, HCELL n_owner) = [HOBJECT n_object]',
        '$(n_object < |S_R.OBJECTS|)', 'S_R.OBJECTS[n_object] = STDINSTANCE',
        '$objectprops_at(S_R.OBJECTPROPS, n_object) = (eps)',
        '$object_table_at(S_R.OBJECTTABLES, n_object) = eps',
        '~$instance_storage_freeing(S_R, n_object)',
        '$node_children(S_R, HOBJECT n_object) = eps',
        '$heap_member(HOBJECT n_object, $heap_prune(H_R).NODES)',
        '$heap_edge_owners(HOBJECT n_object, H_R.EDGES, [HCELL n_owner]) = 1',
        '$heap_owners(H_R, HOBJECT n_object) = 1',
        '$heap_owners($heap_prune(H_R), HOBJECT n_object) = 1',
        '$heap_count(HOBJECT n_object, H_R.ROOTS) = 0',
        '$lookup(S_R.ENV, $ptascii("objectWeak")) = (n_weak_cell)',
        'S_R.STORE[n_weak_cell] = DEFINED (POBJECT n_wrapper)',
        '$weakref_at(S_R, n_wrapper) = (WEAKREFERENCE (n_object))',
        '$weakref_get(S_R, n_wrapper) = POBJECT n_object',
        '$node_children(S_R, HOBJECT n_wrapper) = eps',
        '$cast_truth_int(S_R, PARRAY n_array) = 1',
        '$lookup(S_R.ENV, $ptascii("last")) = (n_last)',
        'S_R.STORE[n_last] = DEFINED (PINT 7)']
    return checks


def conditions(program, path):
    prior.INDEX, prior.cases, prior.PRELAW, prior.front = INDEX, cases, PRELAW, front
    checks, derived = BASE_CONDITIONS(program, path)
    if not PRELAW:
        assert derived == 17
        checks = checks[:-derived]
        derived = 0
        assert not any('n_grand' in line for line in checks)
    name = tuple(cases.CASES)[INDEX]
    at = checks.index('S_DONE = $drive_steps(S_tail, 3000)')
    retained = ['S_ret_found = $review_object_alias_seek($drive_steps(S_tail, 1), ' + raw.shared.term(cases.RETAINED_OUTPUTS[name]) + ', 3000)',
        '$review_object_alias_at(S_ret_found, ' + raw.shared.term(cases.RETAINED_OUTPUTS[name]) + ')',
        'S_RET = $review_cv_running(S_ret_found)', 'S_RET.COMPLETION = NORMAL',
        '$lookup(S_RET.ENV, n_key_name*) = eps',
        '$lookup(S_RET.ENV, $ptascii("objectAlias")) = (n_owner)',
        'S_RET.STORE[n_owner] = DEFINED (POBJECT n_after)',
        'n_after =/= n_object', '$(n_after < |S_RET.OBJECTS|)',
        'S_RET.OBJECTS[n_after] = STDINSTANCE',
        '$objectprops_at(S_RET.OBJECTPROPS, n_after) = (eps)',
        '$object_table_at(S_RET.OBJECTTABLES, n_after) = eps',
        '$lookup(S_RET.ENV, $ptascii("objectWeakAfter")) = (n_weak_after_cell)',
        'S_RET.STORE[n_weak_after_cell] = DEFINED (POBJECT n_wrapper_after)',
        '$weakref_at(S_RET, n_wrapper_after) = (WEAKREFERENCE (n_after))',
        '$weakref_get(S_RET, n_wrapper_after) = POBJECT n_after',
        '$weakref_get(S_RET, n_wrapper) = PNULL',
        '~$heap_member(HOBJECT n_object, S_RET.ALLOCATIONS)',
        'H_RET = $heap_graph(S_RET)', '$heap_valid(H_RET)',
        '$heap_member(HCELL n_owner, H_RET.ROOTS)',
        '$heap_member(HCELL n_owner, $heap_prune(H_RET).NODES)',
        '$node_children(S_RET, HCELL n_owner) = [HOBJECT n_after]',
        '$heap_edge_owners(HOBJECT n_after, H_RET.EDGES, [HCELL n_owner]) = 1',
        '$heap_owners(H_RET, HOBJECT n_after) = 1',
        '$heap_member(HOBJECT n_after, $heap_prune(H_RET).NODES)',
        '~$heap_member(HARRAY n_array, $heap_prune(H_RET).NODES)',
        '~$heap_member(HARRAY n_middle, $heap_prune(H_RET).NODES)']
    checks[at:at + 1] = retained + ['S_DONE = $drive_steps(S_RET, 3000)']
    final = ['$lookup(S_DONE.ENV, $ptascii("objectAlias")) = eps',
        '$weakref_get(S_DONE, n_wrapper) = PNULL',
        '$weakref_get(S_DONE, n_wrapper_after) = PNULL',
        '~$heap_member(HCELL n_owner, S_DONE.ALLOCATIONS)',
        '~$heap_member(HOBJECT n_object, S_DONE.ALLOCATIONS)',
        '~$heap_member(HOBJECT n_after, S_DONE.ALLOCATIONS)',
        '~$heap_member(HCELL n_owner, $heap_prune($heap_graph(S_DONE)).NODES)']
    checks += final
    direct = ['S_direct = S_R[.ARRAYS[n_middle].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8)), ENTRY (KINT 1) (DIRECT (POBJECT n_object)), ENTRY (KINT 2) (DIRECT (POBJECT n_object))]]',
        '$heap_valid($heap_graph(S_direct))',
        '$heap_owners($heap_graph(S_direct), HOBJECT n_object) = 3',
        '$string_unset_bool_cv_post_nonempty_array(S_direct, n_key)']
    checks += direct
    if PRELAW:
        return checks, derived + len(retained) + len(final) + len(direct)
    derived = len(direct) + 1
    checks += ['$string_unset_bool_cv_post_object_cell(S_R, n_owner)',
        '$string_unset_bool_cv_post_object_cell(S_direct, n_owner)',
        'S_public = $drive_steps(S_P, 1)', 'S_public.COMPLETION = BUDGET',
        '$drive_steps($review_cv_running(S_public), 3000) = S_DONE']
    at = len(checks)
    for tag, changed in (
        ('unmarked', 'S_R[.REFCELLS = $literal_reference_delete(S_R.REFCELLS, n_owner)]'),
        ('unallocated', 'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HCELL n_owner)]'),
        ('undefined', 'S_R[.STORE[n_owner] = UNDEFINED]'),
        ('object_unallocated', 'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HOBJECT n_object)]'),
        ('typed', 'S_R[.PROPREFS = [{CELL n_owner, SOURCES eps}]]'),
    ):
        state = 'S_bad_' + tag
        checks += [state + ' = ' + changed,
            '~$string_unset_bool_cv_post_object_cell(' + state + ', n_owner)',
            '~$string_unset_bool_cv_post_nonempty_array(' + state + ', n_key)']
    checks += ['S_props = $objectprops_mark(S_R[.OBJECTPROPS = $objectprops_set(S_R.OBJECTPROPS, n_object, [{DECL eps, NAME $ptascii("extra"), STATE PROP_VALUE (DIRECT (PINT 1))}])], n_object)',
        '$heap_valid($heap_graph(S_props))',
        '~$string_unset_bool_cv_post_object_cell(S_props, n_owner)',
        '~$string_unset_bool_cv_post_nonempty_array(S_props, n_key)',
        'S_key_only = S_R[.ENV = $unbind(S_R.ENV, $ptascii("objectAlias"))][.GLOBALTABLE = eps]',
        '$heap_valid($heap_graph(S_key_only))',
        '~$heap_member(HCELL n_owner, $heap_graph(S_key_only).ROOTS)',
        '$heap_member(HCELL n_owner, $heap_prune($heap_graph(S_key_only)).NODES)',
        '$string_unset_bool_cv_post_object_cell(S_key_only, n_owner)',
        '$string_unset_bool_cv_post_nonempty_array(S_key_only, n_key)']
    for changed in ('S_R[.CODE = eps]', 'S_R[.SOURCES = eps]', 'S_R[.ORIGIN = eps]'):
        checks += ['~$call_task_valid(' + changed + ', STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key)']
    return checks, derived + len(checks) - at


if __name__ == '__main__':
    PRELAW = '--prelaw' in sys.argv
    if PRELAW:
        sys.argv.remove('--prelaw')
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in range(2)
    name = tuple(cases.CASES)[INDEX]
    watched = [Path(__file__), Path(raw.__file__), Path(prior.__file__),
               Path(raw.shared.__file__), Path(raw.sl.__file__), Path(cases.prior.__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner = raw.runner
    runner.NAME, runner.OUTPUT = name, cases.OUTPUTS[name]
    runner.cases, runner.conditions = cases, conditions
    runner.PREFIX, runner.recorded = PREFIX, raw.sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Actual object-alias source, quiet read and full heap precede Unsupported; '
        'separately derived rebind/key-retainer/final cell-object retirement and old DIRECT control, source0/native0.'
        if PRELAW else 'Source-reached fieldless object aliases preserve exact Error or same Throwable, '
        'whole/split/public states, rebind and staged cell/object retirement; malformed controls separate, source0/native0.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
