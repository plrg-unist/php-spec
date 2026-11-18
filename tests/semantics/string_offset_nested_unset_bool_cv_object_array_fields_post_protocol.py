#!/usr/bin/env python3
"""Reached DIRECT array fields retain COW, embedded references and outside owners."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_object_scalar_fields_post_protocol as prior
import string_offset_nested_unset_bool_cv_object_array_fields_post_cases as cases

INDEX = 0
PRELAW = False
PART = 'all'
FRONT = prior.front
PREFIX = prior.PREFIX


def fields(left, right):
    return ('[{DECL eps, NAME $ptascii("left"), STATE PROP_VALUE (DIRECT (PARRAY ' + left + '))}, '
            '{DECL eps, NAME $ptascii("right"), STATE PROP_VALUE (DIRECT (PARRAY ' + right + '))}]')


def items(value):
    return '[ENTRY (KINT 0) (DIRECT (PINT ' + str(value) + ')), ENTRY (KINT 1) (ALIAS n_field)]'


def front(program, path):
    checks = FRONT(program, path)
    old = '$node_children(S_R, HOBJECT n_object) = eps'
    assert checks.count(old) == 1
    checks[checks.index(old)] = '$node_children(S_R, HOBJECT n_object) = [HARRAY n_payload, HARRAY n_payload]'
    checks += ['$lookup(S_R.ENV, $ptascii("outside")) = (n_outside)',
        'S_R.STORE[n_outside] = DEFINED (PARRAY n_payload)',
        '$(n_payload < |S_R.ARRAYS|)', r'n_payload =/= n_array /\ n_payload =/= n_middle',
        'S_R.ARRAYS[n_payload].ITEMS = ' + items(11),
        '$lookup(S_R.ENV, $ptascii("fieldValue")) = (n_field)',
        'S_R.STORE[n_field] = DEFINED (PINT 7)',
        '$literal_reference_plain_cell(S_R, n_field)',
        '$node_children(S_R, HCELL n_outside) = [HARRAY n_payload]',
        '$node_children(S_R, HARRAY n_payload) = [HCELL n_field]',
        '$node_children(S_R, HCELL n_field) = eps',
        '$heap_member(HCELL n_outside, H_R.ROOTS)',
        '$heap_member(HCELL n_field, H_R.ROOTS)',
        '$heap_member(HARRAY n_payload, $heap_prune(H_R).NODES)',
        '$heap_edge_owners(HARRAY n_payload, H_R.EDGES, [HOBJECT n_object]) = 2',
        '$heap_edge_owners(HARRAY n_payload, H_R.EDGES, [HCELL n_outside]) = 1',
        '$heap_owners(H_R, HARRAY n_payload) = 3',
        '$heap_edge_owners(HCELL n_field, H_R.EDGES, [HARRAY n_payload]) = 1',
        '$property_release_nodes(' + fields('n_payload', 'n_payload') + ') = [HARRAY n_payload, HARRAY n_payload]']
    return checks


def conditions(program, path):
    prior.INDEX, prior.PRELAW, prior.cases = INDEX, PRELAW, cases
    prior.INITIAL = fields('n_payload', 'n_payload')
    prior.CHANGED, prior.REBOUND = fields('n_left', 'n_right'), 'eps'
    prior.front = front
    try:
        checks, derived = prior.conditions(program, path)
    finally:
        prior.front = FRONT
    old = '$node_children(S_B, HOBJECT n_object) = eps'
    assert checks.count(old) == 1
    checks[checks.index(old)] = '$node_children(S_B, HOBJECT n_object) = [HARRAY n_left, HARRAY n_right]'
    at = checks.index('H_B = $heap_graph(S_B)') + 1
    extra = [r'n_left =/= n_payload /\ n_right =/= n_payload /\ n_left =/= n_right',
        '$(n_left < |S_B.ARRAYS|)', '$(n_right < |S_B.ARRAYS|)',
        'S_B.ARRAYS[n_left].ITEMS = ' + items(19),
        'S_B.ARRAYS[n_right].ITEMS = ' + items(11),
        'S_B.ARRAYS[n_payload].ITEMS = ' + items(11),
        'S_B.STORE[n_outside] = DEFINED (PARRAY n_payload)',
        '$lookup(S_B.ENV, $ptascii("fieldValue")) = eps',
        'S_B.STORE[n_field] = DEFINED (PINT 13)',
        '$literal_reference_plain_cell(S_B, n_field)',
        '$node_children(S_B, HARRAY n_left) = [HCELL n_field]',
        '$node_children(S_B, HARRAY n_right) = [HCELL n_field]',
        '$node_children(S_B, HARRAY n_payload) = [HCELL n_field]',
        '$heap_owners(H_B, HARRAY n_left) = 1', '$heap_owners(H_B, HARRAY n_right) = 1',
        '$heap_owners(H_B, HARRAY n_payload) = 1',
        '$heap_count(HCELL n_field, H_B.ROOTS) = 0', '$heap_owners(H_B, HCELL n_field) = 3']
    checks[at:at] = extra
    derived += len(extra)
    at = checks.index('H_RET = $heap_graph(S_RET)') + 1
    extra = ['~$heap_member(HARRAY n_left, S_RET.ALLOCATIONS)',
        '~$heap_member(HARRAY n_right, S_RET.ALLOCATIONS)',
        '$heap_member(HARRAY n_payload, S_RET.ALLOCATIONS)',
        'S_RET.ARRAYS[n_payload].ITEMS = ' + items(11),
        'S_RET.STORE[n_field] = DEFINED (PINT 13)',
        '$heap_owners(H_RET, HARRAY n_payload) = 1',
        '$heap_edge_owners(HARRAY n_payload, H_RET.EDGES, [HCELL n_outside]) = 1',
        '$heap_owners(H_RET, HCELL n_field) = 1',
        '$heap_count(HCELL n_field, H_RET.ROOTS) = 0']
    checks[at:at] = extra
    derived += len(extra)
    name = tuple(cases.CASES)[INDEX]
    term = prior.prior.raw.shared.term
    at = checks.index('S_DONE = $drive_steps(S_RET, 3000)')
    extra = ['S_OUT_found = $review_scalar_fields_seek($drive_steps(S_RET, 1), ' + term(cases.OUTSIDE_OUTPUTS[name]) + ', 3000)',
        '$review_scalar_fields_at(S_OUT_found, ' + term(cases.OUTSIDE_OUTPUTS[name]) + ')',
        'S_OUT = $review_cv_running(S_OUT_found)', 'S_OUT.COMPLETION = NORMAL',
        '$lookup(S_OUT.ENV, $ptascii("outside")) = eps',
        '~$heap_member(HCELL n_outside, S_OUT.ALLOCATIONS)',
        '~$heap_member(HARRAY n_payload, S_OUT.ALLOCATIONS)',
        '~$heap_member(HCELL n_field, S_OUT.ALLOCATIONS)',
        '$weakref_get(S_OUT, n_wrapper) = PNULL',
        '$weakref_get(S_OUT, n_wrapper_after) = POBJECT n_after',
        '$heap_valid($heap_graph(S_OUT))',
        'S_DONE = $drive_steps(S_OUT, 3000)']
    checks[at:at + 1] = extra
    derived += len(extra) - 1
    if PRELAW:
        return checks, derived
    reached = len(checks)
    checks += ['$string_unset_bool_cv_post_object_fields(S_R, ' + fields('n_payload', 'n_payload') + ')',
        '$string_unset_bool_cv_post_array_node(S_R, eps, n_payload)',
        '$string_unset_bool_cv_post_field_nodes(S_R, $heap_reach([HARRAY n_payload], eps, H_R.EDGES))',
        '$string_unset_bool_cv_post_object(S_B, n_object)']
    for tag, item in (
        ('parent_direct', 'DIRECT (POBJECT n_object)'),
        ('parent_alias', 'ALIAS n_owner'),
        ('array_cycle', 'DIRECT (PARRAY n_payload)'),
        ('uninitialized', 'UNINITIALIZED'),
        ('raw_string', 'DIRECT (PSTRING ($ptascii("raw")))'),
        ('nul', 'DIRECT (PSTRING_CARRIER INTERNED_STRING ([65, 0, 66]))'),
        ('wide_int', 'DIRECT (PINT 9223372036854775808)'),
    ):
        state = 'S_bad_' + tag
        checks += [state + ' = S_R[.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (' + item + ')]]',
            '~$string_unset_bool_cv_post_object(' + state + ', n_object)',
            '~$string_unset_bool_cv_post_nonempty_array(' + state + ', n_key)']
    for state in (
        'S_R[.REFCELLS = $literal_reference_delete(S_R.REFCELLS, n_field)]',
        'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HARRAY n_payload)]',
        'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HCELL n_field)]',
        'S_R[.STORE[n_field] = UNDEFINED]',
        'S_R[.PROPREFS = {CELL n_field, SOURCES eps} :: S_R.PROPREFS]',
        'S_R[.REFCOERCIONS = {CELL n_field, SITE porigin_site, LINE z, VALUE eps} :: S_R.REFCOERCIONS]',
        'S_R[.PARAMETERBACKINGS = {FUNCTION porigin_site, INDEX 0, CELL n_field, LINE z, VALUE eps} :: S_R.PARAMETERBACKINGS]',
    ):
        checks += ['~$string_unset_bool_cv_post_object(' + state + ', n_object)',
            '~$string_unset_bool_cv_post_nonempty_array(' + state + ', n_key)']
    checks += ['S_shared = S_R[.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_array)), ENTRY (KINT 1) (DIRECT (PARRAY n_array))]][.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 4))]]',
        '$heap_valid($heap_graph(S_shared))',
        '$string_unset_bool_cv_post_object(S_shared, n_object)',
        '$string_unset_bool_cv_post_array_node(S_shared, eps, n_payload)',
        'S_empty = S_R[.ARRAYS[n_payload].ITEMS = eps]',
        '$heap_valid($heap_graph(S_empty))',
        '$string_unset_bool_cv_post_object(S_empty, n_object)',
        'S_deep = S_shared[.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_middle))]][.ARRAYS[n_middle].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_array))]]',
        '$heap_valid($heap_graph(S_deep))',
        '$string_unset_bool_cv_post_object(S_deep, n_object)',
        'S_array_alias = S_R[.STORE[n_field] = DEFINED (PARRAY n_array)][.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 4))]]',
        '$heap_valid($heap_graph(S_array_alias))',
        '$call_reference_operand_valid(S_array_alias, REFERENCE n_field)',
        '$node_children(S_array_alias, HCELL n_field) = [HARRAY n_array]',
        '$string_unset_bool_cv_post_object(S_array_alias, n_object)',
        'S_alias_field = S_array_alias[.OBJECTPROPS = $objectprops_set(S_array_alias.OBJECTPROPS, n_object, [{DECL eps, NAME $ptascii("held"), STATE PROP_VALUE (ALIAS n_field)}])]',
        '$heap_valid($heap_graph(S_alias_field))',
        '~$string_unset_bool_cv_post_object(S_alias_field, n_object)']
    return checks, derived + len(checks) - reached


def selected_conditions(program, path):
    checks, derived = conditions(program, path)
    if PRELAW or PART == 'all':
        return checks, derived
    at = checks.index('$string_unset_bool_cv_post_object(S_R, n_object)')
    core, guards = checks[:at], checks[at:]
    for check in ('$string_unset_bool_cv_post_nonempty_array(S_B, n_key)',
                  '$string_unset_bool_cv_post_object(S_B, n_object)'):
        assert guards.count(check) == 1
        guards.remove(check)
        core.append(check)
    if PART == 'core':
        # Independent budget fixtures cover these complete continuation replays.
        replay = ('$drive_steps(S_P, 3000) = S_DONE' if cases.FACTS[tuple(cases.CASES)[INDEX]]['throwing'] else
                  '$drive_steps($review_cv_running($drive_steps(S_R, 1)), 3000) = S_DONE')
        assert core.count(replay) == 1
        core.remove(replay)
        return core, derived - len(guards)
    prefix = checks[:checks.index('~$string_unset_bool_cv_post_value(PARRAY n_array)')]
    assert not any(state in check for check in guards for state in ('S_B', 'S_RET', 'S_OUT', 'S_DONE', 'S_next'))
    return prefix + guards, len(guards)


if __name__ == '__main__':
    PRELAW = '--prelaw' in sys.argv
    if PRELAW:
        sys.argv.remove('--prelaw')
    if '--part' in sys.argv:
        at = sys.argv.index('--part')
        PART = sys.argv[at + 1]
        del sys.argv[at:at + 2]
    assert PART in ('all', 'core', 'guards')
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (0, 1)
    watched = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__),
        Path(prior.prior.prior.__file__), Path(cases.__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner = prior.prior.raw.runner
    runner.NAME = tuple(cases.CASES)[INDEX]
    runner.OUTPUT = cases.OUTPUTS[runner.NAME]
    runner.cases, runner.conditions = cases, selected_conditions
    runner.PREFIX, runner.recorded = PREFIX, prior.prior.raw.sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['part'] = PART
    report['source_bridge_credit'] = 0  # The independent pending budget fixture owns that credit.
    report['scope'] = ('Reached DIRECT array fields and outside owners precede old Unsupported; derived tail/COW/retirement source0/native0.'
        if PRELAW else 'Checked original SOURCE through exact new step, COW, shared references and B/R/O/native-output continuation; independent budget fixtures separately require complete direct resumption, with no public-CLI pending pass claim.'
        if PART == 'core' else 'Reached SOURCE prefix plus separately derived malformed/recursive array-field controls; source0/native0.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
