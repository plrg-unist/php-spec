#!/usr/bin/env python3
"""Reached primitive property references retain duplicate real cell edges."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_object_scalar_fields_post_protocol as prior
import string_offset_nested_unset_bool_cv_object_primitive_alias_fields_post_cases as cases

INDEX = 0
PRELAW = False
BASE_FRONT = prior.front
LEGACY = prior.INITIAL
FIELDS = ('[{DECL eps, NAME $ptascii("count"), STATE PROP_VALUE (ALIAS n_field)}, '
          '{DECL eps, NAME $ptascii("mirror"), STATE PROP_VALUE (ALIAS n_field)}]')
CHILDREN = '[HCELL n_field, HCELL n_field]'


def front(program, path):
    checks = BASE_FRONT(program, path)
    old = '$node_children(S_R, HOBJECT n_object) = eps'
    assert checks.count(old) == 1
    checks[checks.index(old)] = '$node_children(S_R, HOBJECT n_object) = ' + CHILDREN
    checks += ['$lookup(S_R.ENV, $ptascii("fieldValue")) = (n_field)',
        r'n_field =/= n_owner /\ n_field =/= n_key',
        'S_R.STORE[n_field] = DEFINED (PINT 7)',
        '$call_reference_operand_valid(S_R, REFERENCE n_field)',
        '$literal_reference_plain_cell(S_R, n_field)',
        '$propref_at(S_R.PROPREFS, n_field) = eps',
        '$reference_coercion_at(S_R.REFCOERCIONS, n_field) = eps',
        '$parameter_backing_at(S_R.PARAMETERBACKINGS, n_field) = eps',
        '$node_children(S_R, HCELL n_field) = eps',
        '$property_release_nodes(' + FIELDS + ') = ' + CHILDREN,
        '$heap_member(HCELL n_field, H_R.ROOTS)',
        '$heap_member(HCELL n_field, $heap_prune(H_R).NODES)',
        '$heap_edge_owners(HCELL n_field, H_R.EDGES, [HOBJECT n_object]) = 2']
    return checks


def conditions(program, path):
    prior.INDEX, prior.PRELAW, prior.cases = INDEX, PRELAW, cases
    prior.INITIAL, prior.CHANGED, prior.REBOUND = FIELDS, FIELDS, 'eps'
    prior.front = front
    try:
        checks, derived = prior.conditions(program, path)
    finally:
        prior.front = BASE_FRONT
    old = '$node_children(S_B, HOBJECT n_object) = eps'
    assert checks.count(old) == 1
    checks[checks.index(old)] = '$node_children(S_B, HOBJECT n_object) = ' + CHILDREN
    at = checks.index('H_B = $heap_graph(S_B)') + 1
    checks[at:at] = ['$lookup(S_B.ENV, $ptascii("fieldValue")) = eps',
        'S_B.STORE[n_field] = DEFINED (PINT 13)',
        '$literal_reference_plain_cell(S_B, n_field)',
        '$node_children(S_B, HCELL n_field) = eps',
        '$heap_member(HCELL n_field, $heap_prune(H_B).NODES)',
        '$heap_count(HCELL n_field, H_B.ROOTS) = 0',
        '$heap_edge_owners(HCELL n_field, H_B.EDGES, [HOBJECT n_object]) = 2',
        '$heap_owners(H_B, HCELL n_field) = 2']
    derived += 8
    at = checks.index('H_RET = $heap_graph(S_RET)') + 1
    checks[at:at] = ['$lookup(S_RET.ENV, $ptascii("fieldValue")) = eps',
        '~$heap_member(HCELL n_field, S_RET.ALLOCATIONS)',
        '~$heap_member(HCELL n_field, $heap_prune(H_RET).NODES)',
        '~$call_reference_operand_valid(S_RET, REFERENCE n_field)']
    derived += 4
    checks += ['~$heap_member(HCELL n_field, S_DONE.ALLOCATIONS)']
    derived += 1
    if PRELAW:
        return checks, derived
    reached = len(checks)
    checks += ['$string_unset_bool_cv_post_object_fields(S_R, ' + FIELDS + ')',
        '$string_unset_bool_cv_post_object_fields(S_R, ' + LEGACY + ')',
        'S_legacy = S_R[.OBJECTPROPS = $objectprops_set(S_R.OBJECTPROPS, n_object, ' + LEGACY + ')]',
        '$node_children(S_legacy, HOBJECT n_object) = eps',
        '$heap_valid($heap_graph(S_legacy))',
        '$string_unset_bool_cv_post_object(S_legacy, n_object)',
        '$string_unset_bool_cv_post_nonempty_array(S_legacy, n_key)']
    for value in ('PNULL', 'PBOOL false', 'PBOOL true', 'PINT (-9223372036854775808)',
                  'PINT 9223372036854775807', 'PFLOAT 0', 'PFLOAT 9223372036854775808',
                  'PFLOAT 9218868437227405312', 'PFLOAT 9221120237041090560'):
        state = 'S_R[.STORE[n_field] = DEFINED (' + value + ')]'
        checks += ['$literal_reference_plain_cell(' + state + ', n_field)',
            '$string_unset_bool_cv_post_object(' + state + ', n_object)',
            '$string_unset_bool_cv_post_nonempty_array(' + state + ', n_key)']
    for state in (
        'S_R[.REFCELLS = $literal_reference_delete(S_R.REFCELLS, n_field)]',
        'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HCELL n_field)]',
        'S_R[.STORE[n_field] = UNDEFINED]',
        'S_R[.STORE[n_field] = DEFINED (PARRAY n_array)]',
        'S_R[.STORE[n_field] = DEFINED (POBJECT n_object)]',
        'S_R[.STORE[n_field] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("held")))]',
        'S_R[.STORE[n_field] = DEFINED (PINT 9223372036854775808)]',
        'S_R[.STORE[n_field] = DEFINED (PFLOAT 18446744073709551616)]',
        'S_R[.PROPREFS = {CELL n_field, SOURCES eps} :: S_R.PROPREFS]',
        'S_R[.REFCOERCIONS = {CELL n_field, SITE porigin_site, LINE z, VALUE eps} :: S_R.REFCOERCIONS]',
        'S_R[.PARAMETERBACKINGS = {FUNCTION porigin_site, INDEX 0, CELL n_field, LINE z, VALUE eps} :: S_R.PARAMETERBACKINGS]',
    ):
        checks += ['~$string_unset_bool_cv_post_object(' + state + ', n_object)',
            '~$string_unset_bool_cv_post_nonempty_array(' + state + ', n_key)']
    request_fields = '[{DECL eps, NAME $ptascii("tag"), STATE PROP_VALUE (DIRECT pvalue_request)}]'
    checks += ['S_seed = $string_request(S_R, $ptascii("kept"))',
        'S_seed.RESULT = KNOWN pvalue_request', '$string_carrier_valid(S_seed, pvalue_request)',
        'S_request = S_seed[.OBJECTPROPS = $objectprops_set(S_seed.OBJECTPROPS, n_object, ' + request_fields + ')]',
        '$node_children(S_request, HOBJECT n_object) = eps',
        '$string_unset_bool_cv_post_object(S_request, n_object)',
        '$string_unset_bool_cv_post_nonempty_array(S_request, n_key)',
        '~$string_unset_bool_cv_post_object(S_seed[.STORE[n_field] = DEFINED pvalue_request], n_object)',
        '~$string_unset_bool_cv_post_nonempty_array(S_seed[.STORE[n_field] = DEFINED pvalue_request], n_key)']
    return checks, derived + len(checks) - reached


if __name__ == '__main__':
    PRELAW = '--prelaw' in sys.argv
    if PRELAW:
        sys.argv.remove('--prelaw')
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
    runner.PREFIX, runner.recorded = prior.PREFIX, prior.prior.raw.sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Reached duplicate primitive property-reference edges precede old Unsupported; tail states are derived/source0/native0.'
        if PRELAW else 'Reached primitive property references preserve Error/Throwable, exact duplicate owners and field/object retirement. Primitive/invalid-wrapper/legacy controls are derived/source0/native0.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
