#!/usr/bin/env python3
"""Reached selected method, Iterator cursor, warning, and rejection states."""
import argparse
from pathlib import Path
import fiber_state_review as review
import method_iterator_unpack_sources as sources


ROOT = Path(__file__).resolve().parents[2]
CLEAN_SOURCE = Path(__file__).with_name('method_iterator_unpack_clean.php')
INPUT_BYTES = {path: path.read_bytes() for path in
               (Path(__file__), Path(review.__file__), Path(sources.__file__), CLEAN_SOURCE)}
VALID = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']

CASES = {
    'method-selection-and-borrowed-iterator': {
        'source': sources.CASES['selected-receiver'].decode(),
        'stage': 'S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail* '
                 '-- if punpackcall.FUNCTION = METHOD_TARGET n_old porigin_method',
        'checks': [
            'S.RESULT = VARIABLE ($ptascii("iterator")) z',
            '$unpack_class(S, punpackcall) = (UNPACK_CV)',
            '$lookup(S.ENV, $ptascii("receiver")) = (n_receiver)',
            'S.STORE[n_receiver] = DEFINED (POBJECT n_old)',
            '$lookup(S.ENV, $ptascii("iterator")) = (n_iterator)',
            'S.STORE[n_iterator] = DEFINED (POBJECT n_data)',
            '$iterator_unpack_plain(S, punpackcall)',
            '$target_nodes(punpackcall.FUNCTION) = [HOBJECT n_old]',
            '$heap_owners($heap_graph(S), HOBJECT n_old) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 1',
            '~$iterator_unpack_plain(S, punpackcall[.FUNCTION = METHOD_TARGET n_data porigin_method])',
            *VALID, *ONE,
            'S_one.TODO = (ITERATOR_UNPACK piteratorunpack "rewind-start") :: ptask_tail*',
            'piteratorunpack.CALL = punpackcall',
            'piteratorunpack.INPUT = S.RESULT',
            'piteratorunpack.OBJECT = n_data',
            '$task_nodes(ITERATOR_UNPACK piteratorunpack "rewind-start") = '
            '[HOBJECT n_data, HOBJECT n_old]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_old) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 2',
            '$iterator_unpack_result_valid(S_one, piteratorunpack, "rewind-start")',
            '$call_task_valid(S_one, ITERATOR_UNPACK piteratorunpack "rewind-start")',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'key-rebind-keeps-selected-method': {
        'source': sources.CASES['selected-receiver'].decode(),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "key") :: ptask_tail* '
                 '-- if piteratorunpack.CALL.FUNCTION = METHOD_TARGET n_old porigin_method',
        'checks': [
            '$lookup(S.ENV, $ptascii("receiver")) = (n_receiver)',
            'S.STORE[n_receiver] = DEFINED (POBJECT n_new)',
            'n_old =/= n_new',
            '$target_nodes(piteratorunpack.CALL.FUNCTION) = [HOBJECT n_old]',
            '$heap_owners($heap_graph(S), HOBJECT n_old) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_new) = 1',
            '$iterator_unpack_result_valid(S, piteratorunpack, "key")',
            *VALID, *ONE,
            'S_one.TODO = (ITERATOR_UNPACK piteratorunpack_send "send") :: ptask_tail*',
            'piteratorunpack_send.CALL.FUNCTION = METHOD_TARGET n_old porigin_method',
            'piteratorunpack_send.KEY = KNOWN (PINT 0)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_old) = 1',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'method-warning-uses-declaring-class': {
        'source': sources.CASES['byref-warning'].decode(),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                 '-- if piteratorunpack.CALL.FUNCTION = METHOD_TARGET n_receiver porigin_method',
        'checks': [
            'piteratorunpack.KEY = KNOWN (PINT 0)',
            'piteratorunpack.CURRENT = KNOWN (PINT 5)',
            '$iterator_unpack_warning_target(S, piteratorunpack.CALL.FUNCTION) = '
            '$ptascii("ReferenceReceiver118::take")',
            '$iterator_unpack_warning_message(S, piteratorunpack) = '
            '$ptascii("Cannot pass by-reference argument 1 of ReferenceReceiver118::take() '
            'by unpacking a Traversable, passing by-value instead")',
            *VALID, *ONE,
            'S_one.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack_warned "byref"',
            'perrorcall.MESSAGE = $iterator_unpack_warning_message(S, piteratorunpack)',
            'perrorcall.LINE = 19',
            '$call_task_valid(S_one, ERROR_HANDLER_INVOKE perrorcall)',
            '$call_after_origin(S_one, ERROR_HANDLER_INVOKE perrorcall).ORIGIN = '
            'piteratorunpack.CALL.CALLSITE',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'handler-result-restores-method-site': {
        'source': sources.CASES['byref-warning'].decode(),
        'stage': 'S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail* '
                 '-- if perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack "byref"',
        'checks': [
            '$call_task_valid(S, ERROR_HANDLER_RESULT perrorcall)',
            '$iterator_unpack_warning_resume(perrorcall.RESUME)',
            '$call_after_origin(S, ERROR_HANDLER_RESULT perrorcall).ORIGIN = '
            'piteratorunpack.CALL.CALLSITE',
            *VALID,
        ],
    },
    'handler-cleanup-restores-method-site': {
        'source': INPUT_BYTES[CLEAN_SOURCE].decode(),
        'stage': 'S.TODO = (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail* '
                 '-- if perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack "byref"',
        'checks': [
            'S.DESTRUCTION.CLEANUPS = pdestructioncleanup :: pdestructioncleanup_tail*',
            'pdestructioncleanup.SOURCE = ERROR_HANDLER_RESULT perrorcall',
            '$call_task_valid(S, ERROR_HANDLER_CLEAN perrorcall)',
            '$call_after_origin(S, ERROR_HANDLER_CLEAN perrorcall).DESTRUCTION.CLEANUPS = '
            'pdestructioncleanup_tail*',
            '$call_after_origin(S, ERROR_HANDLER_CLEAN perrorcall).ORIGIN = '
            'piteratorunpack.CALL.CALLSITE',
            *VALID,
        ],
    },
    'invalid-key-precedes-method-entry': {
        'source': sources.CASES['invalid-key'].decode(),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                 '-- if piteratorunpack.CALL.FUNCTION = METHOD_TARGET n_receiver porigin_method',
        'checks': [
            'piteratorunpack.KEY = KNOWN (PBOOL false)',
            'piteratorunpack.CURRENT = KNOWN (PINT 5)',
            'piteratorunpack.CALL.SENT = {SLOTS eps, NAMED eps}',
            '$iterator_unpack_result_valid(S, piteratorunpack, "send")',
            *VALID,
            'S_error = $iterator_unpack_send(S, piteratorunpack, ptask_tail*)',
            'S_error.COMPLETION = THROWN "Error" '
            '($ptascii("Keys must be of type int|string during argument unpacking")) '
            '$unpack_line(S, piteratorunpack.CALL)',
            'S_error.TODO = (ITERATOR_UNPACK piteratorunpack "error") :: ptask_tail*',
            '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
        ],
    },
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    assert not args.case or set(args.case) <= CASES.keys()
    review.ROOT = ROOT
    review.CASES = CASES
    for name in args.case or list(CASES):
        assert review.run([name])
        assert all(path.read_bytes() == data for path, data in INPUT_BYTES.items())
