#!/usr/bin/env python3
"""Independent owning-array aliases and staged last-owner retirement."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_empty_array_post_review_state as prior
import string_offset_nested_unset_bool_cv_array_alias_post_cases as cases

INDEX = 0
PRELAW = False
PREFIX = prior.seek.PREFIX + r'''
dec $review_array_owner_seek(pstate, nat*, nat) : pstate
def $review_array_owner_seek(S, n_want*, 0) = S
def $review_array_owner_seek(S, n_want*, n) = S
  -- if $(n > 0)
  -- if $review_cv_outputs(S.EVENTS) = n_want* \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $review_array_owner_seek(S, n_want*, n) = $review_array_owner_seek($drive_steps($review_cv_running(S), 1), n_want*, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if $review_cv_outputs(S.EVENTS) =/= n_want*
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def front(program, path):
    prior.INDEX, prior.cases, prior.PRELAW = INDEX, cases, True
    checks, _ = prior.conditions(program, path)
    checks = checks[:checks.index('~$string_unset_bool_cv_post_value(PARRAY n_array)')]
    for old, new in (
        ('parray_saved.ITEMS = eps', 'parray_saved.ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7)), ENTRY (KINT 1) (DIRECT (PARRAY n_middle))]'),
        ('$entries_nodes(parray_saved.ITEMS) = eps', '$entries_nodes(parray_saved.ITEMS) = [HARRAY n_middle]'),
        ('$node_children(S_R, HARRAY n_array) = eps', '$node_children(S_R, HARRAY n_array) = [HARRAY n_middle]'),
    ):
        assert checks.count(old) == 1
        checks[checks.index(old)] = new
    checks += ['$(n_middle < |S_R.ARRAYS|)',
        'n_middle =/= n_array',
        'S_R.ARRAYS[n_middle].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8)), ENTRY (KINT 1) (ALIAS n_owner), ENTRY (KINT 2) (ALIAS n_owner)]',
        '$node_children(S_R, HARRAY n_middle) = [HCELL n_owner, HCELL n_owner]',
        '$lookup(S_R.ENV, $ptascii("arrayOwnerAlias")) = (n_owner)',
        'n_owner =/= n_key',
        '$(n_owner < |S_R.STORE|)',
        'S_R.STORE[n_owner] = DEFINED (PARRAY n_child)',
        'n_owner <- S_R.REFCELLS',
        '$call_reference_operand_valid(S_R, REFERENCE n_owner)',
        '$propref_at(S_R.PROPREFS, n_owner) = eps',
        '$reference_coercion_at(S_R.REFCOERCIONS, n_owner) = eps',
        '$parameter_backing_at(S_R.PARAMETERBACKINGS, n_owner) = eps',
        '$node_children(S_R, HCELL n_owner) = [HARRAY n_child]',
        '$(n_child < |S_R.ARRAYS|)',
        r'n_child =/= n_array /\ n_child =/= n_middle',
        '$heap_member(HARRAY n_middle, $heap_prune(H_saved).NODES)',
        '$heap_member(HCELL n_owner, $heap_prune(H_saved).NODES)',
        '$heap_member(HARRAY n_child, $heap_prune(H_saved).NODES)',
        '$heap_edge_owners(HCELL n_owner, H_saved.EDGES, [HARRAY n_middle]) = 2',
        '$heap_edge_owners(HCELL n_owner, H_saved.EDGES, H_saved.NODES) = 2',
        'n_owner_roots = $heap_count(HCELL n_owner, H_saved.ROOTS)',
        '$(n_owner_roots > 0)',
        '$heap_count(HCELL n_owner, H_saved.DEBTS) = 0',
        '$heap_owners(H_saved, HCELL n_owner) = $(n_owner_roots + 2)',
        '$heap_edge_owners(HARRAY n_child, H_saved.EDGES, [HCELL n_owner]) = 1',
        '$heap_edge_owners(HARRAY n_child, H_saved.EDGES, [HARRAY n_middle]) = 0',
        '$heap_owners(H_saved, HARRAY n_child) = 1',
        '$heap_count(HARRAY n_child, H_saved.ROOTS) = 0',
        '$heap_count(HARRAY n_child, $pools_nodes(S_R.POOLS)) = 0',
        '~$literal_reference_plain_cell(S_R, n_owner)',
        '$cast_truth_int(S_R, PARRAY n_array) = 1',
        '$lookup(S_R.ENV, $ptascii("last")) = (n_last)',
        'S_R.STORE[n_last] = DEFINED (PINT 7)']
    mixed = cases.FACTS[tuple(cases.CASES)[INDEX]]['mixed']
    if not mixed:
        return checks + ['S_R.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]']
    checks += ['S_R.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9)), ENTRY (KINT 1) (ALIAS n_alias), ENTRY (KINT 2) (DIRECT (POBJECT n_object)), ENTRY (KINT 3) (DIRECT (PSTRING_CARRIER (REQUEST_STRING n_text) ($ptascii("req-text"))))]',
        '$node_children(S_R, HARRAY n_child) = [HCELL n_alias, HOBJECT n_object]',
        '$lookup(S_R.ENV, $ptascii("arrayAlias")) = (n_alias)',
        r'n_alias =/= n_owner /\ n_alias =/= n_key',
        '$(n_alias < |S_R.STORE|)',
        'S_R.STORE[n_alias] = DEFINED (PINT 9)',
        '$literal_reference_plain_cell(S_R, n_alias)',
        '$heap_edge_owners(HCELL n_alias, H_saved.EDGES, [HARRAY n_child]) = 1',
        '$(n_object < |S_R.OBJECTS|)',
        'S_R.OBJECTS[n_object] = STDINSTANCE',
        '$objectprops_at(S_R.OBJECTPROPS, n_object) = (eps)',
        '$object_table_at(S_R.OBJECTTABLES, n_object) = eps',
        '$node_children(S_R, HOBJECT n_object) = eps',
        '$heap_owners(H_saved, HOBJECT n_object) = 1',
        '$lookup(S_R.ENV, $ptascii("arrayWeak")) = (n_weak_cell)',
        'S_R.STORE[n_weak_cell] = DEFINED (POBJECT n_wrapper)',
        '$weakref_at(S_R, n_wrapper) = (WEAKREFERENCE (n_object))',
        '$weakref_get(S_R, n_wrapper) = POBJECT n_object',
        '$node_children(S_R, HOBJECT n_wrapper) = eps',
        '$heap_edge_owners(HOBJECT n_object, H_saved.EDGES, [HOBJECT n_wrapper]) = 0',
        '$(n_text < |S_R.STRINGDATA|)',
        'S_R.STRINGDATA[n_text] = $ptascii("req-text")',
        '$string_carrier_valid(S_R, PSTRING_CARRIER (REQUEST_STRING n_text) ($ptascii("req-text")))',
        '$value_nodes(PSTRING_CARRIER (REQUEST_STRING n_text) ($ptascii("req-text"))) = eps']
    return checks


def conditions(program, path):
    checks = front(program, path)
    name = tuple(cases.CASES)[INDEX]
    pending, mixed = cases.FACTS[name]['throwing'], cases.FACTS[name]['mixed']
    resume = 'STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key'
    normal_error = ('S_R[.TODO = ptask_after*][.RESULT = KNOWN PNULL]'
        '[.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE]'
        '[.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z]')
    checks += ['~$string_unset_bool_cv_post_empty_array(S_R, n_key)',
        '~$string_unset_bool_cv_post_value(PARRAY n_array)',
        '~$string_unset_bool_cv_post_normal_value(PARRAY n_array)',
        '$string_unset_cv_range_plan(S_R) = eps']
    admitted = '~' if PRELAW else ''
    checks += [admitted + '$string_unset_bool_cv_post_nonempty_array(S_R, n_key)',
        admitted + '$string_unset_bool_cv_post_cell(S_R, n_key_name*, z_key, n_key)',
        admitted + '$string_unset_bool_cv_post_normal_cell(S_R, n_key_name*, z_key, n_key)']
    if PRELAW:
        if pending:
            checks += ['$error_read_discard(S_R, ' + resume + ') = S_R[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]',
                'PhpStep: S_P ~> S_old',
                'S_old = S_R[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
        else:
            checks += ['PhpStep: S_R ~> S_old',
                'S_old = S_R[.TODO = ptask_after*][.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
        tail = 'S_R' if pending else normal_error
    else:
        checks += ['$string_unset_bool_cv_post_discard_cell(S_R, n_key_name*, z_key, n_key)']
        if pending:
            checks += ['$error_read_discard(S_R, ' + resume + ') = S_R',
                '$return_discard(S_cut, ERROR_HANDLER_RESULT perrorcall_entered) = S_R',
                'PhpStep: S_P ~> S_next', 'S_next = S_R',
                'S_next.OBJECTS[n_exception] = S_P.OBJECTS[n_exception]',
                'S_public = $drive_steps(S_P, 1)',
                'S_public = S_next[.COMPLETION = BUDGET]']
        else:
            checks += ['PhpStep: S_R ~> S_next', 'S_next = ' + normal_error,
                'S_public = $drive_steps(S_R, 1)',
                'S_public.COMPLETION = BUDGET',
                'S_public.TODO = (THROW_SEARCH n_error) :: ptask_after*',
                'S_public.OBJECTS[n_error] = THROWABLE pthrowable_error',
                'pthrowable_error.KIND = "Error"',
                '$throwable_field(S_public, n_error, "message") = PSTRING ($ptascii("Cannot use string offset as an array"))',
                '$throwable_field(S_public, n_error, "line") = PINT z']
        checks += ['$heap_graph(S_next) = H_saved',
            'S_next.STORE = S_R.STORE', 'S_next.ARRAYS = S_R.ARRAYS',
            'S_next.ALLOCATIONS = S_R.ALLOCATIONS', 'S_next.EVENTS = S_R.EVENTS',
            '$drive_steps(S_R, 0) = S_R[.COMPLETION = BUDGET]']
        tail = 'S_next'
    reached = len(checks)
    checks += ['S_tail = ' + tail,
        'S_ret_found = $review_array_owner_seek($drive_steps(S_tail, 1), ' + prior.seek.term(cases.RETAINED_OUTPUTS[name]) + ', 3000)',
        '$review_cv_outputs(S_ret_found.EVENTS) = ' + prior.seek.term(cases.RETAINED_OUTPUTS[name]),
        'S_RET = $review_cv_running(S_ret_found)',
        'S_RET.COMPLETION = NORMAL',
        '$lookup(S_RET.ENV, n_key_name*) = eps',
        '$lookup(S_RET.ENV, $ptascii("arrayOwnerAlias")) = (n_owner)',
        'S_RET.STORE[n_owner] = DEFINED (PARRAY n_retained)',
        '$(n_retained < |S_RET.ARRAYS|)',
        'H_RET = $heap_graph(S_RET)', '$heap_valid(H_RET)',
        '$heap_member(HCELL n_owner, $heap_prune(H_RET).NODES)',
        '$heap_member(HARRAY n_retained, $heap_prune(H_RET).NODES)',
        '~$heap_member(HARRAY n_array, $heap_prune(H_RET).NODES)',
        '~$heap_member(HARRAY n_middle, $heap_prune(H_RET).NODES)',
        '$node_children(S_RET, HCELL n_owner) = [HARRAY n_retained]',
        '$heap_edge_owners(HARRAY n_retained, H_RET.EDGES, [HCELL n_owner]) = 1',
        '$heap_owners($heap_prune(H_RET), HARRAY n_retained) = 1',
        '$heap_count(HARRAY n_retained, $pools_nodes(S_RET.POOLS)) = 0',
        'S_DONE = $drive_steps(S_RET, 3000)',
        r'S_DONE.COMPLETION = NORMAL /\ S_DONE.TODO = eps /\ S_DONE.EXITSTATUS = 0',
        r'S_DONE.CURRENT = eps /\ S_DONE.FRAMES = eps /\ S_DONE.HELD = eps',
        '$lookup(S_DONE.ENV, $ptascii("arrayOwnerAlias")) = eps',
        '~$heap_member(HCELL n_owner, $heap_prune($heap_graph(S_DONE)).NODES)',
        '~$heap_member(HARRAY n_retained, $heap_prune($heap_graph(S_DONE)).NODES)',
        '$review_cv_outputs(S_DONE.EVENTS) = ' + prior.seek.term(cases.OUTPUTS[name]),
        *prior.seek.public('S_DONE')]
    if mixed:
        checks += ['$weakref_get(S_RET, n_wrapper) = POBJECT n_object',
            '$heap_member(HOBJECT n_object, $heap_prune(H_RET).NODES)',
            '$heap_owners($heap_prune(H_RET), HOBJECT n_object) = 1',
            'S_RET.STORE[n_alias] = DEFINED (PINT 11)',
            '$weakref_get(S_DONE, n_wrapper) = PNULL',
            '~$heap_member(HOBJECT n_object, S_DONE.ALLOCATIONS)',
            '$lookup(S_DONE.ENV, $ptascii("arrayAlias")) = (n_alias)',
            'S_DONE.STORE[n_alias] = DEFINED (PINT 11)',
            '$heap_member(HCELL n_alias, S_DONE.ALLOCATIONS)']
    else:
        checks += ['S_RET.ARRAYS[n_retained].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 11))]']
    if pending:
        checks += ['S_DONE.OBJECTS[n_exception] = S_R.OBJECTS[n_exception]']
    if PRELAW:
        return checks, len(checks) - reached
    checks += ['$drive_steps(S_E, 5000) = S_DONE',
        '$drive_steps(S_tail, 3000) = S_DONE',
        '$drive_steps($review_cv_running(S_public), 3000) = S_DONE']
    reached = len(checks)
    for tag, target in (('root', 'n_array'), ('middle', 'n_middle')):
        state = 'S_cycle_' + tag
        checks += [state + ' = S_R[.STORE[n_owner] = DEFINED (PARRAY ' + target + ')]',
            '$heap_valid($heap_graph(' + state + '))',
            '~$string_unset_bool_cv_post_nonempty_array(' + state + ', n_key)']
    checks += ['S_cycle_child = S_R[.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (ALIAS n_owner)]]',
        '$heap_valid($heap_graph(S_cycle_child))',
        '~$string_unset_bool_cv_post_nonempty_array(S_cycle_child, n_key)']
    for changed in (
        'S_R[.REFCELLS = $literal_reference_delete(S_R.REFCELLS, n_owner)]',
        'S_R[.STORE[n_owner] = UNDEFINED]',
        'S_R[.STORE[n_owner] = DEFINED (PARRAY (|S_R.ARRAYS|))]',
        'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HCELL n_owner)]',
        'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HARRAY n_child)]',
        'S_R[.REFCELLS = S_R.REFCELLS ++ [n_key]]',
    ):
        checks += ['~$string_unset_bool_cv_post_cell(' + changed + ', n_key_name*, z_key, n_key)']
    for changed in ('S_R[.CODE = eps]', 'S_R[.SOURCES = eps]', 'S_R[.ORIGIN = eps]'):
        checks += ['~$call_task_valid(' + changed + ', ' + resume + ')']
    checks += ['S_string_alias = S_R[.STORE[n_owner] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("alias-text")))]',
        '$call_reference_operand_valid(S_string_alias, REFERENCE n_owner)',
        '$heap_valid($heap_graph(S_string_alias))',
        '$string_unset_bool_cv_post_nonempty_array(S_string_alias, n_key)',
        '$string_unset_bool_cv_post_cell(S_string_alias, n_key_name*, z_key, n_key)']
    if mixed:
        checks += ['S_scalar_alias_cycle = S_R[.STORE[n_alias] = DEFINED (PARRAY n_middle)]',
            '$heap_valid($heap_graph(S_scalar_alias_cycle))',
            '~$string_unset_bool_cv_post_nonempty_array(S_scalar_alias_cycle, n_key)']
    return checks, len(checks) - reached


if __name__ == '__main__':
    PRELAW = '--prelaw' in sys.argv
    if PRELAW:
        sys.argv.remove('--prelaw')
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in range(4)
    watched = [Path(__file__), Path(prior.__file__), Path(prior.seek.__file__),
               Path(prior.sl.__file__), Path(cases.prior.__file__),
               *[prior.runner.ROOT / name for name in cases.WATCHED]]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner = prior.runner
    runner.NAME = tuple(cases.CASES)[INDEX]
    runner.OUTPUT = cases.OUTPUTS[runner.NAME]
    runner.cases, runner.conditions = cases, conditions
    runner.PREFIX, runner.recorded = PREFIX, prior.sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    output = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(output.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Independent source/quiet-read/fullheap proves two real ALIAS entries to one marked '
        'cell and one child-array edge before old Unsupported. Hypothetical caller retainer/final '
        'retirement checkpoints remain separately derived, source0/native0.' if PRELAW else
        'Independent owning-array alias reception preserves exact Error or pending Throwable and '
        'complete source/public/split states, live retainer after key retirement, final alias/object '
        'retirement and WeakReference NULL. Derived cycle/cell/source refusals stay separate; source0/native0.')
    output.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
