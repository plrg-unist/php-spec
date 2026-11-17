#!/usr/bin/env python3
"""Independent reached nonempty-array descendants and exact continuations."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_empty_array_post_review_state as prior
import string_offset_nested_unset_bool_cv_nonempty_array_post_cases as cases

INDEX = 0
PRELAW = False


def conditions(program, path):
    facts = cases.FACTS[tuple(cases.CASES)[INDEX]]
    pending, mixed = facts['throwing'], facts['mixed']
    # Retain the earlier independent source/quiet-read proof, replacing only its
    # three empty-table facts. No new postvalue predicate establishes reachability.
    prior.INDEX, prior.cases, prior.PRELAW = INDEX, cases, True
    checks, _ = prior.conditions(program, path)
    checks = checks[:checks.index('~$string_unset_bool_cv_post_value(PARRAY n_array)')]
    shape = '[ENTRY (KINT 0) (DIRECT (PINT 7))]'
    children = 'eps'
    if mixed:
        shape = ('[ENTRY (KINT 0) (DIRECT (PINT 7)), ENTRY (KINT 1) (DIRECT (PARRAY n_child)), '
                 'ENTRY (KINT 2) (ALIAS n_alias), ENTRY (KINT 3) (DIRECT (POBJECT n_object)), '
                 'ENTRY (KINT 4) (DIRECT (PSTRING_CARRIER (REQUEST_STRING n_text) ($ptascii("req-text"))))]')
        children = '[HARRAY n_child, HCELL n_alias, HOBJECT n_object]'
    for old, new in (
        ('parray_saved.ITEMS = eps', 'parray_saved.ITEMS = ' + shape),
        ('$entries_nodes(parray_saved.ITEMS) = eps', '$entries_nodes(parray_saved.ITEMS) = ' + children),
        ('$node_children(S_R, HARRAY n_array) = eps', '$node_children(S_R, HARRAY n_array) = ' + children),
    ):
        assert checks.count(old) == 1
        checks[checks.index(old)] = new
    checks += ['parray_saved.ITEMS =/= eps',
        '$cast_truth_int(S_R, PARRAY n_array) = 1',
        '$lookup(S_R.ENV, $ptascii("last")) = (n_last)',
        'S_R.STORE[n_last] = DEFINED (PINT 7)']
    if mixed:
        checks += [
            '$(n_child < |S_R.ARRAYS|)',
            'n_child =/= n_array',
            'S_R.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8))]',
            '$node_children(S_R, HARRAY n_child) = eps',
            '$heap_member(HARRAY n_child, H_saved.NODES)',
            '$heap_member(HARRAY n_child, $heap_reach(H_saved.ROOTS, eps, H_saved.EDGES))',
            '$heap_edge_owners(HARRAY n_child, H_saved.EDGES, [HARRAY n_array]) = 1',
            '$($heap_owners(H_saved, HARRAY n_child) > 0)',
            '$lookup(S_R.ENV, $ptascii("arrayAlias")) = (n_alias)',
            'n_alias =/= n_key',
            '$(n_alias < |S_R.STORE|)',
            'S_R.STORE[n_alias] = DEFINED (PINT 9)',
            'n_alias <- S_R.REFCELLS',
            '$call_reference_operand_valid(S_R, REFERENCE n_alias)',
            '$propref_at(S_R.PROPREFS, n_alias) = eps',
            '$reference_coercion_at(S_R.REFCOERCIONS, n_alias) = eps',
            '$parameter_backing_at(S_R.PARAMETERBACKINGS, n_alias) = eps',
            '$node_children(S_R, HCELL n_alias) = eps',
            '$heap_member(HCELL n_alias, H_saved.ROOTS)',
            '$heap_member(HCELL n_alias, $heap_reach(H_saved.ROOTS, eps, H_saved.EDGES))',
            '$heap_edge_owners(HCELL n_alias, H_saved.EDGES, [HARRAY n_array]) = 1',
            '$(n_object < |S_R.OBJECTS|)',
            'S_R.OBJECTS[n_object] = STDINSTANCE',
            '$objectprops_at(S_R.OBJECTPROPS, n_object) = (eps)',
            '$objectprops_record_at(S_R.OBJECTPROPS, n_object) = (pobjectprops_child)',
            'pobjectprops_child.OBJECT = n_object',
            r'pobjectprops_child.SLOTS = eps /\ pobjectprops_child.MATERIALIZED = false',
            '$object_table_at(S_R.OBJECTTABLES, n_object) = eps',
            '$node_children(S_R, HOBJECT n_object) = eps',
            '$gc_trace_children(S_R, HOBJECT n_object) = eps',
            '$heap_member(HOBJECT n_object, $heap_reach(H_saved.ROOTS, eps, H_saved.EDGES))',
            '$heap_edge_owners(HOBJECT n_object, H_saved.EDGES, [HARRAY n_array]) = 1',
            '$heap_owners(H_saved, HOBJECT n_object) = 1',
            '$lookup(S_R.ENV, $ptascii("arrayWeak")) = (n_weak_cell)',
            'S_R.STORE[n_weak_cell] = DEFINED (POBJECT n_wrapper)',
            'n_wrapper =/= n_object',
            '$weakref_at(S_R, n_wrapper) = (WEAKREFERENCE (n_object))',
            '$weakref_get(S_R, n_wrapper) = POBJECT n_object',
            '$node_children(S_R, HOBJECT n_wrapper) = eps',
            '$heap_edge_owners(HOBJECT n_object, H_saved.EDGES, [HOBJECT n_wrapper]) = 0',
            '$(n_text < |S_R.STRINGDATA|)',
            'S_R.STRINGDATA[n_text] = $ptascii("req-text")',
            '$string_carrier_valid(S_R, PSTRING_CARRIER (REQUEST_STRING n_text) ($ptascii("req-text")))',
            '$c_string($ptascii("req-text")) = $ptascii("req-text")',
            '$value_nodes(PSTRING_CARRIER (REQUEST_STRING n_text) ($ptascii("req-text"))) = eps',
        ]
    resume = 'STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key'
    if not PRELAW:
        return postconditions(checks, pending, mixed, resume)
    checks += [
        '~$string_unset_bool_cv_post_empty_array(S_R, n_key)',
        '~$string_unset_bool_cv_post_value(PARRAY n_array)',
        '~$string_unset_bool_cv_post_normal_value(PARRAY n_array)',
        '~$string_unset_bool_cv_post_cell(S_R, n_key_name*, z_key, n_key)',
        '~$string_unset_bool_cv_post_normal_cell(S_R, n_key_name*, z_key, n_key)',
        '$string_unset_cv_range_plan(S_R) = eps',
    ]
    if pending:
        checks += [
            '$error_read_discard(S_R, ' + resume + ') = S_R[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]',
            '$return_discard(S_cut, ERROR_HANDLER_RESULT perrorcall_entered) = S_R[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]',
            'PhpStep: S_P ~> S_old',
            'S_old = S_R[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]',
        ]
    else:
        checks += ['PhpStep: S_R ~> S_old',
            'S_old = S_R[.TODO = ptask_after*][.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
    checks += ['S_old.STORE = S_R.STORE', 'S_old.ARRAYS = S_R.ARRAYS',
        'S_old.ALLOCATIONS = S_R.ALLOCATIONS', 'S_old.OBJECTS = S_R.OBJECTS',
        'S_old.EVENTS = S_R.EVENTS']
    reached = len(checks)
    # This bypassed tail is derived evidence, separate from the reached refusal.
    checks += ['S_tail = ' + ('S_R' if pending else
        'S_R[.TODO = ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z]'),
        '$heap_graph(S_tail) = H_saved',
        '$drive_steps(S_R, 0) = S_R[.COMPLETION = BUDGET]',
        'S_DONE = $drive_steps(S_tail, 3000)',
        r'S_DONE.COMPLETION = NORMAL /\ S_DONE.TODO = eps /\ S_DONE.EXITSTATUS = 0',
        'S_DONE.ERRORHANDLER = S_R.ERRORHANDLER',
        '$lookup(S_DONE.ENV, n_key_name*) = eps',
        '$review_cv_outputs(S_DONE.EVENTS) = ' + prior.seek.term(cases.OUTPUTS[tuple(cases.CASES)[INDEX]]),
        *prior.seek.public('S_DONE'),
        '$drive_steps($review_cv_running($drive_steps(S_tail, 1)), 3000) = S_DONE']
    if mixed:
        checks += ['$weakref_get(S_DONE, n_wrapper) = PNULL',
            '~$heap_member(HOBJECT n_object, S_DONE.ALLOCATIONS)',
            '~$heap_member(HARRAY n_array, S_DONE.ALLOCATIONS)',
            '$lookup(S_DONE.ENV, $ptascii("arrayAlias")) = (n_alias)',
            'S_DONE.STORE[n_alias] = DEFINED (PINT 11)',
            '$heap_member(HCELL n_alias, S_DONE.ALLOCATIONS)',
            '$heap_member(HARRAY n_child, S_DONE.ALLOCATIONS)']
    if pending:
        checks += ['S_DONE.OBJECTS[n_exception] = S_R.OBJECTS[n_exception]']
    return checks, len(checks) - reached


def postconditions(checks, pending, mixed, resume):
    checks += ['~$string_unset_bool_cv_post_empty_array(S_R, n_key)',
        '~$string_unset_bool_cv_post_value(PARRAY n_array)',
        '~$string_unset_bool_cv_post_normal_value(PARRAY n_array)',
        '$string_unset_bool_cv_post_nonempty_array(S_R, n_key)',
        '$string_unset_bool_cv_post_cell(S_R, n_key_name*, z_key, n_key)',
        '$string_unset_bool_cv_post_normal_cell(S_R, n_key_name*, z_key, n_key)',
        '$string_unset_bool_cv_post_discard_cell(S_R, n_key_name*, z_key, n_key)',
        '$string_unset_cv_range_plan(S_R) = eps',
        '~$string_unset_cv_range_discard(S_R, ' + resume + ')']
    if pending:
        checks += ['$error_read_discard(S_R, ' + resume + ') = S_R',
            '$return_discard(S_cut, ERROR_HANDLER_RESULT perrorcall_entered) = S_R',
            'PhpStep: S_P ~> S_next',
            'S_next = S_R',
            'S_next.TODO = (THROW_SEARCH n_exception) :: ptask_after*',
            'S_next.OBJECTS[n_exception] = S_P.OBJECTS[n_exception]',
            'S_public = $drive_steps(S_P, 1)',
            'S_public = S_next[.COMPLETION = BUDGET]']
    else:
        checks += ['PhpStep: S_R ~> S_next',
            'S_next = S_R[.TODO = ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z]',
            'S_public = $drive_steps(S_R, 1)',
            'S_public.COMPLETION = BUDGET',
            'S_public.TODO = (THROW_SEARCH n_error) :: ptask_after*',
            'S_public.OBJECTS[n_error] = THROWABLE pthrowable_error',
            'pthrowable_error.KIND = "Error"',
            '$throwable_field(S_public, n_error, "message") = PSTRING ($ptascii("Cannot use string offset as an array"))',
            '$throwable_field(S_public, n_error, "line") = PINT z',
            *prior.seek.public('S_public')]
    checks += ['$heap_graph(S_next) = H_saved',
        'S_next.STORE = S_R.STORE', 'S_next.ARRAYS = S_R.ARRAYS',
        'S_next.ALLOCATIONS = S_R.ALLOCATIONS', 'S_next.EVENTS = S_R.EVENTS',
        '$drive_steps(S_R, 0) = S_R[.COMPLETION = BUDGET]',
        'S_DONE = $drive_steps($review_cv_running(S_public), 3000)',
        r'S_DONE.COMPLETION = NORMAL /\ S_DONE.TODO = eps /\ S_DONE.EXITSTATUS = 0',
        r'S_DONE.CURRENT = eps /\ S_DONE.FRAMES = eps /\ S_DONE.HELD = eps',
        '$lookup(S_DONE.ENV, n_key_name*) = eps',
        'S_DONE.ERRORHANDLER = S_R.ERRORHANDLER',
        '$review_cv_outputs(S_DONE.EVENTS) = ' + prior.seek.term(cases.OUTPUTS[tuple(cases.CASES)[INDEX]]),
        *prior.seek.public('S_DONE'),
        '$drive_steps(S_E, 5000) = S_DONE']
    if mixed:
        checks += ['$weakref_get(S_DONE, n_wrapper) = PNULL',
            '~$heap_member(HOBJECT n_object, S_DONE.ALLOCATIONS)',
            '~$heap_member(HARRAY n_array, S_DONE.ALLOCATIONS)',
            '$lookup(S_DONE.ENV, $ptascii("arrayAlias")) = (n_alias)',
            'S_DONE.STORE[n_alias] = DEFINED (PINT 11)',
            '$heap_member(HCELL n_alias, S_DONE.ALLOCATIONS)',
            '$heap_member(HARRAY n_child, S_DONE.ALLOCATIONS)']
    if pending:
        checks += ['S_DONE.OBJECTS[n_exception] = S_R.OBJECTS[n_exception]']
    reached = len(checks)
    checks += ['S_ref = S_R[.REFCELLS = S_R.REFCELLS ++ [n_key]]',
        '$string_unset_bool_cv_post_nonempty_array(S_ref, n_key)',
        '~$string_unset_bool_cv_post_cell(S_ref, n_key_name*, z_key, n_key)',
        '~$string_unset_bool_cv_post_normal_cell(S_ref, n_key_name*, z_key, n_key)',
        '~$string_unset_bool_cv_post_nonempty_array(S_R, (|S_R.STORE|))']
    for changed in ('S_R[.ENV = $unbind(S_R.ENV, n_key_name*)]',
                    'S_R[.STORE[n_key] = UNDEFINED]'):
        checks += ['~$string_unset_bool_cv_post_cell(' + changed + ', n_key_name*, z_key, n_key)',
            '~$string_unset_bool_cv_post_normal_cell(' + changed + ', n_key_name*, z_key, n_key)']
    for changed in ('S_R[.CODE = eps]', 'S_R[.SOURCES = eps]', 'S_R[.ORIGIN = eps]'):
        checks += ['~$call_task_valid(' + changed + ', ' + resume + ')']
    if mixed and not pending:
        checks += [
            'S_no_props = S_R[.OBJECTPROPS = $objectprops_prune(S_R.OBJECTPROPS, $destruction_node_delete(S_R.ALLOCATIONS, HOBJECT n_object))]',
            '$objectprops_at(S_no_props.OBJECTPROPS, n_object) = eps',
            '$heap_valid($heap_graph(S_no_props))',
            'S_props = $objectprops_mark(S_R[.OBJECTPROPS = $objectprops_set(S_R.OBJECTPROPS, n_object, [{DECL eps, NAME $ptascii("extra"), STATE PROP_VALUE (DIRECT (PINT 1))}])], n_object)',
            '$node_children(S_props, HOBJECT n_object) = eps',
            '$heap_valid($heap_graph(S_props))',
            'n_nul* = [114, 0, 120]',
        ]
        shape = ('[ENTRY (KINT 0) (DIRECT (PINT 7)), ENTRY (KINT 1) (DIRECT (PARRAY n_child)), '
                 'ENTRY (KINT 2) (ALIAS n_alias), ENTRY (KINT 3) (DIRECT (POBJECT n_object)), '
                 'ENTRY (KINT 4) (DIRECT VALUE)]')
        nul_value = 'PSTRING_CARRIER (REQUEST_STRING n_text) n_nul*'
        checks += ['S_nul = S_R[.STRINGDATA[n_text] = n_nul*][.ARRAYS[n_array].ITEMS = ' + shape.replace('VALUE', '(' + nul_value + ')') + ']',
            '$string_carrier_valid(S_nul, ' + nul_value + ')',
            '$heap_graph(S_nul) = H_saved',
            '~$string_unset_bool_cv_post_array_leaf(S_nul, ' + nul_value + ')',
            'n_bad_text = |S_R.STRINGDATA|',
            'S_bad_text = S_R[.ARRAYS[n_array].ITEMS = ' + shape.replace('VALUE', '(PSTRING_CARRIER (REQUEST_STRING n_bad_text) ($ptascii("req-text")))') + ']',
            '$heap_graph(S_bad_text) = H_saved']
        for state in ('S_no_props', 'S_props', 'S_nul', 'S_bad_text'):
            checks += ['~$string_unset_bool_cv_post_nonempty_array(' + state + ', n_key)',
                '~$string_unset_bool_cv_post_cell(' + state + ', n_key_name*, z_key, n_key)',
                '~$string_unset_bool_cv_post_normal_cell(' + state + ', n_key_name*, z_key, n_key)']
    # Genuine fresh scalar-[7] fronts above exercise the exact promoted payload
    # from the two older empty-only counter rows, without renewing those suites.
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
               *[prior.runner.ROOT / path for path in cases.WATCHED]]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner = prior.runner
    runner.NAME = tuple(cases.CASES)[INDEX]
    runner.OUTPUT = cases.OUTPUTS[runner.NAME]
    runner.cases, runner.conditions = cases, conditions
    runner.PREFIX, runner.recorded = prior.seek.PREFIX, prior.sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    output = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(output.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Independent source/quiet-read/live fullheap proof reaches scalar or ordered mixed '
        'nonempty ARRAY with real child, plain alias, fieldless stdClass/weak nonowner and REQUEST text '
        'before the old Unsupported. Separate derived tail/budget checks preserve observers and cleanup; '
        'they establish no new admission or whole-source agreement, source0/native0.' if PRELAW else
        'Independent actual nonempty ARRAY continuation preserves complete raw normal Error or pending '
        'Throwable/tail, all child/alias/object/REQUEST owners, public one-step resumption, final source '
        'observers and cleanup, and exact whole/split state equality. Derived source/current-cell and '
        'fieldless-object/REQUEST-NUL/invalid-carrier refusals stay separate; source0/native0.')
    output.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
