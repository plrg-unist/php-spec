#!/usr/bin/env python3
"""Reach typed property-reference holds, private receives and rejected traces."""
import argparse
import hashlib
import json
from pathlib import Path

import fiber_state_review as review
import iterator_call_unpack_later_fixed_reference_state as prior

CATALOG = Path(__file__).with_name('iterator_call_unpack_typed_fixed_reference_cases.json')
ROWS = json.loads(CATALOG.read_bytes())
SOURCES = {row['source'] for row in ROWS}
INPUTS = [Path(__file__), CATALOG, *prior.INPUTS]


def typed(case):
    source = case['source']
    array = 'function ReferenceArrayTarget35(' in source
    name = 'ReferenceArrayTarget35' if array else 'ReferenceTarget34'
    target_type = '?array' if array else '?ReferencePayload34'
    source = source.replace('function ' + name + '($prefix = 17, &$item = null)',
                            'function ' + name + '($prefix = 17, ' + target_type + ' &$item = null)')
    if array:
        source = source.replace('$item[0] = null; echo "F|";',
                                '$item[0] = null; echo "F|"; $item = 17; echo "Q", $item, "|";')
    else:
        source = source.replace('$item = null; echo "F|";',
                                '$item = 17; echo "F|"; echo "Q", $item, "|";')
    assert source in SOURCES
    checks = [check.replace('OUTPUT $ptascii("F|"), OUTPUT $ptascii("HELD|")',
                            'OUTPUT $ptascii("F|"), OUTPUT $ptascii("Q"), '
                            'OUTPUT $ptascii("17"), OUTPUT $ptascii("|"), OUTPUT $ptascii("HELD|")')
              for check in case['checks']]
    return dict(case, source=source, checks=checks)


CASES = {name.replace('later-fixed-', 'typed-fixed-', 1): typed(case)
         for name, case in prior.CASES.items() if name.startswith('later-fixed-')}
CASES['typed-fixed-object-warning-captures-detached-hold']['checks'] += [
    '$target_function(S, piteratorunpack.CALL.FUNCTION) = (pfunction_bound)',
    'psparam_prefix = pfunction_bound.SIGNATURE.PARAMETERS[0]',
    'psparam_item = pfunction_bound.SIGNATURE.PARAMETERS[1]',
    'pfunction_reverse = pfunction_bound[.SIGNATURE = pfunction_bound.SIGNATURE[.PARAMETERS = '
    '[psparam_prefix, psparam_item[.TYPE = [(PTBRANCH ([PTBUILTIN "null"])), '
    '(PTBRANCH ([PTCLASS $ptascii("ReferencePayload34")]))]]]]]',
    'S_reverse = S[.FUNCTIONS = [pfunction_reverse]]',
    '$target_function(S_reverse, piteratorunpack.CALL.FUNCTION) = (pfunction_reverse)',
    '~$iterator_unpack_reference_allowed(S_reverse, piteratorunpack)',
    'pfunction_nonnullable = pfunction_bound[.SIGNATURE = pfunction_bound.SIGNATURE[.PARAMETERS = '
    '[psparam_prefix, psparam_item[.TYPE = [(PTBRANCH ([PTCLASS $ptascii("ReferencePayload34")]))]]]]]',
    'S_nonnullable = S[.FUNCTIONS = [pfunction_nonnullable]]',
    '$target_function(S_nonnullable, piteratorunpack.CALL.FUNCTION) = (pfunction_nonnullable)',
    '~$iterator_unpack_reference_allowed(S_nonnullable, piteratorunpack)',
    'pfunction_variadic = pfunction_bound[.SIGNATURE = pfunction_bound.SIGNATURE[.PARAMETERS = '
    '[psparam_prefix, psparam_item[.VARIADIC = true]]]]',
    'S_variadic = S[.FUNCTIONS = [pfunction_variadic]]',
    '$target_function(S_variadic, piteratorunpack.CALL.FUNCTION) = (pfunction_variadic)',
    '~$iterator_unpack_reference_allowed(S_variadic, piteratorunpack)',
]
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
RECEIVE = [
    '$receiving_function(S, porigin_function) = (pfunction)',
    'pcallcontext.ARGC = 2', 'pcallcontext.HOLES = [0]',
    'pcallcontext.NAMED = eps', 'pcallcontext.EXTRA = eps',
    '$lookup(S.ENV, $ptascii("prefix")) = (n_prefix)',
    'S.STORE[n_prefix] = DEFINED (PINT 17)',
    '$lookup(S.ENV, $ptascii("item")) = (n_private)',
    'S.STORE[n_private] = DEFINED (POBJECT n_payload)',
    'n_private <- S.REFCELLS',
    '$propref_at(S.PROPREFS, n_private) = eps',
    'pfunction.SIGNATURE.PARAMETERS[1].BYREF',
    '~$typed_parameter_source(S, pfunction.SIGNATURE.PARAMETERS[1])',
    '$heap_owners($heap_graph(S), HCELL n_private) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
    'S.DESTRUCTION.CALLED = [n_data]', 'n_data =/= n_payload',
    '~((HOBJECT n_data) <- S.ALLOCATIONS)',
    '$typed_receive_valid(S, porigin_function, 1)',
    '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
]
STAGE = ('S.TODO = [TYPE_RECEIVE porigin_function 1] '
         '-- if S.CURRENT = (pcallcontext) '
         '-- if pcallcontext.NAME = $ptascii("ReferenceTarget34")')
