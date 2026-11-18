#!/usr/bin/env python3
"""Reached shared deep-array owners precede post-Warning admission."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_empty_array_post_protocol as prior
import string_offset_nested_unset_bool_cv_deep_array_post_cases as cases

INDEX = 0
PRELAW = False


def front(program, path):
    prior.INDEX, prior.cases = INDEX, cases
    checks = prior.front(program, path)
    mixed = cases.FACTS[tuple(cases.CASES)[INDEX]]['mixed']
    checks[checks.index('parray_key.ITEMS = eps')] = ('parray_key.ITEMS = '
        '[ENTRY (KINT 0) (DIRECT (PINT 7)), ENTRY (KINT 1) (DIRECT (PARRAY n_middle))]')
    checks[checks.index('$node_children(S_R, HARRAY n_array) = eps')] = '$node_children(S_R, HARRAY n_array) = [HARRAY n_middle]'
    grand_items = '[ENTRY (KINT 0) (DIRECT (PINT 9))]'
    grand_children = 'eps'
    if mixed:
        grand_items = ('[ENTRY (KINT 0) (DIRECT (PINT 9)), ENTRY (KINT 1) (ALIAS n_alias), '
                       'ENTRY (KINT 2) (DIRECT (POBJECT n_object)), '
                       'ENTRY (KINT 3) (DIRECT (PSTRING_CARRIER (REQUEST_STRING n_text) ($ptascii("req-text"))))]')
        grand_children = '[HCELL n_alias, HOBJECT n_object]'
    checks += ['$(n_middle < |S_R.ARRAYS|)',
        'n_middle =/= n_array',
        'S_R.ARRAYS[n_middle].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8)), ENTRY (KINT 1) (DIRECT (PARRAY n_grand)), ENTRY (KINT 2) (DIRECT (PARRAY n_grand))]',
        '$(n_grand < |S_R.ARRAYS|)',
        r'n_grand =/= n_middle /\ n_grand =/= n_array',
        'S_R.ARRAYS[n_grand].ITEMS = ' + grand_items,
        '$node_children(S_R, HARRAY n_middle) = [HARRAY n_grand, HARRAY n_grand]',
        '$node_children(S_R, HARRAY n_grand) = ' + grand_children,
        '$heap_member(HARRAY n_middle, $heap_prune(H_R).NODES)',
        '$heap_member(HARRAY n_grand, $heap_prune(H_R).NODES)',
        '$heap_edge_owners(HARRAY n_middle, H_R.EDGES, [HARRAY n_array]) = 1',
        '$heap_edge_owners(HARRAY n_grand, H_R.EDGES, [HARRAY n_middle]) = 2',
        '$heap_owners(H_R, HARRAY n_middle) = 1',
        '$heap_owners(H_R, HARRAY n_grand) = ' + ('2' if mixed else '3'),
        '$heap_owners($heap_prune(H_R), HARRAY n_grand) = ' + ('2' if mixed else '3'),
        '$heap_count(HARRAY n_grand, H_R.ROOTS) = ' + ('0' if mixed else '1'),
        '$heap_count(HARRAY n_grand, $pools_nodes(S_R.POOLS)) = ' + ('0' if mixed else '1'),
        '$cast_truth_int(S_R, PARRAY n_array) = 1',
        '$lookup(S_R.ENV, $ptascii("last")) = (n_last)',
        'S_R.STORE[n_last] = DEFINED (PINT 7)']
    if mixed:
        checks += ['$lookup(S_R.ENV, $ptascii("arrayAlias")) = (n_alias)',
            'n_alias =/= n_key',
            'S_R.STORE[n_alias] = DEFINED (PINT 9)',
            'n_alias <- S_R.REFCELLS',
            '$literal_reference_plain_cell(S_R, n_alias)',
            '$heap_member(HCELL n_alias, H_R.ROOTS)',
            '$node_children(S_R, HCELL n_alias) = eps',
            '$heap_edge_owners(HCELL n_alias, H_R.EDGES, [HARRAY n_grand]) = 1',
            '$(n_object < |S_R.OBJECTS|)',
            'S_R.OBJECTS[n_object] = STDINSTANCE',
            '$objectprops_at(S_R.OBJECTPROPS, n_object) = (eps)',
            '$object_table_at(S_R.OBJECTTABLES, n_object) = eps',
            '$node_children(S_R, HOBJECT n_object) = eps',
            '$heap_edge_owners(HOBJECT n_object, H_R.EDGES, [HARRAY n_grand]) = 1',
            '$heap_owners(H_R, HOBJECT n_object) = 1',
            '$lookup(S_R.ENV, $ptascii("arrayWeak")) = (n_weak_cell)',
            'S_R.STORE[n_weak_cell] = DEFINED (POBJECT n_wrapper)',
            '$weakref_at(S_R, n_wrapper) = (WEAKREFERENCE (n_object))',
            '$weakref_get(S_R, n_wrapper) = POBJECT n_object',
            '$node_children(S_R, HOBJECT n_wrapper) = eps',
            '$(n_text < |S_R.STRINGDATA|)',
            'S_R.STRINGDATA[n_text] = $ptascii("req-text")',
            '$string_carrier_valid(S_R, PSTRING_CARRIER (REQUEST_STRING n_text) ($ptascii("req-text")))',
            '$value_nodes(PSTRING_CARRIER (REQUEST_STRING n_text) ($ptascii("req-text"))) = eps']
    return checks


def conditions(program, path):
    checks = front(program, path)
    name = tuple(cases.CASES)[INDEX]
    facts = cases.FACTS[name]
    resume = 'STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key'
    normal_error = ('S_R[.TODO = ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]'
                    '[.LOCATION = NOWHERE][.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z]')
    checks += ['~$string_unset_bool_cv_post_value(PARRAY n_array)',
        '~$string_unset_bool_cv_post_normal_value(PARRAY n_array)',
        '~$string_unset_bool_cv_post_empty_array(S_R, n_key)',
        '$string_unset_cv_range_plan(S_R) = eps']
    admitted = '~' if PRELAW else ''
    checks += [admitted + '$string_unset_bool_cv_post_nonempty_array(S_R, n_key)',
        admitted + '$string_unset_bool_cv_post_cell(S_R, n_key_name*, z_key, n_key)',
        admitted + '$string_unset_bool_cv_post_normal_cell(S_R, n_key_name*, z_key, n_key)']
    if PRELAW:
        if facts['throwing']:
            checks += ['$error_read_discard(S_R, ' + resume + ') = S_R[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]',
                'PhpStep: S_P ~> S_old',
                'S_old = S_R[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
        else:
            checks += ['PhpStep: S_R ~> S_old',
                'S_old = S_R[.TODO = ptask_after*][.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
        tail = 'S_R' if facts['throwing'] else normal_error
    else:
        if facts['throwing']:
            checks += ['$error_read_discard(S_R, ' + resume + ') = S_R',
                '$return_discard(S_cut, ERROR_HANDLER_RESULT perrorcall_entered) = S_R',
                'PhpStep: S_P ~> S_next', 'S_next = S_R',
                'S_next.OBJECTS[n_throwable] = S_P.OBJECTS[n_throwable]']
        else:
            checks += ['PhpStep: S_R ~> S_next', 'S_next = ' + normal_error]
        checks += ['$heap_graph(S_next) = H_R',
            'S_next.STORE = S_R.STORE', 'S_next.ARRAYS = S_R.ARRAYS',
            'S_next.ALLOCATIONS = S_R.ALLOCATIONS', 'S_next.EVENTS = S_R.EVENTS',
            '$drive_steps(S_R, 0) = S_R[.COMPLETION = BUDGET]']
        tail = 'S_next'
    reached = len(checks)
    checks += ['S_tail = ' + tail,
        'S_DONE = $drive_steps(S_tail, 3000)',
        r'S_DONE.COMPLETION = NORMAL /\ S_DONE.TODO = eps /\ S_DONE.EXITSTATUS = 0',
        r'S_DONE.CURRENT = eps /\ S_DONE.FRAMES = eps /\ S_DONE.HELD = eps',
        'S_DONE.ERRORHANDLER = S_R.ERRORHANDLER',
        '$lookup(S_DONE.ENV, n_key_name*) = eps',
        '$review_cv_outputs(S_DONE.EVENTS) = ' + prior.shared.term(cases.OUTPUTS[name]),
        *prior.shared.public('S_DONE')]
    if facts['mixed']:
        checks += ['S_DONE.STORE[n_alias] = DEFINED (PINT 11)',
            '$lookup(S_DONE.ENV, $ptascii("arrayAlias")) = (n_alias)',
            '$weakref_get(S_DONE, n_wrapper) = PNULL',
            '~$heap_member(HOBJECT n_object, S_DONE.ALLOCATIONS)',
            '$heap_member(HCELL n_alias, S_DONE.ALLOCATIONS)']
    if facts['throwing']:
        checks += ['S_DONE.OBJECTS[n_throwable] = S_R.OBJECTS[n_throwable]']
    if PRELAW:
        return checks, len(checks) - reached
    checks += ['$drive_steps(S_E, 5000) = S_DONE', '$drive_steps(S_P, 3000) = S_DONE',
        '$drive_steps(S_P, 1) = S_next[.COMPLETION = BUDGET]' if facts['throwing'] else
        '$drive_steps($review_cv_running($drive_steps(S_R, 1)), 3000) = S_DONE']
    reached = len(checks)
    for tag, target in [('self', 'n_grand'), ('middle', 'n_middle'), ('root', 'n_array')]:
        bad = 'S_cycle_' + tag
        checks += [bad + ' = S_R[.ARRAYS[n_grand].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY ' + target + '))]]',
            '$heap_valid($heap_graph(' + bad + '))',
            '~$string_unset_bool_cv_post_nonempty_array(' + bad + ', n_key)']
    for changed in (
        'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HARRAY n_middle)]',
        'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HARRAY n_grand)]',
        'S_R[.ARRAYS[n_grand].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING ($ptascii("raw"))))]]',
        'S_R[.ARRAYS[n_grand].ITEMS = [ENTRY (KINT 0) (DIRECT PUNDEFINED)]]',
        'S_R[.ARRAYS[n_grand].ITEMS = [ENTRY (KINT 0) UNINITIALIZED]]',
    ):
        checks += ['~$string_unset_bool_cv_post_nonempty_array(' + changed + ', n_key)']
    for changed in ('S_R[.CODE = eps]', 'S_R[.SOURCES = eps]', 'S_R[.ORIGIN = eps]'):
        checks += ['~$call_task_valid(' + changed + ', ' + resume + ')']
    return checks, len(checks) - reached


if __name__ == '__main__':
    PRELAW = '--prelaw' in sys.argv
    if PRELAW:
        sys.argv.remove('--prelaw')
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in range(4)
    name = tuple(cases.CASES)[INDEX]
    watched = [Path(__file__), Path(prior.__file__), Path(prior.shared.__file__),
               Path(prior.sl.__file__), Path(cases.prior.__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner = prior.runner
    runner.NAME, runner.OUTPUT = name, cases.OUTPUTS[name]
    runner.cases, runner.conditions = cases, conditions
    runner.PREFIX, runner.recorded = prior.PREFIX, prior.sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Genuine deep-array source/quiet read/full heap with shared grandchildren and real '
                       'leaf owners before old Unsupported; separately derived caller cleanup; source0/native0.'
                       if PRELAW else 'Source-reached shared deep-array owners, exact Error or pending '
                       'Throwable/tail, whole/split budgets and cleanup; derived cycle/payload/source controls separate; source0/native0.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
