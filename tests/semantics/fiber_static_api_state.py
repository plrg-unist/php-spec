#!/usr/bin/env python3
"""Source-selected static Fiber Closure buffers and unpack certificates."""
import argparse
import json
from pathlib import Path
import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(__file__).with_name('fiber_static_api_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCES = {row['id']: row['source'] for row in json.loads(SOURCE_BYTES)}
COMMON = [
    'pconfigcall.OWNER = (n_capture)', 'pconfigcall.SELECTION = (n_capture)',
    'S.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
    'pfibercapture.KIND = pconfigcall.KIND',
    'pfibercapture.INPUT = eps', '$fiber_capture_live(S, n_capture)',
    '$fiber_capture_source_valid(S, pfibercapture)',
    '$node_children(S, HOBJECT n_capture) = eps',
    '$fiber_capture_config_tag(pconfigcall)',
    '$selected_task_nonce(CONFIG_INVOKE pconfigcall) = eps',
    '$config_selected_valid(S, pconfigcall)', '$config_invoke_valid(S, pconfigcall)',
    'ptask_tail* = (FIBER_CAPTURE_RELEASE n_capture pconfigcall.SITE) :: ptask_after*',
    '$task_nodes(FIBER_CAPTURE_RELEASE n_capture pconfigcall.SITE) = [HOBJECT n_capture]',
    '$config_nodes(pconfigcall) = $named_slots_roots(pconfigcall.SENT)',
    'S.ACTIVEFIBER = (n_fiber)', '$fiber_at(S, n_fiber) = (pfiber)',
    'S.CURRENT = (pcallcontext)', '$fiber_context_valid(S, pcallcontext)',
    'pconfigcall.INDEX = 1', 'pconfigcall.PACKS = [pconfigpack]',
    'pconfigpack.INDEX = 0', '$config_pack_source_valid(S, pconfigcall, pconfigpack)',
    '$config_sent_shape(S, pconfigcall)',
    '~$config_selected_valid(S, pconfigcall[.SELECTION = eps])',
    '~$config_selected_valid(S, pconfigcall[.OWNER = eps])',
    '~$fiber_capture_source_valid(S, pfibercapture[.NAME = $ptascii("missing")])',
    'pconfigcall_bad = pconfigcall[.LINE = 0]',
    'S_bad = S[.TODO = (CONFIG_INVOKE pconfigcall_bad) :: ptask_tail*]',
    '$heap_graph(S_bad) = $heap_graph(S)',
    '~$config_invoke_valid(S_bad, pconfigcall_bad)', '~$call_descriptors_valid(S_bad)',
    'S_duplicate = S[.TODO = (CONFIG_INVOKE pconfigcall) :: (FIBER_CAPTURE_RELEASE n_capture pconfigcall.SITE) :: ptask_tail*]',
    '~$config_selected_valid(S_duplicate, pconfigcall)',
    '~$call_descriptors_valid(S_duplicate)',
    'S_tail = S[.TODO = (CONFIG_INVOKE pconfigcall) :: DISCARD :: ptask_tail*]',
    '$heap_graph(S_tail) = $heap_graph(S)',
    '~$config_selected_valid(S_tail, pconfigcall)',
    '~$call_descriptors_valid(S_tail)',
    *review.VALID,
    'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
    'S_zero[.COMPLETION = NORMAL] = S',
]
EVENTS = ('S_done.EVENTS = [OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), '
          'OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), OUTPUT $ptascii("Closure"), '
          'OUTPUT $ptascii("|"), OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), '
          'OUTPUT $ptascii("W"), OUTPUT $ptascii("|"), OUTPUT $ptascii("R"), '
          'OUTPUT $ptascii("|"), OUTPUT $ptascii("11"), OUTPUT $ptascii("|"), OUTPUT $ptascii("1")]')
CASES = {
    'class-alias-dynamic-casefold-empty-unpack-selection': {
        'source': SOURCES['author-static-alias-casefold-unpack'],
        'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_CURRENT '
                  '-- if $fiber_capture_config_tag(pconfigcall)'),
        'checks': [
            *COMMON, 'pfibercapture.NAME = $ptascii("gEtCURRENT")',
            'pconfigcall.SENT = eps', 'pconfigpack.ITEMS = eps',
            'S.GLOBALTABLE = (psymboltable)',
            '$lookup(psymboltable.ENV, $ptascii("b")) = (n_other_cell)',
            'S.STORE[n_other_cell] = DEFINED (POBJECT n_other)',
            'n_other =/= n_capture', '$fiber_capture_live(S, n_other)',
            'S.OBJECTS[n_other] = FIBERAPICLOSURE pfibercapture_other',
            'pfibercapture_other.KIND = pfibercapture.KIND',
            'pconfigcall_other = pconfigcall[.OWNER = (n_other)][.SELECTION = (n_other)]',
            'S_other = S[.TODO = (CONFIG_INVOKE pconfigcall_other) :: ptask_tail*]',
            '$heap_graph(S_other) = $heap_graph(S)',
            '~$config_selected_valid(S_other, pconfigcall_other)',
            '~$call_descriptors_valid(S_other)',
            'pconfigcall_kind = pconfigcall[.KIND = INTRINSIC_FIBER_SUSPEND]',
            'S_kind = S[.TODO = (CONFIG_INVOKE pconfigcall_kind) :: ptask_tail*]',
            '$heap_graph(S_kind) = $heap_graph(S)',
            '~$config_selected_valid(S_kind, pconfigcall_kind)',
            '~$call_descriptors_valid(S_kind)',
            'S_one = $drive_steps(S, 1)', 'S_one.COMPLETION = BUDGET',
            'S_one.RESULT = KNOWN (POBJECT n_fiber)',
            'S_one.TODO = (FIBER_CAPTURE_RESULT n_capture pconfigcall false) :: ptask_after*',
            '$fiber_capture_result_valid(S_one[.COMPLETION = NORMAL], n_capture, pconfigcall, false)',
            '$task_nodes(FIBER_CAPTURE_RESULT n_capture pconfigcall false) = [HOBJECT n_capture]',
            '~$fiber_capture_result_valid(S_one[.COMPLETION = NORMAL], n_capture, pconfigcall, true)',
            '$call_descriptors_valid(S_one[.COMPLETION = NORMAL])',
            'S_done = $drive(S, 4000)', *review.DONE, EVENTS,
        ],
    },
    'named-unpack-suspend-preserves-selected-closure-and-c-buffer': {
        'source': SOURCES['author-static-alias-casefold-unpack'],
        'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_SUSPEND '
                  '-- if $fiber_capture_config_tag(pconfigcall)'),
        'checks': [
            *COMMON, 'pfibercapture.NAME = $ptascii("suspend")',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (PSTRING $ptascii("W")))]',
            'pconfigpack.ITEMS = [ENTRY (KSTRING $ptascii("value")) (DIRECT (PSTRING $ptascii("W")))]',
            'S_one = $drive_steps(S, 1)', 'S_one.COMPLETION = BUDGET',
            'S_one.ACTIVEFIBER = eps', 'S_one.FIBERCALLERS = eps',
            'S_one.OBJECTS[n_fiber] = FIBER pfiber_parked',
            'pfiber_parked.STATUS = FIBER_SUSPENDED', 'pfiber_parked.VM = (pfibervm)',
            'pfibervm.TODO = (FIBER_CONTINUE pfiberapi) :: (FIBER_CAPTURE_RESULT n_capture pconfigcall false) :: ptask_after*',
            'pfiberapi.OBJECT = n_fiber', 'pfiberapi.SENT = (PSTRING $ptascii("W"))',
            'S_view = $fiber_vm_restore(S_one, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]',
            '$fiber_continue_valid(S_view, pfiberapi)',
            '~$fiber_continue_valid(S_view, pfiberapi[.SENT = (PSTRING $ptascii("forged"))])',
            '~$fiber_continue_valid(S_view, pfiberapi[.SEQUENCE = S_one.FIBERSEQ])',
            '$fiber_vm_valid(S_one[.COMPLETION = NORMAL], pfibervm, (n_fiber), eps)',
            '$call_descriptors_valid(S_one[.COMPLETION = NORMAL])',
            'S_done = $drive(S, 4000)', *review.DONE, EVENTS,
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
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'Static Fiber source catalog changed during run'
    raise SystemExit(0 if passed else 1)
