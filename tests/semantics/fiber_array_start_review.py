#!/usr/bin/env python3
"""Independent array-start selection, receiver lifetime and saved caller checks."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('fiber_array_start_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCES = {row['id']: row['source'] for row in json.loads(SOURCE_BYTES)}
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
FINISH = ['S_done = $drive(S, 4000)', *review.DONE]


def events(*pieces):
    return 'S_done.EVENTS = [' + ', '.join(
        'OUTPUT $ptascii(' + json.dumps(piece) + ')' for piece in pieces) + ']'


def pending_record(name, expression):
    return [
        f'pfiberarray_{name} = {expression}',
        f'S_{name} = S[.TODO = (FIBER_ARGS pfiberstart) :: '
        f'(FIBER_ARRAY_START_RELEASE pfiberarray_{name}) :: ptask_tail*]',
        f'$heap_graph(S_{name}) = H',
        f'~$fiber_array_start_source_valid(S_{name}, pfiberarray_{name})',
        f'~$fiber_start_valid(S_{name}, pfiberstart, false)',
        f'~$call_descriptors_valid(S_{name})',
    ]


CASES = {
    'array-start-last-receiver-keeps-original-named-buffer': {
        'source': SOURCES['peer-fiber-array-start-freezes-members-before-last-receiver-retirement'],
        'stage': ('S.TODO = (FIBER_ARGS pfiberstart) :: ptask_array* '
                  '-- if pfiberstart.INDEX = 2 '
                  '-- if ptask_array* = (FIBER_ARRAY_START_RELEASE pfiberarray) :: ptask_tail*'),
        'checks': [
            'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps',
            'S.CURRENT = eps', 'S.FRAMES = eps',
            'pfiberarray.KIND = INTRINSIC_FIBER_START',
            'pfiberarray.NAME = $ptascii("StArT")',
            'pfiberarray.INPUT = (n_receiver)', 'pfiberstart.OBJECT = n_receiver',
            'pfiberarray.SITE = pfiberstart.SITE', 'pfiberarray.LINE = pfiberstart.LINE',
            'n_callback = pfiberarray.ARRAY',
            'pfiberarray.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)), '
            'ENTRY (KINT 1) (DIRECT (PSTRING ($ptascii("StArT"))))]',
            'pfiberstart.SENT.SLOTS = eps',
            'pfiberstart.SENT.NAMED = [($ptascii("value"), KNOWN (PSTRING ($ptascii("7")))), '
            '($ptascii("extra"), KNOWN (PSTRING ($ptascii("X"))))]',
            '$entry_lookup(S.ARRAYS[n_callback].ITEMS, KINT 0) = (ALIAS n_receiver_cell)',
            '$entry_lookup(S.ARRAYS[n_callback].ITEMS, KINT 1) = (ALIAS n_method_cell)',
            '$entry_value(S, ALIAS n_receiver_cell) = POBJECT n_other',
            '$entry_value(S, ALIAS n_method_cell) = PSTRING ($ptascii("resume"))',
            'n_other =/= n_receiver', '$fiber_at(S, n_other) = (pfiber_other)',
            'pfiber_other.STATUS = FIBER_INIT',
            '$fiber_at(S, n_receiver) = (pfiber_receiver)',
            'pfiber_receiver.STATUS = FIBER_INIT', 'pfiber_receiver.READY',
            'psymboltable_global = $fiber_globals(S)',
            '$lookup(psymboltable_global.ENV, $ptascii("target")) = (n_target_cell)',
            'S.STORE[n_target_cell] = DEFINED PNULL',
            '$lookup(psymboltable_global.ENV, $ptascii("pair")) = (n_pair_cell)',
            'S.STORE[n_pair_cell] = DEFINED PNULL',
            '~((HARRAY n_callback) <- S.ALLOCATIONS)',
            'H = $heap_graph(S)', '$heap_owners(H, HARRAY n_callback) = 0',
            '$heap_owners(H, HOBJECT n_receiver) = 1',
            '$task_nodes(FIBER_ARGS pfiberstart) = [HOBJECT n_receiver]',
            '$task_nodes(FIBER_ARRAY_START_RELEASE pfiberarray) = eps',
            '$fiber_array_start_source_valid(S, pfiberarray)',
            '$fiber_array_start_matches(pfiberarray, pfiberstart)',
            '$fiber_array_start_pair(S.TODO, pfiberstart) = (pfiberarray)',
            '$fiber_array_count(S.TODO, pfiberarray.SITE) = 1',
            '$fiber_array_start_buffer_valid(S, pfiberarray, pfiberstart)',
            '$fiber_array_start_release_valid(S, pfiberarray)',
            '$fiber_array_start_pending(S, pfiberstart)',
            '$fiber_start_valid(S, pfiberstart, false)',
            '~$fiber_start_valid(S, pfiberstart, true)',
            'n_beyond = |S.ARRAYS|',
            *pending_record('arena', 'pfiberarray[.ARRAY = n_beyond]'),
            *pending_record('init', 'pfiberarray[.INIT = $(pfiberarray.INIT + 1)]'),
            *pending_record('input', 'pfiberarray[.INPUT = (n_other)]'),
            *pending_record('name', 'pfiberarray[.NAME = $ptascii("resume")]'),
            'pfiberstart_line = pfiberstart[.LINE = $(pfiberstart.LINE + 1)]',
            'pfiberarray_line = pfiberarray[.LINE = pfiberstart_line.LINE]',
            'S_line = S[.TODO = (FIBER_ARGS pfiberstart_line) :: '
            '(FIBER_ARRAY_START_RELEASE pfiberarray_line) :: ptask_tail*]',
            '$heap_graph(S_line) = H',
            '~$fiber_array_start_source_valid(S_line, pfiberarray_line)',
            '~$fiber_start_valid(S_line, pfiberstart_line, false)',
            '~$call_descriptors_valid(S_line)',
            'S_missing = S[.TODO = (FIBER_ARGS pfiberstart) :: ptask_tail*]',
            '$heap_graph(S_missing) = H',
            '~$fiber_start_valid(S_missing, pfiberstart, false)',
            '~$call_descriptors_valid(S_missing)',
            'S_duplicate = S[.TODO = (FIBER_ARGS pfiberstart) :: '
            '(FIBER_ARRAY_START_RELEASE pfiberarray) :: '
            '(FIBER_ARRAY_START_RELEASE pfiberarray) :: ptask_tail*]',
            '$heap_graph(S_duplicate) = H',
            '$fiber_array_count(S_duplicate.TODO, pfiberarray.SITE) = 2',
            '~$fiber_start_valid(S_duplicate, pfiberstart, false)',
            '~$call_descriptors_valid(S_duplicate)',
            'pfiberstart_index = pfiberstart[.INDEX = 3]',
            'S_index = S[.TODO = (FIBER_ARGS pfiberstart_index) :: '
            '(FIBER_ARRAY_START_RELEASE pfiberarray) :: ptask_tail*]',
            '$heap_graph(S_index) = H',
            '~$fiber_start_valid(S_index, pfiberstart_index, false)',
            '~$call_descriptors_valid(S_index)',
            *review.VALID, *ZERO,
            'S_one = $drive_steps(S, 1)', 'S_one.COMPLETION = BUDGET',
            'S_one.ACTIVEFIBER = (n_receiver)',
            'S_one.TODO = (FIBER_ENTER n_receiver pnamedargs) :: ptask_finish*',
            'ptask_finish* = [FIBER_FINISH n_receiver]',
            'pnamedargs = pfiberstart.SENT',
            'S_one.FIBERCALLERS = [pfibercaller]',
            'pfibercaller.OBJECT = n_receiver', 'pfibercaller.PREVIOUS = eps',
            'pfiberapi = pfibercaller.API',
            'pfiberapi.OBJECT = n_receiver', 'pfiberapi.KIND = eps',
            'pfiberapi.START = (pfiberstart.SENT)', 'pfiberapi.SENT = eps',
            'pfibercaller.VM.TODO = (FIBER_WAIT pfiberapi) :: '
            '(FIBER_ARRAY_START_RESULT pfiberarray pfiberstart) :: ptask_tail*',
            '$task_nodes(FIBER_ARRAY_START_RESULT pfiberarray pfiberstart) = eps',
            '$fiber_api_nodes(pfiberapi) = [HOBJECT n_receiver]',
            '$fiber_caller_api_nodes(pfibercaller) = [HOBJECT n_receiver]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_receiver) = 1',
            '$call_descriptors_valid(S_one[.COMPLETION = NORMAL])',
            '$heap_valid($heap_graph(S_one))',
            'S_wait = $fiber_vm_restore(S_one[.COMPLETION = NORMAL], pfibercaller.VM)'
            '[.ACTIVEFIBER = eps][.FIBERCALLERS = eps]',
            '$fiber_array_start_result_valid(S_wait, pfiberarray, pfiberstart)',
            '$fiber_api_valid(S_wait, pfiberapi)', '$fiber_wait_valid(S_wait, pfiberapi)',
            *FINISH,
            events('1', '|', '7', '|', 'D', '|', 'X', '|', '1', '|',
                   'F|', 'Y', '|', '1', '|', '0'),
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_done), HOBJECT n_receiver) = 0',
            '$fiber_array_start_source_valid(S_done, pfiberarray)',
        ],
    },
    'array-start-nested-wait-authenticates-real-parent-and-source': {
        'source': SOURCES['peer-fiber-array-start-nested-parent-and-repeat-error-trace'],
        'stage': ('S.TODO = (FIBER_ENTER n_receiver pnamedargs) :: ptask_finish* '
                  '-- if ptask_finish* = [FIBER_FINISH n_receiver] '
                  '-- if S.FIBERCALLERS = [pfibercaller, pfibercaller_outer] '
                  '-- if pfiberapi = pfibercaller.API '
                  '-- if pfibercaller.VM.TODO = (FIBER_WAIT pfiberapi) :: '
                  '(FIBER_ARRAY_START_RESULT pfiberarray pfiberstart) :: ptask_saved*'),
        'checks': [
            'S.ACTIVEFIBER = (n_receiver)', 'S.CURRENT = eps', 'S.FRAMES = eps',
            'pfibercaller.OBJECT = n_receiver', 'pfibercaller.PREVIOUS = (n_parent)',
            '~pfibercaller.VM.GLOBAL',
            'pfibercaller_outer.OBJECT = n_parent', 'pfibercaller_outer.PREVIOUS = eps',
            'pfibercaller_outer.VM.GLOBAL', 'pfibercaller_outer.API.KIND = eps',
            'n_parent =/= n_receiver', 'pfiberstart.OBJECT = n_receiver',
            'pfiberstart.INDEX = 2', 'pfiberstart.SENT = pnamedargs',
            'pnamedargs.SLOTS = eps',
            'pnamedargs.NAMED = [($ptascii("value"), KNOWN (PSTRING ($ptascii("V")))), '
            '($ptascii("extra"), KNOWN (PSTRING ($ptascii("N"))))]',
            'pfiberarray.KIND = INTRINSIC_FIBER_START',
            'pfiberarray.NAME = $ptascii("start")', 'pfiberarray.INPUT = (n_receiver)',
            'pfiberarray.SITE = pfiberstart.SITE', 'pfiberarray.LINE = pfiberstart.LINE',
            'n_callback = pfiberarray.ARRAY',
            'pfiberarray.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)), '
            'ENTRY (KINT 1) (DIRECT (PSTRING ($ptascii("start"))))]',
            'pfiberapi.OBJECT = n_receiver', 'pfiberapi.KIND = eps',
            'pfiberapi.START = (pnamedargs)', 'pfiberapi.SENT = eps',
            'pfiberapi.SITE = pfiberstart.SITE', 'pfiberapi.LINE = pfiberstart.LINE',
            '$fiber_at(S, n_receiver) = (pfiber_receiver)',
            'pfiber_receiver.STATUS = FIBER_RUNNING',
            'pfiber_receiver.ENTRY = (pnamedargs)',
            'S_wait = $fiber_vm_restore(S, pfibercaller.VM)'
            '[.ACTIVEFIBER = (n_parent)][.FIBERCALLERS = [pfibercaller_outer]]',
            '$fiber_array_start_source_valid(S_wait, pfiberarray)',
            '$fiber_array_start_result_valid(S_wait, pfiberarray, pfiberstart)',
            '$fiber_api_valid(S_wait, pfiberapi)', '$fiber_wait_valid(S_wait, pfiberapi)',
            '$fiber_vm_valid(S, pfibercaller.VM, (n_parent), [pfibercaller_outer])',
            '$fiber_callers_valid(S, (n_receiver), S.FIBERCALLERS, eps)',
            '$task_nodes(FIBER_ARRAY_START_RESULT pfiberarray pfiberstart) = eps',
            '$task_nodes(FIBER_WAIT pfiberapi) = eps',
            '$fiber_api_nodes(pfiberapi) = [HOBJECT n_receiver]',
            '$fiber_caller_api_nodes(pfibercaller) = [HOBJECT n_receiver]',
            'psymboltable_global = $fiber_globals(S)',
            '$lookup(psymboltable_global.ENV, $ptascii("target")) = (n_target_cell)',
            'S.STORE[n_target_cell] = DEFINED (POBJECT n_receiver)',
            '$lookup(psymboltable_global.ENV, $ptascii("pair")) = (n_pair_cell)',
            'S.STORE[n_pair_cell] = DEFINED (PARRAY n_callback)',
            '$node_children(S, HCELL n_target_cell) = [HOBJECT n_receiver]',
            '$node_children(S, HARRAY n_callback) = [HOBJECT n_receiver]',
            'H = $heap_graph(S)', '$heap_owners(H, HOBJECT n_receiver) = 3',
            '$heap_owners(H, HOBJECT n_parent) = 2',
            '$fiber_caller_api_trace(S_wait, pfiberapi) = [ptraceframe]',
            'ptraceframe.FUNCTION = $ptascii("start")',
            'ptraceframe.FILE = $call_sourcefile(S.FILES, pfiberstart.SITE)',
            'ptraceframe.LINE = pfiberstart.LINE',
            'ptraceframe.TYPE = ($ptascii("->"))',
            'ptraceframe.ARGS = [(KSTRING ($ptascii("value")), PSTRING ($ptascii("V"))), '
            '(KSTRING ($ptascii("extra")), PSTRING ($ptascii("N")))]',
            'pfiberarray_input = pfiberarray[.INPUT = (n_parent)]',
            'pfibercaller_input = pfibercaller[.VM.TODO = (FIBER_WAIT pfiberapi) :: '
            '(FIBER_ARRAY_START_RESULT pfiberarray_input pfiberstart) :: ptask_saved*]',
            'S_input = S[.FIBERCALLERS = [pfibercaller_input, pfibercaller_outer]]',
            '$heap_graph(S_input) = H',
            '~$fiber_array_start_source_valid(S_input, pfiberarray_input)',
            '~$call_descriptors_valid(S_input)',
            'pfiberstart_line = pfiberstart[.LINE = $(pfiberstart.LINE + 1)]',
            'pfiberarray_line = pfiberarray[.LINE = pfiberstart_line.LINE]',
            'pfiberapi_line = pfiberapi[.LINE = pfiberstart_line.LINE]',
            'pfibercaller_line = pfibercaller[.API = pfiberapi_line]'
            '[.VM.TODO = (FIBER_WAIT pfiberapi_line) :: '
            '(FIBER_ARRAY_START_RESULT pfiberarray_line pfiberstart_line) :: ptask_saved*]',
            'S_line = S[.FIBERCALLERS = [pfibercaller_line, pfibercaller_outer]]',
            '$heap_graph(S_line) = H', '~$call_descriptors_valid(S_line)',
            'S_wait_line = $fiber_vm_restore(S_line, pfibercaller_line.VM)'
            '[.ACTIVEFIBER = (n_parent)][.FIBERCALLERS = [pfibercaller_outer]]',
            '~$fiber_array_start_result_valid(S_wait_line, pfiberarray_line, pfiberstart_line)',
            '~$fiber_api_valid(S_wait_line, pfiberapi_line)',
            'pfibercaller_missing = pfibercaller[.VM.TODO = '
            '(FIBER_WAIT pfiberapi) :: ptask_saved*]',
            'S_missing = S[.FIBERCALLERS = [pfibercaller_missing, pfibercaller_outer]]',
            '$heap_graph(S_missing) = H', '~$call_descriptors_valid(S_missing)',
            'S_wait_missing = $fiber_vm_restore(S_missing, pfibercaller_missing.VM)'
            '[.ACTIVEFIBER = (n_parent)][.FIBERCALLERS = [pfibercaller_outer]]',
            '~$fiber_api_valid(S_wait_missing, pfiberapi)',
            'pfibercaller_duplicate = pfibercaller[.VM.TODO = (FIBER_WAIT pfiberapi) :: '
            '(FIBER_ARRAY_START_RESULT pfiberarray pfiberstart) :: '
            '(FIBER_ARRAY_START_RESULT pfiberarray pfiberstart) :: ptask_saved*]',
            'S_duplicate = S[.FIBERCALLERS = [pfibercaller_duplicate, pfibercaller_outer]]',
            '$heap_graph(S_duplicate) = H', '~$call_descriptors_valid(S_duplicate)',
            'pfiberapi_buffer = pfiberapi[.START = ({SLOTS eps, NAMED eps})]',
            'S_wait_buffer = S_wait[.TODO = (FIBER_WAIT pfiberapi_buffer) :: '
            '(FIBER_ARRAY_START_RESULT pfiberarray pfiberstart) :: ptask_saved*]',
            '$heap_graph(S_wait_buffer) = $heap_graph(S_wait)',
            '~$fiber_api_valid(S_wait_buffer, pfiberapi_buffer)',
            'pfiberapi_sequence = pfiberapi[.SEQUENCE = S.FIBERSEQ]',
            'S_wait_sequence = S_wait[.TODO = (FIBER_WAIT pfiberapi_sequence) :: '
            '(FIBER_ARRAY_START_RESULT pfiberarray pfiberstart) :: ptask_saved*]',
            '$heap_graph(S_wait_sequence) = $heap_graph(S_wait)',
            '~$fiber_api_valid(S_wait_sequence, pfiberapi_sequence)',
            'pfibercaller_previous = pfibercaller[.PREVIOUS = (n_receiver)]',
            'S_previous = S[.FIBERCALLERS = [pfibercaller_previous, pfibercaller_outer]]',
            '$heap_graph(S_previous) = H', '~$call_descriptors_valid(S_previous)',
            *review.VALID, *ZERO, *FINISH,
            events('P|', 'V', '|', 'N', '|', '1', '|', '1', '|', '17', '|', '19', '|',
                   'A|', 'E|', 'Cannot start a fiber that has already been started', '|',
                   'start', '.', '1', '1', '|', 'END'),
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=CASES)
    args = parser.parse_args()
    review.ROOT = ROOT
    review.CASES = CASES
    review.__file__ = str(Path(__file__).resolve())
    passed = review.run(args.case or list(CASES))
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'Array-start originals changed during run'
    raise SystemExit(0 if passed else 1)
