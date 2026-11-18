#!/usr/bin/env python3
"""Source-reached STRING aliases distinguish carrier validity from ownership."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_empty_array_post_protocol as raw
import string_offset_nested_unset_bool_cv_deep_array_post_protocol as prior
import string_offset_nested_unset_bool_cv_string_alias_post_cases as cases

INDEX = 0
PRELAW = False
BASE_CONDITIONS = prior.conditions
PREFIX = raw.PREFIX + r'''
dec $review_string_alias_at(pstate, nat*) : bool
def $review_string_alias_at(S, n_output*) = ($review_cv_outputs(S.EVENTS) = n_output* /\ $lookup(S.ENV, $ptascii("key")) = eps /\ $lookup(S.ENV, $ptascii("textAlias")) =/= eps)
dec $review_string_alias_seek(pstate, nat*, nat) : pstate
def $review_string_alias_seek(S, n_output*, 0) = S
def $review_string_alias_seek(S, n_output*, n) = S
  -- if $(n > 0)
  -- if $review_string_alias_at(S, n_output*) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $review_string_alias_seek(S, n_output*, n) = $review_string_alias_seek($drive_steps($review_cv_running(S), 1), n_output*, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$review_string_alias_at(S, n_output*)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def front(program, path):
    raw.INDEX, raw.cases = INDEX, cases
    checks = raw.front(program, path)
    facts = cases.FACTS[tuple(cases.CASES)[INDEX]]
    checks[checks.index('parray_key.ITEMS = eps')] = ('parray_key.ITEMS = '
        '[ENTRY (KINT 0) (DIRECT (PINT 7)), ENTRY (KINT 1) (DIRECT (PARRAY n_middle))]')
    checks[checks.index('$node_children(S_R, HARRAY n_array) = eps')] = '$node_children(S_R, HARRAY n_array) = [HARRAY n_middle]'
    checks += ['$(n_middle < |S_R.ARRAYS|)',
        'n_middle =/= n_array',
        'S_R.ARRAYS[n_middle].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8)), ENTRY (KINT 1) (ALIAS n_text), ENTRY (KINT 2) (ALIAS n_text)]',
        '$node_children(S_R, HARRAY n_middle) = [HCELL n_text, HCELL n_text]',
        '$heap_member(HARRAY n_middle, $heap_prune(H_R).NODES)',
        '$heap_edge_owners(HARRAY n_middle, H_R.EDGES, [HARRAY n_array]) = 1',
        '$lookup(S_R.ENV, $ptascii("textAlias")) = (n_text)',
        '$(n_text < |S_R.STORE|)',
        'n_text =/= n_key',
        'S_R.STORE[n_text] = DEFINED pvalue_text',
        'n_text <- S_R.REFCELLS',
        '$call_reference_operand_valid(S_R, REFERENCE n_text)',
        '~$literal_reference_plain_cell(S_R, n_text)',
        '$propref_at(S_R.PROPREFS, n_text) = eps',
        '$reference_coercion_at(S_R.REFCOERCIONS, n_text) = eps',
        '$parameter_backing_at(S_R.PARAMETERBACKINGS, n_text) = eps',
        '$heap_member(HCELL n_text, H_R.ROOTS)',
        '$heap_member(HCELL n_text, $heap_prune(H_R).NODES)',
        '$heap_edge_owners(HCELL n_text, H_R.EDGES, [HARRAY n_middle]) = 2',
        '$node_children(S_R, HCELL n_text) = eps',
        '$value_nodes(pvalue_text) = eps']
    value = raw.shared.term(facts['initial'])
    if facts['requested']:
        checks += ['pvalue_text = PSTRING_CARRIER (REQUEST_STRING n_initial) (' + value + ')',
            '$(n_initial < |S_R.STRINGDATA|)', 'S_R.STRINGDATA[n_initial] = ' + value]
    else:
        checks += ['pvalue_text = PSTRING_CARRIER INTERNED_STRING (' + value + ')']
    checks += ['$string_carrier_valid(S_R, pvalue_text)',
        '$c_string(' + value + ') = ' + value,
        '$string_read_array_string_cell(S_R, n_text)',
        '$cast_truth_int(S_R, pvalue_text) = ' + ('1' if facts['requested'] else '0'),
        '$cast_truth_int(S_R, PARRAY n_array) = 1',
        '$lookup(S_R.ENV, $ptascii("last")) = (n_last)',
        'S_R.STORE[n_last] = DEFINED (PINT 7)']
    return checks


def conditions(program, path):
    prior.INDEX, prior.cases, prior.PRELAW, prior.front = INDEX, cases, PRELAW, front
    checks, derived = BASE_CONDITIONS(program, path)
    if not PRELAW:
        # Retain the tested common continuation proof; its ARRAY-child-specific
        # malformed controls belong to the earlier family and stay untouched.
        assert derived == 17
        checks = checks[:-derived]
        derived = 0
        assert not any('n_grand' in line for line in checks)
    name = tuple(cases.CASES)[INDEX]
    at = checks.index('S_DONE = $drive_steps(S_tail, 3000)')
    middle = ['S_retained_found = $review_string_alias_seek($drive_steps(S_tail, 1), ' + raw.shared.term(cases.RETAINED_OUTPUTS[name]) + ', 3000)',
        '$review_string_alias_at(S_retained_found, ' + raw.shared.term(cases.RETAINED_OUTPUTS[name]) + ')',
        'S_retained = $review_cv_running(S_retained_found)',
        'S_retained.COMPLETION = NORMAL',
        '$lookup(S_retained.ENV, n_key_name*) = eps',
        '$lookup(S_retained.ENV, $ptascii("textAlias")) = (n_text)',
        'S_retained.STORE[n_text] = DEFINED pvalue_after',
        'pvalue_after = PSTRING_CARRIER (REQUEST_STRING n_after) ($ptascii("after-text"))',
        '$(n_after < |S_retained.STRINGDATA|)',
        'S_retained.STRINGDATA[n_after] = $ptascii("after-text")',
        '$string_carrier_valid(S_retained, pvalue_after)',
        '$string_read_array_string_cell(S_retained, n_text)',
        '$value_nodes(pvalue_after) = eps',
        '$node_children(S_retained, HCELL n_text) = eps',
        'H_retained = $heap_graph(S_retained)',
        '$heap_valid(H_retained)',
        '$heap_member(HCELL n_text, H_retained.ROOTS)',
        '$heap_member(HCELL n_text, $heap_prune(H_retained).NODES)']
    checks[at:at + 1] = middle + ['S_DONE = $drive_steps(S_retained, 3000)']
    final = ['$lookup(S_DONE.ENV, $ptascii("textAlias")) = eps',
        '~$heap_member(HCELL n_text, $heap_graph(S_DONE).ROOTS)',
        '~$heap_member(HCELL n_text, $heap_prune($heap_graph(S_DONE)).NODES)',
        'S_DONE.STRINGDATA[n_after] = $ptascii("after-text")',
        '$string_carrier_valid(S_DONE, pvalue_after)',
        '~$string_read_array_string_cell(S_DONE, n_text)']
    checks += final
    if PRELAW:
        return checks, derived + len(middle) + len(final)
    at = len(checks)
    for tag, changed in (
        ('unmarked', 'S_R[.REFCELLS = $literal_reference_delete(S_R.REFCELLS, n_text)]'),
        ('unallocated', 'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HCELL n_text)]'),
        ('undefined', 'S_R[.STORE[n_text] = UNDEFINED]'),
        ('raw', 'S_R[.STORE[n_text] = DEFINED (PSTRING ($ptascii("raw")))]'),
        ('nul', 'S_R[.STORE[n_text] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([0]))]'),
        ('bad_request', 'S_R[.STORE[n_text] = DEFINED (PSTRING_CARRIER (REQUEST_STRING (|S_R.STRINGDATA|)) ($ptascii("bad")))]'),
    ):
        state = 'S_bad_' + tag
        checks += [state + ' = ' + changed,
            '~$string_read_array_string_cell(' + state + ', n_text)',
            '~$string_unset_bool_cv_post_nonempty_array(' + state + ', n_key)']
    checks += ['S_promoted = S_R[.STORE[n_text] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("string-alias")))]',
        '$heap_valid($heap_graph(S_promoted))',
        '$string_read_array_string_cell(S_promoted, n_text)',
        '$string_unset_bool_cv_post_nonempty_array(S_promoted, n_key)',
        '$string_unset_bool_cv_post_cell(S_promoted, n_key_name*, z_key, n_key)',
        'S_key_only = S_R[.ENV = $unbind(S_R.ENV, $ptascii("textAlias"))][.GLOBALTABLE = eps]',
        '$heap_valid($heap_graph(S_key_only))',
        '~$heap_member(HCELL n_text, $heap_graph(S_key_only).ROOTS)',
        '$heap_member(HCELL n_text, $heap_prune($heap_graph(S_key_only)).NODES)',
        '$string_read_array_string_cell(S_key_only, n_text)',
        '$string_unset_bool_cv_post_nonempty_array(S_key_only, n_key)']
    for changed in ('S_R[.CODE = eps]', 'S_R[.SOURCES = eps]', 'S_R[.ORIGIN = eps]'):
        checks += ['~$call_task_valid(' + changed + ', STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key)']
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
    watched = [Path(__file__), Path(raw.__file__), Path(prior.__file__),
               Path(raw.shared.__file__), Path(raw.sl.__file__), Path(cases.prior.__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner = raw.runner
    runner.NAME, runner.OUTPUT = name, cases.OUTPUTS[name]
    runner.cases, runner.conditions = cases, conditions
    runner.PREFIX, runner.recorded = PREFIX, raw.sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Genuine STRING-alias source/quiet read/cell/header facts before Unsupported; '
                       'separately derived retainer/last-cell retirement, registry is not ownership; source0/native0.'
                       if PRELAW else 'Source-reached STRING aliases preserve exact continuation/whole-split states '
                       'and two retirement stages; malformed and promoted current controls separate; source0/native0.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
