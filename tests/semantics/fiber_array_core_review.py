#!/usr/bin/env python3
"""Independent RAW-array cache, borrowed receiver and suspended-source checks."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('fiber_array_core_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCES = {row['id']: row['source'] for row in json.loads(SOURCE_BYTES)}
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
FINISH = ['S_done = $drive(S, 4000)', *review.DONE]


def events(*pieces):
    return 'S_done.EVENTS = [' + ', '.join(
        'OUTPUT $ptascii(' + json.dumps(piece) + ')' for piece in pieces) + ']'


def static_vm(name, expression):
    return [
        f'pfibervm_{name} = {expression}',
        f'pfiber_{name} = pfiber_runner[.VM = (pfibervm_{name})]',
        f'S_{name} = S[.OBJECTS = $object_set(S.OBJECTS, n_runner, FIBER pfiber_{name})]',
        f'$heap_graph(S_{name}) = H',
        f'~$fiber_vm_valid(S_{name}, pfibervm_{name}, (n_runner), eps)',
        f'~$fiber_record_valid(S_{name}, n_runner, pfiber_{name})',
        f'~$call_descriptors_valid(S_{name})',
    ]


CASES = {
    'raw-array-ref-cache-borrows-selected-receiver-through-real-wait': {
        'source': SOURCES['peer-fiber-raw-array-reference-members-use-borrowed-frozen-cache'],
        'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_core* '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
                  '-- if ptask_core* = [FIBER_CORE_RESULT n_runner pconfigcall, FIBER_FINISH n_runner]'),
        'checks': [
            'S.ACTIVEFIBER = (n_runner)', 'S.CURRENT = eps', 'S.FRAMES = eps',
            '$fiber_at(S, n_runner) = (pfiber_runner)',
            'pfiber_runner.STATUS = FIBER_RUNNING', 'pfiber_runner.VM = eps',
            'pfiber_runner.RAW = PARRAY n_raw',
            'pfiber_runner.TARGET = (FIBER_ARRAY_TARGET pfiberrawapi)',
            'pfiberrawapi.KIND = INTRINSIC_FIBER_RESUME',
            'pfiberrawapi.NAME = $ptascii("ReSuMe")',
            'pfiberrawapi.INPUT = (n_receiver)',
            'pfiberrawapi.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)), '
            'ENTRY (KINT 1) (DIRECT (PSTRING ($ptascii("ReSuMe"))))]',
            '$entry_lookup(S.ARRAYS[n_raw].ITEMS, KINT 0) = (ALIAS n_receiver_ref)',
            '$entry_lookup(S.ARRAYS[n_raw].ITEMS, KINT 1) = (ALIAS n_method_ref)',
            '$entry_value(S, ALIAS n_receiver_ref) = POBJECT n_other',
            '$entry_value(S, ALIAS n_method_ref) = PSTRING ($ptascii("throw"))',
            'n_other =/= n_receiver', '$fiber_at(S, n_other) = (pfiber_other)',
            'pfiber_other.STATUS = FIBER_INIT',
            '$fiber_at(S, n_receiver) = (pfiber_receiver)',
            'pfiber_receiver.STATUS = FIBER_SUSPENDED',
            'psymboltable_global = $fiber_globals(S)',
            '$lookup(psymboltable_global.ENV, $ptascii("target")) = (n_target_cell)',
            'S.STORE[n_target_cell] = DEFINED (POBJECT n_receiver)',
            '$lookup(psymboltable_global.ENV, $ptascii("pair")) = (n_pair_cell)',
            'S.STORE[n_pair_cell] = DEFINED PNULL',
            'pconfigcall.OWNER = (n_receiver)', 'pconfigcall.SELECTION = (n_runner)',
            'pconfigcall.INDEX = 1', '~pconfigcall.NAMED', 'pconfigcall.PACKS = eps',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (PSTRING ($ptascii("R"))))]',
            'pfiber_runner.ENTRY = ({SLOTS pconfigcall.SENT, NAMED eps})',
            'S.FIBERCALLERS = [pfibercaller_outer]',
            'pfibercaller_outer.OBJECT = n_runner', 'pfibercaller_outer.PREVIOUS = eps',
            'pfibercaller_outer.API.KIND = eps',
            'pfibercaller_outer.API.START = ({SLOTS eps, '
            'NAMED [($ptascii("value"), KNOWN (PSTRING ($ptascii("R"))))]})',
            'pfibercaller_outer.API.SITE = pconfigcall.SITE',
            'pfibercaller_outer.API.LINE = pconfigcall.LINE',
            'pfiberapi_outer = pfibercaller_outer.API',
            'pfibercaller_outer.VM.TODO = (FIBER_WAIT pfiberapi_outer) :: ptask_outer*',
            '$fiber_raw_cached_valid(S, pfiber_runner)',
            '$fiber_raw_receiver_live(S, pfiberrawapi)',
            '$fiber_cache_valid(S, n_runner, pfiber_runner)',
            '$fiber_raw_outer_valid(S, n_runner)',
            '$fiber_core_binding(S, pfiber_runner) = (pconfigcall.OWNER, pconfigcall.SELECTION)',
            '$fiber_capture_config_tag(pconfigcall)',
            '~$config_selected_valid(S, pconfigcall)',
            '$fiber_core_config_valid(S, pconfigcall)', '$config_invoke_valid(S, pconfigcall)',
            '$selected_task_nonce(CONFIG_INVOKE pconfigcall) = eps',
            '$config_nodes(pconfigcall) = eps',
            '$task_nodes(FIBER_CORE_RESULT n_runner pconfigcall) = eps',
            '$target_nodes(FIBER_ARRAY_TARGET pfiberrawapi) = eps',
            '$node_children(S, HOBJECT n_runner) = [HARRAY n_raw]',
            'H = $heap_graph(S)', '$heap_owners(H, HOBJECT n_receiver) = 1',
            '$heap_owners(H, HOBJECT n_runner) = 2', '$heap_owners(H, HARRAY n_raw) = 1',
            'pconfigcall_owner = pconfigcall[.OWNER = (n_other)]',
            'S_owner = S[.TODO = [CONFIG_INVOKE pconfigcall_owner, '
            'FIBER_CORE_RESULT n_runner pconfigcall_owner, FIBER_FINISH n_runner]]',
            '$heap_graph(S_owner) = H', '~$fiber_core_config_valid(S_owner, pconfigcall_owner)',
            '~$call_descriptors_valid(S_owner)',
            'pconfigcall_line = pconfigcall[.LINE = $(pconfigcall.LINE + 1)]',
            'pfiberapi_outer_line = pfiberapi_outer[.LINE = pconfigcall_line.LINE]',
            'pfibercaller_line = pfibercaller_outer[.API = pfiberapi_outer_line]'
            '[.VM.TODO = (FIBER_WAIT pfiberapi_outer_line) :: ptask_outer*]',
            'S_line = S[.TODO = [CONFIG_INVOKE pconfigcall_line, '
            'FIBER_CORE_RESULT n_runner pconfigcall_line, FIBER_FINISH n_runner]]'
            '[.FIBERCALLERS = [pfibercaller_line]]',
            '$heap_graph(S_line) = H', '~$fiber_core_config_valid(S_line, pconfigcall_line)',
            '~$call_descriptors_valid(S_line)',
            'S_missing = S[.TODO = [CONFIG_INVOKE pconfigcall, FIBER_FINISH n_runner]]',
            '$heap_graph(S_missing) = H', '~$fiber_core_config_valid(S_missing, pconfigcall)',
            '~$call_descriptors_valid(S_missing)',
            'S_duplicate = S[.TODO = [CONFIG_INVOKE pconfigcall, '
            'FIBER_CORE_RESULT n_runner pconfigcall, FIBER_CORE_RESULT n_runner pconfigcall, '
            'FIBER_FINISH n_runner]]',
            '$heap_graph(S_duplicate) = H', '~$fiber_core_config_valid(S_duplicate, pconfigcall)',
            '~$call_descriptors_valid(S_duplicate)',
            'pfibercaller_previous = pfibercaller_outer[.PREVIOUS = (n_other)]',
            'S_previous = S[.FIBERCALLERS = [pfibercaller_previous]]',
            '$heap_graph(S_previous) = H', '~$call_descriptors_valid(S_previous)',
            'pfiberapi_outer_sequence = pfibercaller_outer.API[.SEQUENCE = S.FIBERSEQ]',
            'pfibercaller_sequence = pfibercaller_outer[.API = pfiberapi_outer_sequence]'
            '[.VM.TODO = (FIBER_WAIT pfiberapi_outer_sequence) :: ptask_outer*]',
            'S_sequence = S[.FIBERCALLERS = [pfibercaller_sequence]]',
            '$heap_graph(S_sequence) = H', '~$fiber_raw_outer_valid(S_sequence, n_runner)',
            '~$fiber_core_config_valid(S_sequence, pconfigcall)',
            '~$call_descriptors_valid(S_sequence)',
            'S_one = $drive_steps(S, 1)',
            'S_one.COMPLETION = BUDGET',
            'S_one.FIBERCALLERS = [pfibercaller_inner, pfibercaller_outer]',
            'pfibercaller_inner.OBJECT = n_receiver',
            'pfibercaller_inner.PREVIOUS = (n_runner)',
            'pfiberapi = pfibercaller_inner.API',
            'pfiberapi.KIND = (INTRINSIC_FIBER_RESUME)',
            'pfiberapi.OBJECT = n_receiver', 'pfiberapi.START = eps',
            'pfiberapi.SENT = (PSTRING ($ptascii("R")))',
            'pfibercaller_inner.VM.TODO = (FIBER_WAIT pfiberapi) :: ptask_core*',
            '$fiber_caller_api_nodes(pfibercaller_inner) = eps',
            '$heap_owners($heap_graph(S_one), HOBJECT n_receiver) = 1',
            'S_wait = $fiber_vm_restore(S_one, pfibercaller_inner.VM)'
            '[.ACTIVEFIBER = (n_runner)][.FIBERCALLERS = [pfibercaller_outer]]',
            '$fiber_raw_core_call(S_wait, pfiberapi) = (pconfigcall)',
            '$fiber_api_valid(S_wait, pfiberapi)', '$fiber_wait_valid(S_wait, pfiberapi)',
            '$call_descriptors_valid(S_one[.COMPLETION = NORMAL])',
            '$heap_valid($heap_graph(S_one))',
            'pfiberapi_sequence = pfiberapi[.SEQUENCE = S_wait.FIBERSEQ]',
            'S_wait_sequence = S_wait[.TODO = [FIBER_WAIT pfiberapi_sequence, '
            'FIBER_CORE_RESULT n_runner pconfigcall, FIBER_FINISH n_runner]]',
            '$heap_graph(S_wait_sequence) = $heap_graph(S_wait)',
            '$fiber_raw_core_call(S_wait_sequence, pfiberapi_sequence) = eps',
            '~$fiber_api_valid(S_wait_sequence, pfiberapi_sequence)',
            *review.VALID, *ZERO, *FINISH,
            events('Y', '|', 'R', '|', '1', '|', '17', '|', '0', '|', '1'),
        ],
    },
    'raw-static-array-suspended-history-has-no-extra-input-owner': {
        'source': SOURCES['peer-fiber-raw-static-array-keeps-history-across-array-start-and-captured-resume'],
        'stage': ('S.ACTIVEFIBER = eps '
                  '-- if S.TODO = (EMIT z_emit) :: ptask_tail* '
                  '-- if $lookup(S.ENV, $ptascii("runner")) = (n_runner_cell) '
                  '-- if S.STORE[n_runner_cell] = DEFINED (POBJECT n_runner) '
                  '-- if S.OBJECTS[n_runner] = FIBER pfiber_runner '
                  '-- if pfiber_runner.STATUS = FIBER_SUSPENDED '
                  '-- if S.RESULT = KNOWN (PSTRING ($ptascii("V")))'),
        'checks': [
            'S.FIBERCALLERS = eps', 'S.CURRENT = eps', 'S.FRAMES = eps',
            'pfiber_runner.RAW = PARRAY n_raw',
            'pfiber_runner.TARGET = (FIBER_ARRAY_TARGET pfiberrawapi)',
            'pfiberrawapi.KIND = INTRINSIC_FIBER_SUSPEND',
            'pfiberrawapi.NAME = $ptascii("SuSpEnD")',
            'pfiberrawapi.INPUT = (n_input)',
            'pfiberrawapi.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_input)), '
            'ENTRY (KINT 1) (DIRECT (PSTRING ($ptascii("SuSpEnD"))))]',
            '$entry_lookup(S.ARRAYS[n_raw].ITEMS, KINT 0) = (DIRECT (POBJECT n_input))',
            '$fiber_at(S, n_input) = (pfiber_input)', 'pfiber_input.STATUS = FIBER_INIT',
            '$lookup(S.ENV, $ptascii("start")) = (n_start_cell)',
            'S.STORE[n_start_cell] = DEFINED (PARRAY n_start)',
            '$entry_lookup(S.ARRAYS[n_start].ITEMS, KINT 0) = (DIRECT (POBJECT n_runner))',
            '$lookup(S.ENV, $ptascii("resume")) = (n_resume_cell)',
            'S.STORE[n_resume_cell] = DEFINED (POBJECT n_resume)',
            'S.OBJECTS[n_resume] = FIBERAPICLOSURE pfibercapture_resume',
            'pfibercapture_resume.KIND = INTRINSIC_FIBER_RESUME',
            'pfibercapture_resume.INPUT = (n_runner)',
            '$node_children(S, HOBJECT n_resume) = [HOBJECT n_runner]',
            'pfiber_runner.VM = (pfibervm)', '~pfibervm.GLOBAL',
            'pfibervm.CURRENT = eps', 'pfibervm.FRAMES = eps',
            'pfibervm.TODO = (FIBER_CONTINUE pfiberapi) :: '
            '(FIBER_CORE_RESULT n_runner pconfigcall) :: ptask_saved*',
            'ptask_saved* = [FIBER_FINISH n_runner]',
            'pfibervm.ORIGIN = (pconfigcall.SITE)',
            'pconfigcall.KIND = INTRINSIC_FIBER_SUSPEND',
            'pconfigcall.OWNER = (n_runner)', 'pconfigcall.SELECTION = (n_runner)',
            'pconfigcall.INDEX = 1', '~pconfigcall.NAMED', 'pconfigcall.PACKS = eps',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (PSTRING ($ptascii("V"))))]',
            'pfiberapi.OBJECT = n_runner', 'pfiberapi.KIND = (INTRINSIC_FIBER_SUSPEND)',
            'pfiberapi.START = eps', 'pfiberapi.SENT = (PSTRING ($ptascii("V")))',
            'pfiberapi.SITE = pconfigcall.SITE', 'pfiberapi.LINE = pconfigcall.LINE',
            'pfiberapi.SEQUENCE = pfiber_runner.SEQUENCE',
            '$fiber_raw_cached_valid(S, pfiber_runner)',
            '$fiber_cache_valid(S, n_runner, pfiber_runner)',
            '$fiber_record_valid(S, n_runner, pfiber_runner)',
            '$fiber_vm_valid(S, pfibervm, (n_runner), eps)',
            '$target_nodes(FIBER_ARRAY_TARGET pfiberrawapi) = eps',
            '$config_nodes(pconfigcall) = eps',
            '$task_nodes(FIBER_CORE_RESULT n_runner pconfigcall) = eps',
            '$task_nodes(FIBER_CONTINUE pfiberapi) = eps',
            'H = $heap_graph(S)', '$heap_owners(H, HOBJECT n_input) = 1',
            '$heap_owners(H, HARRAY n_raw) = 1', '$heap_owners(H, HOBJECT n_runner) = 3',
            'S_saved = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_runner)]'
            '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
            '$fiber_raw_outer_valid(S_saved, n_runner)',
            '~$fiber_method_site(S_saved, pconfigcall.SITE, eps)',
            '$fiber_capture_call_site(S_saved, pconfigcall.SITE)',
            '$fiber_core_site_valid(S_saved, pconfigcall)',
            '$fiber_core_result_valid(S_saved, n_runner, pconfigcall)',
            '$fiber_core_config_valid(S_saved, pconfigcall)',
            '~$config_selected_valid(S_saved, pconfigcall)',
            '$selected_task_nonce(CONFIG_INVOKE pconfigcall) = eps',
            '$fiber_api_valid(S_saved, pfiberapi)', '$fiber_continue_valid(S_saved, pfiberapi)',
            'pconfigcall_owner = pconfigcall[.OWNER = (n_input)]',
            *static_vm('owner', 'pfibervm[.TODO = [FIBER_CONTINUE pfiberapi, '
                       'FIBER_CORE_RESULT n_runner pconfigcall_owner, FIBER_FINISH n_runner]]'),
            'pconfigcall_selection = pconfigcall[.SELECTION = (n_input)]',
            *static_vm('selection', 'pfibervm[.TODO = [FIBER_CONTINUE pfiberapi, '
                       'FIBER_CORE_RESULT n_runner pconfigcall_selection, FIBER_FINISH n_runner]]'),
            'pconfigcall_line = pconfigcall[.LINE = $(pconfigcall.LINE + 1)]',
            'pfiberapi_line = pfiberapi[.LINE = pconfigcall_line.LINE]',
            *static_vm('line', 'pfibervm[.TODO = [FIBER_CONTINUE pfiberapi_line, '
                       'FIBER_CORE_RESULT n_runner pconfigcall_line, FIBER_FINISH n_runner]]'),
            *static_vm('missing', 'pfibervm[.TODO = [FIBER_CONTINUE pfiberapi, FIBER_FINISH n_runner]]'),
            *static_vm('duplicate', 'pfibervm[.TODO = [FIBER_CONTINUE pfiberapi, '
                       'FIBER_CORE_RESULT n_runner pconfigcall, FIBER_CORE_RESULT n_runner pconfigcall, '
                       'FIBER_FINISH n_runner]]'),
            'pfiberrawapi_input = pfiberrawapi[.INPUT = (n_runner)]',
            'pfiber_input_forged = pfiber_runner[.TARGET = (FIBER_ARRAY_TARGET pfiberrawapi_input)]',
            'S_input = S[.OBJECTS = $object_set(S.OBJECTS, n_runner, FIBER pfiber_input_forged)]',
            '$heap_graph(S_input) = H', '~$fiber_raw_cached_valid(S_input, pfiber_input_forged)',
            '~$fiber_record_valid(S_input, n_runner, pfiber_input_forged)',
            '~$call_descriptors_valid(S_input)',
            *review.VALID, *ZERO, *FINISH,
            events('1', '|', 'V', '|', '1', '|', '1', '|', 'R', '|', '1'),
            '~((HOBJECT n_input) <- S_done.ALLOCATIONS)',
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
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'RAW-array originals changed during run'
    raise SystemExit(0 if passed else 1)
