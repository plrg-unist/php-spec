#!/usr/bin/env python3
"""Independent bound Fiber API receiver, waiting-call and wrapper ownership checks."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('fiber_bound_api_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCES = {row['id']: row['source'] for row in json.loads(SOURCE_BYTES)}
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
FINISH = ['S_done = $drive(S, 4000)', *review.DONE]
CAPTURE = [
    'S.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
    '$fiber_bound_kind(pfibercapture.KIND)', 'pfibercapture.INPUT = (n_receiver)',
    '$(n_receiver < n_capture)', '$fiber_capture_source_valid(S, pfibercapture)',
    '$fiber_capture_live(S, n_capture)',
    '$node_children(S, HOBJECT n_capture) = [HOBJECT n_receiver]',
    '$fiber_capture_owner(pfibercapture, n_capture) = (n_receiver)',
    '$closure_scope_at(S.CLOSURESCOPES, n_capture) = eps',
    '$closure_binding_at(S.CLOSUREBINDINGS, n_capture) = eps',
    '$fiber_capture_core_live(S, n_capture)',
    '$fiber_callback_resolution(S, POBJECT n_capture) = HANDLERRESOLVED (FIBER_API_TARGET n_capture)',
    'pconfigcall.OWNER = (n_receiver)', 'pconfigcall.SELECTION = (n_capture)',
    'pconfigcall.KIND = pfibercapture.KIND',
    '$fiber_capture_config_tag(pconfigcall)',
]


def waiting_stage(kind, invoke=None):
    stage = ('S.FIBERCALLERS = [pfibercaller] '
             '-- if pfibercaller.API.KIND = (' + kind + ') '
             '-- if pfibercaller.VM.TODO = (FIBER_WAIT pfibercaller.API) :: '
             '(FIBER_CAPTURE_RESULT n_capture pconfigcall b_invoke) :: ptask_after* '
             '-- if pconfigcall.OWNER = (n_receiver) '
             '-- if S.ACTIVEFIBER = (n_receiver)')
    if invoke is not None:
        stage += ' -- if b_invoke = ' + str(invoke).lower()
    return stage


WAIT = [
    *CAPTURE,
    'pfibercaller.OBJECT = n_receiver', 'pfibercaller.PREVIOUS = eps',
    'pfibercaller.VM.GLOBAL', 'pfibercaller.VM.CURRENT = eps',
    'pfibercaller.VM.FRAMES = eps', 'pfibercaller.API.START = eps',
    'pfibercaller.API.SITE = pconfigcall.SITE',
    'pfibercaller.API.LINE = pconfigcall.LINE',
    'pfibercaller.API.SENT = $fiber_config_sent(pconfigcall)',
    '$fiber_caller_api_nodes(pfibercaller) = $fiber_value_nodes(pfibercaller.API.SENT)',
    '$fiber_api_nodes(pfibercaller.API) = [HOBJECT n_receiver] ++ $fiber_value_nodes(pfibercaller.API.SENT)',
    '$heap_count(HOBJECT n_receiver, $fiber_caller_api_nodes(pfibercaller)) = 0',
    '$task_nodes(FIBER_WAIT pfibercaller.API) = eps',
    'S_wait = $fiber_vm_restore(S, pfibercaller.VM)[.ACTIVEFIBER = eps][.FIBERCALLERS = eps]',
    '$fiber_api_valid(S_wait, pfibercaller.API)',
    '$fiber_wait_valid(S_wait, pfibercaller.API)',
    '$fiber_capture_result_valid(S_wait, n_capture, pconfigcall, b_invoke)',
    '$fiber_vm_valid(S, pfibercaller.VM, eps, eps)',
    '~$fiber_api_valid(S_wait, pfibercaller.API[.LINE = $(pfibercaller.API.LINE + 1)])',
    '~$fiber_api_valid(S_wait, pfibercaller.API[.SITE = pfibercapture.SITE])',
    '~$fiber_api_valid(S_wait, pfibercaller.API[.OBJECT = n_capture])',
    '~$fiber_api_valid(S_wait, pfibercaller.API[.SEQUENCE = S.FIBERSEQ])',
    'S_without = S_wait[.TODO = (FIBER_WAIT pfibercaller.API) :: ptask_after*]',
    '~$fiber_api_valid(S_without, pfibercaller.API)',
    'S_mode = S_wait[.TODO = (FIBER_WAIT pfibercaller.API) :: '
    '(FIBER_CAPTURE_RESULT n_capture pconfigcall (~b_invoke)) :: ptask_after*]',
    '~$fiber_api_valid(S_mode, pfibercaller.API)',
    'S_duplicate = S_wait[.TODO = (FIBER_WAIT pfibercaller.API) :: '
    '(FIBER_CAPTURE_RESULT n_capture pconfigcall b_invoke) :: '
    '(FIBER_CAPTURE_RESULT n_capture pconfigcall b_invoke) :: ptask_after*]',
    '~$fiber_api_valid(S_duplicate, pfibercaller.API)',
    'S_owner = S_wait[.TODO = (FIBER_WAIT pfibercaller.API) :: '
    '(FIBER_CAPTURE_RESULT n_capture (pconfigcall[.OWNER = (n_capture)]) b_invoke) :: ptask_after*]',
    '~$fiber_api_valid(S_owner, pfibercaller.API)',
    'S_selection = S_wait[.TODO = (FIBER_WAIT pfibercaller.API) :: '
    '(FIBER_CAPTURE_RESULT n_capture (pconfigcall[.SELECTION = eps]) b_invoke) :: ptask_after*]',
    '~$fiber_api_valid(S_selection, pfibercaller.API)',
    'S_hidden = S_wait[.TODO = (FIBER_WAIT pfibercaller.API) :: '
    '(AT pconfigcall.SITE (FIBER_CAPTURE_RESULT n_capture pconfigcall b_invoke)) :: ptask_after*]',
    '~$generator_flat_tasks(S_hidden.TODO)',
    '~$fiber_api_valid(S_hidden, pfibercaller.API)',
]

CASES = {
    'bound-selection-keeps-immutable-receiver-without-config-owner': {
        'source': SOURCES['peer-bound-alias-clone-receiver'],
        'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
                  '-- if ptask_tail* = (FIBER_CAPTURE_RELEASE n_capture porigin_release) :: ptask_after* '
                  '-- if porigin_release = pconfigcall.SITE '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_STARTED '
                  '-- if pconfigcall.OWNER = (n_receiver) '
                  '-- if pconfigcall.SELECTION = (n_capture)'),
        'checks': [
            *CAPTURE, 'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps',
            'pconfigcall.INDEX = 0', 'pconfigcall.SENT = eps',
            '$config_nodes(pconfigcall) = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_receiver) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_capture) = 2',
            '$config_selected_valid(S, pconfigcall)', '$config_invoke_valid(S, pconfigcall)',
            '$lookup(S.ENV, $ptascii("g")) = (n_gcell)',
            'S.STORE[n_gcell] = DEFINED (POBJECT n_other)', 'n_other =/= n_receiver',
            '$lookup(S.ENV, $ptascii("other")) = (n_ccell)',
            'S.STORE[n_ccell] = DEFINED (POBJECT n_other_capture)',
            '~$named_closure_same(S, n_capture, n_other_capture)',
            'pconfigcall_other = pconfigcall[.OWNER = (n_other)]',
            'S_other = S[.TODO = (CONFIG_INVOKE pconfigcall_other) :: '
            '(FIBER_CAPTURE_RELEASE n_capture pconfigcall.SITE) :: ptask_after*]',
            '$heap_graph(S_other) = $heap_graph(S)',
            '~$config_selected_valid(S_other, pconfigcall_other)',
            '~$call_descriptors_valid(S_other)',
            'pconfigcall_selected = pconfigcall[.SELECTION = (n_other_capture)]',
            'S_selected = S[.TODO = (CONFIG_INVOKE pconfigcall_selected) :: '
            '(FIBER_CAPTURE_RELEASE n_capture pconfigcall.SITE) :: ptask_after*]',
            '$heap_graph(S_selected) = $heap_graph(S)',
            '~$config_selected_valid(S_selected, pconfigcall_selected)',
            '~$call_descriptors_valid(S_selected)',
            'pconfigcall_missing = pconfigcall[.SELECTION = eps]',
            'S_missing = S[.TODO = (CONFIG_INVOKE pconfigcall_missing) :: '
            '(FIBER_CAPTURE_RELEASE n_capture pconfigcall.SITE) :: ptask_after*]',
            '~$config_selected_valid(S_missing, pconfigcall_missing)',
            '~$call_descriptors_valid(S_missing)',
            *review.VALID, *ZERO,
            'S_one = $drive_steps(S, 1)', 'S_one.COMPLETION = BUDGET',
            'S_one.RESULT = KNOWN (PBOOL false)',
            'S_one.TODO = (FIBER_CAPTURE_RESULT n_capture pconfigcall false) :: ptask_after*',
            '$fiber_capture_result_valid(S_one[.COMPLETION = NORMAL], n_capture, pconfigcall, false)',
            '$call_descriptors_valid(S_one[.COMPLETION = NORMAL])',
            *FINISH,
            '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        ],
    },
    'bound-direct-resume-borrows-receiver-and-owns-inner-buffer': {
        'source': SOURCES['peer-bound-direct-last-capture-arguments'],
        'stage': waiting_stage('INTRINSIC_FIBER_RESUME', False)
                 + ' -- if S.TODO = (FIBER_CONTINUE pfiberapi) :: ptask_child* '
                   '-- if pfibercaller.API.SENT = (POBJECT n_arg)',
        'checks': [
            *WAIT, '~b_invoke',
            '$heap_owners($heap_graph(S), HOBJECT n_receiver) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_capture) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 2',
            '$fiber_caller_api_nodes(pfibercaller) = [HOBJECT n_arg]',
            '$task_nodes(FIBER_CAPTURE_RESULT n_capture pconfigcall false) = [HOBJECT n_capture]',
            '$heap_count(HOBJECT n_arg, $fiber_vm_nodes(pfibercaller.VM)) = 0',
            '$heap_count(HOBJECT n_capture, $fiber_vm_nodes(pfibercaller.VM)) = 1',
            '~$fiber_api_valid(S_wait, pfibercaller.API[.SENT = eps])',
            *review.VALID, *ZERO, *FINISH,
            'S_done.EVENTS = [OUTPUT $ptascii("B|"), OUTPUT $ptascii("D"), '
            'OUTPUT $ptascii("1"), OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), '
            'OUTPUT $ptascii("F|"), OUTPUT $ptascii("1"), OUTPUT $ptascii("1")]',
            '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            'n_arg <- S_done.DESTRUCTION.CALLED',
        ],
    },
    'bound-invoke-resume-preserves-outer-buffer-and-second-closure': {
        'source': SOURCES['peer-bound-invoke-last-capture-arguments'],
        'stage': waiting_stage('INTRINSIC_FIBER_RESUME', True)
                 + ' -- if S.TODO = (FIBER_CONTINUE pfiberapi) :: ptask_child* '
                   '-- if pfibercaller.API.SENT = (POBJECT n_arg)',
        'checks': [
            *WAIT, 'b_invoke',
            '$heap_owners($heap_graph(S), HOBJECT n_receiver) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_capture) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 3',
            '$task_nodes(FIBER_CAPTURE_RESULT n_capture pconfigcall true) = '
            '[HOBJECT n_capture, HOBJECT n_capture, HOBJECT n_arg]',
            '$heap_count(HOBJECT n_arg, $fiber_vm_nodes(pfibercaller.VM)) = 1',
            '$heap_count(HOBJECT n_capture, $fiber_vm_nodes(pfibercaller.VM)) = 2',
            '$fiber_caller_api_trace(S_wait, pfibercaller.API) = [ptraceframe, ptraceframe_invoke]',
            'ptraceframe.FILE = eps', 'ptraceframe.LINE = $(-1)',
            'ptraceframe.FUNCTION = $ptascii("resume")',
            'ptraceframe.TYPE = ($ptascii("->"))',
            'ptraceframe_invoke.FILE = $call_sourcefile(S.FILES, pconfigcall.SITE)',
            'ptraceframe_invoke.LINE = pconfigcall.LINE',
            'ptraceframe_invoke.CLASS = ($ptascii("Closure"))',
            'ptraceframe_invoke.FUNCTION = $ptascii("__invoke")',
            *review.VALID, *ZERO, *FINISH,
            'S_done.EVENTS = [OUTPUT $ptascii("B|"), OUTPUT $ptascii("D"), '
            'OUTPUT $ptascii("1"), OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), '
            'OUTPUT $ptascii("F|"), OUTPUT $ptascii("1"), OUTPUT $ptascii("1")]',
            '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            'n_arg <- S_done.DESTRUCTION.CALLED',
        ],
    },
    'bound-throw-keeps-exact-injected-throwable-and-callsite': {
        'source': SOURCES['peer-bound-throw-return'],
        'stage': waiting_stage('INTRINSIC_FIBER_THROW', False)
                 + ' -- if pfibercaller.API.SENT = (POBJECT n_error)',
        'checks': [
            *WAIT, '$throwable_live(S, n_error)',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_error))]',
            '$fiber_caller_api_nodes(pfibercaller) = [HOBJECT n_error]',
            '~$fiber_api_valid(S_wait, pfibercaller.API[.SENT = (PINT 1)])',
            'pconfigcall_bad = pconfigcall[.SENT = [NAMED_SENT (KNOWN (PINT 1))]]',
            'pfiberapi_bad = pfibercaller.API[.SENT = (PINT 1)]',
            'S_bad = S_wait[.TODO = (FIBER_WAIT pfiberapi_bad) :: '
            '(FIBER_CAPTURE_RESULT n_capture pconfigcall_bad false) :: ptask_after*]',
            '~$fiber_api_valid(S_bad, pfiberapi_bad)',
            '$fiber_caller_api_trace(S_wait, pfibercaller.API) = [ptraceframe]',
            'ptraceframe.FILE = $call_sourcefile(S.FILES, pconfigcall.SITE)',
            'ptraceframe.LINE = pconfigcall.LINE',
            'ptraceframe.FUNCTION = $ptascii("throw")',
            'ptraceframe.TYPE = ($ptascii("->"))',
            *review.VALID, *ZERO, *FINISH,
            '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        ],
    },
    'nested-bound-resume-validates-real-saved-parent-continuation': {
        'source': SOURCES['peer-bound-nested-resume-status'],
        'stage': ('S.FIBERCALLERS = [pfibercaller, pfibercaller_main] '
                  '-- if pfibercaller.API.KIND = (INTRINSIC_FIBER_RESUME) '
                  '-- if pfibercaller.VM.TODO = (FIBER_WAIT pfibercaller.API) :: '
                  '(FIBER_CAPTURE_RESULT n_capture pconfigcall b_invoke) :: ptask_after* '
                  '-- if pconfigcall.OWNER = (n_receiver) '
                  '-- if S.ACTIVEFIBER = (n_receiver)'),
        'checks': [
            *CAPTURE, '~b_invoke', 'pfibercaller.OBJECT = n_receiver',
            'pfibercaller.PREVIOUS = (n_parent)', 'pfibercaller_main.OBJECT = n_parent',
            'pfibercaller_main.PREVIOUS = eps', '~pfibercaller.VM.GLOBAL',
            'pfibercaller_main.VM.GLOBAL', 'pfibercaller.API.SENT = eps',
            '$fiber_caller_api_nodes(pfibercaller) = eps',
            '$fiber_caller_api_nodes(pfibercaller_main) = [HOBJECT n_parent]',
            '$fiber_vm_valid(S, pfibercaller.VM, (n_parent), [pfibercaller_main])',
            '$fiber_vm_valid(S, pfibercaller_main.VM, eps, eps)',
            '$fiber_callers_valid(S, (n_receiver), S.FIBERCALLERS, eps)',
            'S_parent = $fiber_vm_restore(S, pfibercaller.VM)'
            '[.ACTIVEFIBER = (n_parent)][.FIBERCALLERS = [pfibercaller_main]]',
            '$fiber_wait_valid(S_parent, pfibercaller.API)',
            'pfibervm_bad = pfibercaller.VM[.TODO = (FIBER_WAIT pfibercaller.API) :: '
            '(FIBER_CAPTURE_RESULT n_capture (pconfigcall[.OWNER = (n_parent)]) false) :: ptask_after*]',
            '~$fiber_vm_valid(S, pfibervm_bad, (n_parent), [pfibercaller_main])',
            'pfibervm_hidden = pfibercaller.VM[.TODO = (FIBER_WAIT pfibercaller.API) :: '
            '(CHOOSE ([FIBER_CAPTURE_RESULT n_capture pconfigcall false]) eps 0) :: ptask_after*]',
            '~$generator_flat_tasks(pfibervm_hidden.TODO)',
            '~$fiber_vm_valid(S, pfibervm_hidden, (n_parent), [pfibercaller_main])',
            *review.VALID, *ZERO, *FINISH,
            'S_done.OBJECTS[n_receiver] = FIBER pfiber_done',
            'pfiber_done.STATUS = FIBER_TERMINATED', 'pfiber_done.VALUE = PINT 19',
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
