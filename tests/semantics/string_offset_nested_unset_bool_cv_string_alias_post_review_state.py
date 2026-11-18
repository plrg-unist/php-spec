#!/usr/bin/env python3
"""Independent non-NUL STRING aliases, header validity and real cell owners."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_empty_array_post_review_state as prior
import string_offset_nested_unset_bool_cv_string_alias_post_cases as cases

INDEX = 0
PRELAW = False
PREFIX = prior.seek.PREFIX + r'''
dec $review_text_alias_seek(pstate, nat*, nat) : pstate
def $review_text_alias_seek(S, n_want*, 0) = S
def $review_text_alias_seek(S, n_want*, n) = S
  -- if $(n > 0)
  -- if $review_cv_outputs(S.EVENTS) = n_want* \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $review_text_alias_seek(S, n_want*, n) = $review_text_alias_seek($drive_steps($review_cv_running(S), 1), n_want*, $nabs($(n - 1)))
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
    facts = cases.FACTS[tuple(cases.CASES)[INDEX]]
    checks += ['$(n_middle < |S_R.ARRAYS|)',
        'n_middle =/= n_array',
        'S_R.ARRAYS[n_middle].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8)), ENTRY (KINT 1) (ALIAS n_alias), ENTRY (KINT 2) (ALIAS n_alias)]',
        '$node_children(S_R, HARRAY n_middle) = [HCELL n_alias, HCELL n_alias]',
        '$lookup(S_R.ENV, $ptascii("textAlias")) = (n_alias)',
        'n_alias =/= n_key',
        '$(n_alias < |S_R.STORE|)',
        'S_R.STORE[n_alias] = DEFINED (PSTRING_CARRIER pstringidentity_initial n_initial*)',
        'n_initial* = ' + prior.seek.term(facts['initial']),
        'n_alias <- S_R.REFCELLS',
        '$call_reference_operand_valid(S_R, REFERENCE n_alias)',
        '$propref_at(S_R.PROPREFS, n_alias) = eps',
        '$reference_coercion_at(S_R.REFCOERCIONS, n_alias) = eps',
        '$parameter_backing_at(S_R.PARAMETERBACKINGS, n_alias) = eps',
        '$string_carrier_valid(S_R, PSTRING_CARRIER pstringidentity_initial n_initial*)',
        '$c_string(n_initial*) = n_initial*',
        '$value_nodes(PSTRING_CARRIER pstringidentity_initial n_initial*) = eps',
        '$node_children(S_R, HCELL n_alias) = eps',
        '$heap_member(HARRAY n_middle, $heap_prune(H_saved).NODES)',
        '$heap_member(HCELL n_alias, $heap_prune(H_saved).NODES)',
        '$heap_edge_owners(HCELL n_alias, H_saved.EDGES, [HARRAY n_middle]) = 2',
        '$heap_edge_owners(HCELL n_alias, H_saved.EDGES, H_saved.NODES) = 2',
        'n_alias_roots = $heap_count(HCELL n_alias, H_saved.ROOTS)',
        '$(n_alias_roots > 0)',
        '$heap_count(HCELL n_alias, H_saved.DEBTS) = 0',
        '$heap_owners(H_saved, HCELL n_alias) = $(n_alias_roots + 2)',
        '~$literal_reference_plain_cell(S_R, n_alias)',
        '$string_read_array_string_cell(S_R, n_alias)',
        '$cast_truth_int(S_R, PARRAY n_array) = 1',
        '$cast_truth_int(S_R, PSTRING_CARRIER pstringidentity_initial n_initial*) = ' + ('1' if facts['requested'] else '0'),
        '$lookup(S_R.ENV, $ptascii("last")) = (n_last)',
        'S_R.STORE[n_last] = DEFINED (PINT 7)']
    if facts['requested']:
        checks += ['pstringidentity_initial = REQUEST_STRING n_initial_text',
            '$(n_initial_text < |S_R.STRINGDATA|)',
            'S_R.STRINGDATA[n_initial_text] = n_initial*']
    else:
        checks += ['pstringidentity_initial = INTERNED_STRING',
            '$startup_bytes(n_initial*)']
    return checks


def conditions(program, path):
    checks = front(program, path)
    name = tuple(cases.CASES)[INDEX]
    facts = cases.FACTS[name]
    pending = facts['throwing']
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
        'S_ret_found = $review_text_alias_seek($drive_steps(S_tail, 1), ' + prior.seek.term(cases.RETAINED_OUTPUTS[name]) + ', 3000)',
        '$review_cv_outputs(S_ret_found.EVENTS) = ' + prior.seek.term(cases.RETAINED_OUTPUTS[name]),
        'S_RET = $review_cv_running(S_ret_found)',
        'S_RET.COMPLETION = NORMAL',
        '$lookup(S_RET.ENV, n_key_name*) = eps',
        '$lookup(S_RET.ENV, $ptascii("textAlias")) = (n_alias)',
        'S_RET.STORE[n_alias] = DEFINED (PSTRING_CARRIER (REQUEST_STRING n_after_text) n_after*)',
        'n_after* = $ptascii("after-text")',
        '$(n_after_text < |S_RET.STRINGDATA|)',
        'S_RET.STRINGDATA[n_after_text] = n_after*',
        '$string_carrier_valid(S_RET, PSTRING_CARRIER (REQUEST_STRING n_after_text) n_after*)',
        '$value_nodes(PSTRING_CARRIER (REQUEST_STRING n_after_text) n_after*) = eps',
        '$node_children(S_RET, HCELL n_alias) = eps',
        'H_RET = $heap_graph(S_RET)', '$heap_valid(H_RET)',
        '$heap_member(HCELL n_alias, $heap_prune(H_RET).NODES)',
        '~$heap_member(HARRAY n_array, $heap_prune(H_RET).NODES)',
        '~$heap_member(HARRAY n_middle, $heap_prune(H_RET).NODES)',
        '$heap_edge_owners(HCELL n_alias, $heap_prune(H_RET).EDGES, $heap_prune(H_RET).NODES) = 0',
        '$($heap_owners($heap_prune(H_RET), HCELL n_alias) > 0)',
        'S_DONE = $drive_steps(S_RET, 3000)',
        r'S_DONE.COMPLETION = NORMAL /\ S_DONE.TODO = eps /\ S_DONE.EXITSTATUS = 0',
        r'S_DONE.CURRENT = eps /\ S_DONE.FRAMES = eps /\ S_DONE.HELD = eps',
        '$lookup(S_DONE.ENV, $ptascii("textAlias")) = eps',
        '~$heap_member(HCELL n_alias, $heap_prune($heap_graph(S_DONE)).NODES)',
        'S_DONE.STRINGDATA[n_after_text] = n_after*',
        '$string_carrier_valid(S_DONE, PSTRING_CARRIER (REQUEST_STRING n_after_text) n_after*)',
        '~$string_read_array_string_cell(S_DONE, n_alias)',
        '$review_cv_outputs(S_DONE.EVENTS) = ' + prior.seek.term(cases.OUTPUTS[name]),
        *prior.seek.public('S_DONE')]
    if facts['requested']:
        checks += ['n_after_text =/= n_initial_text']
    if pending:
        checks += ['S_DONE.OBJECTS[n_exception] = S_R.OBJECTS[n_exception]']
    if PRELAW:
        return checks, len(checks) - reached
    checks += ['$drive_steps(S_E, 5000) = S_DONE',
        '$drive_steps(S_tail, 3000) = S_DONE',
        '$drive_steps($review_cv_running(S_public), 3000) = S_DONE']
    reached = len(checks)
    for changed in (
        'S_R[.REFCELLS = $literal_reference_delete(S_R.REFCELLS, n_alias)]',
        'S_R[.STORE[n_alias] = UNDEFINED]',
        'S_R[.STORE[n_alias] = DEFINED (PSTRING n_initial*)]',
        'S_R[.STORE[n_alias] = DEFINED (PSTRING_CARRIER (REQUEST_STRING (|S_R.STRINGDATA|)) n_initial*)]',
        'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HCELL n_alias)]',
        'S_R[.REFCELLS = S_R.REFCELLS ++ [n_key]]',
    ):
        checks += ['~$string_unset_bool_cv_post_cell(' + changed + ', n_key_name*, z_key, n_key)']
    for changed in ('S_R[.CODE = eps]', 'S_R[.SOURCES = eps]', 'S_R[.ORIGIN = eps]'):
        checks += ['~$call_task_valid(' + changed + ', ' + resume + ')']
    checks += ['S_promoted = S_R[.STORE[n_alias] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("alias-text")))]',
        '$heap_graph(S_promoted) = H_saved',
        '$string_read_array_string_cell(S_promoted, n_alias)',
        '$string_unset_bool_cv_post_nonempty_array(S_promoted, n_key)',
        '$string_unset_bool_cv_post_cell(S_promoted, n_key_name*, z_key, n_key)']
    if facts['requested']:
        checks += ['n_nul* = [114, 0, 120]',
            'S_nul = S_R[.STRINGDATA[n_initial_text] = n_nul*][.STORE[n_alias] = DEFINED (PSTRING_CARRIER (REQUEST_STRING n_initial_text) n_nul*)]',
            '$heap_graph(S_nul) = H_saved',
            '$string_carrier_valid(S_nul, PSTRING_CARRIER (REQUEST_STRING n_initial_text) n_nul*)',
            '~$string_read_array_string_cell(S_nul, n_alias)',
            '~$string_unset_bool_cv_post_nonempty_array(S_nul, n_key)']
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
    report['scope'] = ('Independent source/quiet-read/fullheap proves live same-cell STRING aliases, actual '
        'INTERNED falsey or REQUEST header and no heap child before old Unsupported; separately derived '
        'retainer/last-cell checkpoints distinguish registry validity from ownership, source0/native0.' if PRELAW else
        'Independent non-NUL STRING alias reception preserves exact Error or same Throwable and '
        'source/public/whole/split states. Reassignment, key-retired/live-retainer and final cell retirement '
        'keep registry/header validity separate from real ownership. Derived source/cell/carrier/NUL '
        'refusals stay separate; source0/native0.')
    output.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
