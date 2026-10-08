#!/usr/bin/env python3
"""Independent static Fiber Closure source, buffer and retirement checks."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('fiber_static_api_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCES = {row['id']: row['source'] for row in json.loads(SOURCE_BYTES)}


def events(chunks):
    return 'S_done.EVENTS = [' + ', '.join(
        'OUTPUT $ptascii(' + json.dumps(chunk) + ')' for chunk in chunks) + ']'


CAPTURE = [
    'S.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
    '$fiber_capture_live(S, n_capture)',
    '$fiber_capture_source_valid(S, pfibercapture)',
    '$node_children(S, HOBJECT n_capture) = eps',
    '$closure_scope_at(S.CLOSURESCOPES, n_capture) = eps',
    '$closure_binding_at(S.CLOSUREBINDINGS, n_capture) = eps',
    '$target_nodes(FIBER_API_TARGET n_capture) = eps',
]
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
FINISH = ['S_done = $drive(S, 4000)', *review.DONE]
RETIRED_CAPTURE = [
    '$heap_owners($heap_graph(S_done), HOBJECT n_capture) = 0',
    '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
    'pfiber_done.RAW = PNULL', 'pfiber_done.CALL = eps',
    'pfiber_done.TARGET = eps', 'pfiber_done.ENTRY = eps',
    'pfiber_done.VM = eps',
]
CURRENT_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_FIBER_CURRENT '
    '-- if $fiber_capture_config_tag(pconfigcall) '
    '-- if ptask_tail* = (FIBER_CAPTURE_RELEASE n_capture pconfigcall.SITE) :: ptask_after* '
    '-- if S.ACTIVEFIBER = eps')
PENDING_CURRENT = [
    *CAPTURE,
    'pfibercapture.KIND = INTRINSIC_FIBER_CURRENT',
    'pconfigcall.OWNER = (n_capture)', 'pconfigcall.SELECTION = (n_capture)',
    'pconfigcall.INDEX = 0', 'pconfigcall.SENT = eps',
    'pconfigcall.PACKS = eps', '~pconfigcall.NAMED',
    '$config_nodes(pconfigcall) = eps',
    '$selected_task_nonce(CONFIG_INVOKE pconfigcall) = eps',
    '$config_selected_valid(S, pconfigcall)', '$config_invoke_valid(S, pconfigcall)',
    '$fiber_capture_call_site(S, pconfigcall.SITE)',
    '$fiber_capture_count(S.TODO, n_capture, pconfigcall.SITE) = 1',
    '$task_nodes(FIBER_CAPTURE_RELEASE n_capture pconfigcall.SITE) = [HOBJECT n_capture]',
    '~$config_selected_valid(S, pconfigcall[.OWNER = eps])',
    '~$config_selected_valid(S, pconfigcall[.SELECTION = eps])',
    'pconfigcall_bad = pconfigcall[.LINE = $(pconfigcall.LINE + 1)]',
    'S_bad = S[.TODO = (CONFIG_INVOKE pconfigcall_bad) :: '
    '(FIBER_CAPTURE_RELEASE n_capture pconfigcall.SITE) :: ptask_after*]',
    '$heap_graph(S_bad) = $heap_graph(S)',
    '~$config_invoke_valid(S_bad, pconfigcall_bad)', '~$call_descriptors_valid(S_bad)',
    'S_duplicate = S[.TODO = (CONFIG_INVOKE pconfigcall) :: '
    '(FIBER_CAPTURE_RELEASE n_capture pconfigcall.SITE) :: '
    '(FIBER_CAPTURE_RELEASE n_capture pconfigcall.SITE) :: ptask_after*]',
    '~$config_selected_valid(S_duplicate, pconfigcall)',
    '~$call_descriptors_valid(S_duplicate)',
    'S_tail = S[.TODO = (CONFIG_INVOKE pconfigcall) :: DISCARD :: '
    '(FIBER_CAPTURE_RELEASE n_capture pconfigcall.SITE) :: ptask_after*]',
    '$heap_graph(S_tail) = $heap_graph(S)',
    '~$config_selected_valid(S_tail, pconfigcall)',
    '~$call_descriptors_valid(S_tail)',
]
CURRENT_ONE = [
    'S_one = $drive_steps(S, 1)', 'S_one.COMPLETION = BUDGET',
    'S_one.RESULT = KNOWN PNULL',
    'S_one.TODO = (FIBER_CAPTURE_RESULT n_capture pconfigcall false) :: ptask_after*',
    '$fiber_capture_result_valid(S_one[.COMPLETION = NORMAL], n_capture, pconfigcall, false)',
    '~$fiber_capture_result_valid(S_one[.COMPLETION = NORMAL], n_capture, pconfigcall, true)',
    '$call_descriptors_valid(S_one[.COMPLETION = NORMAL])',
]


def parked_stage(kind, owner):
    return (
        'S.TODO = (CONFIG_INVOKE pconfigcall_outer) :: ptask_outer* '
        '-- if pconfigcall_outer.KIND = ' + kind + ' '
        '-- if pconfigcall_outer.OWNER = (n_fiber) '
        '-- if S.ACTIVEFIBER = eps '
        '-- if S.FIBERCALLERS = eps '
        '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
        '-- if pfiber.STATUS = FIBER_SUSPENDED '
        '-- if pfiber.VM = (pfibervm) '
        '-- if pfibervm.TODO = (FIBER_CONTINUE pfiberapi) :: ' + owner)


PARKED = [
    *CAPTURE,
    'pfibercapture.KIND = INTRINSIC_FIBER_SUSPEND',
    'pfibercapture.INPUT = eps', 'pfibercapture.NAME = $ptascii("suspend")',
    'pfiberapi.OBJECT = n_fiber',
    'pfiberapi.KIND = (INTRINSIC_FIBER_SUSPEND)', 'pfiberapi.START = eps',
    'pfiberapi.SEQUENCE = pfiber.SEQUENCE',
    'pfiberapi.SITE = pconfigcall.SITE', 'pfiberapi.LINE = pconfigcall.LINE',
    'pfiberapi.SENT = (POBJECT n_arg)',
    'pconfigcall.KIND = INTRINSIC_FIBER_SUSPEND',
    'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_arg))]',
    'pconfigcall.INDEX = 1', 'pconfigcall.PACKS = eps',
    '$task_nodes(FIBER_CONTINUE pfiberapi) = [HOBJECT n_arg]',
    '(HOBJECT n_arg) <- S.ALLOCATIONS',
    '~pfibervm.GLOBAL',
    '$lookup(S.ENV, $ptascii("weak")) = (n_weak_cell)',
    'S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
    'S.OBJECTS[n_weak] = WEAKREFERENCE (n_capture)',
    '$weakref_get(S, n_weak) = POBJECT n_capture',
    'S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)]',
    '$fiber_continue_valid(S_view, pfiberapi)',
    '~$fiber_continue_valid(S_view, pfiberapi[.SENT = (PNULL)])',
    '~$fiber_continue_valid(S_view, pfiberapi[.SEQUENCE = S.FIBERSEQ])',
    '~$fiber_continue_valid(S_view, pfiberapi[.OBJECT = n_capture])',
    '$fiber_vm_valid(S, pfibervm, (n_fiber), eps)',
    '$config_invoke_valid(S, pconfigcall_outer)',
]


def parked_capture_guards(invoke):
    opposite = 'false' if invoke == 'true' else 'true'
    owner = 'FIBER_CAPTURE_RESULT n_capture pconfigcall ' + invoke
    return [
        'pconfigcall.OWNER = (n_capture)', 'pconfigcall.SELECTION = (n_capture)',
        '$fiber_capture_config_tag(pconfigcall)',
        '$fiber_capture_result_valid(S_view, n_capture, pconfigcall, ' + invoke + ')',
        '~$fiber_capture_result_valid(S_view, n_capture, pconfigcall, ' + opposite + ')',
        '~$fiber_capture_result_valid(S_view, n_capture, pconfigcall[.OWNER = eps], ' + invoke + ')',
        '~$fiber_capture_result_valid(S_view, n_capture, pconfigcall[.SELECTION = eps], ' + invoke + ')',
        'pconfigcall_line = pconfigcall[.LINE = $(pconfigcall.LINE + 1)]',
        'pfibervm_line = pfibervm[.TODO = (FIBER_CONTINUE pfiberapi) :: '
        '(FIBER_CAPTURE_RESULT n_capture pconfigcall_line ' + invoke + ') :: ptask_after*]',
        'S_line = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_line)])',
        '$heap_graph(S_line) = $heap_graph(S)',
        '~$fiber_vm_valid(S_line, pfibervm_line, (n_fiber), eps)',
        '~$call_descriptors_valid(S_line)',
        'pfibervm_duplicate = pfibervm[.TODO = (FIBER_CONTINUE pfiberapi) :: '
        '(' + owner + ') :: (' + owner + ') :: ptask_after*]',
        '~$fiber_vm_valid(S, pfibervm_duplicate, (n_fiber), eps)',
        'pfibervm_at = pfibervm[.TODO = (FIBER_CONTINUE pfiberapi) :: '
        '(' + owner + ') :: (AT pconfigcall.SITE (' + owner + ')) :: ptask_after*]',
        '~$generator_flat_tasks(pfibervm_at.TODO)',
        '~$fiber_vm_valid(S, pfibervm_at, (n_fiber), eps)',
        '~$call_descriptors_valid($fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_at)]))',
        'pfibervm_choose = pfibervm[.TODO = (FIBER_CONTINUE pfiberapi) :: '
        '(' + owner + ') :: (CHOOSE ([' + owner + ']) eps 1) :: ptask_after*]',
        '~$generator_flat_tasks(pfibervm_choose.TODO)',
        '~$fiber_vm_valid(S, pfibervm_choose, (n_fiber), eps)',
    ]


CORE = [
    'pfiber.RAW = POBJECT n_capture', 'pfiber.TARGET = (FIBER_API_TARGET n_capture)',
    '$fiber_cached_target_valid(S, pfiber)', '$fiber_cache_valid(S, n_fiber, pfiber)',
    '$fiber_callback_nodes(pfiber) = [HOBJECT n_capture]',
    'pconfigcall.OWNER = eps', 'pconfigcall.SELECTION = eps',
    'pconfigcall.PACKS = eps', '~pconfigcall.NAMED',
    'pconfigcall.INDEX = |pconfigcall.SENT|',
    'pfiber.ENTRY = ({SLOTS pconfigcall.SENT, NAMED eps})',
    '$task_nodes(FIBER_API_CORE_RESULT n_fiber n_capture pconfigcall) = [HOBJECT n_capture]',
    '$task_nodes(FIBER_CORE_RESULT n_fiber pconfigcall) = eps',
    '$heap_owners($heap_graph(S), HOBJECT n_capture) = 2',
    '~$fiber_cached_target_valid(S, pfiber[.RAW = PNULL])',
    '~$fiber_cached_target_valid(S, pfiber[.TARGET = (FIBER_API_TARGET n_fiber)])',
]


def core_guards(view):
    return [
        '$fiber_core_result_valid(' + view + ', n_fiber, pconfigcall)',
        '$fiber_core_result_task(S, n_fiber, pfiber, pconfigcall) = '
        'FIBER_API_CORE_RESULT n_fiber n_capture pconfigcall',
        '~$fiber_core_result_valid(' + view + ', n_fiber, pconfigcall[.OWNER = (n_capture)])',
        '~$fiber_core_result_valid(' + view + ', n_fiber, pconfigcall[.SELECTION = (n_capture)])',
        '~$fiber_core_result_valid(' + view + ', n_fiber, pconfigcall[.LINE = 0])',
        '~$fiber_core_result_valid(' + view + ', n_capture, pconfigcall)',
        '~$call_task_valid(' + view + ', FIBER_API_CORE_RESULT n_fiber n_fiber pconfigcall)',
        '~$call_task_valid(' + view + '[.ORIGIN = eps], FIBER_API_CORE_RESULT n_fiber n_capture pconfigcall)',
        '~$call_task_valid(' + view + ', FIBER_API_CORE_RESULT n_fiber n_capture (pconfigcall[.LINE = 0]))',
        '~$call_task_valid(' + view + ', FIBER_API_CORE_RESULT n_fiber n_capture (pconfigcall[.KIND = INTRINSIC_FIBER_CONSTRUCT]))',
        '~$call_task_valid(' + view + ', FIBER_API_CORE_RESULT n_fiber n_capture (pconfigcall[.OWNER = (n_capture)]))',
    ]


def core_parked_guards():
    return [
        'pfibervm.CURRENT = eps', 'pfibervm.FRAMES = eps',
        'pfibervm.TABLE = $empty_table()',
        *core_guards('S_view'),
        'pconfigcall_line = pconfigcall[.LINE = $(pconfigcall.LINE + 1)]',
        'pfibervm_line = pfibervm[.TODO = [FIBER_CONTINUE pfiberapi, '
        'FIBER_API_CORE_RESULT n_fiber n_capture pconfigcall_line, FIBER_FINISH n_fiber]]',
        'S_line = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_line)])',
        '$heap_graph(S_line) = $heap_graph(S)',
        '~$fiber_vm_valid(S_line, pfibervm_line, (n_fiber), eps)',
        '~$call_descriptors_valid(S_line)',
        'pfibervm_unowned = pfibervm[.TODO = [FIBER_CONTINUE pfiberapi, '
        'FIBER_CORE_RESULT n_fiber pconfigcall, FIBER_FINISH n_fiber]]',
        '~$fiber_vm_valid(S, pfibervm_unowned, (n_fiber), eps)',
        'pfibervm_at = pfibervm[.TODO = [FIBER_CONTINUE pfiberapi, '
        'AT pconfigcall.SITE (FIBER_API_CORE_RESULT n_fiber n_capture pconfigcall), '
        'FIBER_API_CORE_RESULT n_fiber n_capture pconfigcall, FIBER_FINISH n_fiber]]',
        '~$generator_flat_tasks(pfibervm_at.TODO)',
        '~$fiber_vm_valid(S, pfibervm_at, (n_fiber), eps)',
        '~$call_descriptors_valid($fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_at)]))',
        'pfibervm_choose = pfibervm[.TODO = [FIBER_CONTINUE pfiberapi, '
        'CHOOSE ([FIBER_API_CORE_RESULT n_fiber n_capture pconfigcall]) eps 1, '
        'FIBER_API_CORE_RESULT n_fiber n_capture pconfigcall, FIBER_FINISH n_fiber]]',
        '~$generator_flat_tasks(pfibervm_choose.TODO)',
        '~$fiber_vm_valid(S, pfibervm_choose, (n_fiber), eps)',
    ]


CASES = {
    'clone-and-invoke-alias-retain-frozen-static-capture': {
        'source': SOURCES['peer-static-current-clone-invoke-alias'],
        'stage': CURRENT_STAGE,
        'checks': [
            *PENDING_CURRENT, 'pfibercapture.INPUT = eps',
            'pfibercapture.NAME = $ptascii("gEtCurrent")',
            '$lookup(S.ENV, $ptascii("current")) = (n_original_cell)',
            'S.STORE[n_original_cell] = DEFINED (POBJECT n_original)',
            '$lookup(S.ENV, $ptascii("alias")) = (n_alias_cell)',
            'S.STORE[n_alias_cell] = DEFINED (POBJECT n_original)',
            '$lookup(S.ENV, $ptascii("copy")) = (n_copy_cell)',
            'S.STORE[n_copy_cell] = DEFINED (POBJECT n_capture)',
            'n_capture =/= n_original',
            'S.OBJECTS[n_original] = FIBERAPICLOSURE pfibercapture',
            '$named_closure_same(S, n_original, n_capture)',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_capture) = 2',
            '$typed_object_exact(S, [(PTBRANCH ([(PTCLASS ($ptascii("Closure")))]))], POBJECT n_capture)',
            '~$typed_object_exact(S, [(PTBRANCH ([(PTCLASS ($ptascii("Fiber")))]))], POBJECT n_capture)',
            '$typed_given(S, POBJECT n_capture) = $ptascii("Closure")',
            'pfibercapture_bad = pfibercapture[.KIND = INTRINSIC_FIBER_SUSPEND]',
            'S_kind = S[.OBJECTS = $object_set(S.OBJECTS, n_capture, FIBERAPICLOSURE pfibercapture_bad)]',
            '$heap_graph(S_kind) = $heap_graph(S)', '~$fiber_capture_live(S_kind, n_capture)',
            '~$call_descriptors_valid(S_kind)',
            '~$fiber_capture_source_valid(S, pfibercapture[.SITE = pconfigcall.SITE])',
            '~$fiber_capture_source_valid(S, pfibercapture[.INPUT = (n_capture)])',
            'S_at = S[.TODO = (CONFIG_INVOKE pconfigcall) :: '
            '(AT pconfigcall.SITE (FIBER_CAPTURE_RELEASE n_capture pconfigcall.SITE)) :: '
            '(FIBER_CAPTURE_RELEASE n_capture pconfigcall.SITE) :: ptask_after*]',
            '$fiber_capture_count(S_at.TODO, n_capture, pconfigcall.SITE) = 1',
            '$heap_owners($heap_graph(S_at), HOBJECT n_capture) = 3',
            '$heap_valid($heap_graph(S_at))', '~$generator_flat_tasks(S_at.TODO)',
            '~$config_selected_valid(S_at, pconfigcall)', '~$call_descriptors_valid(S_at)',
            'S_choose = S[.TODO = (CONFIG_INVOKE pconfigcall) :: '
            '(CHOOSE ([FIBER_CAPTURE_RELEASE n_capture pconfigcall.SITE]) eps 1) :: '
            '(FIBER_CAPTURE_RELEASE n_capture pconfigcall.SITE) :: ptask_after*]',
            '$fiber_capture_count(S_choose.TODO, n_capture, pconfigcall.SITE) = 1',
            '~$generator_flat_tasks(S_choose.TODO)',
            '~$config_selected_valid(S_choose, pconfigcall)', '~$call_descriptors_valid(S_choose)',
            *review.VALID, *ZERO, *CURRENT_ONE, *FINISH,
            events(['1', '|', '1', '|', '1', '|', '1', '|', '17']),
        ],
    },
    'dynamic-static-capture-outlives-borrowed-input-fiber': {
        'source': SOURCES['peer-static-dynamic-name-retired-input'],
        'stage': CURRENT_STAGE,
        'checks': [
            *PENDING_CURRENT,
            'pfibercapture.NAME = $ptascii("gEtCuRrEnT")',
            'pfibercapture.INPUT = (n_input)', '$(n_input < n_capture)',
            'S.OBJECTS[n_input] = FIBER pfiber_input',
            '~((HOBJECT n_input) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_input) = 0',
            '$lookup(S.ENV, $ptascii("name")) = (n_name_cell)',
            'S.STORE[n_name_cell] = DEFINED (PSTRING $ptascii("missing"))',
            '$lookup(S.ENV, $ptascii("weak")) = (n_weak_cell)',
            'S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
            'S.OBJECTS[n_weak] = WEAKREFERENCE (n_input)',
            '$weakref_get(S, n_weak) = PNULL',
            '~$fiber_capture_source_valid(S, pfibercapture[.INPUT = eps])',
            '~$fiber_capture_source_valid(S, pfibercapture[.INPUT = (n_capture)])',
            '~$fiber_capture_source_valid(S, pfibercapture[.NAME = $ptascii("missing")])',
            'S_input = S[.OBJECTS = $object_set(S.OBJECTS, n_capture, '
            'FIBERAPICLOSURE (pfibercapture[.INPUT = (n_capture)]))]',
            '$heap_graph(S_input) = $heap_graph(S)', '~$fiber_capture_live(S_input, n_capture)',
            '~$call_descriptors_valid(S_input)',
            *review.VALID, *ZERO, *CURRENT_ONE, *FINISH,
            events(['1', '|', '1', '|', 'W', '|', 'R', '|', '23']),
        ],
    },
    'direct-temporary-suspend-owner-survives-argument-destructor': {
        'source': SOURCES['peer-static-direct-temporary-suspend-lifetime'],
        'stage': parked_stage('INTRINSIC_FIBER_RESUME',
            '(FIBER_CAPTURE_RESULT n_capture pconfigcall false) :: ptask_after*'),
        'checks': [
            *PARKED, *parked_capture_guards('false'),
            'pfibervm.CURRENT = (pcallcontext)',
            '$fiber_context_valid(S_view, pcallcontext)',
            '$heap_owners($heap_graph(S), HOBJECT n_capture) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 1',
            '$task_nodes(FIBER_CAPTURE_RESULT n_capture pconfigcall false) = [HOBJECT n_capture]',
            '$heap_count(HOBJECT n_arg, $fiber_vm_nodes(pfibervm)) = 1',
            '$heap_count(HOBJECT n_capture, $fiber_vm_nodes(pfibervm)) = 1',
            *review.VALID, *ZERO, *FINISH,
            events(['E|', '1', '|', 'K|', 'D', '1', '|', 'R', '|', '1', '|', '7']),
            'S_done.OBJECTS[n_fiber] = FIBER pfiber_done',
            'pfiber_done.STATUS = FIBER_TERMINATED', 'pfiber_done.RETURNED',
            '~pfiber_done.FAILED', 'pfiber_done.VALUE = PINT 7',
            *RETIRED_CAPTURE,
        ],
    },
    'explicit-invoke-owns-two-call-buffers-through-injected-throw': {
        'source': SOURCES['peer-static-invoke-suspend-throw-lifetime'],
        'stage': parked_stage('INTRINSIC_FIBER_THROW',
            '(FIBER_CAPTURE_RESULT n_capture pconfigcall true) :: ptask_after*'),
        'checks': [
            *PARKED, *parked_capture_guards('true'),
            'pfibervm.CURRENT = (pcallcontext)',
            '$fiber_context_valid(S_view, pcallcontext)',
            '$heap_owners($heap_graph(S), HOBJECT n_capture) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 2',
            '$task_nodes(FIBER_CAPTURE_RESULT n_capture pconfigcall true) = '
            '[HOBJECT n_capture, HOBJECT n_capture, HOBJECT n_arg]',
            '$lookup(pfibervm.TABLE.ENV, $ptascii("alias")) = (n_alias_cell)',
            'S.STORE[n_alias_cell] = DEFINED (POBJECT n_capture)',
            *review.VALID, *ZERO, *FINISH,
            events(['K|', 'D', '1', '|', 'T', 'X', '|', '1', '|', '19']),
            'S_done.OBJECTS[n_fiber] = FIBER pfiber_done',
            'pfiber_done.STATUS = FIBER_TERMINATED', 'pfiber_done.RETURNED',
            '~pfiber_done.FAILED', 'pfiber_done.VALUE = PINT 19',
            *RETIRED_CAPTURE,
        ],
    },
    'getcurrent-c-root-holds-raw-and-real-c-closure-owner': {
        'source': SOURCES['peer-static-current-c-root-callback'],
        'stage': ('S.TODO = [CONFIG_INVOKE pconfigcall, '
                  'FIBER_API_CORE_RESULT n_fiber n_capture pconfigcall, FIBER_FINISH n_fiber] '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_CURRENT '
                  '-- if S.ACTIVEFIBER = (n_fiber) '
                  '-- if S.OBJECTS[n_fiber] = FIBER pfiber'),
        'checks': [
            *CAPTURE, *CORE, *core_guards('S'),
            'pconfigcall.SENT = eps', 'S.CURRENT = eps', 'S.FRAMES = eps',
            '$fiber_core_config_valid(S, pconfigcall)', '$config_invoke_valid(S, pconfigcall)',
            '$fiber_core_count(S.TODO) = 1',
            'S_unowned = S[.TODO = [CONFIG_INVOKE pconfigcall, '
            'FIBER_CORE_RESULT n_fiber pconfigcall, FIBER_FINISH n_fiber]]',
            '~$fiber_core_result_valid(S_unowned, n_fiber, pconfigcall)',
            '~$call_descriptors_valid(S_unowned)',
            'S_at = S[.TODO = [CONFIG_INVOKE pconfigcall, '
            'AT pconfigcall.SITE (FIBER_API_CORE_RESULT n_fiber n_capture pconfigcall), '
            'FIBER_API_CORE_RESULT n_fiber n_capture pconfigcall, FIBER_FINISH n_fiber]]',
            '$fiber_core_count(S_at.TODO) = 1', '~$generator_flat_tasks(S_at.TODO)',
            '~$fiber_core_result_valid(S_at, n_fiber, pconfigcall)',
            '~$call_descriptors_valid(S_at)',
            *review.VALID, *ZERO,
            'S_one = $drive_steps(S, 1)', 'S_one.COMPLETION = BUDGET',
            'S_one.RESULT = KNOWN (POBJECT n_fiber)',
            'S_one.TODO = [FIBER_API_CORE_RESULT n_fiber n_capture pconfigcall, FIBER_FINISH n_fiber]',
            '$call_descriptors_valid(S_one[.COMPLETION = NORMAL])',
            'S_result_line = S_one[.COMPLETION = NORMAL][.TODO = '
            '[FIBER_API_CORE_RESULT n_fiber n_capture (pconfigcall[.LINE = 0]), FIBER_FINISH n_fiber]]',
            '$heap_graph(S_result_line) = $heap_graph(S_one)',
            '~$call_descriptors_valid(S_result_line)',
            'S_result_kind = S_one[.COMPLETION = NORMAL][.TODO = '
            '[FIBER_API_CORE_RESULT n_fiber n_capture (pconfigcall[.KIND = INTRINSIC_FIBER_SUSPEND]), FIBER_FINISH n_fiber]]',
            '$heap_graph(S_result_kind) = $heap_graph(S_one)',
            '~$call_descriptors_valid(S_result_kind)',
            'S_result_owner = S_one[.COMPLETION = NORMAL][.TODO = '
            '[FIBER_API_CORE_RESULT n_fiber n_capture (pconfigcall[.OWNER = (n_capture)]), FIBER_FINISH n_fiber]]',
            '$heap_graph(S_result_owner) = $heap_graph(S_one)',
            '~$call_descriptors_valid(S_result_owner)',
            *FINISH, events(['1', '|', '1', '|', '1']),
            'S_done.OBJECTS[n_fiber] = FIBER pfiber_done',
            'pfiber_done.STATUS = FIBER_TERMINATED', 'pfiber_done.RETURNED',
            '~pfiber_done.FAILED', 'pfiber_done.VALUE = POBJECT n_fiber',
            *RETIRED_CAPTURE,
        ],
    },
    'named-suspend-c-root-borrows-final-config-and-resumes-once': {
        'source': SOURCES['peer-static-suspend-c-root-named-resume-lifetime'],
        'stage': parked_stage('INTRINSIC_FIBER_RESUME',
            '[FIBER_API_CORE_RESULT n_fiber n_capture pconfigcall, FIBER_FINISH n_fiber]'),
        'checks': [
            *PARKED, *CORE, *core_parked_guards(),
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 1',
            '$heap_count(HOBJECT n_arg, $fiber_vm_nodes(pfibervm)) = 1',
            '$heap_count(HOBJECT n_capture, $fiber_vm_nodes(pfibervm)) = 1',
            *review.VALID, *ZERO, *FINISH,
            events(['1', '|', 'K|', 'D', '1', '|', '1', '|', '29']),
            'S_done.OBJECTS[n_fiber] = FIBER pfiber_done',
            'pfiber_done.STATUS = FIBER_TERMINATED', 'pfiber_done.RETURNED',
            '~pfiber_done.FAILED', 'pfiber_done.VALUE = PINT 29',
            *RETIRED_CAPTURE,
        ],
    },
    'suspend-c-root-injected-throw-releases-owned-closure-tail': {
        'source': SOURCES['peer-static-suspend-c-root-throw-lifetime'],
        'stage': parked_stage('INTRINSIC_FIBER_THROW',
            '[FIBER_API_CORE_RESULT n_fiber n_capture pconfigcall, FIBER_FINISH n_fiber]'),
        'checks': [
            *PARKED, *CORE, *core_parked_guards(),
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 1',
            '$heap_count(HOBJECT n_arg, $fiber_vm_nodes(pfibervm)) = 1',
            *review.VALID, *ZERO, *FINISH,
            events(['K|', 'D', '1', '|', 'T', 'X', '|', '1', '|', '1']),
            'S_done.OBJECTS[n_fiber] = FIBER pfiber_done',
            'pfiber_done.STATUS = FIBER_TERMINATED', 'pfiber_done.FAILED',
            '~pfiber_done.RETURNED', 'pfiber_done.VALUE = PNULL',
            *RETIRED_CAPTURE,
        ],
    },
    'getcurrent-c-root-arity-error-retains-argument-after-closure-retirement': {
        'source': SOURCES['peer-static-current-c-root-arity-release'],
        'stage': ('S.TODO = [CONFIG_INVOKE pconfigcall, '
                  'FIBER_API_CORE_RESULT n_fiber n_capture pconfigcall, FIBER_FINISH n_fiber] '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_CURRENT '
                  '-- if S.ACTIVEFIBER = (n_fiber) '
                  '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
                  '-- if pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_arg))]'),
        'checks': [
            *CAPTURE, *CORE, *core_guards('S'),
            'S.CURRENT = eps', 'S.FRAMES = eps', 'pconfigcall.INDEX = 1',
            '$fiber_core_config_valid(S, pconfigcall)', '$config_invoke_valid(S, pconfigcall)',
            '$task_nodes(CONFIG_INVOKE pconfigcall) = [HOBJECT n_arg]',
            'S.FIBERCALLERS = [pfibercaller]',
            'pfibercaller.API.START = ({SLOTS pconfigcall.SENT, NAMED eps})',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 2',
            *review.VALID, *ZERO, *FINISH,
            events(['A|', '1', 'D', '0', '|']),
            'S_done.OBJECTS[n_fiber] = FIBER pfiber_done',
            'pfiber_done.STATUS = FIBER_TERMINATED', 'pfiber_done.FAILED',
            '~pfiber_done.RETURNED', *RETIRED_CAPTURE,
            'n_arg <- S_done.DESTRUCTION.CALLED',
            '~((HOBJECT n_arg) <- S_done.ALLOCATIONS)',
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
