#!/usr/bin/env python3
"""Independent reached deep-array sharing, owners and exact continuations."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_empty_array_post_review_state as prior
import string_offset_nested_unset_bool_cv_deep_array_post_cases as cases

INDEX = 0
PRELAW = False


def front(program, path):
    mixed = cases.FACTS[tuple(cases.CASES)[INDEX]]['mixed']
    grand_owners, grand_roots = ('2', '0') if mixed else ('3', '1')
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
        'S_R.ARRAYS[n_middle].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8)), ENTRY (KINT 1) (DIRECT (PARRAY n_grand)), ENTRY (KINT 2) (DIRECT (PARRAY n_grand))]',
        '$(n_grand < |S_R.ARRAYS|)',
        r'n_grand =/= n_middle /\ n_grand =/= n_array',
        '$node_children(S_R, HARRAY n_middle) = [HARRAY n_grand, HARRAY n_grand]',
        '$heap_member(HARRAY n_middle, H_saved.NODES)',
        '$heap_member(HARRAY n_grand, H_saved.NODES)',
        '$heap_member(HARRAY n_middle, $heap_reach(H_saved.ROOTS, eps, H_saved.EDGES))',
        '$heap_member(HARRAY n_grand, $heap_reach(H_saved.ROOTS, eps, H_saved.EDGES))',
        '$heap_edge_owners(HARRAY n_middle, H_saved.EDGES, [HARRAY n_array]) = 1',
        '$heap_edge_owners(HARRAY n_grand, H_saved.EDGES, [HARRAY n_middle]) = 2',
        '$heap_owners(H_saved, HARRAY n_middle) = 1',
        '$heap_owners(H_saved, HARRAY n_grand) = ' + grand_owners,
        '$heap_owners($heap_prune(H_saved), HARRAY n_grand) = ' + grand_owners,
        '$heap_count(HARRAY n_grand, H_saved.ROOTS) = ' + grand_roots,
        '$heap_count(HARRAY n_grand, $pools_nodes(S_R.POOLS)) = ' + grand_roots,
        '$heap_count(HARRAY n_grand, H_saved.DEBTS) = 0',
        '~$string_read_array_child(S_R, PARRAY n_middle)',
        '$cast_truth_int(S_R, PARRAY n_array) = 1',
        '$lookup(S_R.ENV, $ptascii("grand")) = eps',
        '$lookup(S_R.ENV, $ptascii("middle")) = eps',
        '$lookup(S_R.ENV, $ptascii("last")) = (n_last)',
        'S_R.STORE[n_last] = DEFINED (PINT 7)']
    if not mixed:
        return checks + ['S_R.ARRAYS[n_grand].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]',
            '$node_children(S_R, HARRAY n_grand) = eps']
    checks += ['S_R.ARRAYS[n_grand].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9)), ENTRY (KINT 1) (ALIAS n_alias), ENTRY (KINT 2) (DIRECT (POBJECT n_object)), ENTRY (KINT 3) (DIRECT (PSTRING_CARRIER (REQUEST_STRING n_text) ($ptascii("req-text"))))]',
        '$node_children(S_R, HARRAY n_grand) = [HCELL n_alias, HOBJECT n_object]',
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
        '$heap_edge_owners(HCELL n_alias, H_saved.EDGES, [HARRAY n_grand]) = 1',
        '$(n_object < |S_R.OBJECTS|)',
        'S_R.OBJECTS[n_object] = STDINSTANCE',
        '$objectprops_at(S_R.OBJECTPROPS, n_object) = (eps)',
        '$objectprops_record_at(S_R.OBJECTPROPS, n_object) = (pobjectprops_child)',
        r'pobjectprops_child.SLOTS = eps /\ pobjectprops_child.MATERIALIZED = false',
        '$object_table_at(S_R.OBJECTTABLES, n_object) = eps',
        '$node_children(S_R, HOBJECT n_object) = eps',
        '$gc_trace_children(S_R, HOBJECT n_object) = eps',
        '$heap_member(HOBJECT n_object, $heap_reach(H_saved.ROOTS, eps, H_saved.EDGES))',
        '$heap_edge_owners(HOBJECT n_object, H_saved.EDGES, [HARRAY n_grand]) = 1',
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
                '$return_discard(S_cut, ERROR_HANDLER_RESULT perrorcall_entered) = S_R[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]',
                'PhpStep: S_P ~> S_old',
                'S_old = S_R[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
        else:
            checks += ['PhpStep: S_R ~> S_old',
                'S_old = S_R[.TODO = ptask_after*][.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
        checks += ['S_old.STORE = S_R.STORE', 'S_old.ARRAYS = S_R.ARRAYS',
            'S_old.ALLOCATIONS = S_R.ALLOCATIONS', 'S_old.EVENTS = S_R.EVENTS']
        tail = 'S_R' if pending else normal_error
    else:
        checks += ['$string_unset_bool_cv_post_discard_cell(S_R, n_key_name*, z_key, n_key)',
            '~$string_unset_cv_range_discard(S_R, ' + resume + ')']
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
                '$throwable_field(S_public, n_error, "line") = PINT z',
                *prior.seek.public('S_public')]
        checks += ['$heap_graph(S_next) = H_saved',
            'S_next.STORE = S_R.STORE', 'S_next.ARRAYS = S_R.ARRAYS',
            'S_next.ALLOCATIONS = S_R.ALLOCATIONS', 'S_next.EVENTS = S_R.EVENTS',
            '$drive_steps(S_R, 0) = S_R[.COMPLETION = BUDGET]']
        tail = 'S_next'
    reached = len(checks)
    checks += ['S_tail = ' + tail,
        '$heap_graph(S_tail) = H_saved',
        'S_DONE = $drive_steps(S_tail, 3000)',
        r'S_DONE.COMPLETION = NORMAL /\ S_DONE.TODO = eps /\ S_DONE.EXITSTATUS = 0',
        r'S_DONE.CURRENT = eps /\ S_DONE.FRAMES = eps /\ S_DONE.HELD = eps',
        '$lookup(S_DONE.ENV, n_key_name*) = eps',
        'S_DONE.ERRORHANDLER = S_R.ERRORHANDLER',
        '$review_cv_outputs(S_DONE.EVENTS) = ' + prior.seek.term(cases.OUTPUTS[name]),
        *prior.seek.public('S_DONE')]
    if mixed:
        checks += ['$weakref_get(S_DONE, n_wrapper) = PNULL',
            '~$heap_member(HOBJECT n_object, S_DONE.ALLOCATIONS)',
            '$lookup(S_DONE.ENV, $ptascii("arrayAlias")) = (n_alias)',
            'S_DONE.STORE[n_alias] = DEFINED (PINT 11)',
            '$heap_member(HCELL n_alias, S_DONE.ALLOCATIONS)']
    if pending:
        checks += ['S_DONE.OBJECTS[n_exception] = S_R.OBJECTS[n_exception]']
    if PRELAW:
        return checks, len(checks) - reached
    checks += ['$drive_steps(S_E, 5000) = S_DONE',
        '$drive_steps($review_cv_running(S_public), 3000) = S_DONE']
    reached = len(checks)
    for tag, target in (('self', 'n_grand'), ('middle', 'n_middle'), ('root', 'n_array')):
        state = 'S_cycle_' + tag
        checks += [state + ' = S_R[.ARRAYS[n_grand].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY ' + target + '))]]',
            '$heap_valid($heap_graph(' + state + '))',
            '~$string_unset_bool_cv_post_nonempty_array(' + state + ', n_key)',
            '~$string_unset_bool_cv_post_cell(' + state + ', n_key_name*, z_key, n_key)']
    for changed in (
        'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HARRAY n_middle)]',
        'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HARRAY n_grand)]',
        'S_R[.ALLOCATIONS = S_R.ALLOCATIONS ++ [HARRAY n_grand]]',
        'S_R[.ARRAYS[n_grand].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING ($ptascii("raw"))))]]',
        'S_R[.ARRAYS[n_grand].ITEMS = [ENTRY (KINT 0) (DIRECT PUNDEFINED)]]',
        'S_R[.ARRAYS[n_grand].ITEMS = [ENTRY (KINT 0) UNINITIALIZED]]',
        'S_R[.ENV = $unbind(S_R.ENV, n_key_name*)]',
        'S_R[.REFCELLS = S_R.REFCELLS ++ [n_key]]',
    ):
        checks += ['~$string_unset_bool_cv_post_cell(' + changed + ', n_key_name*, z_key, n_key)',
            '~$string_unset_bool_cv_post_normal_cell(' + changed + ', n_key_name*, z_key, n_key)']
    for changed in ('S_R[.CODE = eps]', 'S_R[.SOURCES = eps]', 'S_R[.ORIGIN = eps]'):
        checks += ['~$call_task_valid(' + changed + ', ' + resume + ')']
    if mixed:
        checks += ['S_props = $objectprops_mark(S_R[.OBJECTPROPS = $objectprops_set(S_R.OBJECTPROPS, n_object, [{DECL eps, NAME $ptascii("extra"), STATE PROP_VALUE (DIRECT (PINT 1))}])], n_object)',
            '$node_children(S_props, HOBJECT n_object) = eps',
            '$heap_valid($heap_graph(S_props))',
            'n_nul* = [114, 0, 120]',
            'S_nul = S_R[.STRINGDATA[n_text] = n_nul*][.ARRAYS[n_grand].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9)), ENTRY (KINT 1) (ALIAS n_alias), ENTRY (KINT 2) (DIRECT (POBJECT n_object)), ENTRY (KINT 3) (DIRECT (PSTRING_CARRIER (REQUEST_STRING n_text) n_nul*))]]',
            '$string_carrier_valid(S_nul, PSTRING_CARRIER (REQUEST_STRING n_text) n_nul*)',
            '$heap_graph(S_nul) = H_saved',
            'S_alias_array = S_R[.STORE[n_alias] = DEFINED (PARRAY n_middle)]',
            '$call_reference_operand_valid(S_alias_array, REFERENCE n_alias)']
        for state in ('S_props', 'S_nul', 'S_alias_array'):
            checks += ['~$string_unset_bool_cv_post_nonempty_array(' + state + ', n_key)',
                '~$string_unset_bool_cv_post_cell(' + state + ', n_key_name*, z_key, n_key)']
    if pending:
        # The fresh source can allocate arrays before throwing. Authenticate its
        # trace identity through the Throwable rather than assuming ARRAY0.
        checks += ['$throwable_field(S_R, n_exception, "trace") = PARRAY n_trace',
            '$(n_trace < |S_R.ARRAYS|)',
            'S_R.ARRAYS[n_trace].ITEMS =/= eps',
            '$entry_lookup(S_R.ARRAYS[n_trace].ITEMS, KINT 0) = (DIRECT (PARRAY n_trace_frame))',
            '$(n_trace_frame < |S_R.ARRAYS|)',
            '$entry_lookup(S_R.ARRAYS[n_trace_frame].ITEMS, KSTRING $ptascii("function")) = (DIRECT (PSTRING n_function*))',
            'n_function* =/= eps',
            '~$string_unset_bool_cv_post_array_leaf(S_R, PSTRING n_function*)',
            '~$string_unset_bool_cv_post_array_entries(S_R, [n_trace], S_R.ARRAYS[n_trace].ITEMS)',
            'S_trace = S_R[.STORE[n_key] = DEFINED (PARRAY n_trace)]',
            '$heap_valid($heap_graph(S_trace))',
            '$call_task_valid(S_trace, ' + resume + ')',
            '~$string_unset_bool_cv_post_value(PARRAY n_trace)',
            '~$string_unset_bool_cv_post_nonempty_array(S_trace, n_key)',
            '~$string_unset_bool_cv_post_cell(S_trace, n_key_name*, z_key, n_key)',
            '~$string_unset_bool_cv_post_normal_cell(S_trace, n_key_name*, z_key, n_key)']
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
    runner.PREFIX, runner.recorded = prior.seek.PREFIX, prior.sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    output = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(output.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Independent source-reached deep-array fullheap with shared grandchildren, real '
        'scalar alias, sole fieldless object owner/WeakReference nonowner and REQUEST bytes precedes '
        'old Unsupported; hypothetical caller cleanup is separate, source0/native0.' if PRELAW else
        'Independent exact deep-array normal Error or same pending Throwable/tail preserves payload, '
        'heap and shared owners through public/whole/split budgets and source observers/cleanup. '
        'Derived cycles, payload, source and current-cell refusals stay separate; source0/native0.')
    output.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
