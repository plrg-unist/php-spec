#!/usr/bin/env python3
"""Reached scalar object fields retain real DIRECT/ALIAS owners and retirement."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_object_alias_post_protocol as prior
import string_offset_nested_unset_bool_cv_object_scalar_fields_post_cases as cases

INDEX = 0
PRELAW = False
BASE_FRONT = prior.front
PREFIX = prior.raw.PREFIX + r'''
dec $review_scalar_fields_at(pstate, nat*) : bool
def $review_scalar_fields_at(S, n_output*) = ($review_cv_outputs(S.EVENTS) = n_output*)
dec $review_scalar_fields_seek(pstate, nat*, nat) : pstate
def $review_scalar_fields_seek(S, n_output*, 0) = S
def $review_scalar_fields_seek(S, n_output*, n) = S
  -- if $(n > 0)
  -- if $review_scalar_fields_at(S, n_output*) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $review_scalar_fields_seek(S, n_output*, n) = $review_scalar_fields_seek($drive_steps($review_cv_running(S), 1), n_output*, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$review_scalar_fields_at(S, n_output*)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def slots(count, enabled, tag, ratio):
    return ('[{DECL eps, NAME $ptascii("count"), STATE PROP_VALUE (DIRECT (PINT ' + str(count) + '))}, '
            '{DECL eps, NAME $ptascii("enabled"), STATE PROP_VALUE (DIRECT (PBOOL ' + enabled + '))}, '
            '{DECL eps, NAME $ptascii("tag"), STATE PROP_VALUE (DIRECT (PSTRING_CARRIER INTERNED_STRING ($ptascii("' + tag + '"))))}, '
            '{DECL eps, NAME $ptascii("empty"), STATE PROP_VALUE (DIRECT PNULL)}, '
            '{DECL eps, NAME $ptascii("ratio"), STATE PROP_VALUE (DIRECT (PFLOAT ' + str(ratio) + '))}]')


INITIAL = slots(7, 'true', 'old', 4609434218613702656)
CHANGED = slots(9, 'true', 'changed', 4609434218613702656)
REBOUND = slots(11, 'false', 'new', 4612811918334230528)
ITEMS = ('[ENTRY (KINT 0) (DIRECT (PINT 8)), ENTRY (KINT 1) (ALIAS n_owner), '
         'ENTRY (KINT 2) (ALIAS n_owner), ENTRY (KINT 3) (DIRECT (POBJECT n_object))]')


def front(program, path):
    prior.INDEX, prior.cases = INDEX, cases
    checks = BASE_FRONT(program, path)
    changes = {
        'S_R.ARRAYS[n_middle].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8)), ENTRY (KINT 1) (ALIAS n_owner), ENTRY (KINT 2) (ALIAS n_owner)]':
            'S_R.ARRAYS[n_middle].ITEMS = ' + ITEMS,
        '$node_children(S_R, HARRAY n_middle) = [HCELL n_owner, HCELL n_owner]':
            '$node_children(S_R, HARRAY n_middle) = [HCELL n_owner, HCELL n_owner, HOBJECT n_object]',
        '$objectprops_at(S_R.OBJECTPROPS, n_object) = (eps)':
            '$objectprops_at(S_R.OBJECTPROPS, n_object) = (' + INITIAL + ')',
        '$heap_owners(H_R, HOBJECT n_object) = 1': '$heap_owners(H_R, HOBJECT n_object) = 2',
        '$heap_owners($heap_prune(H_R), HOBJECT n_object) = 1': '$heap_owners($heap_prune(H_R), HOBJECT n_object) = 2',
    }
    for old, new in changes.items():
        assert checks.count(old) == 1, old
        checks[checks.index(old)] = new
    checks += ['$objectprops_valid(S_R, S_R.OBJECTPROPS)',
        '$objectprops_materialized(S_R.OBJECTPROPS, n_object)',
        '$heap_edge_owners(HOBJECT n_object, H_R.EDGES, [HARRAY n_middle]) = 1']
    return checks


def conditions(program, path):
    prior.prior.INDEX, prior.prior.cases = INDEX, cases
    prior.prior.PRELAW, prior.prior.front = PRELAW, front
    checks, derived = prior.BASE_CONDITIONS(program, path)
    if not PRELAW:
        assert derived == 17
        checks, derived = checks[:-derived], 0
        checks.remove('$drive_steps(S_E, 5000) = S_DONE')
        if not cases.FACTS[tuple(cases.CASES)[INDEX]]['throwing']:
            checks.remove('$drive_steps(S_P, 3000) = S_DONE')
        checks += ['S_next.OBJECTPROPS = S_R.OBJECTPROPS',
            'S_next.OBJECTTABLES = S_R.OBJECTTABLES', 'S_next.PROPREFS = S_R.PROPREFS']
    name = tuple(cases.CASES)[INDEX]
    term = prior.raw.shared.term
    stages = ['S_B_found = $review_scalar_fields_seek($drive_steps(S_tail, 1), ' + term(cases.REBOUND_OUTPUTS[name]) + ', 3000)',
        '$review_scalar_fields_at(S_B_found, ' + term(cases.REBOUND_OUTPUTS[name]) + ')',
        'S_B = $review_cv_running(S_B_found)', 'S_B.COMPLETION = NORMAL',
        '$lookup(S_B.ENV, n_key_name*) = (n_key)',
        'S_B.ARRAYS[n_middle].ITEMS = ' + ITEMS,
        '$lookup(S_B.ENV, $ptascii("objectAlias")) = (n_owner)',
        'S_B.STORE[n_owner] = DEFINED (POBJECT n_after)', 'n_after =/= n_object',
        '$(n_after < |S_B.OBJECTS|)', 'S_B.OBJECTS[n_after] = STDINSTANCE',
        '$objectprops_at(S_B.OBJECTPROPS, n_object) = (' + CHANGED + ')',
        '$objectprops_at(S_B.OBJECTPROPS, n_after) = (' + REBOUND + ')',
        '$objectprops_valid(S_B, S_B.OBJECTPROPS)',
        '$node_children(S_B, HOBJECT n_object) = eps', '$node_children(S_B, HOBJECT n_after) = eps',
        '$weakref_get(S_B, n_wrapper) = POBJECT n_object',
        '$lookup(S_B.ENV, $ptascii("objectWeakAfter")) = (n_weak_after_cell)',
        'S_B.STORE[n_weak_after_cell] = DEFINED (POBJECT n_wrapper_after)',
        '$weakref_get(S_B, n_wrapper_after) = POBJECT n_after',
        'H_B = $heap_graph(S_B)', '$heap_valid(H_B)',
        '$heap_owners(H_B, HOBJECT n_object) = 1', '$heap_owners(H_B, HOBJECT n_after) = 1',
        '$heap_edge_owners(HOBJECT n_object, H_B.EDGES, [HARRAY n_middle]) = 1',
        '$heap_edge_owners(HOBJECT n_after, H_B.EDGES, [HCELL n_owner]) = 1',
        'S_RET_found = $review_scalar_fields_seek($drive_steps(S_B, 1), ' + term(cases.RETAINED_OUTPUTS[name]) + ', 3000)',
        '$review_scalar_fields_at(S_RET_found, ' + term(cases.RETAINED_OUTPUTS[name]) + ')',
        'S_RET = $review_cv_running(S_RET_found)', 'S_RET.COMPLETION = NORMAL',
        '$lookup(S_RET.ENV, n_key_name*) = eps',
        '$lookup(S_RET.ENV, $ptascii("objectAlias")) = (n_owner)',
        'S_RET.STORE[n_owner] = DEFINED (POBJECT n_after)',
        '$objectprops_at(S_RET.OBJECTPROPS, n_after) = (' + REBOUND + ')',
        '$objectprops_at(S_RET.OBJECTPROPS, n_object) = eps',
        '$weakref_get(S_RET, n_wrapper) = PNULL',
        '$weakref_get(S_RET, n_wrapper_after) = POBJECT n_after',
        '~$heap_member(HOBJECT n_object, S_RET.ALLOCATIONS)',
        '~$heap_member(HARRAY n_array, S_RET.ALLOCATIONS)',
        '~$heap_member(HARRAY n_middle, S_RET.ALLOCATIONS)',
        'H_RET = $heap_graph(S_RET)', '$heap_valid(H_RET)',
        '$heap_member(HCELL n_owner, H_RET.ROOTS)',
        '$heap_owners(H_RET, HOBJECT n_after) = 1',
        '$node_children(S_RET, HCELL n_owner) = [HOBJECT n_after]']
    at = checks.index('S_DONE = $drive_steps(S_tail, 3000)')
    checks[at:at + 1] = stages + ['S_DONE = $drive_steps(S_RET, 3000)']
    final = ['$lookup(S_DONE.ENV, $ptascii("objectAlias")) = eps',
        '$weakref_get(S_DONE, n_wrapper) = PNULL', '$weakref_get(S_DONE, n_wrapper_after) = PNULL',
        '~$heap_member(HCELL n_owner, S_DONE.ALLOCATIONS)',
        '~$heap_member(HOBJECT n_object, S_DONE.ALLOCATIONS)',
        '~$heap_member(HOBJECT n_after, S_DONE.ALLOCATIONS)']
    checks += final
    derived += len(stages) + len(final)
    if PRELAW:
        checks += ['~$string_unset_bool_cv_post_object(S_R, n_object)',
            '~$string_unset_bool_cv_post_object_cell(S_R, n_owner)']
        return checks, derived
    reached = len(checks)
    checks += ['$string_unset_bool_cv_post_object(S_R, n_object)',
        '$string_unset_bool_cv_post_object_cell(S_R, n_owner)',
        '$string_unset_bool_cv_post_nonempty_array(S_B, n_key)',
        'S_direct = S_R[.ARRAYS[n_middle].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8)), ENTRY (KINT 1) (DIRECT (POBJECT n_object)), ENTRY (KINT 2) (DIRECT (POBJECT n_object))]]',
        '$heap_valid($heap_graph(S_direct))', '$heap_owners($heap_graph(S_direct), HOBJECT n_object) = 3',
        '$string_unset_bool_cv_post_nonempty_array(S_direct, n_key)',
        'S_props = $objectprops_mark(S_R[.OBJECTPROPS = $objectprops_set(S_R.OBJECTPROPS, n_object, [{DECL eps, NAME $ptascii("extra"), STATE PROP_VALUE (DIRECT (PINT 1))}])], n_object)',
        '$heap_valid($heap_graph(S_props))',
        '$string_unset_bool_cv_post_object_cell(S_props, n_owner)',
        '$string_unset_bool_cv_post_nonempty_array(S_props, n_key)']
    for field in (
        '{DECL eps, NAME $ptascii("bad"), STATE PROP_VALUE (ALIAS n_owner)}',
        '{DECL eps, NAME $ptascii("bad"), STATE PROP_VALUE (DIRECT (PARRAY n_array))}',
        '{DECL eps, NAME $ptascii("bad"), STATE PROP_VALUE (DIRECT (POBJECT n_object))}',
        '{DECL eps, NAME $ptascii("bad"), STATE PROP_VALUE (DIRECT PUNDEFINED)}',
        '{DECL eps, NAME $ptascii("bad"), STATE PROP_UNSET}',
        '{DECL eps, NAME ([256]), STATE PROP_VALUE (DIRECT PNULL)}',
        '{DECL eps, NAME ([0]), STATE PROP_VALUE (DIRECT PNULL)}',
        '{DECL eps, NAME $ptascii("bad"), STATE PROP_VALUE (DIRECT (PINT 9223372036854775808))}',
        '{DECL eps, NAME $ptascii("bad"), STATE PROP_VALUE (DIRECT (PFLOAT 18446744073709551616))}',
    ):
        changed = 'S_R[.OBJECTPROPS = $objectprops_set(S_R.OBJECTPROPS, n_object, [' + field + '])]'
        checks += ['~$string_unset_bool_cv_post_object(' + changed + ', n_object)',
            '~$string_unset_bool_cv_post_nonempty_array(' + changed + ', n_key)']
    for changed in ('S_R[.CODE = eps]', 'S_R[.SOURCES = eps]', 'S_R[.ORIGIN = eps]'):
        checks += ['~$call_task_valid(' + changed + ', STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key)']
    return checks, derived + len(checks) - reached


if __name__ == '__main__':
    PRELAW = '--prelaw' in sys.argv
    if PRELAW:
        sys.argv.remove('--prelaw')
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in range(2)
    name = tuple(cases.CASES)[INDEX]
    watched = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), Path(cases.__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner = prior.raw.runner
    runner.NAME, runner.OUTPUT = name, cases.OUTPUTS[name]
    runner.cases, runner.conditions = cases, conditions
    runner.PREFIX, runner.recorded = PREFIX, prior.raw.sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Actual scalar-field source/quiet-read/full-heap facts before old Unsupported; derived caller tail/lifetimes source0/native0.'
        if PRELAW else 'Source-reached scalar-field DIRECT/ALIAS objects preserve Error or Throwable, exact properties, split budgets and staged old/new retirement; derived refusals source0/native0.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
