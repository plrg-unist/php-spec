#!/usr/bin/env python3
"""Reached array-valued property ALIAS cells retain shared writes and cleanup."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_object_scalar_fields_post_protocol as prior
import string_offset_nested_unset_bool_cv_object_array_alias_fields_post_cases as cases

INDEX = 0
PRELAW = False
PART = 'all'
FRONT = prior.front
PREFIX = prior.PREFIX


def fields():
    return ('[{DECL eps, NAME $ptascii("left"), STATE PROP_VALUE (ALIAS n_payload)}, '
            '{DECL eps, NAME $ptascii("right"), STATE PROP_VALUE (ALIAS n_payload)}]')


def items(value):
    return '[ENTRY (KINT 0) (DIRECT (PINT ' + str(value) + ')), ENTRY (KINT 1) (ALIAS n_field)]'


def front(program, path):
    checks = FRONT(program, path)
    old = '$node_children(S_R, HOBJECT n_object) = eps'
    assert checks.count(old) == 1
    checks[checks.index(old)] = '$node_children(S_R, HOBJECT n_object) = [HCELL n_payload, HCELL n_payload]'
    checks += ['$lookup(S_R.ENV, $ptascii("payload")) = (n_payload)',
        '$call_reference_operand_valid(S_R, REFERENCE n_payload)',
        'S_R.STORE[n_payload] = DEFINED (PARRAY n_initial)',
        '$(n_initial < |S_R.ARRAYS|)', 'S_R.ARRAYS[n_initial].ITEMS = ' + items(11),
        '$lookup(S_R.ENV, $ptascii("outside")) = (n_outside)',
        'S_R.STORE[n_outside] = DEFINED (PARRAY n_initial)',
        '$lookup(S_R.ENV, $ptascii("fieldValue")) = (n_field)',
        'S_R.STORE[n_field] = DEFINED (PINT 7)',
        '$literal_reference_plain_cell(S_R, n_field)',
        '$node_children(S_R, HCELL n_payload) = [HARRAY n_initial]',
        '$node_children(S_R, HCELL n_outside) = [HARRAY n_initial]',
        '$node_children(S_R, HARRAY n_initial) = [HCELL n_field]',
        '$node_children(S_R, HCELL n_field) = eps',
        '$heap_member(HCELL n_payload, H_R.ROOTS)',
        '$heap_member(HCELL n_payload, $heap_prune(H_R).NODES)',
        '$heap_member(HCELL n_field, H_R.ROOTS)',
        '$heap_member(HARRAY n_initial, $heap_prune(H_R).NODES)',
        '$heap_edge_owners(HCELL n_payload, H_R.EDGES, [HOBJECT n_object]) = 2',
        '$heap_edge_owners(HARRAY n_initial, H_R.EDGES, [HCELL n_payload]) = 1',
        '$heap_edge_owners(HARRAY n_initial, H_R.EDGES, [HCELL n_outside]) = 1',
        '$heap_owners(H_R, HARRAY n_initial) = 2',
        '$heap_edge_owners(HCELL n_field, H_R.EDGES, [HARRAY n_initial]) = 1',
        '$property_release_nodes(' + fields() + ') = [HCELL n_payload, HCELL n_payload]']
    return checks


def conditions(program, path):
    prior.INDEX, prior.PRELAW, prior.cases = INDEX, PRELAW, cases
    prior.INITIAL = prior.CHANGED = fields()
    prior.REBOUND, prior.front = 'eps', front
    try:
        checks, derived = prior.conditions(program, path)
    finally:
        prior.front = FRONT
    if not PRELAW:
        at = checks.index('$string_unset_bool_cv_post_object(S_R, n_object)')
        checks = checks[:at]
        replay = ('$drive_steps(S_P, 3000) = S_DONE' if cases.FACTS[tuple(cases.CASES)[INDEX]]['throwing'] else
                  '$drive_steps($review_cv_running($drive_steps(S_R, 1)), 3000) = S_DONE')
        assert checks.count(replay) == 1
        checks.remove(replay)  # Required independent budget fixtures own the complete replay.
    name = tuple(cases.CASES)[INDEX]
    term = prior.prior.raw.shared.term
    at = next(i for i, check in enumerate(checks) if check.startswith('S_B_found = '))
    changed = ['S_C_found = $review_scalar_fields_seek($drive_steps(S_tail, 1), ' + term(cases.CHANGED_OUTPUTS[name]) + ', 3000)',
        '$review_scalar_fields_at(S_C_found, ' + term(cases.CHANGED_OUTPUTS[name]) + ')',
        'S_C = $review_cv_running(S_C_found)', 'S_C.COMPLETION = NORMAL',
        '$objectprops_at(S_C.OBJECTPROPS, n_object) = (' + fields() + ')',
        'S_C.STORE[n_payload] = DEFINED (PARRAY n_changed)', 'n_changed =/= n_initial',
        'S_C.ARRAYS[n_changed].ITEMS = ' + items(19),
        'S_C.ARRAYS[n_initial].ITEMS = ' + items(11),
        'S_C.STORE[n_outside] = DEFINED (PARRAY n_initial)',
        'S_C.STORE[n_field] = DEFINED (PINT 9)',
        '$node_children(S_C, HOBJECT n_object) = [HCELL n_payload, HCELL n_payload]',
        '$node_children(S_C, HCELL n_payload) = [HARRAY n_changed]',
        'H_C = $heap_graph(S_C)', '$heap_valid(H_C)',
        '$heap_edge_owners(HCELL n_payload, H_C.EDGES, [HOBJECT n_object]) = 2',
        '$heap_owners(H_C, HARRAY n_changed) = 1',
        '$heap_owners(H_C, HARRAY n_initial) = 1',
        '$heap_edge_owners(HCELL n_field, H_C.EDGES, [HARRAY n_changed]) = 1',
        '$heap_edge_owners(HCELL n_field, H_C.EDGES, [HARRAY n_initial]) = 1']
    checks[at:at] = changed
    checks[at + len(changed)] = checks[at + len(changed)].replace('S_tail', 'S_C')
    old = '$node_children(S_B, HOBJECT n_object) = eps'
    assert checks.count(old) == 1
    checks[checks.index(old)] = '$node_children(S_B, HOBJECT n_object) = [HCELL n_payload, HCELL n_payload]'
    at = checks.index('H_B = $heap_graph(S_B)') + 2
    checks[at:at] = ['$lookup(S_B.ENV, $ptascii("payload")) = eps',
        '$lookup(S_B.ENV, $ptascii("fieldValue")) = eps',
        '$call_reference_operand_valid(S_B, REFERENCE n_payload)',
        'S_B.STORE[n_payload] = DEFINED (PARRAY n_current)',
        r'n_current =/= n_initial /\ n_current =/= n_changed',
        'S_B.ARRAYS[n_current].ITEMS = ' + items(23),
        'S_B.ARRAYS[n_initial].ITEMS = ' + items(11),
        'S_B.STORE[n_outside] = DEFINED (PARRAY n_initial)',
        'S_B.STORE[n_field] = DEFINED (PINT 13)',
        '$literal_reference_plain_cell(S_B, n_field)',
        '$node_children(S_B, HCELL n_payload) = [HARRAY n_current]',
        '~$heap_member(HARRAY n_changed, S_B.ALLOCATIONS)',
        '$heap_count(HCELL n_payload, H_B.ROOTS) = 0',
        '$heap_owners(H_B, HCELL n_payload) = 2',
        '$heap_edge_owners(HCELL n_payload, H_B.EDGES, [HOBJECT n_object]) = 2',
        '$heap_owners(H_B, HARRAY n_current) = 1',
        '$heap_owners(H_B, HARRAY n_initial) = 1',
        '$heap_count(HCELL n_field, H_B.ROOTS) = 0',
        '$heap_owners(H_B, HCELL n_field) = 2']
    at = checks.index('H_RET = $heap_graph(S_RET)') + 2
    checks[at:at] = ['~$heap_member(HCELL n_payload, S_RET.ALLOCATIONS)',
        '~$heap_member(HARRAY n_current, S_RET.ALLOCATIONS)',
        '$heap_member(HARRAY n_initial, S_RET.ALLOCATIONS)',
        '$heap_member(HCELL n_field, S_RET.ALLOCATIONS)',
        'S_RET.ARRAYS[n_initial].ITEMS = ' + items(11),
        'S_RET.STORE[n_field] = DEFINED (PINT 13)',
        '$heap_owners(H_RET, HARRAY n_initial) = 1',
        '$heap_edge_owners(HARRAY n_initial, H_RET.EDGES, [HCELL n_outside]) = 1',
        '$heap_owners(H_RET, HCELL n_field) = 1',
        '$heap_count(HCELL n_field, H_RET.ROOTS) = 0']
    at = checks.index('S_DONE = $drive_steps(S_RET, 3000)')
    checks[at:at + 1] = ['S_OUT_found = $review_scalar_fields_seek($drive_steps(S_RET, 1), ' + term(cases.OUTSIDE_OUTPUTS[name]) + ', 3000)',
        '$review_scalar_fields_at(S_OUT_found, ' + term(cases.OUTSIDE_OUTPUTS[name]) + ')',
        'S_OUT = $review_cv_running(S_OUT_found)', 'S_OUT.COMPLETION = NORMAL',
        '$lookup(S_OUT.ENV, $ptascii("outside")) = eps',
        '~$heap_member(HCELL n_outside, S_OUT.ALLOCATIONS)',
        '~$heap_member(HARRAY n_initial, S_OUT.ALLOCATIONS)',
        '~$heap_member(HCELL n_field, S_OUT.ALLOCATIONS)',
        '$weakref_get(S_OUT, n_wrapper) = PNULL',
        '$weakref_get(S_OUT, n_wrapper_after) = POBJECT n_after',
        '$heap_valid($heap_graph(S_OUT))',
        'S_DONE = $drive_steps(S_OUT, 3000)']
    if PRELAW:
        checks += ['$string_unset_bool_cv_post_field_nodes(S_R, $heap_reach([HCELL n_payload], eps, H_R.EDGES))',
            '$string_unset_bool_cv_post_array_entries(S_R, eps, [ENTRY (KINT 0) (ALIAS n_payload)])']
        return checks, len(checks) - len(front(program, path))
    core = checks
    guards = ['$string_unset_bool_cv_post_object_fields(S_R, ' + fields() + ')',
        '$string_unset_bool_cv_post_field_nodes(S_R, $heap_reach([HCELL n_payload], eps, H_R.EDGES))',
        '$string_unset_bool_cv_post_array_entries(S_R, eps, [ENTRY (KINT 0) (ALIAS n_payload)])',
        '$string_unset_bool_cv_post_object(S_B, n_object)']
    for state in (
        'S_R[.REFCELLS = $literal_reference_delete(S_R.REFCELLS, n_payload)]',
        'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HCELL n_payload)]',
        'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HARRAY n_initial)]',
        'S_R[.STORE[n_payload] = UNDEFINED]',
        'S_R[.PROPREFS = {CELL n_payload, SOURCES eps} :: S_R.PROPREFS]',
        'S_R[.REFCOERCIONS = {CELL n_payload, SITE porigin_site, LINE z, VALUE eps} :: S_R.REFCOERCIONS]',
        'S_R[.PARAMETERBACKINGS = {FUNCTION porigin_site, INDEX 0, CELL n_payload, LINE z, VALUE eps} :: S_R.PARAMETERBACKINGS]',
        'S_R[.ARRAYS[n_initial].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_initial))]]',
        'S_R[.ARRAYS[n_initial].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object))]]',
        'S_R[.ARRAYS[n_initial].ITEMS = [ENTRY (KINT 0) (ALIAS n_owner)]]',
        'S_R[.ARRAYS[n_initial].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING ($ptascii("raw"))))]]',
        'S_R[.ARRAYS[n_initial].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING_CARRIER INTERNED_STRING ([65, 0, 66])))]]',
    ):
        guards += ['~$string_unset_bool_cv_post_object(' + state + ', n_object)',
            '~$string_unset_bool_cv_post_nonempty_array(' + state + ', n_key)']
    guards += ['S_shared = S_R[.ARRAYS[n_initial].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_array)), ENTRY (KINT 1) (DIRECT (PARRAY n_array))]][.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 4))]]',
        '$heap_valid($heap_graph(S_shared))',
        '$string_unset_bool_cv_post_object(S_shared, n_object)',
        'S_empty = S_R[.ARRAYS[n_initial].ITEMS = eps]',
        '$heap_valid($heap_graph(S_empty))',
        '$string_unset_bool_cv_post_object(S_empty, n_object)',
        'S_scalar = S_R[.OBJECTPROPS = $objectprops_set(S_R.OBJECTPROPS, n_object, [{DECL eps, NAME $ptascii("scalar"), STATE PROP_VALUE (DIRECT (PINT 4))}, {DECL eps, NAME $ptascii("alias"), STATE PROP_VALUE (ALIAS n_field)}])]',
        '$heap_valid($heap_graph(S_scalar))',
        '$string_unset_bool_cv_post_object(S_scalar, n_object)',
        'S_string = S_scalar[.STORE[n_field] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("text")))]',
        '$heap_valid($heap_graph(S_string))',
        '$string_unset_bool_cv_post_object(S_string, n_object)']
    # B is established by the source continuation, so keep this check in core.
    core.append(guards.pop(3))
    if PART == 'core':
        return core, len(core) - len(front(program, path))
    if PART == 'guards':
        return front(program, path) + guards, len(guards)
    return core + guards, len(core + guards) - len(front(program, path))


if __name__ == '__main__':
    PRELAW = '--prelaw' in sys.argv
    if PRELAW:
        sys.argv.remove('--prelaw')
    if '--part' in sys.argv:
        at = sys.argv.index('--part')
        PART = sys.argv[at + 1]
        del sys.argv[at:at + 2]
    assert PART in ('all', 'core', 'guards') and (not PRELAW or PART == 'all')
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
    runner.cases, runner.conditions = cases, conditions
    runner.PREFIX, runner.recorded = PREFIX, prior.prior.raw.sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['part'], report['source_bridge_credit'] = PART, 0
    report['scope'] = ('Reached array-valued property ALIAS cells precede Unsupported; separately derived COW/rebinding/retirement source0/native0.'
        if PRELAW else 'Checked original prefix, exact new step, shared property cells, COW, rebinding and C/B/R/O/native-output continuation; complete direct replay is independently required.'
        if PART == 'core' else 'Reached source prefix and separately derived array-property-ALIAS storage/constraint/cycle/byte controls; source0/native0.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
