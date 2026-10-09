#!/usr/bin/env python3
"""Independent START pack snapshots, saved provenance and explicit unwind owners."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('fiber_start_unpack_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCES = {row['id']: row['source'] for row in json.loads(SOURCE_BYTES)}
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
FINISH = ['S_done = $drive(S, 4000)', *review.DONE]


def events(*pieces):
    return 'S_done.EVENTS = [' + ', '.join(
        'OUTPUT $ptascii(' + json.dumps(piece) + ')' for piece in pieces) + ']'


def active_pack(name, expression):
    return [
        f'pfiberstart_{name} = {expression}',
        f'S_{name} = S[.TODO = (FIBER_UNPACK_NEXT eps pfiberstart_{name} poperand n_cursor)'
        ' :: ptask_unpack*]',
        f'$heap_graph(S_{name}) = H',
        f'~$fiber_start_unpack_valid(S_{name}, eps, pfiberstart_{name}, poperand, n_cursor)',
        f'~$call_descriptors_valid(S_{name})',
    ]


def saved_pack(name, expression):
    return [
        f'pfiberstart_{name} = pfiberstart[.PACKS = {expression}]',
        f'pfiberapi_{name} = pfiberapi[.PACKS = pfiberstart_{name}.PACKS]',
        f'pfibercaller_{name} = pfibercaller[.API = pfiberapi_{name}]'
        f'[.VM.TODO = (FIBER_WAIT pfiberapi_{name}) :: '
        f'(FIBER_START_CAPTURE_RESULT n_capture pfiberstart_{name} true) :: ptask_saved*]',
        f'S_{name} = S[.FIBERCALLERS = [pfibercaller_{name}]]',
        f'$heap_graph(S_{name}) = H',
        f'~$call_descriptors_valid(S_{name})',
        f'S_wait_{name} = $fiber_vm_restore(S_{name}, pfibercaller_{name}.VM)'
        '[.ACTIVEFIBER = eps][.FIBERCALLERS = eps]',
        f'~$fiber_start_capture_result_valid(S_wait_{name}, n_capture, pfiberstart_{name}, true)',
        f'~$fiber_api_valid(S_wait_{name}, pfiberapi_{name})',
    ]


CASES = {
    'start-unpack-active-pack-keeps-sole-frozen-array-receiver': {
        'source': SOURCES['peer-fiber-array-start-unpack-freezes-ref-selector-before-global-retirement'],
        'stage': ('S.TODO = (FIBER_UNPACK_NEXT eps pfiberstart poperand n_cursor) :: ptask_unpack* '
                  '-- if n_cursor = 0 '
                  '-- if ptask_unpack* = (FIBER_ARRAY_START_RELEASE pfiberarray) :: ptask_tail*'),
        'checks': [
            'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps',
            'S.CURRENT = eps', 'S.FRAMES = eps',
            'pfiberstart.INDEX = 0', '$intrinsic_count(S, pfiberstart.SITE) = (1)',
            'pfiberstart.SENT = {SLOTS eps, NAMED eps}',
            'pfiberstart.PACKS = [(FIBER_ARRAY_PACK pconfigpack)]',
            'pconfigpack.INDEX = pfiberstart.INDEX',
            'poperand = KNOWN (PARRAY n_pack)', 'pconfigpack.ARRAY = n_pack',
            'pconfigpack.ITEMS = [ENTRY (KSTRING ($ptascii("value"))) (DIRECT (PSTRING ($ptascii("7")))), '
            'ENTRY (KSTRING ($ptascii("tail"))) (DIRECT (PSTRING ($ptascii("X"))))]',
            'pconfigpack.ITEMS = $config_pack_capture(S, S.ARRAYS[n_pack].ITEMS)',
            '(HARRAY n_pack) <- S.ALLOCATIONS',
            'pfiberarray.KIND = INTRINSIC_FIBER_START',
            'pfiberarray.NAME = $ptascii("StArT")',
            'pfiberarray.INPUT = (n_receiver)', 'pfiberstart.OBJECT = n_receiver',
            'pfiberarray.SITE = pfiberstart.SITE', 'pfiberarray.LINE = pfiberstart.LINE',
            'n_selector = pfiberarray.ARRAY',
            'pfiberarray.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)), '
            'ENTRY (KINT 1) (DIRECT (PSTRING ($ptascii("StArT"))))]',
            '$entry_lookup(S.ARRAYS[n_selector].ITEMS, KINT 0) = (ALIAS n_receiver_ref)',
            '$entry_lookup(S.ARRAYS[n_selector].ITEMS, KINT 1) = (ALIAS n_method_ref)',
            '$entry_value(S, ALIAS n_receiver_ref) = POBJECT n_other',
            '$entry_value(S, ALIAS n_method_ref) = PSTRING ($ptascii("resume"))',
            'n_other =/= n_receiver', '$fiber_at(S, n_other) = (pfiber_other)',
            'pfiber_other.STATUS = FIBER_INIT',
            '$fiber_at(S, n_receiver) = (pfiber_receiver)',
            'pfiber_receiver.STATUS = FIBER_INIT', 'pfiber_receiver.READY',
            'psymboltable_global = $fiber_globals(S)',
            '$lookup(psymboltable_global.ENV, $ptascii("target")) = (n_target_cell)',
            'S.STORE[n_target_cell] = DEFINED PNULL',
            '$lookup(psymboltable_global.ENV, $ptascii("pair")) = (n_pair_cell)',
            'S.STORE[n_pair_cell] = DEFINED PNULL',
            '~((HARRAY n_selector) <- S.ALLOCATIONS)',
            'H = $heap_graph(S)', '$heap_owners(H, HARRAY n_selector) = 0',
            '$heap_owners(H, HARRAY n_pack) = 2',
            '$heap_count(HARRAY n_pack, $pools_nodes(S.POOLS)) = 1',
            '$heap_owners(H, HOBJECT n_receiver) = 1',
            '$task_nodes(FIBER_UNPACK_NEXT eps pfiberstart poperand n_cursor) = '
            '[HOBJECT n_receiver, HARRAY n_pack]',
            '$task_nodes(FIBER_ARRAY_START_RELEASE pfiberarray) = eps',
            '$fiber_array_start_source_valid(S, pfiberarray)',
            '$fiber_start_unpack_valid(S, eps, pfiberstart, poperand, n_cursor)',
            '$call_task_valid(S, FIBER_UNPACK_NEXT eps pfiberstart poperand n_cursor)',
            'n_beyond = |S.ARRAYS|',
            *active_pack('arena', 'pfiberstart[.PACKS = [(FIBER_ARRAY_PACK pconfigpack[.ARRAY = n_beyond])]]'),
            *active_pack('site', 'pfiberstart[.PACKS = [(FIBER_ARRAY_PACK pconfigpack[.SITE = pfiberstart.SITE])]]'),
            *active_pack('line', 'pfiberstart[.PACKS = [(FIBER_ARRAY_PACK pconfigpack[.LINE = $(pconfigpack.LINE + 1)])]]'),
            *active_pack('index', 'pfiberstart[.PACKS = [(FIBER_ARRAY_PACK pconfigpack[.INDEX = 1])]]'),
            *active_pack('missing', 'pfiberstart[.PACKS = eps]'),
            *active_pack('duplicate', 'pfiberstart[.PACKS = [(FIBER_ARRAY_PACK pconfigpack), (FIBER_ARRAY_PACK pconfigpack)]]'),
            *active_pack('prefix', 'pfiberstart[.SENT.NAMED = '
                         '[($ptascii("value"), KNOWN (PSTRING ($ptascii("7"))))]]'),
            'S_cursor = S[.TODO = (FIBER_UNPACK_NEXT eps pfiberstart poperand 3) :: ptask_unpack*]',
            '$heap_graph(S_cursor) = H',
            '~$fiber_start_unpack_valid(S_cursor, eps, pfiberstart, poperand, 3)',
            '~$call_descriptors_valid(S_cursor)',
            *review.VALID, *ZERO,
            'S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
            'S_one = S_one_budget[.COMPLETION = NORMAL]',
            'S_one.TODO = (FIBER_UNPACK_NEXT eps pfiberstart_one poperand 1) :: ptask_unpack*',
            'pfiberstart_one.INDEX = pfiberstart.INDEX',
            'pfiberstart_one.PACKS = pfiberstart.PACKS',
            'pfiberstart_one.SENT.SLOTS = eps',
            'pfiberstart_one.SENT.NAMED = [($ptascii("value"), KNOWN (PSTRING ($ptascii("7"))))]',
            '$fiber_start_unpack_valid(S_one, eps, pfiberstart_one, poperand, 1)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_receiver) = 1',
            '$heap_owners($heap_graph(S_one), HARRAY n_pack) = 2',
            'S_one.POOLS = S.POOLS',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
            *FINISH,
            events('P|', '7', '|', 'D', '|', 'X', '|', 'F|', 'Y', '|', '1', '|', '0'),
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            '(HARRAY n_pack) <- S_done.ALLOCATIONS',
            '$heap_owners($heap_graph(S_done), HARRAY n_pack) = 1',
            '$heap_count(HARRAY n_pack, $pools_nodes(S_done.POOLS)) = 1',
        ],
    },
    'start-unpack-explicit-wait-authenticates-retired-pack-history': {
        'source': SOURCES['peer-fiber-fcc-start-unpack-dynamic-pack-retired-history'],
        'stage': ('S.FIBERCALLERS = [pfibercaller] '
                  '-- if pfiberapi = pfibercaller.API '
                  '-- if pfibercaller.VM.TODO = (FIBER_WAIT pfiberapi) :: '
                  '(FIBER_START_CAPTURE_RESULT n_capture pfiberstart true) :: ptask_saved* '
                  '-- if S.TODO = [FIBER_ENTER n_receiver pnamedargs, FIBER_FINISH n_receiver]'),
        'checks': [
            'S.ACTIVEFIBER = (n_receiver)', 'S.CURRENT = eps', 'S.FRAMES = eps',
            'pfibercaller.OBJECT = n_receiver', 'pfibercaller.PREVIOUS = eps',
            'pfibercaller.VM.GLOBAL',
            'S.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
            'pfibercapture.KIND = INTRINSIC_FIBER_START',
            'pfibercapture.INPUT = (n_receiver)', '$fiber_capture_live(S, n_capture)',
            '$node_children(S, HOBJECT n_capture) = [HOBJECT n_receiver]',
            'pfiberstart.OBJECT = n_receiver', 'pfiberstart.INDEX = 1',
            '$intrinsic_count(S, pfiberstart.SITE) = (1)',
            'pfiberstart.SENT = pnamedargs', 'pnamedargs.SLOTS = eps',
            'pnamedargs.NAMED = [($ptascii("value"), KNOWN (PSTRING ($ptascii("7")))), '
            '($ptascii("tail"), KNOWN (PSTRING ($ptascii("X"))))]',
            'pfiberstart.PACKS = [(FIBER_ARRAY_PACK pconfigpack)]',
            'pconfigpack.INDEX = 0', 'n_pack = pconfigpack.ARRAY',
            'pconfigpack.ITEMS = [ENTRY (KSTRING ($ptascii("value"))) (DIRECT (PSTRING ($ptascii("7")))), '
            'ENTRY (KSTRING ($ptascii("tail"))) (DIRECT (PSTRING ($ptascii("X"))))]',
            '~((HARRAY n_pack) <- S.ALLOCATIONS)',
            'pfiberapi.PACKS = pfiberstart.PACKS',
            'pfiberapi.KIND = eps', 'pfiberapi.SENT = eps',
            'pfiberapi.START = (pnamedargs)', 'pfiberapi.OBJECT = n_receiver',
            'pfiberapi.SITE = pfiberstart.SITE', 'pfiberapi.LINE = pfiberstart.LINE',
            '$exit_method_site(S, pfiberstart.SITE)',
            'psymboltable_global = $fiber_globals(S)',
            '$lookup(psymboltable_global.ENV, $ptascii("start")) = (n_start_cell)',
            'S.STORE[n_start_cell] = DEFINED PNULL',
            '$fiber_at(S, n_receiver) = (pfiber_receiver)',
            'pfiber_receiver.STATUS = FIBER_RUNNING',
            'H = $heap_graph(S)', '$heap_owners(H, HARRAY n_pack) = 0',
            '$heap_owners(H, HOBJECT n_capture) = 2',
            '$heap_owners(H, HOBJECT n_receiver) = 2',
            '$fiber_caller_api_nodes(pfibercaller) = eps',
            '$fiber_api_nodes(pfiberapi) = [HOBJECT n_receiver]',
            '$heap_count(HOBJECT n_capture, $fiber_vm_nodes(pfibercaller.VM)) = 2',
            'S_wait = $fiber_vm_restore(S, pfibercaller.VM)[.ACTIVEFIBER = eps][.FIBERCALLERS = eps]',
            '$fiber_start_capture_result_valid(S_wait, n_capture, pfiberstart, true)',
            '$fiber_api_valid(S_wait, pfiberapi)', '$fiber_wait_valid(S_wait, pfiberapi)',
            '$fiber_vm_valid(S, pfibercaller.VM, eps, eps)',
            'n_beyond = |S.ARRAYS|',
            *saved_pack('missing', 'eps'),
            *saved_pack('duplicate', '[(FIBER_ARRAY_PACK pconfigpack), (FIBER_ARRAY_PACK pconfigpack)]'),
            *saved_pack('arena', '[(FIBER_ARRAY_PACK pconfigpack[.ARRAY = n_beyond])]'),
            *saved_pack('index', '[(FIBER_ARRAY_PACK pconfigpack[.INDEX = 1])]'),
            *saved_pack('site', '[(FIBER_ARRAY_PACK pconfigpack[.SITE = pfiberstart.SITE])]'),
            *saved_pack('line', '[(FIBER_ARRAY_PACK pconfigpack[.LINE = $(pconfigpack.LINE + 1)])]'),
            'pfiberapi_sequence = pfiberapi[.SEQUENCE = S.FIBERSEQ]',
            'S_wait_sequence = S_wait[.TODO = (FIBER_WAIT pfiberapi_sequence) :: '
            '(FIBER_START_CAPTURE_RESULT n_capture pfiberstart true) :: ptask_saved*]',
            '~$fiber_api_valid(S_wait_sequence, pfiberapi_sequence)',
            *review.VALID, *ZERO, *FINISH,
            events('P|', '7', '|', 'D', '|', 'X', '|', '1', '|', '29', '|', '1'),
            '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
        ],
    },
    'start-unpack-explicit-throw-transfers-closure-before-named-payload': {
        'source': SOURCES['peer-fiber-start-unpack-direct-and-explicit-capture-abrupt-named-order'],
        'stage': ('S.TODO = (THROW_SEARCH n_throwable) :: '
                  '(FIBER_UNPACK_PREP (n_capture) pfiberstart) :: '
                  '(FIBER_CAPTURE_RELEASE n_capture porigin) :: ptask_tail* '
                  '-- if pfiberstart.INDEX = 1 '
                  '-- if $exit_method_site(S, pfiberstart.SITE)'),
        'checks': [
            'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps',
            'S.CURRENT = eps', 'S.FRAMES = eps',
            'S.ORIGIN = (pfiberstart.SITE)', 'porigin = pfiberstart.SITE',
            '$intrinsic_count(S, pfiberstart.SITE) = (2)',
            'pfiberstart.SENT.SLOTS = eps',
            'pfiberstart.SENT.NAMED = [($ptascii("value"), KNOWN (POBJECT n_arg))]',
            'pfiberstart.PACKS = [(FIBER_ARRAY_PACK pconfigpack)]', 'pconfigpack.INDEX = 0',
            'pconfigpack.ITEMS = [ENTRY (KSTRING ($ptascii("value"))) (DIRECT (POBJECT n_arg))]',
            '~((HARRAY pconfigpack.ARRAY) <- S.ALLOCATIONS)',
            'S.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
            'pfibercapture.KIND = INTRINSIC_FIBER_START',
            'pfibercapture.INPUT = (n_receiver)', 'pfiberstart.OBJECT = n_receiver',
            '$node_children(S, HOBJECT n_capture) = [HOBJECT n_receiver]',
            '$fiber_at(S, n_receiver) = (pfiber_receiver)',
            'pfiber_receiver.STATUS = FIBER_SUSPENDED', 'pfiber_receiver.VM =/= eps',
            'psymboltable_global = $fiber_globals(S)',
            '$lookup(psymboltable_global.ENV, $ptascii("target")) = (n_target_cell)',
            'S.STORE[n_target_cell] = DEFINED PNULL',
            '$lookup(psymboltable_global.ENV, $ptascii("start")) = (n_start_cell)',
            'S.STORE[n_start_cell] = DEFINED PNULL',
            'H = $heap_graph(S)', '$heap_owners(H, HOBJECT n_capture) = 1',
            '$heap_owners(H, HOBJECT n_receiver) = 1',
            '$heap_owners(H, HOBJECT n_arg) = 1',
            '$task_nodes(FIBER_UNPACK_PREP (n_capture) pfiberstart) = [HOBJECT n_arg]',
            '$task_nodes(FIBER_CAPTURE_RELEASE n_capture porigin) = [HOBJECT n_capture]',
            '$fiber_start_unpack_pending(S, (n_capture), pfiberstart)',
            '$call_task_valid(S, FIBER_UNPACK_PREP (n_capture) pfiberstart)',
            'pfiberstart_bad = pfiberstart[.PACKS = [(FIBER_ARRAY_PACK pconfigpack[.INDEX = 1])]]',
            'S_bad = S[.TODO = (THROW_SEARCH n_throwable) :: '
            '(FIBER_UNPACK_PREP (n_capture) pfiberstart_bad) :: '
            '(FIBER_CAPTURE_RELEASE n_capture porigin) :: ptask_tail*]',
            '$heap_graph(S_bad) = H',
            '~$fiber_start_unpack_pending(S_bad, (n_capture), pfiberstart_bad)',
            '~$call_descriptors_valid(S_bad)',
            *review.VALID, *ZERO,
            'S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
            'S_one = S_one_budget[.COMPLETION = NORMAL]',
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(THROW_SEARCH n_throwable) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_capture), '
            'DESTRUCTION_VALUE (HOBJECT n_arg)]',
            'pdestructionrelease.CALLER = S.CURRENT',
            'pdestructionrelease.ORIGIN = S.ORIGIN',
            'pdestructionrelease.CONSTCONTEXT = S.CONSTCONTEXT',
            'S_one.DESTRUCTION.RELEASES = pdestructionrelease :: S.DESTRUCTION.RELEASES',
            'S_one.ALLOCATIONS = S.ALLOCATIONS',
            '$heap_owners($heap_graph(S_one), HOBJECT n_capture) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_receiver) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_arg) = 1',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
            'S_done = $drive(S_one, 4000)', *review.DONE,
            events('P|', 'D', '0', '|', 'F|', 'C|', '1', '|',
                   'P|', 'F|', 'D', '1', '|', 'C|', '1', '|END'),
            '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_arg) <- S_done.ALLOCATIONS)',
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
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'START unpack originals changed during run'
    raise SystemExit(0 if passed else 1)
