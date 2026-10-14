#!/usr/bin/env python3
"""Reach later fixed sends, sparse argument slots and earlier default binding."""
import argparse
import hashlib
import json
from pathlib import Path

import fiber_state_review as review
import iterator_call_unpack_named_reference_state as prior

CATALOG = Path(__file__).with_name('iterator_call_unpack_later_fixed_reference_cases.json')
SOURCES = {row['source'] for row in json.loads(CATALOG.read_bytes())}
INPUTS = [Path(__file__), CATALOG, *prior.INPUTS]


def later(case):
    source = case['source']
    name = 'ReferenceArrayTarget35' if 'function ReferenceArrayTarget35(' in source else 'ReferenceTarget34'
    source = source.replace('function ' + name + '(&$item)',
                            'function ' + name + '($prefix = 17, &$item = null)')
    source = source.replace('echo "B|";',
                            'echo "D", $prefix, "|", func_num_args(), "|"; echo "B|";')
    assert source in SOURCES
    checks = [check.replace('by-reference argument 1', 'by-reference argument 2')
                   .replace('SENT.SLOTS = [NAMED_SENT (REFERENCE n_private)]',
                            'SENT.SLOTS = [NAMED_HOLE, NAMED_SENT (REFERENCE n_private)]')
              for check in case['checks']]
    return dict(case, source=source, checks=checks)


CASES = {name.replace('named-', 'later-fixed-', 1): later(case)
         for name, case in prior.CASES.items()}
CASES['earlier-hole-default-binds-with-selected-private-reference-alive'] = {
    'source': next(row['source'] for row in json.loads(CATALOG.read_bytes())
                   if row['id'] == 'iterator-call-unpack-later-fixed-reference-object-normal'),
    'stage': ('S.TODO = [NAMED_PREFLIGHT porigin_function 0] '
              '-- if S.CURRENT = (pcallcontext) '
              '-- if pcallcontext.NAME = $ptascii("ReferenceTarget34")'),
    'checks': [
        '$receiving_function(S, porigin_function) = (pfunction)',
        'pfunction.SIGNATURE.PARAMETERS[0].NAME = $ptascii("prefix")',
        'pfunction.SIGNATURE.PARAMETERS[1].NAME = $ptascii("item")',
        'pcallcontext.ARGC = 2', 'pcallcontext.HOLES = [0]',
        'pcallcontext.NAMED = eps', 'pcallcontext.EXTRA = eps',
        '~$named_defined(S, $ptascii("prefix"))',
        '$lookup(S.ENV, $ptascii("item")) = (n_private)',
        'S.STORE[n_private] = DEFINED (POBJECT n_payload)',
        'n_private <- S.REFCELLS',
        '$heap_owners($heap_graph(S), HCELL n_private) = 1',
        '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
        'S.DESTRUCTION.CALLED = [n_data]', 'n_data =/= n_payload',
        '~((HOBJECT n_data) <- S.ALLOCATIONS)',
        '$default_at(pfunction.DEFAULTS, 0) = (pdefault)',
        'pdefault.KIND = PDSTORED',
        '$compiled_read(S, pdefault.ORIGIN) = (PINT 17)',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S',
        'S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
        'S_one = S_one_budget[.COMPLETION = NORMAL]',
        'S_one.TODO = [NAMED_PREFLIGHT porigin_function 1]',
        '$named_defined(S_one, $ptascii("prefix"))',
        '$lookup(S_one.ENV, $ptascii("prefix")) = (n_prefix)',
        'S_one.STORE[n_prefix] = DEFINED (PINT 17)',
        'S_one.STORE[n_private] = S.STORE[n_private]',
        'S_one.CURRENT = S.CURRENT', 'S_one.EVENTS = S.EVENTS',
        '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 1',
        '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
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
