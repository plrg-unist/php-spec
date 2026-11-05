#!/usr/bin/env python3
"""The real API error cursor retains public-NaN source and borrowed ownership."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/quiet-public-nan-one-default.php').read_text()
STAGE = (
    'S.TODO = (API_CALLBACK_SEND papiargcursor) :: ptask_tail* '
    '-- if papiargcursor.CALL = API_ERROR perrorcall '
    '-- if perrorcall.RESUME = PROPERTY_PUBLIC_NAN ppropertypublicnan '
    '-- if papiargcursor.INDEX = 0')
CHECKS = [
    'S.CURRENT = eps /\\ S.FRAMES = eps',
    'S.ORIGIN = (ppropertypublicnan.READ.SITE)',
    'ppropertypublicnan.OWNER = 0 /\\ ppropertypublicnan.CALLER = eps',
    'ppropertypublicnan.CELL = eps',
    'ppropertypublicnan.READ.NAME = $ptascii("value")',
    'ppropertypublicnan.FLOAT = 9221120237041090560',
    'ppropertypublicnan.TAIL = ptask_tail*',
    'papiargcursor.SENT = eps /\\ |papiargcursor.VALUES| = 4',
    'papiargcursor.VALUES[0] = PINT 2',
    '$target_nodes(papiargcursor.TARGET) = eps',
    '$property_public_nan_source(S, ppropertypublicnan.READ)',
    '$property_public_nan_descriptor(S, ppropertypublicnan)',
    '$property_public_nan_slot(S, ppropertypublicnan) = (9221120237041090560)',
    '$source_operand_marker(API_CALLBACK_SEND papiargcursor) = API_CALLBACK_SEND papiargcursor',
    '~$source_operand_suffix(S.TODO, perrorcall.RESUME, ptask_tail*)',
    '$property_public_nan_marker(API_CALLBACK_SEND papiargcursor) = perrorcall.RESUME',
    '$property_public_nan_suffix(S.TODO, perrorcall.RESUME, ptask_tail*)',
    '$property_public_nan_valid(S, ppropertypublicnan)',
    '$error_call_valid(S, perrorcall)',
    '$api_cursor_valid(S, papiargcursor)',
    '$call_task_valid(S, API_CALLBACK_SEND papiargcursor)',
    '$task_nodes(perrorcall.RESUME) = eps',
    '$task_nodes(API_CALLBACK_SEND papiargcursor) = eps',
    'n_child = ppropertypublicnan.OBJECT',
    '$lookup(S.ENV, $ptascii("child")) = (n_child_cell)',
    'S.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
    '$lookup(S.ENV, $ptascii("saved")) = (n_saved_cell)',
    'S.STORE[n_saved_cell] = DEFINED (POBJECT n_child)',
    'n_child_cell =/= n_saved_cell',
    '$node_children(S, HOBJECT n_child) = eps',
    '$heap_owners($heap_graph(S), HOBJECT n_child) = 2',
    '$heap_valid($heap_graph(S))',
    '$property_public_nan_marker(ERROR_HANDLER_INVOKE perrorcall) = perrorcall.RESUME',
    '$property_public_nan_marker(ERROR_HANDLER_RESULT perrorcall) = perrorcall.RESUME',
    '$property_public_nan_marker(API_CALLBACK_REF papiargcursor) = perrorcall.RESUME',
    'S_ref = S[.TODO = (API_CALLBACK_REF papiargcursor) :: ptask_tail*]',
    '$property_public_nan_valid(S_ref, ppropertypublicnan)',
    '~$call_task_valid(S_ref, API_CALLBACK_REF papiargcursor)',
    'ppropertypublicnan_owner = ppropertypublicnan[.OWNER = 1]',
    'papiargcursor_owner = papiargcursor[.CALL = API_ERROR perrorcall[.RESUME = PROPERTY_PUBLIC_NAN ppropertypublicnan_owner]]',
    'S_owner = S[.TODO = (API_CALLBACK_SEND papiargcursor_owner) :: ptask_tail*]',
    '~$property_public_nan_valid(S_owner, ppropertypublicnan_owner)',
    '~$api_cursor_valid(S_owner, papiargcursor_owner)',
    'ppropertypublicnan_tail = ppropertypublicnan[.TAIL = (ISSET_RESULT true ppropertypublicnan.READ.LINE) :: ptask_tail*]',
    'papiargcursor_tail = papiargcursor[.CALL = API_ERROR perrorcall[.RESUME = PROPERTY_PUBLIC_NAN ppropertypublicnan_tail]]',
    'S_tail = S[.TODO = (API_CALLBACK_SEND papiargcursor_tail) :: ptask_tail*]',
    '~$property_public_nan_valid(S_tail, ppropertypublicnan_tail)',
    'perrorcall_line = perrorcall[.LINE = $(perrorcall.LINE + 1)]',
    'papiargcursor_line = papiargcursor[.CALL = API_ERROR perrorcall_line]',
    'S_line = S[.TODO = (API_CALLBACK_SEND papiargcursor_line) :: ptask_tail*]',
    '$property_public_nan_valid(S_line, ppropertypublicnan)',
    '~$error_call_valid(S_line, perrorcall_line)',
    '~$api_cursor_valid(S_line, papiargcursor_line)',
    'papiargcursor_other = papiargcursor[.CALL = API_ERROR perrorcall[.RESUME = ISSET_RESULT true ppropertypublicnan.READ.LINE]]',
    '$property_public_nan_marker(API_CALLBACK_SEND papiargcursor_other) = API_CALLBACK_SEND papiargcursor_other',
    '~$property_public_nan_suffix((API_CALLBACK_SEND papiargcursor_other) :: ptask_tail*, perrorcall.RESUME, ptask_tail*)',
    '$property_public_nan_suffix((ISSET_RESULT true ppropertypublicnan.READ.LINE) :: S.TODO, perrorcall.RESUME, ptask_tail*)',
    '~$property_public_nan_suffix([perrorcall.RESUME, ISSET_RESULT true ppropertypublicnan.READ.LINE] ++ ptask_tail* ++ [perrorcall.RESUME] ++ ptask_tail*, perrorcall.RESUME, ptask_tail*)',
    'S_zero = $drive_steps(S, 0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_paused = $drive_steps(S, 1)',
    'S_paused.COMPLETION = BUDGET',
    'S_sent = S_paused[.COMPLETION = NORMAL]',
    'S_sent.TODO = (API_CALLBACK_SEND papiargcursor_sent) :: ptask_tail*',
    'papiargcursor_sent = papiargcursor[.INDEX = 1][.SENT = [KNOWN (PINT 2)]]',
    '$call_task_valid(S_sent, API_CALLBACK_SEND papiargcursor_sent)',
    '$task_nodes(API_CALLBACK_SEND papiargcursor_sent) = eps',
    'S_sent.STORE = S.STORE /\\ S_sent.OBJECTPROPS = S.OBJECTPROPS',
    'S_sent.OBJECTS = S.OBJECTS /\\ S_sent.ALLOCATIONS = S.ALLOCATIONS',
    'S_sent.EVENTS = S.EVENTS /\\ S_sent.GC = S.GC',
    '$heap_owners($heap_graph(S_sent), HOBJECT n_child) = 2',
    'S_done = $drive_steps(S, 4000)',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 4000) = S_done',
    '$drive_steps(S_sent, 4000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {'property-nan-api-cursor': {'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=180) else 1)
