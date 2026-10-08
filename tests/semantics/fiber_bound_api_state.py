#!/usr/bin/env python3
"""Source-selected bound Fiber API snapshot and named-unpack admission."""
import argparse
import json
from pathlib import Path
import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(__file__).with_name('fiber_bound_api_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCES = {row['id']: row['source'] for row in json.loads(SOURCE_BYTES)}
CASES = {
    'bound-resume-snapshot-and-named-unpack': {
        'source': SOURCES['author-bound-fixed-api-status-unpack'],
        'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
                  '-- if ptask_tail* = (FIBER_CAPTURE_RELEASE n_capture pconfigcall.SITE) :: ptask_after* '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
                  '-- if pconfigcall.SELECTION = (n_capture) '
                  '-- if pconfigcall.OWNER = (n_receiver)'),
        'checks': [
            'S.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
            'pfibercapture.KIND = pconfigcall.KIND',
            'pfibercapture.INPUT = (n_receiver)',
            'pfibercapture.NAME = $ptascii("ReSuMe")',
            '$(n_receiver < n_capture)', '$fiber_capture_live(S, n_capture)',
            '$node_children(S, HOBJECT n_capture) = [HOBJECT n_receiver]',
            '$fiber_capture_owner(pfibercapture, n_capture) = (n_receiver)',
            '$lookup(S.ENV, $ptascii("name")) = (n_name)',
            'S.STORE[n_name] = DEFINED (PSTRING $ptascii("missing"))',
            'pconfigcall.INDEX = 1', 'pconfigcall.NAMED',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (PSTRING $ptascii("R")))]',
            'pconfigcall.PACKS = [pconfigpack]', 'pconfigpack.INDEX = 0',
            'pconfigpack.ITEMS = [ENTRY (KSTRING $ptascii("value")) (DIRECT (PSTRING $ptascii("R")))]',
            '$config_pack_source_valid(S, pconfigcall, pconfigpack)',
            '$config_sent_shape(S, pconfigcall)', '$config_nodes(pconfigcall) = eps',
            '$selected_task_nonce(CONFIG_INVOKE pconfigcall) = eps',
            '$config_selected_valid(S, pconfigcall)', '$config_invoke_valid(S, pconfigcall)',
            '~$fiber_capture_source_valid(S, pfibercapture[.INPUT = eps])',
            '~$fiber_capture_source_valid(S, pfibercapture[.INPUT = (n_capture)])',
            '~$fiber_capture_source_valid(S, pfibercapture[.NAME = $ptascii("isStarted")])',
            'S_future = S[.OBJECTS = $object_set(S.OBJECTS, n_capture, FIBERAPICLOSURE (pfibercapture[.INPUT = (n_capture)]))]',
            '~$fiber_capture_live(S_future, n_capture)',
            'pconfigcall_bad = pconfigcall[.OWNER = (n_capture)]',
            'S_bad = S[.TODO = (CONFIG_INVOKE pconfigcall_bad) :: '
            '(FIBER_CAPTURE_RELEASE n_capture pconfigcall.SITE) :: ptask_after*]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$config_selected_valid(S_bad, pconfigcall_bad)',
            '~$call_descriptors_valid(S_bad)',
            *review.VALID,
            'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
            'S_zero[.COMPLETION = NORMAL] = S',
            'S_one = $drive_steps(S, 1)', 'S_one.COMPLETION = BUDGET',
            'S_one.ACTIVEFIBER = (n_receiver)', 'S_one.FIBERCALLERS = [pfibercaller]',
            'pfibercaller.API.SENT = (PSTRING $ptascii("R"))',
            'pfibercaller.VM.TODO = (FIBER_WAIT pfibercaller.API) :: '
            '(FIBER_CAPTURE_RESULT n_capture pconfigcall false) :: ptask_after*',
            '$fiber_caller_api_nodes(pfibercaller) = eps',
            '$call_descriptors_valid(S_one[.COMPLETION = NORMAL])',
            'S_done = $drive(S, 4000)', *review.DONE,
            'S_done.OBJECTS[n_receiver] = FIBER pfiber_done',
            'pfiber_done.STATUS = FIBER_TERMINATED', 'pfiber_done.VALUE = PINT 23',
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', default=[])
    args = parser.parse_args()
    assert set(args.case) <= CASES.keys()
    review.ROOT = ROOT
    review.CASES = CASES
    review.__file__ = str(Path(__file__).resolve())
    passed = all(review.run([name]) for name in args.case or list(CASES))
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'Bound Fiber source catalog changed during run'
    raise SystemExit(0 if passed else 1)
