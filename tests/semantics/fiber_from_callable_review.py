#!/usr/bin/env python3
"""Independent factory history, receiver ownership and C-root cleanup checks."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('fiber_from_callable_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCES = {row['id']: row['source'] for row in json.loads(SOURCE_BYTES)}
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
FINISH = ['S_done = $drive(S, 4000)', *review.DONE]


def events(*pieces):
    return 'S_done.EVENTS = [' + ', '.join('OUTPUT $ptascii(' + json.dumps(x) + ')' for x in pieces) + ']'


def changed_factory(name, factory):
    return [
        f'pfibercapture_{name} = pfibercapture[.FACTORY = ({factory})]',
        f'S_{name} = S[.OBJECTS = $object_set(S.OBJECTS, n_capture, FIBERAPICLOSURE pfibercapture_{name})]',
        f'$heap_graph(S_{name}) = H', f'~$fiber_capture_live(S_{name}, n_capture)',
        f'~$call_descriptors_valid(S_{name})',
    ]


HISTORY = [
    'S.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
    'pfibercapture.KIND = INTRINSIC_FIBER_RESUME', 'pfibercapture.INPUT = (n_receiver)',
    'pfibercapture.FACTORY = (pfiberfactory)', 'pconfigcall_factory = pfiberfactory.CALL',
    'pconfigcall_factory.KIND = INTRINSIC_FROM_CALLABLE',
    'pconfigcall_factory.SITE = pfibercapture.SITE', 'pconfigcall_factory.SELECTION = eps',
    'pconfigcall_factory.INDEX = 1', 'pconfigcall_factory.PACKS = eps',
    'pconfigcall_factory.SENT = [NAMED_SENT (KNOWN (PARRAY n_callback))]',
    '~((HARRAY n_callback) <- S.ALLOCATIONS)',
    '$config_selected_valid(S, pconfigcall_factory)',
    '$call_line_valid(S, (pconfigcall_factory.SITE), pconfigcall_factory.LINE)',
    '$intrinsic_count(S, pconfigcall_factory.SITE) = (pconfigcall_factory.INDEX)',
    '$config_sent_shape(S, pconfigcall_factory)', '~$config_slots_valid(S, pconfigcall_factory.SENT)',
    '$fiber_capture_source_valid(S, pfibercapture)', '$fiber_capture_live(S, n_capture)',
    '$node_children(S, HOBJECT n_capture) = [HOBJECT n_receiver]',
    '$fiber_at(S, n_receiver) = (pfiber_receiver)',
    'pfiber_receiver.STATUS = FIBER_SUSPENDED', 'H = $heap_graph(S)',
    '$heap_owners(H, HARRAY n_callback) = 0',
]

CASES = {
    'factory-wait-trace-keeps-real-resume-and-invoke-sites': {
        'source': SOURCES['author-fiber-from-resume-body-identity-trace'],
        'stage': ('S.FIBERCALLERS = [pfibercaller] '
                  '-- if pfibercaller.API.KIND = (INTRINSIC_FIBER_RESUME) '
                  '-- if pfibercaller.VM.TODO = (FIBER_WAIT pfibercaller.API) :: '
                  '(FIBER_CAPTURE_RESULT n_capture pconfigcall true) :: ptask_saved* '
                  '-- if S.TODO = (FIBER_CONTINUE pfiberapi_continue) :: ptask_child*'),
        'checks': [
            'S.ACTIVEFIBER = (n_receiver)', 'pfibercaller.OBJECT = n_receiver',
            'pfibercaller.PREVIOUS = eps', 'pfibercaller.VM.GLOBAL',
            'pconfigcall.KIND = INTRINSIC_FIBER_RESUME',
            'pconfigcall.OWNER = (n_receiver)', 'pconfigcall.SELECTION = (n_capture)',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (PINT 17))]', 'pconfigcall.NAMED',
            'S.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
            'pfibercapture.FACTORY = (pfiberfactory)',
            '$fiber_capture_live(S, n_capture)',
            'S_wait = $fiber_vm_restore(S, pfibercaller.VM)[.ACTIVEFIBER = eps][.FIBERCALLERS = eps]',
            '$fiber_capture_result_valid(S_wait, n_capture, pconfigcall, true)',
            '$fiber_api_valid(S_wait, pfibercaller.API)',
            '$fiber_wait_valid(S_wait, pfibercaller.API)',
            '$fiber_continue_valid(S, pfiberapi_continue)',
            '$config_trace_frames(S_wait, pconfigcall, [PINT 17]) = [ptraceframe_handler, ptraceframe_invoke]',
            'ptraceframe_handler.FILE = eps', 'ptraceframe_handler.LINE = $(-1)',
            'ptraceframe_handler.FUNCTION = $ptascii("resume")',
            'ptraceframe_handler.ARGS = [(KINT 0, PINT 17)]',
            'ptraceframe_invoke.FUNCTION = $ptascii("__invoke")',
            'ptraceframe_invoke.FILE = $call_sourcefile(S.FILES, pconfigcall.SITE)',
            'ptraceframe_invoke.LINE = pconfigcall.LINE',
            'ptraceframe_invoke.ARGS = ptraceframe_handler.ARGS',
            '$fiber_caller_api_trace(S_wait, pfibercaller.API) = [ptraceframe_wait, ptraceframe_invoke]',
            'ptraceframe_wait = ptraceframe_handler[.FILE = $call_sourcefile(S.FILES, pconfigcall.SITE)][.LINE = pconfigcall.LINE]',
            '$fiber_callers_valid(S, S.ACTIVEFIBER, S.FIBERCALLERS, eps)',
            *review.VALID, *ZERO, *FINISH,
            events('1', '|', 'body', '|', 'fromFiberResumeBody19', '.', '0', '0', '|',
                   'resume', '->', '1', '1', '|', '__invoke', '->', '1', '1', '|', '1', '0'),
        ],
    },
    'factory-resume-freezes-members-after-history-retires': {
        'source': SOURCES['peer-fiber-from-callable-frozen-pair-retired-factory'],
        'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_capture* '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
                  '-- if pconfigcall.SELECTION = (n_capture) '
                  '-- if ptask_capture* = (FIBER_CAPTURE_RELEASE n_capture porigin) :: ptask_tail*'),
        'checks': [
            *HISTORY, 'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps',
            'pconfigcall_factory.OWNER = (n_factory_owner)',
            '~((HOBJECT n_factory_owner) <- S.ALLOCATIONS)',
            '$closure_static_api_owner_valid(S, n_factory_owner)',
            '$from_method_site(S, pconfigcall_factory.SITE)', 'pconfigcall_factory.NAMED',
            'pfiberfactory.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)), '
            'ENTRY (KINT 1) (DIRECT (PSTRING $ptascii("ReSuMe")))]',
            'S.ARRAYS[n_callback].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_other)), '
            'ENTRY (KINT 1) (DIRECT (PSTRING $ptascii("throw")))]',
            'n_other =/= n_receiver', '$fiber_at(S, n_other) = (pfiber_other)',
            'pfiber_other.STATUS = FIBER_INIT',
            '$fiber_factory_members(S, PARRAY n_callback, pfiberfactory.ITEMS) = '
            '((POBJECT n_receiver, $ptascii("ReSuMe")))',
            '$fiber_factory_selection(S, PARRAY n_callback, pfiberfactory.ITEMS) = '
            '((INTRINSIC_FIBER_RESUME, $ptascii("ReSuMe"), pfibercapture.INPUT))',
            'pconfigcall.OWNER = (n_receiver)', 'pconfigcall.SELECTION = (n_capture)',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (PSTRING $ptascii("R")))]',
            'pconfigcall.NAMED', '$config_nodes(pconfigcall) = eps',
            'porigin = pconfigcall.SITE',
            '$task_nodes(FIBER_CAPTURE_RELEASE n_capture porigin) = [HOBJECT n_capture]',
            '$fiber_capture_release_valid(S, n_capture, porigin)',
            '$config_invoke_valid(S, pconfigcall)',
            'psymboltable_global = $fiber_globals(S)',
            '$lookup(psymboltable_global.ENV, $ptascii("copy")) = (n_copy_cell)',
            '$node_children(S, HCELL n_copy_cell) = [HOBJECT n_capture]',
            '$lookup(psymboltable_global.ENV, $ptascii("resume")) = (n_resume_cell)',
            '$node_children(S, HCELL n_resume_cell) = [HOBJECT n_original]',
            'S.OBJECTS[n_original] = FIBERAPICLOSURE pfibercapture',
            '$lookup(psymboltable_global.ENV, $ptascii("fcc")) = (n_fcc_cell)',
            '$node_children(S, HCELL n_fcc_cell) = [HOBJECT n_fcc]',
            'S.OBJECTS[n_fcc] = FIBERAPICLOSURE pfibercapture_fcc',
            'pfibercapture_fcc.FACTORY = eps', 'pfibercapture_fcc.INPUT = (n_receiver)',
            '$named_closure_same(S, n_capture, n_fcc)',
            '$heap_owners(H, HOBJECT n_capture) = 2',
            '$heap_owners(H, HOBJECT n_receiver) = 6',
            *changed_factory('line', 'pfiberfactory[.CALL = pconfigcall_factory[.LINE = $(pconfigcall_factory.LINE + 1)]]'),
            *changed_factory('index', 'pfiberfactory[.CALL = pconfigcall_factory[.INDEX = 0]]'),
            *changed_factory('selection', 'pfiberfactory[.CALL = pconfigcall_factory[.SELECTION = (n_capture)]]'),
            *changed_factory('owner', 'pfiberfactory[.CALL = pconfigcall_factory[.OWNER = (n_receiver)]]'),
            *changed_factory('members', 'pfiberfactory[.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)), '
                             'ENTRY (KINT 1) (DIRECT (PSTRING $ptascii("throw")))]]'),
            *changed_factory('keys', 'pfiberfactory[.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)), '
                             'ENTRY (KINT 2) (DIRECT (PSTRING $ptascii("ReSuMe")))]]'),
            'pfibercapture_fcc_forgery = pfibercapture[.FACTORY = eps]',
            'S_fcc_forgery = S[.OBJECTS = $object_set(S.OBJECTS, n_capture, FIBERAPICLOSURE pfibercapture_fcc_forgery)]',
            '$heap_graph(S_fcc_forgery) = H', '~$fiber_capture_live(S_fcc_forgery, n_capture)',
            '~$call_descriptors_valid(S_fcc_forgery)',
            *review.VALID, *ZERO, *FINISH,
            events('1', '0', '1', '|', '1', '|', 'T|', 'Y', '|', '1', '|', 'R', '|', '1', '|', '17', '|', '1'),
            '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        ],
    },
    'factory-core-last-raw-keeps-one-receiver-edge': {
        'source': SOURCES['peer-fiber-from-callable-core-last-raw-retirement'],
        'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_core* '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
                  '-- if pconfigcall.OWNER = (n_receiver) '
                  '-- if ptask_core* = [FIBER_API_CORE_RESULT n_runner n_capture pconfigcall, FIBER_FINISH n_runner]'),
        'checks': [
            *HISTORY, 'S.ACTIVEFIBER = (n_runner)', 'S.CURRENT = eps', 'S.FRAMES = eps',
            'S.EVENTS = eps', 'pconfigcall_factory.OWNER = eps', '~pconfigcall_factory.NAMED',
            'pfiberfactory.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)), '
            'ENTRY (KINT 1) (DIRECT (PSTRING $ptascii("resume")))]',
            '$fiber_at(S, n_runner) = (pfiber_runner)', 'pfiber_runner.STATUS = FIBER_RUNNING',
            'pfiber_runner.RAW = POBJECT n_capture',
            'pfiber_runner.TARGET = (FIBER_API_TARGET n_capture)',
            'pconfigcall.SELECTION = (n_capture)',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_arg))]',
            'pfiber_runner.ENTRY = ({SLOTS pconfigcall.SENT, NAMED eps})',
            '$fiber_capture_core_live(S, n_capture)', '$fiber_cached_target_valid(S, pfiber_runner)',
            '$node_children(S, HOBJECT n_runner) = [HOBJECT n_capture]',
            '$fiber_core_binding(S, pfiber_runner) = (pconfigcall.OWNER, pconfigcall.SELECTION)',
            'S.FIBERCALLERS = [pfibercaller]', 'pfibercaller.OBJECT = n_runner',
            'pfibercaller.PREVIOUS = eps', 'pfibercaller.VM.GLOBAL',
            'pfibercaller.API.START = ({SLOTS pconfigcall.SENT, NAMED eps})',
            '$fiber_caller_api_nodes(pfibercaller) = [HOBJECT n_runner, HOBJECT n_arg]',
            '$config_nodes(pconfigcall) = [HOBJECT n_arg]',
            '$task_nodes(FIBER_API_CORE_RESULT n_runner n_capture pconfigcall) = [HOBJECT n_capture]',
            '$heap_owners(H, HOBJECT n_arg) = 2', '$heap_owners(H, HOBJECT n_capture) = 2',
            '$heap_owners(H, HOBJECT n_receiver) = 1', '$heap_owners(H, HOBJECT n_runner) = 2',
            '$fiber_core_result_valid(S, n_runner, pconfigcall)',
            '$fiber_api_core_result_valid(S, n_runner, n_capture, pconfigcall)',
            '$fiber_core_config_valid(S, pconfigcall)', '$config_invoke_valid(S, pconfigcall)',
            '$config_trace_frames(S, pconfigcall, [POBJECT n_arg]) = [ptraceframe]',
            'ptraceframe.FILE = eps', 'ptraceframe.LINE = $(-1)',
            'ptraceframe.FUNCTION = $ptascii("resume")',
            'pconfigcall_owner = pconfigcall[.OWNER = (n_runner)]',
            'S_owner = S[.TODO = [CONFIG_INVOKE pconfigcall_owner, '
            'FIBER_API_CORE_RESULT n_runner n_capture pconfigcall_owner, FIBER_FINISH n_runner]]',
            '$heap_graph(S_owner) = H', '~$fiber_core_config_valid(S_owner, pconfigcall_owner)',
            '~$call_descriptors_valid(S_owner)',
            *changed_factory('line', 'pfiberfactory[.CALL = pconfigcall_factory[.LINE = $(pconfigcall_factory.LINE + 1)]]'),
            'S_missing = S[.TODO = [CONFIG_INVOKE pconfigcall, FIBER_FINISH n_runner]]',
            '~$fiber_core_config_valid(S_missing, pconfigcall)', '~$call_descriptors_valid(S_missing)',
            'S_tail = S[.TODO = [CONFIG_INVOKE pconfigcall, FIBER_API_CORE_RESULT n_runner n_capture pconfigcall]]',
            '$heap_graph(S_tail) = H', '~$fiber_core_config_valid(S_tail, pconfigcall)',
            '~$call_descriptors_valid(S_tail)',
            *review.VALID, *ZERO, *FINISH,
            events('B|', 'F|', 'D', '1', '1', '|', '', '|', '1', '1', '1'),
            '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_arg) <- S_done.ALLOCATIONS)', 'n_arg <- S_done.DESTRUCTION.CALLED',
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
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'Factory capture catalog changed during run'
    raise SystemExit(0 if passed else 1)
