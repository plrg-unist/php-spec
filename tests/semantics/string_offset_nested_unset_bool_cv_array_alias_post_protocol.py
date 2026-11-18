#!/usr/bin/env python3
"""Reached owning alias cells and separate key/retainer retirement."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_deep_array_post_protocol as prior
import string_offset_nested_unset_bool_cv_array_alias_post_cases as cases

INDEX = 0
PRELAW = False
BASE_FRONT, BASE_CONDITIONS = prior.front, prior.conditions
PREFIX = prior.prior.PREFIX + r'''
dec $review_array_alias_at(pstate, nat*) : bool
def $review_array_alias_at(S, n_output*) = ($review_cv_outputs(S.EVENTS) = n_output* /\ $lookup(S.ENV, $ptascii("key")) = eps /\ $lookup(S.ENV, $ptascii("arrayOwnerAlias")) =/= eps)
dec $review_array_alias_seek(pstate, nat*, nat) : pstate
def $review_array_alias_seek(S, n_output*, 0) = S
def $review_array_alias_seek(S, n_output*, n) = S
  -- if $(n > 0)
  -- if $review_array_alias_at(S, n_output*) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $review_array_alias_seek(S, n_output*, n) = $review_array_alias_seek($drive_steps($review_cv_running(S), 1), n_output*, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$review_array_alias_at(S, n_output*)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def front(program, path):
    checks = BASE_FRONT(program, path)
    mixed = cases.FACTS[tuple(cases.CASES)[INDEX]]['mixed']
    changes = {
        'S_R.ARRAYS[n_middle].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8)), ENTRY (KINT 1) (DIRECT (PARRAY n_grand)), ENTRY (KINT 2) (DIRECT (PARRAY n_grand))]':
            'S_R.ARRAYS[n_middle].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8)), ENTRY (KINT 1) (ALIAS n_owner), ENTRY (KINT 2) (ALIAS n_owner)]',
        '$node_children(S_R, HARRAY n_middle) = [HARRAY n_grand, HARRAY n_grand]':
            '$node_children(S_R, HARRAY n_middle) = [HCELL n_owner, HCELL n_owner]',
        '$heap_edge_owners(HARRAY n_grand, H_R.EDGES, [HARRAY n_middle]) = 2':
            '$heap_edge_owners(HARRAY n_grand, H_R.EDGES, [HARRAY n_middle]) = 0',
    }
    for old, new in changes.items():
        assert checks.count(old) == 1
        checks[checks.index(old)] = new
    for graph in ('H_R', '$heap_prune(H_R)'):
        old = '$heap_owners(' + graph + ', HARRAY n_grand) = ' + ('2' if mixed else '3')
        assert checks.count(old) == 1
        checks[checks.index(old)] = '$heap_owners(' + graph + ', HARRAY n_grand) = 1'
    if not mixed:
        for where in ('H_R.ROOTS', '$pools_nodes(S_R.POOLS)'):
            old = '$heap_count(HARRAY n_grand, ' + where + ') = 1'
            assert checks.count(old) == 1
            checks[checks.index(old)] = old[:-1] + '0'
    at = checks.index('$(n_grand < |S_R.ARRAYS|)')
    checks[at:at] = ['$(n_owner < |S_R.STORE|)',
        'S_R.STORE[n_owner] = DEFINED (PARRAY n_grand)',
        '$lookup(S_R.ENV, $ptascii("arrayOwnerAlias")) = (n_owner)',
        'n_owner =/= n_key',
        'n_owner <- S_R.REFCELLS',
        '$call_reference_operand_valid(S_R, REFERENCE n_owner)',
        '~$literal_reference_plain_cell(S_R, n_owner)',
        '$propref_at(S_R.PROPREFS, n_owner) = eps',
        '$reference_coercion_at(S_R.REFCOERCIONS, n_owner) = eps',
        '$parameter_backing_at(S_R.PARAMETERBACKINGS, n_owner) = eps',
        '$heap_member(HCELL n_owner, H_R.ROOTS)',
        '$heap_member(HCELL n_owner, $heap_prune(H_R).NODES)',
        '$node_children(S_R, HCELL n_owner) = [HARRAY n_grand]',
        '$heap_edge_owners(HCELL n_owner, H_R.EDGES, [HARRAY n_middle]) = 2',
        '$heap_edge_owners(HARRAY n_grand, H_R.EDGES, [HCELL n_owner]) = 1']
    if mixed:
        checks += ['n_owner =/= n_alias']
    return checks


def conditions(program, path):
    prior.INDEX, prior.cases, prior.PRELAW, prior.front = INDEX, cases, PRELAW, front
    checks, derived = BASE_CONDITIONS(program, path)
    name = tuple(cases.CASES)[INDEX]
    at = checks.index('S_DONE = $drive_steps(S_tail, 3000)')
    middle = ['S_retained_found = $review_array_alias_seek($drive_steps(S_tail, 1), ' + prior.prior.shared.term(cases.RETAINED_OUTPUTS[name]) + ', 3000)',
        '$review_array_alias_at(S_retained_found, ' + prior.prior.shared.term(cases.RETAINED_OUTPUTS[name]) + ')',
        'S_retained = $review_cv_running(S_retained_found)',
        'S_retained.COMPLETION = NORMAL',
        '$lookup(S_retained.ENV, n_key_name*) = eps',
        '$lookup(S_retained.ENV, $ptascii("arrayOwnerAlias")) = (n_owner)',
        'S_retained.STORE[n_owner] = DEFINED (PARRAY n_retained)',
        '$(n_retained < |S_retained.ARRAYS|)',
        '$call_reference_operand_valid(S_retained, REFERENCE n_owner)',
        'H_retained = $heap_graph(S_retained)',
        '$heap_valid(H_retained)',
        '$heap_member(HCELL n_owner, H_retained.ROOTS)',
        '$heap_member(HARRAY n_retained, $heap_prune(H_retained).NODES)',
        '$node_children(S_retained, HCELL n_owner) = [HARRAY n_retained]']
    if cases.FACTS[name]['mixed']:
        middle += ['$weakref_get(S_retained, n_wrapper) = POBJECT n_object',
            '$heap_member(HOBJECT n_object, $heap_prune(H_retained).NODES)',
            'S_retained.STORE[n_alias] = DEFINED (PINT 11)']
    else:
        middle += ['S_retained.ARRAYS[n_retained].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 11))]']
    checks[at:at + 1] = middle + ['S_DONE = $drive_steps(S_retained, 3000)']
    checks += ['$lookup(S_DONE.ENV, $ptascii("arrayOwnerAlias")) = eps']
    if PRELAW:
        return checks, derived + len(middle) + 1
    at = len(checks)
    for target in ('n_array', 'n_middle'):
        state = 'S_owner_cycle_' + target
        checks += [state + ' = S_R[.STORE[n_owner] = DEFINED (PARRAY ' + target + ')]',
            '$heap_valid($heap_graph(' + state + '))',
            '~$string_unset_bool_cv_post_nonempty_array(' + state + ', n_key)']
    for changed in (
        'S_R[.REFCELLS = $literal_reference_delete(S_R.REFCELLS, n_owner)]',
        'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HCELL n_owner)]',
        'S_R[.STORE[n_owner] = UNDEFINED]',
    ):
        checks += ['~$string_unset_bool_cv_post_nonempty_array(' + changed + ', n_key)']
    checks += ['S_string_alias = S_R[.STORE[n_owner] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("string-alias")))]',
        '$string_read_array_string_cell(S_string_alias, n_owner)',
        '$string_unset_bool_cv_post_nonempty_array(S_string_alias, n_key)']
    checks += ['S_no_retainer = S_R[.ENV = $unbind(S_R.ENV, $ptascii("arrayOwnerAlias"))][.GLOBALTABLE = eps]',
        '$heap_valid($heap_graph(S_no_retainer))',
        '~$heap_member(HCELL n_owner, $heap_graph(S_no_retainer).ROOTS)',
        '$heap_member(HCELL n_owner, $heap_prune($heap_graph(S_no_retainer)).NODES)',
        '$string_unset_bool_cv_post_nonempty_array(S_no_retainer, n_key)']
    return checks, derived + len(checks) - at


if __name__ == '__main__':
    PRELAW = '--prelaw' in sys.argv
    if PRELAW:
        sys.argv.remove('--prelaw')
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in range(4)
    name = tuple(cases.CASES)[INDEX]
    watched = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__),
               Path(prior.prior.shared.__file__), Path(prior.prior.sl.__file__), Path(cases.prior.__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner = prior.prior.runner
    runner.NAME, runner.OUTPUT = name, cases.OUTPUTS[name]
    runner.cases, runner.conditions = cases, conditions
    runner.PREFIX, runner.recorded = PREFIX, prior.prior.sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Source-reached owning alias cell/child edge before Unsupported; separately derived '
                       'key-retired/live-retainer then final alias retirement/WeakReference cleanup; source0/native0.'
                       if PRELAW else 'Source-reached owning array aliases preserve exact continuation and two '
                       'retirement stages; whole/split and derived source/owner/cycle bounds separate; source0/native0.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
