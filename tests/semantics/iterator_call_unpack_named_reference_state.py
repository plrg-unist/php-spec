#!/usr/bin/env python3
"""Reach named fixed-slot sends using the established property-reference checks."""
import argparse
import hashlib
import json
from pathlib import Path

import fiber_state_review as review
import iterator_call_unpack_reference_array_review as arrays
import iterator_call_unpack_reference_object_review as objects

CATALOG = Path(__file__).with_name('iterator_call_unpack_named_reference_cases.json')
SOURCES = {row['source'] for row in json.loads(CATALOG.read_bytes())}
INPUTS = [Path(__file__), CATALOG, Path(review.__file__), Path(arrays.__file__),
          arrays.CATALOG, Path(objects.__file__), objects.CATALOG]


def named(case):
    source = case['source'].replace('return 0;', 'return "item";')
    assert source in SOURCES
    checks = []
    for check in case['checks']:
        if check == 'piteratorunpack.KEY = KNOWN (PINT 0)':
            checks.extend(['piteratorunpack.KEY = KNOWN pvalue_key',
                           '$fiber_traversal_key(pvalue_key) = (KSTRING ($ptascii("item")))'])
        elif check == '~piteratorunpack_next.NAMED':
            checks.append('piteratorunpack_next.NAMED')
        else:
            checks.append(check)
    return dict(case, source=source, checks=checks)


CASES = {
    'named-object-warning-captures-detached-hold': named(objects.CASES[
        'property-reference-warning-adds-payload-owner-with-nonowning-snapshot']),
    'named-object-send-transfers-hold-to-fresh-cell': named(objects.CASES[
        'stable-property-reference-transfers-hold-to-distinct-fresh-cell']),
    'named-array-send-transfers-container-to-fresh-cell': named(arrays.CASES[
        'stable-property-reference-array-transfers-hold-to-distinct-fresh-cell']),
    'named-array-global-alias-keeps-original-after-callee-copy': named(arrays.CASES[
        'global-alias-retains-original-array-through-callee-nested-copy']),
    'named-object-parked-warning-preserves-independent-owners': named(objects.CASES[
        'parked-reference-warning-keeps-cell-and-payload-owners-distinct']),
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
