#!/usr/bin/env python3
"""Independent repeated raw sources and noninitial private-cell alias separation."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('iterator_call_unpack_noninitial_reference_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
SOURCES = {row['id']: row['source'] for row in json.loads(INPUT_BYTES[CATALOG])}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']

CASES = {
    'same-raw-property-second-send-creates-another-private-cell': {
        'source': SOURCES['iterator-noninitial-reference-review-same-source-two-private-cells'],
        'stage': ('S.TODO = (ITERATOR_UNPACK piteratorunpack "byref") :: ptask_tail* '
                  '-- if piteratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (REFERENCE n_prior)]'),
        'checks': [
            'piteratorunpack.CALL.SENT.NAMED = eps', '~piteratorunpack.NAMED',
            'piteratorunpack.CALL.LINE = 16', 'piteratorunpack.KEY = KNOWN (PINT 1)',
            'piteratorunpack.CURRENT = REFERENCE n_raw',
            'piteratorunpack.SNAPSHOT = (POBJECT n_payload)',
            'piteratorunpack.HOLD = KNOWN (POBJECT n_payload)',
            'n_data = piteratorunpack.OBJECT',
            'piteratorunpack.INPUT = KNOWN (POBJECT n_data)',
            '$object_name(S, n_data) = $ptascii("ReviewNoninitialRepeat04")',
            '$object_name(S, n_payload) = $ptascii("ReviewNoninitialShared04")',
            'S.STORE[n_raw] = DEFINED (POBJECT n_payload)',
            'S.STORE[n_prior] = DEFINED (POBJECT n_payload)',
            'n_raw =/= n_prior', 'n_raw <- S.REFCELLS', 'n_prior <- S.REFCELLS',
            '$objectprops_record_at(S.OBJECTPROPS, n_data) = (pobjectprops)',
            '$property_slot_at(pobjectprops.SLOTS, $ptascii("payload")) = (ppropertyslot)',
            'ppropertyslot.STATE = PROP_VALUE (ALIAS n_raw)',
            '$node_children(S, HOBJECT n_data) = [HCELL n_raw]',
            '$node_children(S, HCELL n_raw) = [HOBJECT n_payload]',
            '$node_children(S, HCELL n_prior) = [HOBJECT n_payload]',
            '$iterator_unpack_named_target(S, piteratorunpack) = NAMED_POSITION 1',
            '$target_function(S, piteratorunpack.CALL.FUNCTION) = (pfunction)',
            'psparam = pfunction.SIGNATURE.PARAMETERS[1]',
            r'psparam.BYREF /\ ~psparam.VARIADIC', 'psparam.TYPE = eps',
            '$iterator_unpack_reference_allowed(S, piteratorunpack)',
            '$iterator_unpack_hold_live(S, piteratorunpack, "byref")',
            '$iterator_unpack_hold_allowed(S, piteratorunpack, "byref")',
            '$heap_owners($heap_graph(S), HCELL n_raw) = 2',
            '$heap_owners($heap_graph(S), HCELL n_prior) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2', *ADMISSION,
            'piteratorunpack_bad = piteratorunpack[.CALL = piteratorunpack.CALL'
            '[.SENT = {SLOTS ([NAMED_SENT (KNOWN (POBJECT n_payload))]), NAMED eps}]]',
            'S_bad = S[.TODO = (ITERATOR_UNPACK piteratorunpack_bad "byref") :: ptask_tail*]',
            '~$call_descriptors_valid(S_bad)',
            'piteratorunpack_missing = piteratorunpack[.HOLD = KNOWN PNULL][.SNAPSHOT = eps]',
            'S_missing = S[.TODO = (ITERATOR_UNPACK piteratorunpack_missing "byref") :: ptask_tail*]',
            '~$call_descriptors_valid(S_missing)', *ZERO, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(ITERATOR_UNPACK piteratorunpack_next "next-start") :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_raw)]',
            'piteratorunpack_next.CURRENT = KNOWN PNULL',
            'piteratorunpack_next.KEY = KNOWN PNULL',
            'piteratorunpack_next.HOLD = KNOWN PNULL',
            'piteratorunpack_next.SNAPSHOT = eps', '~piteratorunpack_next.NAMED',
            'piteratorunpack_next.CALL.SENT.SLOTS = '
            '[NAMED_SENT (REFERENCE n_prior), NAMED_SENT (REFERENCE n_fresh)]',
            'piteratorunpack_next.CALL.SENT.NAMED = eps',
            'n_fresh =/= n_raw', 'n_fresh =/= n_prior', 'n_fresh <- S_one.REFCELLS',
            'S_one.STORE[n_raw] = S.STORE[n_raw]',
            'S_one.STORE[n_prior] = S.STORE[n_prior]',
            'S_one.STORE[n_fresh] = DEFINED (POBJECT n_payload)',
            '$node_children(S_one, HCELL n_fresh) = [HOBJECT n_payload]',
            '$heap_owners($heap_graph(S_one), HCELL n_raw) = 2',
            '$heap_owners($heap_graph(S_one), HCELL n_prior) = 1',
            '$heap_owners($heap_graph(S_one), HCELL n_fresh) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 3',
            'S_one.EVENTS = S.EVENTS',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
            'S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
            '$drive(S, 4001) = S_done',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("X|"), OUTPUT $ptascii("V|"), '
            'OUTPUT $ptascii("I|"), OUTPUT $ptascii("BODY|"), OUTPUT $ptascii("ONE|"), '
            'OUTPUT $ptascii("HELD|"), OUTPUT $ptascii("O|"), OUTPUT $ptascii("TWO|"), '
            'OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HCELL n_raw) = 0',
            '$heap_owners($heap_graph(S_done), HCELL n_prior) = 0',
            '$heap_owners($heap_graph(S_done), HCELL n_fresh) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_payload) = 0',
            'n_data <- S_done.DESTRUCTION.CALLED',
            'n_payload <- S_done.DESTRUCTION.CALLED',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        ],
    },
    'reversed-fixed-current-write-preserves-only-current-source-alias': {
        'source': SOURCES['iterator-noninitial-reference-review-reversed-current-alias'],
        'stage': ('S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.NAME = $ptascii("reviewNoninitial04") '
                  '-- if S.TODO = (EMIT z_emit) :: ptask_tail* '
                  '-- if S.RESULT = KNOWN pvalue_text '
                  '-- if $string_bytes(pvalue_text) = ($ptascii("F|"))'),
        'checks': [
            'pcallcontext.ARGC = 2', 'pcallcontext.HOLES = eps',
            'pcallcontext.NAMED = eps', 'pcallcontext.EXTRA = eps',
            'pcallcontext.LINE = 19',
            '$lookup(S.ENV, $ptascii("first")) = (n_current_private)',
            '$lookup(S.ENV, $ptascii("second")) = (n_earlier_private)',
            'n_current_private =/= n_earlier_private',
            'n_current_private <- S.REFCELLS', 'n_earlier_private <- S.REFCELLS',
            'S.STORE[n_current_private] = DEFINED PNULL',
            'S.STORE[n_earlier_private] = DEFINED (POBJECT n_earlier)',
            '$object_name(S, n_earlier) = $ptascii("ReviewNoninitialA04")',
            'S.GLOBALTABLE = (psymboltable_global)',
            '$lookup(psymboltable_global.ENV, $ptascii("alias")) = (n_raw)',
            'n_raw =/= n_current_private', 'n_raw =/= n_earlier_private',
            'n_raw <- S.REFCELLS',
            'S.STORE[n_raw] = DEFINED (POBJECT n_current)',
            '$object_name(S, n_current) = $ptascii("ReviewNoninitialB04")',
            'n_current =/= n_earlier',
            '$node_children(S, HCELL n_raw) = [HOBJECT n_current]',
            '$node_children(S, HCELL n_earlier_private) = [HOBJECT n_earlier]',
            '$heap_owners($heap_graph(S), HCELL n_current_private) = 1',
            '$heap_owners($heap_graph(S), HCELL n_earlier_private) = 1',
            '$heap_owners($heap_graph(S), HCELL n_raw) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_current) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_earlier) = 1',
            'S.DESTRUCTION.CALLED = [n_data]',
            '$object_name(S, n_data) = $ptascii("ReviewNoninitialIterator04")',
            '~((HOBJECT n_data) <- S.ALLOCATIONS)',
            '~(n_current <- S.DESTRUCTION.CALLED)',
            '~(n_earlier <- S.DESTRUCTION.CALLED)', *ADMISSION, *ZERO, *ONE,
            'S_one.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("F|")]',
            'S_one.STORE = S.STORE', *POST,
            'S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
            '$drive(S, 4001) = S_done',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("F|"), OUTPUT $ptascii("A|"), '
            'OUTPUT $ptascii("G|"), OUTPUT $ptascii("HELD|"), OUTPUT $ptascii("B|"), '
            'OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HCELL n_raw) = 0',
            '$heap_owners($heap_graph(S_done), HCELL n_current_private) = 0',
            '$heap_owners($heap_graph(S_done), HCELL n_earlier_private) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_current) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_earlier) = 0',
            'n_data <- S_done.DESTRUCTION.CALLED',
            'n_earlier <- S_done.DESTRUCTION.CALLED',
            'n_current <- S_done.DESTRUCTION.CALLED',
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