CASES['positional-class-receive-keeps-source-free-private-cell'] = {
    'source': next(row['source'] for row in ROWS
                   if row['id'] == 'iterator-call-unpack-typed-fixed-reference-positional-class-normal'),
    'stage': STAGE.replace('TYPE_RECEIVE porigin_function 1', 'TYPE_RECEIVE porigin_function 0'),
    'checks': [
        '$receiving_function(S, porigin_function) = (pfunction)',
        'pcallcontext.ARGC = 1', 'pcallcontext.HOLES = eps',
        'pcallcontext.NAMED = eps', 'pcallcontext.EXTRA = eps',
        '$lookup(S.ENV, $ptascii("item")) = (n_private)',
        'S.STORE[n_private] = DEFINED (POBJECT n_payload)',
        'n_private <- S.REFCELLS',
        '$propref_at(S.PROPREFS, n_private) = eps',
        'pfunction.SIGNATURE.PARAMETERS[0].BYREF',
        '~$typed_parameter_source(S, pfunction.SIGNATURE.PARAMETERS[0])',
        '$heap_owners($heap_graph(S), HCELL n_private) = 1',
        '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
        'S.DESTRUCTION.CALLED = [n_data]', 'n_data =/= n_payload',
        '~((HOBJECT n_data) <- S.ALLOCATIONS)',
        '$typed_receive_valid(S, porigin_function, 0)',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'pfunction.SIGNATURE.PARAMETERS[0].TYPE = '
        '[(PTBRANCH ([PTCLASS $ptascii("ReferencePayload34")])), (PTBRANCH ([PTBUILTIN "null"]))]',
        '$typed_parameter_conversion(S, pfunction.SIGNATURE.PARAMETERS[0], POBJECT n_payload) = '
        'TYPEVALUE (POBJECT n_payload)',
        *ZERO, *ONE,
        'S_one.TODO = $call_receive_body(S_one, pfunction)',
        'S_one.STORE = S.STORE', 'S_one.CURRENT = S.CURRENT',
        'S_one.PROPREFS = S.PROPREFS', 'S_one.EVENTS = S.EVENTS',
        '$heap_owners($heap_graph(S_one), HCELL n_private) = 1',
        '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 1',
        '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
    ],
}
CASES['wrong-class-receive-materializes-owning-TypeError-before-body'] = {
    'source': next(row['source'] for row in ROWS
                   if row['id'] == 'iterator-call-unpack-typed-fixed-reference-object-wrong-class-receive'),
    'stage': STAGE,
    'checks': [
        *RECEIVE,
        'pfunction.SIGNATURE.PARAMETERS[1].TYPE = '
        '[(PTBRANCH ([PTCLASS $ptascii("ReferenceIterator34")])), (PTBRANCH ([PTBUILTIN "null"]))]',
        '$typed_parameter_conversion(S, pfunction.SIGNATURE.PARAMETERS[1], POBJECT n_payload) = TYPEREJECT',
        *ZERO, *ONE,
        'S_one.TODO = (THROW_SEARCH n_error) :: ptask_after*',
        'S_one.OBJECTS[n_error] = THROWABLE pthrowable',
        'pthrowable.KIND = "TypeError"',
        '$throwable_field(S_one, n_error, "line") = PINT 14',
        '$throwable_field(S_one, n_error, "message") = PSTRING '
        '($ptascii("ReferenceTarget34(): Argument #2 ($item) must be of type ?ReferenceIterator34, ReferencePayload34 given") '
        '++ $wrapper_called_suffix(S, pcallcontext))',
        '$throwable_field(S_one, n_error, "trace") = PARRAY n_trace',
        '$entry_lookup(S_one.ARRAYS[n_trace].ITEMS, KINT 0) = (DIRECT (PARRAY n_frame))',
        '$entry_lookup(S_one.ARRAYS[n_frame].ITEMS, KSTRING $ptascii("function")) = '
        '(DIRECT (PSTRING $ptascii("ReferenceTarget34")))',
        '$entry_lookup(S_one.ARRAYS[n_frame].ITEMS, KSTRING $ptascii("args")) = '
        '(DIRECT (PARRAY n_args))',
        'S_one.ARRAYS[n_args].ITEMS = '
        '[ENTRY (KINT 0) (DIRECT (PINT 17)), ENTRY (KINT 1) (DIRECT (POBJECT n_payload))]',
        '$trace_graph_valid(S_one, n_trace)',
        'S_one.STORE = S.STORE', 'S_one.CURRENT = S.CURRENT',
        '$heap_owners($heap_graph(S_one), HCELL n_private) = 1',
        '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 2',
        'S_one.EVENTS = S.EVENTS', '$heap_valid($heap_graph(S_one))',
        'S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
        'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("R|"), OUTPUT $ptascii("14"), '
        'OUTPUT $ptascii("|"), OUTPUT $ptascii("A|"), OUTPUT $ptascii("O|"), OUTPUT $ptascii("E")]',
        '$heap_owners($heap_graph(S_done), HCELL n_private) = 0',
        '$heap_owners($heap_graph(S_done), HOBJECT n_payload) = 0',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ],
}


def run(selected):
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    inputs = {str(path): digest(path) for path in INPUTS}
    review.CASES = CASES
    original = review.recorded
    raw = None

    def recorded(command, directory, stem, environment, cap):
        nonlocal raw
        raw = directory.parent
        return original(command, directory, stem, environment, cap)

    review.recorded = recorded
    try:
        passed = review.run(selected)
    finally:
        review.recorded = original
    stable = inputs == {str(path): digest(path) for path in INPUTS}
    path = raw / 'report.json'
    report = json.loads(path.read_bytes())
    report.update(author_inputs=inputs, author_inputs_stable=stable,
                  passed=passed and stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return passed and stable


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
