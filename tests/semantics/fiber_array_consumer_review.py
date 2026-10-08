#!/usr/bin/env python3
"""Independent ordinary Fiber array selection and receiver ownership checks."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('fiber_array_consumer_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCES = {row['id']: row['source'] for row in json.loads(SOURCE_BYTES)}
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
FINISH = ['S_done = $drive(S, 4000)', *review.DONE]


def events(*pieces):
    return 'S_done.EVENTS = [' + ', '.join('OUTPUT $ptascii(' + json.dumps(x) + ')' for x in pieces) + ']'


def changed_record(name, expression):
    return [
        f'pfiberarray_{name} = {expression}',
        f'S_{name} = S[.TODO = (CONFIG_INVOKE pconfigcall) :: '
        f'(FIBER_ARRAY_RELEASE pfiberarray_{name}) :: ptask_tail*]',
        f'$heap_graph(S_{name}) = H',
        f'~$fiber_array_selected(S_{name}, pfiberarray_{name}, pconfigcall)',
        f'~$config_invoke_valid(S_{name}, pconfigcall)',
        f'~$call_descriptors_valid(S_{name})',
    ]


COMMON = [
    'pfiberarray.SITE = pconfigcall.SITE', 'pfiberarray.LINE = pconfigcall.LINE',
    'pfiberarray.ARRAY = n_callback', 'pconfigcall.SELECTION = eps',
    'pconfigcall.INDEX = 1', 'pconfigcall.NAMED', 'pconfigcall.PACKS = eps',
    '~((HARRAY n_callback) <- S.ALLOCATIONS)', 'H = $heap_graph(S)',
    '$heap_owners(H, HARRAY n_callback) = 0',
    '$fiber_array_source_valid(S, pfiberarray)',
    '$fiber_array_config_matches(pfiberarray, pconfigcall)',
    '$fiber_array_config_pair(S.TODO, pconfigcall) = (pfiberarray)',
    '$fiber_array_count(S.TODO, pfiberarray.SITE) = 1',
    '$fiber_array_selected(S, pfiberarray, pconfigcall)',
    '$fiber_array_release_valid(S, pfiberarray)',
    '$fiber_array_config_pending(S, pconfigcall)',
    '$call_task_valid(S, FIBER_ARRAY_RELEASE pfiberarray)',
    '$task_nodes(FIBER_ARRAY_RELEASE pfiberarray) = eps',
    '$config_invoke_valid(S, pconfigcall)',
    'n_beyond = |S.ARRAYS|',
    *changed_record('arena', 'pfiberarray[.ARRAY = n_beyond]'),
    *changed_record('init', 'pfiberarray[.INIT = $(pfiberarray.INIT + 1)]'),
    'pconfigcall_line = pconfigcall[.LINE = $(pconfigcall.LINE + 1)]',
    'pfiberarray_line = pfiberarray[.LINE = pconfigcall_line.LINE]',
    'S_line = S[.TODO = (CONFIG_INVOKE pconfigcall_line) :: '
    '(FIBER_ARRAY_RELEASE pfiberarray_line) :: ptask_tail*]',
    '$heap_graph(S_line) = H',
    '~$fiber_array_source_valid(S_line, pfiberarray_line)',
    '~$config_invoke_valid(S_line, pconfigcall_line)',
    '~$call_descriptors_valid(S_line)',
    'S_missing = S[.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*]',
    '$heap_graph(S_missing) = H', '~$config_invoke_valid(S_missing, pconfigcall)',
    '~$call_descriptors_valid(S_missing)',
    'S_duplicate = S[.TODO = (CONFIG_INVOKE pconfigcall) :: '
    '(FIBER_ARRAY_RELEASE pfiberarray) :: (FIBER_ARRAY_RELEASE pfiberarray) :: ptask_tail*]',
    '$heap_graph(S_duplicate) = H',
    '~$fiber_array_release_valid(S_duplicate, pfiberarray)',
    '~$config_invoke_valid(S_duplicate, pconfigcall)',
    '~$call_descriptors_valid(S_duplicate)',
]

CASES = {
    'array-resume-freezes-references-before-argument-effects': {
        'source': SOURCES['peer-fiber-array-freezes-reference-members-before-arguments'],
        'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_array* '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
                  '-- if ptask_array* = (FIBER_ARRAY_RELEASE pfiberarray) :: ptask_tail*'),
        'checks': [
            *COMMON, 'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps',
            'pfiberarray.KIND = INTRINSIC_FIBER_RESUME',
            'pfiberarray.NAME = $ptascii("ReSuMe")', 'pfiberarray.INPUT = (n_receiver)',
            'pfiberarray.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)), '
            'ENTRY (KINT 1) (DIRECT (PSTRING ($ptascii("ReSuMe"))))]',
            'pconfigcall.OWNER = (n_receiver)',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (PINT 7))]',
            '$entry_lookup(S.ARRAYS[n_callback].ITEMS, KINT 0) = (ALIAS n_receiver_cell)',
            '$entry_lookup(S.ARRAYS[n_callback].ITEMS, KINT 1) = (ALIAS n_method_cell)',
            '$entry_value(S, ALIAS n_receiver_cell) = POBJECT n_other',
            '$entry_value(S, ALIAS n_method_cell) = PSTRING ($ptascii("throw"))',
            'n_other =/= n_receiver', '$fiber_at(S, n_other) = (pfiber_other)',
            'pfiber_other.STATUS = FIBER_INIT',
            '$fiber_at(S, n_receiver) = (pfiber_receiver)',
            'pfiber_receiver.STATUS = FIBER_SUSPENDED',
            '$heap_owners(H, HOBJECT n_receiver) = 1',
            '$config_nodes(pconfigcall) = [HOBJECT n_receiver]',
            '$fiber_array_owner(pfiberarray) = (n_receiver)',
            *changed_record('input', 'pfiberarray[.INPUT = (n_other)]'),
            *changed_record('name', 'pfiberarray[.NAME = $ptascii("throw")]'),
            'pconfigcall_kind = pconfigcall[.KIND = INTRINSIC_FIBER_THROW]',
            'S_kind = S[.TODO = (CONFIG_INVOKE pconfigcall_kind) :: '
            '(FIBER_ARRAY_RELEASE pfiberarray) :: ptask_tail*]',
            '$heap_graph(S_kind) = H', '~$config_invoke_valid(S_kind, pconfigcall_kind)',
            '~$call_descriptors_valid(S_kind)',
            'pconfigcall_owner = pconfigcall[.OWNER = (n_other)]',
            'S_owner = S[.TODO = (CONFIG_INVOKE pconfigcall_owner) :: '
            '(FIBER_ARRAY_RELEASE pfiberarray) :: ptask_tail*]',
            '~$config_invoke_valid(S_owner, pconfigcall_owner)',
            '~$call_descriptors_valid(S_owner)',
            *review.VALID, *ZERO, *FINISH,
            events('Y', '|', '1', '|', '7', '|', '1', '|', '1', '|', '0'),
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_done), HOBJECT n_receiver) = 0',
        ],
    },
    'array-static-suspend-retires-input-before-entering': {
        'source': SOURCES['peer-fiber-array-static-object-does-not-own-receiver'],
        'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_array* '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_SUSPEND '
                  '-- if ptask_array* = (FIBER_ARRAY_RELEASE pfiberarray) :: ptask_tail*'),
        'checks': [
            *COMMON, 'S.ACTIVEFIBER = (n_runner)', 'S.FIBERCALLERS = [pfibercaller]',
            'pfibercaller.OBJECT = n_runner', 'pfibercaller.PREVIOUS = eps',
            'pfibercaller.API.OBJECT = n_runner', 'pfibercaller.API.KIND = eps',
            'pfiberarray.KIND = INTRINSIC_FIBER_SUSPEND',
            'pfiberarray.NAME = $ptascii("SuSpEnD")', 'pfiberarray.INPUT = (n_input)',
            'pfiberarray.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_input)), '
            'ENTRY (KINT 1) (DIRECT (PSTRING ($ptascii("SuSpEnD"))))]',
            'pconfigcall.OWNER = eps',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (PSTRING ($ptascii("V"))))]',
            'n_runner =/= n_input', '~((HOBJECT n_input) <- S.ALLOCATIONS)',
            '$fiber_at(S, n_input) = eps', 'S.OBJECTS[n_input] = FIBER pfiber_input',
            '$heap_owners(H, HOBJECT n_input) = 0',
            '$heap_owners(H, HOBJECT n_runner) = 2',
            '$fiber_array_owner(pfiberarray) = eps', '$config_nodes(pconfigcall) = eps',
            '$fiber_array_receiver_live(S, pfiberarray)',
            *changed_record('input', 'pfiberarray[.INPUT = (n_runner)]'),
            'pconfigcall_owner = pconfigcall[.OWNER = (n_runner)]',
            'S_owner = S[.TODO = (CONFIG_INVOKE pconfigcall_owner) :: '
            '(FIBER_ARRAY_RELEASE pfiberarray) :: ptask_tail*]',
            '~$config_invoke_valid(S_owner, pconfigcall_owner)',
            '~$call_descriptors_valid(S_owner)',
            *review.VALID, *ZERO,
            'S_one = $drive_steps(S, 1)', 'S_one.COMPLETION = BUDGET',
            'S_one.ACTIVEFIBER = eps', 'S_one.FIBERCALLERS = eps',
            # The returned outer start frame releases EX(This) before exposing V.
            # Its real cleanup carrier owns V while the scratch result is null.
            'S_one.RESULT = KNOWN PNULL',
            'S_one.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
            'pdestructionoperation.VALUE = KNOWN (PSTRING ($ptascii("V")))',
            'pdestructionoperation.SOURCE = CONFIG_INVOKE pconfigcall',
            'pdestructionoperation.PENDING = eps',
            'pdestructionoperation.CALLER = pfibercaller.VM.CURRENT',
            'pdestructionoperation.ORIGIN = pfibercaller.VM.ORIGIN',
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_returned*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_runner)]',
            '$call_descriptors_valid(S_one[.COMPLETION = NORMAL])',
            '$heap_valid($heap_graph(S_one))',
            '$heap_owners($heap_graph(S_one), HOBJECT n_runner) = 2',
            # The singleton shared-value release drops only the queued owner.
            'S_released = $drive_steps(S_one[.COMPLETION = NORMAL], 1)',
            'S_released.COMPLETION = BUDGET',
            '$heap_owners($heap_graph(S_released), HOBJECT n_runner) = 1',
            '$call_descriptors_valid(S_released[.COMPLETION = NORMAL])',
            '$heap_valid($heap_graph(S_released))',
            '$fiber_at(S_one, n_runner) = (pfiber_paused)',
            'pfiber_paused.STATUS = FIBER_SUSPENDED', 'pfiber_paused.VM = (pfibervm)',
            'pfibervm.TODO = (FIBER_CONTINUE pfiberapi) :: ptask_saved*',
            'ptask_saved* = (FIBER_ARRAY_RESULT pfiberarray pconfigcall) :: ptask_rest*',
            'pfiberapi.OBJECT = n_runner', 'pfiberapi.KIND = (INTRINSIC_FIBER_SUSPEND)',
            'pfiberapi.START = eps', 'pfiberapi.SENT = (PSTRING ($ptascii("V")))',
            'S_saved = $fiber_vm_restore(S_one[.COMPLETION = NORMAL], pfibervm)'
            '[.ACTIVEFIBER = (n_runner)][.FIBERCALLERS = eps]',
            '$fiber_array_result_valid(S_saved, pfiberarray, pconfigcall)',
            '$fiber_api_valid(S_saved, pfiberapi)', '$fiber_continue_valid(S_saved, pfiberapi)',
            '$task_nodes(FIBER_ARRAY_RESULT pfiberarray pconfigcall) = eps',
            '$task_nodes(FIBER_CONTINUE pfiberapi) = eps',
            *FINISH, events('1', '|', 'V', '|', '1', '|', 'R', '|', '23'),
            '~((HOBJECT n_input) <- S_done.ALLOCATIONS)',
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
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'Array consumer catalog changed during run'
    raise SystemExit(0 if passed else 1)
