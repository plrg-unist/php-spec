#!/usr/bin/env python3
"""Independent array-FCC conversion and last-RAW constructor ownership checks."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('fiber_array_fcc_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCES = {row['id']: row['source'] for row in json.loads(SOURCE_BYTES)}
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
FINISH = ['S_done = $drive(S, 4000)', *review.DONE]


def events(*pieces):
    return 'S_done.EVENTS = [' + ', '.join('OUTPUT $ptascii(' + json.dumps(x) + ')' for x in pieces) + ']'


def changed_convert(name, expression):
    return [
        f'pfiberarray_{name} = {expression}',
        f'S_{name} = S[.TODO = (FIBER_ARRAY_CONVERT pfiberarray_{name}) :: ptask_tail*]',
        f'$heap_graph(S_{name}) = H',
        f'~$fiber_array_capture_source_valid(S_{name}, pfiberarray_{name})',
        f'~$fiber_array_convert_valid(S_{name}, pfiberarray_{name})',
        f'~$call_descriptors_valid(S_{name})',
    ]


def changed_witness(name, expression):
    return [
        f'pfiberarray_{name} = {expression}',
        f'pfibercapture_{name} = pfibercapture[.ARRAY = (pfiberarray_{name})]',
        f'S_{name} = S[.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture_{name}]',
        f'$heap_graph(S_{name}) = H',
        f'~$fiber_capture_source_valid(S_{name}, pfibercapture_{name})',
        f'~$fiber_capture_live(S_{name}, n_capture)',
        f'~$fiber_core_config_valid(S_{name}, pconfigcall)',
        f'~$call_descriptors_valid(S_{name})',
    ]


CASES = {
    'array-fcc-convert-transfers-one-bound-owner-to-closure': {
        'source': SOURCES['peer-fiber-array-fcc-freezes-reference-members-and-clone'],
        'stage': ('S.TODO = (FIBER_ARRAY_CONVERT pfiberarray) :: ptask_tail* '
                  '-- if pfiberarray.KIND = INTRINSIC_FIBER_RESUME'),
        'checks': [
            'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps',
            'S.ORIGIN = (pfiberarray.SITE)', 'S.RESULT = KNOWN PNULL',
            'pfiberarray.NAME = $ptascii("ReSuMe")', 'pfiberarray.INPUT = (n_receiver)',
            'n_callback = pfiberarray.ARRAY',
            'pfiberarray.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)), '
            'ENTRY (KINT 1) (DIRECT (PSTRING ($ptascii("ReSuMe"))))]',
            '$entry_lookup(S.ARRAYS[n_callback].ITEMS, KINT 0) = (ALIAS n_receiver_cell)',
            '$entry_lookup(S.ARRAYS[n_callback].ITEMS, KINT 1) = (ALIAS n_method_cell)',
            '$entry_value(S, ALIAS n_receiver_cell) = POBJECT n_receiver',
            '$entry_value(S, ALIAS n_method_cell) = PSTRING ($ptascii("ReSuMe"))',
            '$lookup(S.ENV, $ptascii("target")) = (n_target_cell)',
            '$node_children(S, HCELL n_target_cell) = [HOBJECT n_receiver]',
            '$node_children(S, HCELL n_receiver_cell) = [HOBJECT n_receiver]',
            '(HARRAY n_callback) <- S.ALLOCATIONS',
            '$fiber_at(S, n_receiver) = (pfiber_receiver)',
            'pfiber_receiver.STATUS = FIBER_SUSPENDED',
            '$origin_node(S.SOURCES, pfiberarray.SITE) = '
            '(NExprFuncCall expression (SEQUENCE phpType7*) metadata)',
            '$ppcall_dynamic(expression)', '$ppfirstclass(phpType7*)',
            '$firstclass_evaluated(S, pfiberarray.SITE)',
            'pfiberarray.INIT = $dynamic_init_line(S, pfiberarray.SITE)',
            '$call_line_valid(S, (pfiberarray.SITE), pfiberarray.LINE)',
            '$fiber_array_capture_source_valid(S, pfiberarray)',
            '~$fiber_array_source_valid(S, pfiberarray)',
            '$fiber_array_convert_valid(S, pfiberarray)',
            '$call_task_valid(S, FIBER_ARRAY_CONVERT pfiberarray)',
            '$task_nodes(FIBER_ARRAY_CONVERT pfiberarray) = [HOBJECT n_receiver]',
            'H = $heap_graph(S)', '$heap_owners(H, HOBJECT n_receiver) = 3',
            '$heap_owners(H, HARRAY n_callback) = 1',
            'n_beyond = |S.ARRAYS|',
            *changed_convert('arena', 'pfiberarray[.ARRAY = n_beyond]'),
            *changed_convert('init', 'pfiberarray[.INIT = $(pfiberarray.INIT + 1)]'),
            *changed_convert('line', 'pfiberarray[.LINE = $(pfiberarray.LINE + 1)]'),
            *changed_convert('name', 'pfiberarray[.NAME = $ptascii("throw")]'),
            *changed_convert('members', 'pfiberarray[.ITEMS = '
                             '[ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)), '
                             'ENTRY (KINT 1) (DIRECT (PSTRING ($ptascii("throw"))))]]'),
            'S_duplicate = S[.TODO = (FIBER_ARRAY_CONVERT pfiberarray) :: '
            '(FIBER_ARRAY_CONVERT pfiberarray) :: ptask_tail*]',
            '$heap_owners($heap_graph(S_duplicate), HOBJECT n_receiver) = 4',
            '~$fiber_array_convert_valid(S_duplicate, pfiberarray)',
            '~$call_task_valid(S_duplicate, FIBER_ARRAY_CONVERT pfiberarray)',
            '~$call_descriptors_valid(S_duplicate)',
            *review.VALID, *ZERO,
            'n_capture = |S.OBJECTS|', 'S_one = $drive_steps(S, 1)',
            'S_one.COMPLETION = BUDGET', 'S_one.TODO = ptask_tail*',
            'S_one.RESULT = KNOWN (POBJECT n_capture)',
            'S_one.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
            'pfibercapture.FACTORY = eps', 'pfibercapture.ARRAY = (pfiberarray)',
            'pfibercapture.SITE = pfiberarray.SITE', 'pfibercapture.KIND = pfiberarray.KIND',
            'pfibercapture.NAME = pfiberarray.NAME', 'pfibercapture.INPUT = (n_receiver)',
            '$node_children(S_one, HOBJECT n_capture) = [HOBJECT n_receiver]',
            '$fiber_capture_live(S_one, n_capture)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_capture) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_receiver) = 3',
            '$heap_owners($heap_graph(S_one), HARRAY n_callback) = 1',
            '$call_descriptors_valid(S_one[.COMPLETION = NORMAL])',
            '$heap_valid($heap_graph(S_one))',
            'pfibercapture_missing = pfibercapture[.ARRAY = eps]',
            'S_missing = S_one[.COMPLETION = NORMAL]'
            '[.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture_missing]',
            '$heap_graph(S_missing) = $heap_graph(S_one)',
            '~$fiber_capture_source_valid(S_missing, pfibercapture_missing)',
            '~$fiber_capture_live(S_missing, n_capture)',
            '~$call_descriptors_valid(S_missing)',
            *FINISH,
            events('Y', '|', '1', '1', '0', '|', '1', '|', '7', '|', '17', '|', '0', '|', '1'),
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_done), HOBJECT n_receiver) = 0',
        ],
    },
    'array-fcc-constructor-last-raw-borrows-receiver-and-retains-trace-argument': {
        'source': SOURCES['peer-fiber-array-fcc-constructor-core-last-raw-retirement'],
        'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_core* '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_CONSTRUCT '
                  '-- if pconfigcall.SELECTION = (n_capture) '
                  '-- if ptask_core* = [FIBER_API_CORE_RESULT n_runner n_capture pconfigcall, '
                  'FIBER_FINISH n_runner]'),
        'checks': [
            'S.ACTIVEFIBER = (n_runner)', 'S.CURRENT = eps', 'S.FRAMES = eps',
            'S.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
            'pfibercapture.FACTORY = eps', 'pfibercapture.ARRAY = (pfiberarray)',
            'pfibercapture.KIND = INTRINSIC_FIBER_CONSTRUCT',
            'pfibercapture.NAME = $ptascii("__construct")',
            'pfibercapture.INPUT = (n_receiver)',
            'pfiberarray.SITE = pfibercapture.SITE', 'pfiberarray.KIND = pfibercapture.KIND',
            'pfiberarray.NAME = pfibercapture.NAME', 'pfiberarray.INPUT = pfibercapture.INPUT',
            'n_callback = pfiberarray.ARRAY',
            'pfiberarray.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)), '
            'ENTRY (KINT 1) (DIRECT (PSTRING ($ptascii("__construct"))))]',
            '~((HARRAY n_callback) <- S.ALLOCATIONS)',
            '$fiber_array_capture_source_valid(S, pfiberarray)',
            '~$fiber_array_source_valid(S, pfiberarray)',
            '$fiber_capture_source_valid(S, pfibercapture)',
            '$fiber_capture_live(S, n_capture)', '$fiber_capture_core_live(S, n_capture)',
            '$fiber_at(S, n_receiver) = (pfiber_receiver)',
            'pfiber_receiver.READY', 'pfiber_receiver.STATUS = FIBER_SUSPENDED',
            '$fiber_at(S, n_runner) = (pfiber_runner)',
            'pfiber_runner.STATUS = FIBER_RUNNING',
            'pfiber_runner.RAW = POBJECT n_capture',
            'pfiber_runner.TARGET = (FIBER_API_TARGET n_capture)',
            '$fiber_cached_target_valid(S, pfiber_runner)',
            'pconfigcall.OWNER = (n_receiver)', 'pconfigcall.INDEX = 1',
            '~pconfigcall.NAMED', 'pconfigcall.PACKS = eps',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_arg))]',
            'pfiber_runner.ENTRY = ({SLOTS pconfigcall.SENT, NAMED eps})',
            '$fiber_core_binding(S, pfiber_runner) = (pconfigcall.OWNER, pconfigcall.SELECTION)',
            'S.FIBERCALLERS = [pfibercaller]', 'pfibercaller.OBJECT = n_runner',
            'pfibercaller.PREVIOUS = eps', 'pfibercaller.VM.GLOBAL',
            'pfibercaller.API.KIND = eps', 'pfibercaller.API.OBJECT = n_runner',
            'pfibercaller.API.START = ({SLOTS pconfigcall.SENT, NAMED eps})',
            '$fiber_caller_api_nodes(pfibercaller) = [HOBJECT n_runner, HOBJECT n_arg]',
            '$node_children(S, HOBJECT n_runner) = [HOBJECT n_capture]',
            '$node_children(S, HOBJECT n_capture) = [HOBJECT n_receiver]',
            '$config_nodes(pconfigcall) = [HOBJECT n_arg]',
            '$task_nodes(FIBER_API_CORE_RESULT n_runner n_capture pconfigcall) = [HOBJECT n_capture]',
            'H = $heap_graph(S)', '$heap_owners(H, HARRAY n_callback) = 0',
            '$heap_owners(H, HOBJECT n_receiver) = 1',
            '$heap_owners(H, HOBJECT n_capture) = 2',
            '$heap_owners(H, HOBJECT n_arg) = 2',
            '$heap_owners(H, HOBJECT n_runner) = 2',
            '$fiber_core_result_valid(S, n_runner, pconfigcall)',
            '$fiber_api_core_result_valid(S, n_runner, n_capture, pconfigcall)',
            '$fiber_core_config_valid(S, pconfigcall)', '$config_invoke_valid(S, pconfigcall)',
            '$config_trace_frames(S, pconfigcall, [POBJECT n_arg]) = [ptraceframe]',
            'ptraceframe.FILE = eps', 'ptraceframe.LINE = $(-1)',
            'ptraceframe.FUNCTION = $ptascii("__construct")',
            'n_beyond = |S.ARRAYS|',
            *changed_witness('arena', 'pfiberarray[.ARRAY = n_beyond]'),
            *changed_witness('init', 'pfiberarray[.INIT = $(pfiberarray.INIT + 1)]'),
            *changed_witness('line', 'pfiberarray[.LINE = $(pfiberarray.LINE + 1)]'),
            'pfibercapture_missing = pfibercapture[.ARRAY = eps]',
            'S_missing = S[.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture_missing]',
            '$heap_graph(S_missing) = H', '~$fiber_capture_live(S_missing, n_capture)',
            '~$fiber_core_config_valid(S_missing, pconfigcall)',
            '~$call_descriptors_valid(S_missing)',
            'pfiberfactory_fake = {CALL pconfigcall, ITEMS pfiberarray.ITEMS}',
            'pfibercapture_mixed = pfibercapture[.FACTORY = (pfiberfactory_fake)]',
            'S_mixed = S[.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture_mixed]',
            '$heap_graph(S_mixed) = H',
            '~$fiber_capture_source_valid(S_mixed, pfibercapture_mixed)',
            '~$fiber_capture_live(S_mixed, n_capture)',
            '~$call_descriptors_valid(S_mixed)',
            'pconfigcall_line = pconfigcall[.LINE = $(pconfigcall.LINE + 1)]',
            'S_callline = S[.TODO = [CONFIG_INVOKE pconfigcall_line, '
            'FIBER_API_CORE_RESULT n_runner n_capture pconfigcall_line, FIBER_FINISH n_runner]]',
            '$heap_graph(S_callline) = H',
            '~$fiber_core_config_valid(S_callline, pconfigcall_line)',
            '~$call_descriptors_valid(S_callline)',
            'S_marker = S[.TODO = [CONFIG_INVOKE pconfigcall, FIBER_FINISH n_runner]]',
            '~$fiber_core_config_valid(S_marker, pconfigcall)',
            '~$call_descriptors_valid(S_marker)',
            'S_tail = S[.TODO = [CONFIG_INVOKE pconfigcall, '
            'FIBER_API_CORE_RESULT n_runner n_capture pconfigcall]]',
            '$heap_graph(S_tail) = H', '~$fiber_core_config_valid(S_tail, pconfigcall)',
            '~$call_descriptors_valid(S_tail)',
            *review.VALID, *ZERO, *FINISH,
            events('Y', '|', 'F|', 'C|', 'Cannot call constructor twice', '|', 'D', '1', '|', '1', '1'),
            '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_arg) <- S_done.ALLOCATIONS)',
            'n_arg <- S_done.DESTRUCTION.CALLED',
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
    review.__file__ = str(Path(__file__).resolve())
    passed = all(review.run([name]) for name in args.case or list(CASES))
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'Array FCC catalog changed during run'
    raise SystemExit(0 if passed else 1)
