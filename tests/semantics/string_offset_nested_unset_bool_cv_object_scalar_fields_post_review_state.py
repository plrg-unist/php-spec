#!/usr/bin/env python3
"""Independent scalar-field objects, simultaneous owners and staged retirement."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_object_alias_post_review_state as base
import string_offset_nested_unset_bool_cv_object_scalar_fields_post_cases as cases

INDEX = 0
PRELAW = False
BASE_FRONT = base.front
PREFIX = base.prior.seek.PREFIX + r'''
dec $review_scalar_fields_at(pstate, nat*, bool) : bool
def $review_scalar_fields_at(S, n_want*, b_retired) = ($review_cv_outputs(S.EVENTS) = n_want* /\ ($lookup(S.ENV, $ptascii("key")) = eps) = b_retired /\ $lookup(S.ENV, $ptascii("objectAlias")) =/= eps)
dec $review_scalar_fields_seek(pstate, nat*, bool, nat) : pstate
def $review_scalar_fields_seek(S, n_want*, b_retired, 0) = S
def $review_scalar_fields_seek(S, n_want*, b_retired, n) = S
  -- if $(n > 0)
  -- if $review_scalar_fields_at(S, n_want*, b_retired) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $review_scalar_fields_seek(S, n_want*, b_retired, n) = $review_scalar_fields_seek($drive_steps($review_cv_running(S), 1), n_want*, b_retired, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$review_scalar_fields_at(S, n_want*, b_retired)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def slot(name, value, decl='eps', state=None):
    if name.startswith('['):
        name = '(' + name + ')'
    rendered = value if value == 'PNULL' else '(' + value + ')'
    return ('{DECL ' + decl + ', NAME ' + name + ', STATE ' +
            (state if state is not None else 'PROP_VALUE (DIRECT ' + rendered + ')') + '}')


def fields(count, enabled, tag, ratio):
    return '[' + ', '.join(slot('$ptascii("' + name + '")', value) for name, value in (
        ('count', 'PINT ' + str(count)), ('enabled', 'PBOOL ' + enabled),
        ('tag', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("' + tag + '"))'),
        ('empty', 'PNULL'), ('ratio', 'PFLOAT ' + str(ratio)))) + ']'


def front(program, path):
    base.INDEX, base.cases = INDEX, cases
    checks = BASE_FRONT(program, path)
    replacements = (
        ('S_R.ARRAYS[n_middle].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8)), ENTRY (KINT 1) (ALIAS n_alias), ENTRY (KINT 2) (ALIAS n_alias)]',
         'S_R.ARRAYS[n_middle].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8)), ENTRY (KINT 1) (ALIAS n_alias), ENTRY (KINT 2) (ALIAS n_alias), ENTRY (KINT 3) (DIRECT (POBJECT n_object))]'),
        ('$node_children(S_R, HARRAY n_middle) = [HCELL n_alias, HCELL n_alias]',
         '$node_children(S_R, HARRAY n_middle) = [HCELL n_alias, HCELL n_alias, HOBJECT n_object]'),
        ('$objectprops_at(S_R.OBJECTPROPS, n_object) = (eps)',
         '$objectprops_at(S_R.OBJECTPROPS, n_object) = (' + fields(7, 'true', 'old', 4609434218613702656) + ')'),
        ('$heap_edge_owners(HOBJECT n_object, H_saved.EDGES, H_saved.NODES) = 1',
         '$heap_edge_owners(HOBJECT n_object, H_saved.EDGES, H_saved.NODES) = 2'),
        ('$heap_owners(H_saved, HOBJECT n_object) = 1',
         '$heap_owners(H_saved, HOBJECT n_object) = 2'),
    )
    for old, new in replacements:
        assert checks.count(old) == 1, old
        checks[checks.index(old)] = new
    checks += [
        'ppropertyslot_before* = ' + fields(7, 'true', 'old', 4609434218613702656),
        '$property_unique_names(ppropertyslot_before*)',
        '$stdclass_slots_valid(S_R, ppropertyslot_before*)',
        '$property_release_nodes(ppropertyslot_before*) = eps',
        '$heap_edge_owners(HOBJECT n_object, H_saved.EDGES, [HARRAY n_middle]) = 1',
    ]
    return checks


def conditions(program, path):
    base.INDEX, base.PRELAW, base.cases, base.front = INDEX, PRELAW, cases, front
    try:
        checks, _ = base.conditions(program, path)
    finally:
        base.front = BASE_FRONT
    start = next(i for i, check in enumerate(checks) if check.startswith('S_tail = '))
    checks = checks[:start + 1]
    name = tuple(cases.CASES)[INDEX]
    pending = cases.FACTS[name]['throwing']
    if not PRELAW:
        checks += ['S_next.OBJECTPROPS = S_R.OBJECTPROPS',
                   'S_next.OBJECTTABLES = S_R.OBJECTTABLES',
                   '$string_unset_bool_cv_post_object_fields(ppropertyslot_before*)',
                   '$string_unset_bool_cv_post_object(S_R, n_object)']
    reached = len(checks)
    rebound = base.prior.seek.term(cases.REBOUND_OUTPUTS[name])
    retained = base.prior.seek.term(cases.RETAINED_OUTPUTS[name])
    checks += [
        'S_B_found = $review_scalar_fields_seek($drive_steps(S_tail, 1), ' + rebound + ', false, 4000)',
        '$review_scalar_fields_at(S_B_found, ' + rebound + ', false)',
        'S_B = $review_cv_running(S_B_found)',
        'S_B.COMPLETION = NORMAL',
        '$lookup(S_B.ENV, n_key_name*) = (n_key)',
        'S_B.STORE[n_key] = DEFINED (PARRAY n_array)',
        '$lookup(S_B.ENV, $ptascii("objectAlias")) = (n_alias)',
        'S_B.STORE[n_alias] = DEFINED (POBJECT n_after)',
        'n_after =/= n_object',
        'S_B.OBJECTS[n_after] = STDINSTANCE',
        'S_B.ARRAYS[n_array] = parray_saved',
        'S_B.ARRAYS[n_middle] = S_R.ARRAYS[n_middle]',
        '$objectprops_at(S_B.OBJECTPROPS, n_object) = (' + fields(9, 'true', 'changed', 4609434218613702656) + ')',
        '$objectprops_at(S_B.OBJECTPROPS, n_after) = (' + fields(11, 'false', 'new', 4612811918334230528) + ')',
        '$node_children(S_B, HCELL n_alias) = [HOBJECT n_after]',
        '$node_children(S_B, HOBJECT n_object) = eps',
        '$node_children(S_B, HOBJECT n_after) = eps',
        '$weakref_at(S_B, n_wrapper) = (WEAKREFERENCE (n_object))',
        '$weakref_get(S_B, n_wrapper) = POBJECT n_object',
        '$lookup(S_B.ENV, $ptascii("objectWeakAfter")) = (n_after_weak_cell)',
        'S_B.STORE[n_after_weak_cell] = DEFINED (POBJECT n_after_wrapper)',
        '$weakref_at(S_B, n_after_wrapper) = (WEAKREFERENCE (n_after))',
        '$weakref_get(S_B, n_after_wrapper) = POBJECT n_after',
        'H_B = $heap_graph(S_B)', '$heap_valid(H_B)',
        '$heap_member(HOBJECT n_object, $heap_prune(H_B).NODES)',
        '$heap_member(HOBJECT n_after, $heap_prune(H_B).NODES)',
        '$heap_edge_owners(HCELL n_alias, H_B.EDGES, [HARRAY n_middle]) = 2',
        '$heap_edge_owners(HOBJECT n_object, H_B.EDGES, [HCELL n_alias]) = 0',
        '$heap_edge_owners(HOBJECT n_object, H_B.EDGES, [HARRAY n_middle]) = 1',
        '$heap_owners(H_B, HOBJECT n_object) = 1',
        '$heap_edge_owners(HOBJECT n_after, H_B.EDGES, [HCELL n_alias]) = 1',
        '$heap_edge_owners(HOBJECT n_after, H_B.EDGES, [HARRAY n_middle]) = 0',
        '$heap_owners(H_B, HOBJECT n_after) = 1',
        'S_ret_found = $review_scalar_fields_seek($drive_steps(S_B, 1), ' + retained + ', true, 4000)',
        '$review_scalar_fields_at(S_ret_found, ' + retained + ', true)',
        'S_RET = $review_cv_running(S_ret_found)',
        'S_RET.COMPLETION = NORMAL',
        '$lookup(S_RET.ENV, n_key_name*) = eps',
        '$lookup(S_RET.ENV, $ptascii("objectAlias")) = (n_alias)',
        'S_RET.STORE[n_alias] = DEFINED (POBJECT n_after)',
        '$objectprops_at(S_RET.OBJECTPROPS, n_after) = (' + fields(11, 'false', 'new', 4612811918334230528) + ')',
        '$weakref_get(S_RET, n_wrapper) = PNULL',
        '$weakref_get(S_RET, n_after_wrapper) = POBJECT n_after',
        '~((HOBJECT n_object) <- S_RET.ALLOCATIONS)',
        'H_RET = $heap_graph(S_RET)', '$heap_valid(H_RET)',
        '$heap_member(HCELL n_alias, $heap_prune(H_RET).NODES)',
        '$heap_member(HOBJECT n_after, $heap_prune(H_RET).NODES)',
        '~$heap_member(HARRAY n_array, $heap_prune(H_RET).NODES)',
        '~$heap_member(HARRAY n_middle, $heap_prune(H_RET).NODES)',
        '$heap_edge_owners(HCELL n_alias, H_RET.EDGES, H_RET.NODES) = 0',
        '$heap_edge_owners(HOBJECT n_after, H_RET.EDGES, [HCELL n_alias]) = 1',
        '$heap_owners(H_RET, HOBJECT n_after) = 1',
        'S_DONE = $drive_steps(S_RET, 4000)',
        r'S_DONE.COMPLETION = NORMAL /\ S_DONE.TODO = eps /\ S_DONE.EXITSTATUS = 0',
        r'S_DONE.CURRENT = eps /\ S_DONE.FRAMES = eps /\ S_DONE.HELD = eps',
        '$lookup(S_DONE.ENV, $ptascii("objectAlias")) = eps',
        '~((HCELL n_alias) <- S_DONE.ALLOCATIONS)',
        '~((HOBJECT n_after) <- S_DONE.ALLOCATIONS)',
        '$weakref_get(S_DONE, n_wrapper) = PNULL',
        '$weakref_get(S_DONE, n_after_wrapper) = PNULL',
        '$review_cv_outputs(S_DONE.EVENTS) = ' + base.prior.seek.term(cases.OUTPUTS[name]),
        *base.prior.seek.public('S_DONE'),
    ]
    if pending:
        checks += ['S_DONE.OBJECTS[n_exception] = S_R.OBJECTS[n_exception]']
    if PRELAW:
        return checks, len(checks) - reached
    checks += ['$drive_steps($review_cv_running(S_public), 4000) = S_DONE']
    reached = len(checks)
    checks += [
        'S_direct = S_R[.ARRAYS[n_middle].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8)), ENTRY (KINT 1) (DIRECT (POBJECT n_object)), ENTRY (KINT 2) (DIRECT (POBJECT n_object))]]',
        '$heap_valid($heap_graph(S_direct))',
        '$heap_edge_owners(HOBJECT n_object, $heap_graph(S_direct).EDGES, $heap_graph(S_direct).NODES) = 3',
        '$string_unset_bool_cv_post_object(S_direct, n_object)',
        '$string_unset_bool_cv_post_object_cell(S_direct, n_alias)',
        '$string_unset_bool_cv_post_nonempty_array(S_direct, n_key)',
    ]
    for name_term in ('eps', '$ptascii("123")', '$ptascii("field")'):
        changed = ('S_R[.OBJECTPROPS = $objectprops_set(S_R.OBJECTPROPS, n_object, [' +
                   slot(name_term, 'PNULL') + '])]')
        checks += ['$heap_graph(' + changed + ') = H_saved',
                   '$string_unset_bool_cv_post_object(' + changed + ', n_object)',
                   '$string_unset_bool_cv_post_object_cell(' + changed + ', n_alias)',
                   '$string_unset_bool_cv_post_nonempty_array(' + changed + ', n_key)']
    bad_slots = [
        '[' + slot('$ptascii("count")', 'PNULL') + ', ' + slot('$ptascii("count")', 'PBOOL false') + ']',
        '[' + slot('[256]', 'PNULL') + ']',
        '[' + slot('[0, 120]', 'PNULL') + ']',
        '[' + slot('$ptascii("declared")', 'PNULL', '(porigin_site)') + ']',
    ]
    for state in ('PROP_UNSET', 'PROP_INITIAL', 'PROP_VALUE (ALIAS n_alias)'):
        bad_slots += ['[' + slot('$ptascii("state")', '', state=state) + ']']
    checks += ['~$string_unset_bool_cv_post_object_fields([' +
               slot('$ptascii("deferred")', '', state='PROP_DEFERRED porigin_site') + '])']
    initial_duplicate = ('[' + slot('$ptascii("same")', 'PNULL') + ', ' +
                         slot('$ptascii("same")', '', state='PROP_INITIAL') + ']')
    checks += ['$heap_graph(S_R[.OBJECTPROPS = $objectprops_set(S_R.OBJECTPROPS, n_object, ' +
               initial_duplicate + ')]) = H_saved']
    bad_slots += [initial_duplicate]
    for value in ('PARRAY n_middle', 'POBJECT n_object',
                  'PSTRING_CARRIER (REQUEST_STRING 0) ([65])',
                  'PSTRING_CARRIER INTERNED_STRING ([0, 65])',
                  'PINT 9223372036854775808', 'PFLOAT 18446744073709551616'):
        bad_slots += ['[' + slot('$ptascii("payload")', value) + ']']
    for slots in bad_slots:
        changed = 'S_R[.OBJECTPROPS = $objectprops_set(S_R.OBJECTPROPS, n_object, ' + slots + ')]'
        checks += ['~$string_unset_bool_cv_post_object(' + changed + ', n_object)',
                   '~$string_unset_bool_cv_post_object_cell(' + changed + ', n_alias)',
                   '~$string_unset_bool_cv_post_nonempty_array(' + changed + ', n_key)']
    for changed in (
        'S_R[.OBJECTPROPS = eps]',
        'S_R[.OBJECTTABLES = {OBJECT n_object, TABLE n_array} :: S_R.OBJECTTABLES]',
        'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HOBJECT n_object)]',
        'S_R[.OBJECTS[n_object] = S_R.OBJECTS[n_wrapper]]',
    ):
        checks += ['~$string_unset_bool_cv_post_object(' + changed + ', n_object)',
                   '~$string_unset_bool_cv_post_nonempty_array(' + changed + ', n_key)']
    for changed in (
        'S_R[.PROPREFS = {CELL n_alias, SOURCES eps} :: S_R.PROPREFS]',
        'S_R[.REFCOERCIONS = {CELL n_alias, SITE porigin_site, LINE z, VALUE eps} :: S_R.REFCOERCIONS]',
        'S_R[.PARAMETERBACKINGS = {FUNCTION porigin_site, INDEX 0, CELL n_alias, LINE z, VALUE eps} :: S_R.PARAMETERBACKINGS]',
    ):
        checks += ['~$string_unset_bool_cv_post_object_cell(' + changed + ', n_alias)',
                   '~$string_unset_bool_cv_post_nonempty_array(' + changed + ', n_key)']
    for changed in ('S_R[.CODE = eps]', 'S_R[.SOURCES = eps]', 'S_R[.ORIGIN = eps]'):
        checks += ['~$call_task_valid(' + changed + ', STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key)']
    return checks, len(checks) - reached


if __name__ == '__main__':
    PRELAW = '--prelaw' in sys.argv
    if PRELAW:
        sys.argv.remove('--prelaw')
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (0, 1)
    watched = [Path(__file__), Path(base.__file__), Path(base.prior.__file__),
               Path(base.prior.seek.__file__), Path(base.prior.sl.__file__),
               Path(cases.prior.__file__), *[base.prior.runner.ROOT / path for path in cases.WATCHED]]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner = base.prior.runner
    runner.NAME = tuple(cases.CASES)[INDEX]
    runner.OUTPUT = cases.OUTPUTS[runner.NAME]
    runner.cases, runner.conditions = cases, conditions
    runner.PREFIX, runner.recorded = PREFIX, base.prior.sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    output = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(output.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Independent raw scalar-field DIRECT/ALIAS source, exact slots/heap and quiet read precede old Unsupported; '
        'derived rebound/key-retainer/final retirement is separate, source0/native0.' if PRELAW else
        'Independent exact Error/same Throwable and unchanged full property storage; source-reached rebound/retainer/final '
        'weak targets, public/whole/split states and separate scalar-field/metadata/ownership refusals, source0/native0.')
    output.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
