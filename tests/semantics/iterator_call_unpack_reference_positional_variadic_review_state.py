#!/usr/bin/env python3
"""Reach packed private cells and retain original EXTRA owners after rest unset."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('iterator_call_unpack_reference_positional_variadic_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
SOURCES = {row['id']: row['source'] for row in json.loads(INPUT_BYTES[CATALOG])}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']

CASES = {
    'second-rest-receive-shares-array-through-distinct-private-cells': {
        'source': SOURCES['iterator-reference-positional-variadic-review-same-raw-array-nested-cow'],
        'stage': ('S.TODO = [VARIADIC_RECEIVE porigin 1] -- if S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.NAME = $ptascii("reviewRestArrays07")'),
        'checks': [
            'pcallcontext.FUNCTION = porigin', 'pcallcontext.ARGC = 2',
            'pcallcontext.HOLES = eps', 'pcallcontext.NAMED = eps', 'pcallcontext.LINE = 15',
            'pcallcontext.EXTRA = [REFERENCE n_first, REFERENCE n_second]',
            '$receiving_function(S, porigin) = (pfunction)',
            'pfunction.SIGNATURE.PARAMETERS = [psparam]',
            'psparam.NAME = $ptascii("items")',
            r'psparam.BYREF /\ psparam.VARIADIC /\ psparam.TYPE = eps',
            '$lookup(S.ENV, $ptascii("items")) = (n_rest_cell)',
            'S.STORE[n_rest_cell] = DEFINED (PARRAY n_rest)',
            'S.ARRAYS[n_rest].ITEMS = [ENTRY (KINT 0) (ALIAS n_first)]',
            'S.ARRAYS[n_rest].NEXT = 1',
            'n_first =/= n_second', 'n_first =/= n_rest_cell', 'n_second =/= n_rest_cell',
            'n_first <- S.REFCELLS', 'n_second <- S.REFCELLS',
            'S.STORE[n_first] = DEFINED (PARRAY n_payload)',
            'S.STORE[n_second] = DEFINED (PARRAY n_payload)',
            'n_payload =/= n_rest',
            'S.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_child))]',
            '$object_name(S, n_child) = $ptascii("ReviewRestChild07")',
            '$node_children(S, HARRAY n_rest) = [HCELL n_first]',
            '$node_children(S, HCELL n_first) = [HARRAY n_payload]',
            '$node_children(S, HCELL n_second) = [HARRAY n_payload]',
            '$node_children(S, HARRAY n_payload) = [HOBJECT n_child]',
            '$heap_owners($heap_graph(S), HCELL n_first) = 2',
            '$heap_owners($heap_graph(S), HCELL n_second) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_payload) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_rest) = 1',
            '$propref_at(S.PROPREFS, n_first) = eps',
            '$propref_at(S.PROPREFS, n_second) = eps',
            'S.DESTRUCTION.CALLED = [n_data]',
            '$object_name(S, n_data) = $ptascii("ReviewRestArrayIterator07")',
            '~((HOBJECT n_data) <- S.ALLOCATIONS)',
            '$call_task_valid(S, VARIADIC_RECEIVE porigin 1)', *ADMISSION,
            '~$variadic_receive_valid(S[.TODO = [VARIADIC_RECEIVE porigin 0]], porigin, 0)',
            *ZERO, *ONE,
            'S_one.TODO = [VARIADIC_RECEIVE porigin 2]',
            'S_one.CURRENT = S.CURRENT', 'S_one.STORE = S.STORE',
            'S_one.ARRAYS[n_rest].ITEMS = [ENTRY (KINT 0) (ALIAS n_first), ENTRY (KINT 1) (ALIAS n_second)]',
            'S_one.ARRAYS[n_rest].NEXT = 2',
            '$node_children(S_one, HARRAY n_rest) = [HCELL n_first, HCELL n_second]',
            '$heap_owners($heap_graph(S_one), HCELL n_first) = 2',
            '$heap_owners($heap_graph(S_one), HCELL n_second) = 2',
            '$heap_owners($heap_graph(S_one), HARRAY n_payload) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_child) = 1',
            'S_one.EVENTS = S.EVENTS', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', '$drive(S, 2) = S_two_budget',
        ],
    },
    'unset-rest-retires-container-but-preserves-original-extra-cell': {
        'source': SOURCES['iterator-reference-positional-variadic-review-byvalue-array-unset-rest-keeps-extra-owner'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.NAME = $ptascii("reviewRestUnset07") '
                  '-- if S.TODO = (UNSET (NExprVariable (BYTES text_name) metadata)) :: ptask_tail* '
                  '-- if $base64(text_name) = $ptascii("items")'),
        'checks': [
            'pcallcontext.ARGC = 2', 'pcallcontext.HOLES = eps',
            'pcallcontext.NAMED = eps', 'pcallcontext.LINE = 16',
            'pcallcontext.EXTRA = [REFERENCE n_extra]',
            '$receiving_function(S, pcallcontext.FUNCTION) = (pfunction)',
            'pfunction.SIGNATURE.PARAMETERS = [psparam_head, psparam_rest]',
            r'~psparam_head.BYREF /\ ~psparam_head.VARIADIC /\ psparam_head.TYPE = eps',
            r'psparam_rest.BYREF /\ psparam_rest.VARIADIC /\ psparam_rest.TYPE = eps',
            '$lookup(S.ENV, $ptascii("head")) = (n_head_cell)',
            '$lookup(S.ENV, $ptascii("items")) = (n_rest_cell)',
            'n_head_cell =/= n_rest_cell', 'n_extra =/= n_head_cell', 'n_extra =/= n_rest_cell',
            'S.STORE[n_head_cell] = DEFINED (PARRAY n_head)',
            'S.ARRAYS[n_head].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_earlier))]',
            '$object_name(S, n_earlier) = $ptascii("ReviewRestEarlier07")',
            'S.STORE[n_rest_cell] = DEFINED (PARRAY n_rest)',
            'S.ARRAYS[n_rest].ITEMS = [ENTRY (KINT 0) (ALIAS n_extra)]',
            'n_head =/= n_rest', 'n_extra <- S.REFCELLS',
            'S.STORE[n_extra] = DEFINED (POBJECT n_current)',
            '$object_name(S, n_current) = $ptascii("ReviewRestCurrent07")',
            '$node_children(S, HARRAY n_rest) = [HCELL n_extra]',
            '$node_children(S, HCELL n_extra) = [HOBJECT n_current]',
            '$heap_owners($heap_graph(S), HCELL n_extra) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_current) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_rest) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_head) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_earlier) = 1',
            '$propref_at(S.PROPREFS, n_extra) = eps',
            'S.DESTRUCTION.CALLED = [n_data]',
            '$object_name(S, n_data) = $ptascii("ReviewRestMixedIterator07")',
            '~((HOBJECT n_data) <- S.ALLOCATIONS)', *ADMISSION, *ZERO, *ONE,
            '$lookup(S_one.ENV, $ptascii("items")) = eps',
            'S_one.CURRENT = S.CURRENT', 'S_one.STORE = S.STORE',
            'S_one.ARRAYS = S.ARRAYS', 'S_one.EVENTS = S.EVENTS',
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_rest_cell)]',
            'pdestructionoperation.SOURCE = UNSET (NExprVariable (BYTES text_name) metadata)',
            '$destructor_release_valid(S_one, pdestructionrelease)',
            '$eager_operation_source_valid(S_one, pdestructionoperation)',
            '$heap_owners($heap_graph(S_one), HCELL n_extra) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_current) = 1',
            '$heap_owners($heap_graph(S_one), HARRAY n_head) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_earlier) = 1',
            '$heap_owners($heap_graph(S_one), HCELL n_rest_cell) = 1',
            '$heap_owners($heap_graph(S_one), HARRAY n_rest) = 1',
            'S_one.DESTRUCTION.CALLED = S.DESTRUCTION.CALLED', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', '$drive(S, 2) = S_two_budget',
            'S_four_budget = $drive_steps(S_one, 3)', 'S_four_budget.COMPLETION = BUDGET',
            'S_four = S_four_budget[.COMPLETION = NORMAL]', '$drive(S, 4) = S_four_budget',
            'S_four.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_done) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease_done.JOBS = eps',
            'S_four.CURRENT = S.CURRENT', 'S_four.EVENTS = S.EVENTS',
            'S_four.STORE[n_extra] = S.STORE[n_extra]',
            '$heap_owners($heap_graph(S_four), HCELL n_extra) = 1',
            '$heap_owners($heap_graph(S_four), HOBJECT n_current) = 1',
            '$heap_owners($heap_graph(S_four), HARRAY n_head) = 1',
            '$heap_owners($heap_graph(S_four), HOBJECT n_earlier) = 1',
            '$heap_owners($heap_graph(S_four), HCELL n_rest_cell) = 0',
            '$heap_owners($heap_graph(S_four), HARRAY n_rest) = 0',
            '~((HARRAY n_rest) <- S_four.ALLOCATIONS)',
            'S_four.DESTRUCTION.CALLED = S.DESTRUCTION.CALLED',
            '$call_descriptors_valid(S_four)', '$heap_valid($heap_graph(S_four))',
            'S_done = $drive(S_four, 4000)', 'S_done.COMPLETION = NORMAL',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("REST|"), OUTPUT $ptascii("A|"), '
            'OUTPUT $ptascii("HEAD|"), OUTPUT $ptascii("B|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HCELL n_extra) = 0',
            '$heap_owners($heap_graph(S_done), HCELL n_head_cell) = 0',
            '$heap_owners($heap_graph(S_done), HARRAY n_head) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_earlier) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_current) = 0',
            'n_earlier <- S_done.DESTRUCTION.CALLED', 'n_current <- S_done.DESTRUCTION.CALLED',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        ],
    },
}


def run(selected):
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
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
    stable = INPUT_BYTES == {p: p.read_bytes() for p in INPUT_BYTES}
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    path = raw / 'report.json'
    report = json.loads(path.read_bytes())
    report.update(independent_inputs={str(p): hashlib.sha256(b).hexdigest()
                                     for p, b in INPUT_BYTES.items()},
                  independent_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return passed and stable and head_stable


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
