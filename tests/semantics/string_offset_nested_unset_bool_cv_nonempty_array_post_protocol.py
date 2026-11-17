#!/usr/bin/env python3
"""Source-reached nonempty-array owners and separately derived caller cleanup."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_empty_array_post_protocol as prior
import string_offset_nested_unset_bool_cv_nonempty_array_post_cases as cases

INDEX = 0
PRELAW = False


def front(program, path):
    prior.INDEX, prior.cases = INDEX, cases
    checks = prior.front(program, path)
    mixed = cases.FACTS[tuple(cases.CASES)[INDEX]]['mixed']
    shape = '[ENTRY (KINT 0) (DIRECT (PINT 7))]'
    children = 'eps'
    if mixed:
        shape = ('[ENTRY (KINT 0) (DIRECT (PINT 7)), ENTRY (KINT 1) (DIRECT (PARRAY n_child)), '
                 'ENTRY (KINT 2) (ALIAS n_alias), ENTRY (KINT 3) (DIRECT (POBJECT n_object)), '
                 'ENTRY (KINT 4) (DIRECT (PSTRING_CARRIER (REQUEST_STRING n_text) ($ptascii("req-text"))))]')
        children = '[HARRAY n_child, HCELL n_alias, HOBJECT n_object]'
    checks[checks.index('parray_key.ITEMS = eps')] = 'parray_key.ITEMS = ' + shape
    checks[checks.index('$node_children(S_R, HARRAY n_array) = eps')] = '$node_children(S_R, HARRAY n_array) = ' + children
    checks += ['$cast_truth_int(S_R, PARRAY n_array) = 1',
        '~$string_unset_bool_cv_post_empty_array(S_R, n_key)',
        '$lookup(S_R.ENV, $ptascii("last")) = (n_last)',
        'S_R.STORE[n_last] = DEFINED (PINT 7)']
    if mixed:
        checks += ['$(n_child < |S_R.ARRAYS|)',
            'n_child =/= n_array',
            'S_R.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8))]',
            '$heap_member(HARRAY n_child, H_R.NODES)',
            '$heap_member(HARRAY n_child, $heap_prune(H_R).NODES)',
            '$node_children(S_R, HARRAY n_child) = eps',
            '$heap_edge_owners(HARRAY n_child, H_R.EDGES, [HARRAY n_array]) = 1',
            '$($heap_owners(H_R, HARRAY n_child) > 0)',
            '$lookup(S_R.ENV, $ptascii("arrayAlias")) = (n_alias)',
            'n_alias =/= n_key',
            '$(n_alias < |S_R.STORE|)',
            'S_R.STORE[n_alias] = DEFINED (PINT 9)',
            'n_alias <- S_R.REFCELLS',
            '$call_reference_operand_valid(S_R, REFERENCE n_alias)',
            '$literal_reference_plain_cell(S_R, n_alias)',
            '$heap_member(HCELL n_alias, H_R.ROOTS)',
            '$heap_member(HCELL n_alias, $heap_prune(H_R).NODES)',
            '$heap_edge_owners(HCELL n_alias, H_R.EDGES, [HARRAY n_array]) = 1',
            '$node_children(S_R, HCELL n_alias) = eps',
            '$(n_object < |S_R.OBJECTS|)',
            'S_R.OBJECTS[n_object] = STDINSTANCE',
            '$node_children(S_R, HOBJECT n_object) = eps',
            '$heap_member(HOBJECT n_object, $heap_prune(H_R).NODES)',
            '$heap_edge_owners(HOBJECT n_object, H_R.EDGES, [HARRAY n_array]) = 1',
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
    facts = cases.FACTS[tuple(cases.CASES)[INDEX]]
    checks += ['~$string_unset_bool_cv_post_value(PARRAY n_array)',
        '~$string_unset_bool_cv_post_normal_value(PARRAY n_array)']
    resume = 'STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key'
    if PRELAW:
        checks += ['~$string_unset_bool_cv_post_cell(S_R, n_key_name*, z_key, n_key)',
            '~$string_unset_bool_cv_post_normal_cell(S_R, n_key_name*, z_key, n_key)']
        if facts['throwing']:
            checks += ['PhpStep: S_P ~> S_old',
                'S_old = S_R[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
        else:
            checks += ['PhpStep: S_R ~> S_old',
                'S_old = S_R[.TODO = ptask_after*][.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
    else:
        checks += ['$string_unset_bool_cv_post_nonempty_array(S_R, n_key)',
            '$string_unset_bool_cv_post_cell(S_R, n_key_name*, z_key, n_key)',
            '$string_unset_bool_cv_post_normal_cell(S_R, n_key_name*, z_key, n_key)',
            '$string_unset_bool_cv_post_discard_cell(S_R, n_key_name*, z_key, n_key)',
            '~$string_unset_cv_range_discard(S_R, ' + resume + ')']
        if facts['throwing']:
            checks += ['$error_read_discard(S_R, ' + resume + ') = S_R',
                '$return_discard(S_cut, ERROR_HANDLER_RESULT perrorcall_entered) = S_R',
                'PhpStep: S_P ~> S_next', 'S_next = S_R',
                'S_next.OBJECTS[n_throwable] = S_P.OBJECTS[n_throwable]',
                '$drive_steps(S_P, 1) = S_next[.COMPLETION = BUDGET]']
        else:
            checks += ['PhpStep: S_R ~> S_next',
                'S_next = S_R[.TODO = ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z]',
                'S_public = $drive_steps(S_R, 1)',
                'S_public.COMPLETION = BUDGET',
                'S_public.TODO = (THROW_SEARCH n_error) :: ptask_after*',
                'S_public.OBJECTS[n_error] = THROWABLE pthrowable_error',
                'pthrowable_error.KIND = "Error"',
                '$throwable_field(S_public, n_error, "message") = PSTRING ($ptascii("Cannot use string offset as an array"))',
                '$throwable_field(S_public, n_error, "line") = PINT z']
        checks += ['$heap_graph(S_next) = H_R',
            'S_next.STORE = S_R.STORE', 'S_next.ARRAYS = S_R.ARRAYS',
            'S_next.ALLOCATIONS = S_R.ALLOCATIONS', 'S_next.EVENTS = S_R.EVENTS',
            '$drive_steps(S_R, 0) = S_R[.COMPLETION = BUDGET]']
    checks += [
        '$string_unset_cv_range_plan(S_R) = eps']
    reached = len(checks)
    # In PRELAW mode this bypass is derived, never whole-source reachability.
    tail = ('S_R' if facts['throwing'] else 'S_next' if not PRELAW else
            'S_R[.TODO = ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z]')
    checks += ['S_tail = ' + tail,
        'S_DONE = $drive_steps(S_tail, 3000)',
        r'S_DONE.COMPLETION = NORMAL /\ S_DONE.TODO = eps /\ S_DONE.EXITSTATUS = 0',
        r'S_DONE.CURRENT = eps /\ S_DONE.FRAMES = eps /\ S_DONE.HELD = eps',
        'S_DONE.ERRORHANDLER = S_R.ERRORHANDLER',
        '$lookup(S_DONE.ENV, n_key_name*) = eps',
        '$review_cv_outputs(S_DONE.EVENTS) = ' + prior.shared.term(cases.OUTPUTS[tuple(cases.CASES)[INDEX]]),
        *prior.shared.public('S_DONE')]
    if facts['mixed']:
        checks += ['S_DONE.STORE[n_alias] = DEFINED (PINT 11)',
            '$lookup(S_DONE.ENV, $ptascii("arrayAlias")) = (n_alias)',
            '$weakref_get(S_DONE, n_wrapper) = PNULL',
            '~$heap_member(HOBJECT n_object, S_DONE.ALLOCATIONS)',
            '~$heap_member(HARRAY n_array, S_DONE.ALLOCATIONS)',
            '$heap_member(HCELL n_alias, S_DONE.ALLOCATIONS)',
            '$heap_member(HARRAY n_child, S_DONE.ALLOCATIONS)']
    if facts['throwing']:
        checks += ['S_DONE.OBJECTS[n_throwable] = S_R.OBJECTS[n_throwable]']
    if PRELAW:
        return checks, len(checks) - reached
    checks += ['$drive_steps(S_E, 5000) = S_DONE',
        '$drive_steps(S_P, 3000) = S_DONE']
    if not facts['throwing']:
        checks += ['$drive_steps($review_cv_running(S_public), 3000) = S_DONE']
    reached = len(checks)
    for tag, changed in (
        ('no_array', 'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HARRAY n_array)]'),
        ('no_cell', 'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HCELL n_key)]'),
        ('duplicate', 'S_R[.ALLOCATIONS = S_R.ALLOCATIONS ++ [HARRAY n_array]]'),
        ('oob', 'S_R[.STORE[n_key] = DEFINED (PARRAY (|S_R.ARRAYS|))]'),
        ('undefined', 'S_R[.STORE[n_key] = UNDEFINED]'),
        ('uninitialized', 'S_R[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) UNINITIALIZED]]'),
        ('raw_string', 'S_R[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING ($ptascii("raw"))))]]'),
        ('undefined_leaf', 'S_R[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT PUNDEFINED)]]'),
        ('self_child', 'S_R[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_array))]]'),
        ('self_alias', 'S_R[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_key)]]'),
        ('forged_request', 'S_R[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING_CARRIER (REQUEST_STRING (|S_R.STRINGDATA|)) ($ptascii("forged"))))]]'),
    ):
        state = 'S_bad_' + tag
        checks += [state + ' = ' + changed,
            '~$string_unset_bool_cv_post_nonempty_array(' + state + ', n_key)',
            '~$string_unset_bool_cv_post_cell(' + state + ', n_key_name*, z_key, n_key)',
            '~$string_unset_bool_cv_post_normal_cell(' + state + ', n_key_name*, z_key, n_key)']
    if facts['mixed']:
        for tag, changed in (
            ('child', 'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HARRAY n_child)]'),
            ('alias', 'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HCELL n_alias)]'),
            ('object', 'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HOBJECT n_object)]'),
            ('alias_mark', 'S_R[.REFCELLS = $literal_reference_delete(S_R.REFCELLS, n_alias)]'),
            ('object_kind', 'S_R[.OBJECTS[n_object] = WEAKREFERENCE eps]'),
            ('child_cycle', 'S_R[.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_array))]]'),
            ('request_bytes', 'S_R[.STRINGDATA[n_text] = $ptascii("changed")]'),
        ):
            state = 'S_bad_' + tag
            checks += [state + ' = ' + changed,
                '~$string_unset_bool_cv_post_nonempty_array(' + state + ', n_key)',
                '~$string_unset_bool_cv_post_cell(' + state + ', n_key_name*, z_key, n_key)']
    for changed in (
        'S_R[.ENV = $unbind(S_R.ENV, n_key_name*)]',
        'S_R[.REFCELLS = S_R.REFCELLS ++ [n_key]]',
    ):
        checks += ['~$string_unset_bool_cv_post_cell(' + changed + ', n_key_name*, z_key, n_key)',
            '~$string_unset_bool_cv_post_normal_cell(' + changed + ', n_key_name*, z_key, n_key)']
    for changed in ('S_R[.CODE = eps]', 'S_R[.SOURCES = eps]', 'S_R[.ORIGIN = eps]'):
        checks.append('~$call_task_valid(' + changed + ', ' + resume + ')')
    checks += ['~$string_unset_bool_cv_post_nonempty_array(S_R, (|S_R.STORE|))',
        '$call_task_valid(S_bad_self_child, ' + resume + ')']
    if facts['throwing']:
        checks += ['$error_read_discard(S_bad_self_child, ' + resume + ') = S_bad_self_child[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
    else:
        checks += ['PhpStep: S_bad_self_child ~> S_bad_next',
            'S_bad_next = S_bad_self_child[.TODO = ptask_after*][.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
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
    report['scope'] = ('Source-reached nonempty-array saved-CV owners before old Unsupported; separately derived caller cleanup; source0/native0.' if PRELAW else
                       'Source-reached nonempty-array saved-CV source/quiet read/full heap and ordered descendant/alias/'
                       'stdClass/REQUEST owners preserve fixed Error or same pending Throwable/tail. Whole/split budgets, '
                       'key retirement/WeakReference NULL and alias survivor pass; derived malformed payload/owner/source '
                       'refusals remain separate; source0/native0.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
