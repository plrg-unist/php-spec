#!/usr/bin/env python3
"""Independent shared primitive field cells, duplicate edges and retirement."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_object_scalar_fields_post_review_state as prior
import string_offset_nested_unset_bool_cv_object_primitive_alias_fields_post_cases as cases

INDEX = 0
PRELAW = False
FRONT = prior.front
PREFIX = prior.PREFIX


def fields(cell='n_field'):
    return '[' + ', '.join(prior.slot('$ptascii("' + name + '")', '',
        state='PROP_VALUE (ALIAS ' + cell + ')') for name in ('count', 'mirror')) + ']'


def front(program, path):
    prior.INDEX, prior.cases = INDEX, cases
    checks = FRONT(program, path)
    original = prior.fields(7, 'true', 'old', 4609434218613702656)
    assert sum(check.count(original) for check in checks) == 2
    checks = [check.replace(original, fields()).replace(
        '$node_children(S_R, HOBJECT n_object) = eps',
        '$node_children(S_R, HOBJECT n_object) = [HCELL n_field, HCELL n_field]').replace(
        '$property_release_nodes(ppropertyslot_before*) = eps',
        '$property_release_nodes(ppropertyslot_before*) = [HCELL n_field, HCELL n_field]') for check in checks]
    at = checks.index('$objectprops_at(S_R.OBJECTPROPS, n_object) = (' + fields() + ')')
    checks[at:at] = ['$lookup(S_R.ENV, $ptascii("fieldValue")) = (n_field)',
        'n_field =/= n_alias', 'n_field =/= n_key',
        'S_R.STORE[n_field] = DEFINED (PINT 7)',
        '$call_reference_operand_valid(S_R, REFERENCE n_field)',
        '$literal_reference_plain_cell(S_R, n_field)',
        '~$string_read_array_string_cell(S_R, n_field)']
    checks += ['$node_children(S_R, HCELL n_field) = eps',
        '$heap_member(HCELL n_field, $heap_prune(H_saved).NODES)',
        '$heap_edge_owners(HCELL n_field, H_saved.EDGES, [HOBJECT n_object]) = 2',
        '$heap_edge_owners(HCELL n_field, H_saved.EDGES, H_saved.NODES) = 2',
        'n_field_roots = $heap_count(HCELL n_field, H_saved.ROOTS)',
        '$(n_field_roots > 0)',
        '$heap_count(HCELL n_field, H_saved.DEBTS) = 0',
        '$heap_owners(H_saved, HCELL n_field) = $(n_field_roots + 2)']
    if PRELAW:
        checks += ['~$string_unset_bool_cv_post_object_fields(S_R, ppropertyslot_before*)',
                   '~$string_unset_bool_cv_post_object(S_R, n_object)']
    return checks


def conditions(program, path):
    prior.INDEX, prior.PRELAW, prior.cases, prior.front = INDEX, PRELAW, cases, front
    try:
        checks, derived = prior.conditions(program, path)
    finally:
        prior.front = FRONT
    if not PRELAW:
        at = next(i for i, check in enumerate(checks) if check.startswith('S_direct = '))
        checks = checks[:at]
        derived = 0
    changed = prior.fields(9, 'true', 'changed', 4609434218613702656)
    rebound = prior.fields(11, 'false', 'new', 4612811918334230528)
    assert sum(check.count(changed) for check in checks) == 1
    assert sum(check.count(rebound) for check in checks) == 2
    checks = [check.replace(changed, fields()).replace(rebound, 'eps').replace(
        '$node_children(S_B, HOBJECT n_object) = eps',
        '$node_children(S_B, HOBJECT n_object) = [HCELL n_field, HCELL n_field]') for check in checks]
    at = checks.index('H_B = $heap_graph(S_B)') + 2
    extra = ['$lookup(S_B.ENV, $ptascii("fieldValue")) = eps',
        'S_B.STORE[n_field] = DEFINED (PINT 13)',
        '$node_children(S_B, HCELL n_field) = eps',
        '$heap_member(HCELL n_field, $heap_prune(H_B).NODES)',
        '$heap_count(HCELL n_field, H_B.ROOTS) = 0',
        '$heap_count(HCELL n_field, H_B.DEBTS) = 0',
        '$heap_edge_owners(HCELL n_field, H_B.EDGES, [HOBJECT n_object]) = 2',
        '$heap_edge_owners(HCELL n_field, H_B.EDGES, H_B.NODES) = 2',
        '$heap_owners(H_B, HCELL n_field) = 2']
    checks[at:at] = extra
    for marker, state in (('H_RET = $heap_graph(S_RET)', 'S_RET'),
                          ('S_DONE = $drive_steps(S_RET, 4000)', 'S_DONE')):
        at = checks.index(marker) + 1
        checks[at:at] = ['~((HCELL n_field) <- ' + state + '.ALLOCATIONS)',
            '~$heap_member(HCELL n_field, $heap_prune($heap_graph(' + state + ')).NODES)']
    if PRELAW:
        return checks, derived + len(extra) + 4
    reached = len(checks)
    for value in ('PNULL', 'PBOOL false', 'PBOOL true',
                  'PINT (-9223372036854775808)', 'PINT 9223372036854775807',
                  'PFLOAT 0', 'PFLOAT 9223372036854775808',
                  'PFLOAT 9218868437227405312', 'PFLOAT 9221120237041090560',
                  'PFLOAT 18446744073709551615'):
        state = 'S_R[.STORE[n_field] = DEFINED (' + value + ')]'
        checks += ['$heap_graph(' + state + ') = H_saved',
            '$literal_reference_plain_cell(' + state + ', n_field)',
            '$string_unset_bool_cv_post_object(' + state + ', n_object)',
            '$string_unset_bool_cv_post_object_cell(' + state + ', n_alias)',
            '$string_unset_bool_cv_post_nonempty_array(' + state + ', n_key)']
    for changed in (
        'S_R[.REFCELLS = $literal_reference_delete(S_R.REFCELLS, n_field)]',
        'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HCELL n_field)]',
        'S_R[.STORE[n_field] = UNDEFINED]',
        'S_R[.PROPREFS = {CELL n_field, SOURCES eps} :: S_R.PROPREFS]',
        'S_R[.REFCOERCIONS = {CELL n_field, SITE porigin_site, LINE z, VALUE eps} :: S_R.REFCOERCIONS]',
        'S_R[.PARAMETERBACKINGS = {FUNCTION porigin_site, INDEX 0, CELL n_field, LINE z, VALUE eps} :: S_R.PARAMETERBACKINGS]',
    ):
        checks += ['~$string_unset_bool_cv_post_object(' + changed + ', n_object)',
            '~$string_unset_bool_cv_post_object_cell(' + changed + ', n_alias)',
            '~$string_unset_bool_cv_post_nonempty_array(' + changed + ', n_key)']
    for value in ('PARRAY n_middle', 'POBJECT n_object',
                  'PSTRING_CARRIER INTERNED_STRING ([0, 65])',
                  'PINT 9223372036854775808', 'PFLOAT 18446744073709551616'):
        state = 'S_R[.STORE[n_field] = DEFINED (' + value + ')]'
        checks += ['~$string_unset_bool_cv_post_object(' + state + ', n_object)',
            '~$string_unset_bool_cv_post_object_cell(' + state + ', n_alias)',
            '~$string_unset_bool_cv_post_nonempty_array(' + state + ', n_key)']
    state = 'S_R[.STORE[n_field] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("primitive-only")))]'
    checks += ['$string_unset_bool_cv_post_object(' + state + ', n_object)',
        '$string_unset_bool_cv_post_object_cell(' + state + ', n_alias)',
        '$string_unset_bool_cv_post_nonempty_array(' + state + ', n_key)']
    checks += ['~$string_unset_bool_cv_post_object_fields(S_R, ' + fields('(|S_R.STORE|)') + ')',
        'S_request = $string_request(S_R, $ptascii("primitive-only"))',
        'S_request.RESULT = KNOWN pvalue_request',
        '$string_carrier_valid(S_request, pvalue_request)',
        'S_alias_string = S_request[.STORE[n_field] = DEFINED pvalue_request]',
        '$heap_graph(S_alias_string) = H_saved',
        '~$literal_reference_plain_cell(S_alias_string, n_field)',
        '$string_unset_bool_cv_post_object(S_alias_string, n_object)',
        '$string_unset_bool_cv_post_nonempty_array(S_alias_string, n_key)',
        'S_direct_string = S_request[.OBJECTPROPS = $objectprops_set(S_request.OBJECTPROPS, n_object, [' +
            prior.slot('$ptascii("direct")', 'pvalue_request') + '])]',
        '$heap_valid($heap_graph(S_direct_string))',
        '$string_unset_bool_cv_post_object(S_direct_string, n_object)',
        '$string_unset_bool_cv_post_nonempty_array(S_direct_string, n_key)',
        'S_object_only = S_R[.ENV = $unbind(S_R.ENV, $ptascii("fieldValue"))][.GLOBALTABLE = eps]',
        '$heap_valid($heap_graph(S_object_only))',
        '$heap_count(HCELL n_field, $heap_graph(S_object_only).ROOTS) = 0',
        '$heap_owners($heap_graph(S_object_only), HCELL n_field) = 2',
        '$string_unset_bool_cv_post_object(S_object_only, n_object)',
        '$string_unset_bool_cv_post_nonempty_array(S_object_only, n_key)']
    duplicate = '[' + ', '.join(prior.slot('$ptascii("same")', '',
        state='PROP_VALUE (ALIAS n_field)') for _ in range(2)) + ']'
    for slots in (duplicate,
                  '[' + prior.slot('[0, 120]', '', state='PROP_VALUE (ALIAS n_field)') + ']',
                  '[' + prior.slot('$ptascii("declared")', '', '(porigin_site)',
                                    state='PROP_VALUE (ALIAS n_field)') + ']'):
        state = 'S_R[.OBJECTPROPS = $objectprops_set(S_R.OBJECTPROPS, n_object, ' + slots + ')]'
        checks += ['~$string_unset_bool_cv_post_object(' + state + ', n_object)',
            '~$string_unset_bool_cv_post_nonempty_array(' + state + ', n_key)']
    return checks, len(checks) - reached


if __name__ == '__main__':
    PRELAW = '--prelaw' in sys.argv
    if PRELAW:
        sys.argv.remove('--prelaw')
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (0, 1)
    watched = [Path(__file__), Path(prior.__file__), Path(prior.base.__file__),
        Path(prior.base.prior.__file__), Path(prior.base.prior.seek.__file__),
        Path(prior.base.prior.sl.__file__), Path(cases.prior.__file__),
        *[prior.base.prior.runner.ROOT / path for path in cases.WATCHED]]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner = prior.base.prior.runner
    runner.NAME = tuple(cases.CASES)[INDEX]
    runner.OUTPUT = cases.OUTPUTS[runner.NAME]
    runner.cases, runner.conditions = cases, conditions
    runner.PREFIX, runner.recorded = PREFIX, prior.base.prior.sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    output = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(output.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Independent reached shared primitive field cells and duplicate edges precede old Unsupported; '
        'derived object-only cell ownership and staged retirement remain source0/native0.' if PRELAW else
        'Independent shared primitive cell mutation, duplicate object edges, object-only retention and retirement; '
        'full-state/public replay and separate primitive/wrapper/string/owning/metadata fences remain source0/native0.')
    output.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
