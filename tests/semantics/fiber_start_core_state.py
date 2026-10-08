#!/usr/bin/env python3
"""Genuine pre-handler capture and copied named buffer in a nested C-root chain."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('fiber_start_core_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCE = next(row['source'] for row in json.loads(SOURCE_BYTES)
              if row['id'] == 'author-bound-start-core-double-callback-buffer-chain')

CASES = {
    'bound-start-core-preinvoke-keeps-cache-and-copied-named-buffer': {
        'source': SOURCE,
        'stage': ('S.TODO = (FIBER_START_CORE_INVOKE n_outer n_capture pfiberstart) :: '
                  '(FIBER_START_CORE_RESULT n_outer n_capture pfiberstart) :: ptask_tail* '
                  '-- if S.FIBERCALLERS = [pfibercaller]'),
        'checks': [
            'ptask_tail* = [FIBER_FINISH n_outer]',
            'S.ACTIVEFIBER = (n_outer)', 'S.CURRENT = eps', 'S.FRAMES = eps',
            'S.ORIGIN = (pfiberstart.SITE)',
            '$fiber_at(S, n_outer) = (pfiber_outer)',
            'pfiber_outer.RAW = POBJECT n_capture',
            'pfiber_outer.TARGET = (FIBER_API_TARGET n_capture)',
            'pfiber_outer.ENTRY = (pfiberstart.SENT)',
            'pfiber_outer.STATUS = FIBER_RUNNING',
            'S.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
            'pfibercapture.KIND = INTRINSIC_FIBER_START',
            'pfibercapture.INPUT = (n_middle)',
            'pfiberstart.OBJECT = n_middle', 'pfiberstart.INDEX = 1',
            'pfiberstart.SENT.SLOTS = eps',
            'pfiberstart.SENT.NAMED = [($ptascii("payload"), KNOWN (POBJECT n_payload))]',
            'pfibercaller.OBJECT = n_outer', 'pfibercaller.PREVIOUS = eps',
            'pfibercaller.API.OBJECT = n_outer',
            'pfibercaller.API.START = (pfiberstart.SENT)',
            'pfibercaller.API.SITE = pfiberstart.SITE',
            'pfibercaller.API.LINE = pfiberstart.LINE',
            '$fiber_start_core_actor(S)', '$fiber_start_core_live(S, n_capture)',
            '~$fiber_capture_core_live(S, n_capture)',
            '$fiber_core_callback_kind(S, pfiber_outer) = eps',
            '$fiber_callback_resolution(S, POBJECT n_capture) = HANDLERRESOLVED (FIBER_API_TARGET n_capture)',
            '$fiber_start_core_result_valid(S, n_outer, n_capture, pfiberstart)',
            '$call_task_valid(S, FIBER_START_CORE_INVOKE n_outer n_capture pfiberstart)',
            '$task_nodes(FIBER_START_CORE_INVOKE n_outer n_capture pfiberstart) = [HOBJECT n_payload]',
            '$task_nodes(FIBER_START_CORE_RESULT n_outer n_capture pfiberstart) = [HOBJECT n_capture]',
            '$fiber_at(S, n_middle) = (pfiber_middle)',
            'pfiber_middle.RAW = POBJECT n_inner_capture',
            'S.OBJECTS[n_inner_capture] = FIBERAPICLOSURE pfibercapture_inner',
            'pfibercapture_inner.INPUT = (n_leaf)',
            '$node_children(S, HOBJECT n_capture) = [HOBJECT n_middle]',
            '$node_children(S, HOBJECT n_inner_capture) = [HOBJECT n_leaf]',
            'H = $heap_graph(S)', '$heap_owners(H, HOBJECT n_capture) = 2',
            '$heap_owners(H, HOBJECT n_middle) = 2',
            '$heap_owners(H, HOBJECT n_outer) = 2',
            '$heap_owners(H, HOBJECT n_payload) = 2', *review.VALID,
            'S_cache = $fiber_put(S, n_outer, pfiber_outer[.TARGET = (FIBER_API_TARGET n_inner_capture)])',
            '$heap_graph(S_cache) = H',
            '~$fiber_start_core_result_valid(S_cache, n_outer, n_capture, pfiberstart)',
            '~$call_descriptors_valid(S_cache)',
            'pfiberstart_receiver = pfiberstart[.OBJECT = n_leaf]',
            'S_receiver = S[.TODO = [FIBER_START_CORE_INVOKE n_outer n_capture pfiberstart_receiver, FIBER_START_CORE_RESULT n_outer n_capture pfiberstart_receiver, FIBER_FINISH n_outer]]',
            '$heap_graph(S_receiver) = H',
            '~$fiber_start_core_result_valid(S_receiver, n_outer, n_capture, pfiberstart_receiver)',
            '~$call_descriptors_valid(S_receiver)',
            'pfiberstart_line = pfiberstart[.LINE = $(pfiberstart.LINE + 1)]',
            'S_line = S[.TODO = [FIBER_START_CORE_INVOKE n_outer n_capture pfiberstart_line, FIBER_START_CORE_RESULT n_outer n_capture pfiberstart_line, FIBER_FINISH n_outer]]',
            '$heap_graph(S_line) = H',
            '~$fiber_start_core_result_valid(S_line, n_outer, n_capture, pfiberstart_line)',
            '~$call_descriptors_valid(S_line)',
            'pnamedargs_forged = pfiberstart.SENT[.NAMED = [($ptascii("other"), KNOWN (POBJECT n_payload))]]',
            'pfiberstart_buffer = pfiberstart[.SENT = pnamedargs_forged]',
            'S_buffer = $fiber_put(S[.TODO = [FIBER_START_CORE_INVOKE n_outer n_capture pfiberstart_buffer, FIBER_START_CORE_RESULT n_outer n_capture pfiberstart_buffer, FIBER_FINISH n_outer]], n_outer, pfiber_outer[.ENTRY = (pnamedargs_forged)])',
            '$heap_graph(S_buffer) = H',
            '~$fiber_start_core_result_valid(S_buffer, n_outer, n_capture, pfiberstart_buffer)',
            '~$call_descriptors_valid(S_buffer)',
            'S_extra = S[.TODO = [FIBER_START_CORE_INVOKE n_outer n_capture pfiberstart, FIBER_START_CORE_RESULT n_outer n_capture pfiberstart, ECHO_RESULT, FIBER_FINISH n_outer]]',
            '$heap_graph(S_extra) = H',
            '~$fiber_start_core_result_valid(S_extra, n_outer, n_capture, pfiberstart)',
            '~$call_descriptors_valid(S_extra)',
            'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
            'S_zero[.COMPLETION = NORMAL] = S',
            'S_step = $drive_steps(S, 1)', 'S_step.COMPLETION = BUDGET',
            'S_one = S_step[.COMPLETION = NORMAL]',
            'S_one.ACTIVEFIBER = (n_middle)',
            'S_one.FIBERCALLERS = [pfibercaller_inner, pfibercaller]',
            'pfibercaller_inner.PREVIOUS = (n_outer)',
            'pfibercaller_inner.API.START = (pfiberstart.SENT)',
            '$fiber_caller_api_nodes(pfibercaller_inner) = [HOBJECT n_payload]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 2',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
            'S_wait = $fiber_vm_restore(S_one, pfibercaller_inner.VM)[.ACTIVEFIBER = (n_outer)][.FIBERCALLERS = [pfibercaller]]',
            '$fiber_start_core_wait_valid(S_wait, pfibercaller_inner.API)',
            '$fiber_api_valid(S_wait, pfibercaller_inner.API)',
            'S_done = $drive(S_one, 4000)', *review.DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("L"), OUTPUT $ptascii("7"), OUTPUT $ptascii("|"), OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), OUTPUT $ptascii("Y"), OUTPUT $ptascii("|"), OUTPUT $ptascii("D|"), OUTPUT $ptascii("23")]',
            '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_inner_capture) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_payload) <- S_done.ALLOCATIONS)',
        ],
    },
}

if __name__ == '__main__':
    review.ROOT = ROOT
    review.CASES = CASES
    review.__file__ = str(Path(__file__).resolve())
    passed = review.run(list(CASES))
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'Start C-root catalog changed during run'
    raise SystemExit(0 if passed else 1)
