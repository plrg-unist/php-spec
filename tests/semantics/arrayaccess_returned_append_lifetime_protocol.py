"""Reached CV-object result ownership before returned-child retirement."""
from error_handler_protocol import PREFIX


def guards(s):
    return [f'$call_current_valid({s})', f'$call_frames_valid({s}, {s}.FRAMES)',
            f'$call_descriptors_valid({s})', f'$heap_valid($heap_graph({s}))']


STAGE = ('S.TODO = (ACCESS_RESULT paccess) :: ptask_tail* '
         '-- if paccess.MODE = ACCESS_SET '
         '-- if paccess.PHASE = ACCESS_CALL $ptascii("offsetSet")')


def checks(used):
    value = 'POBJECT n_payload' if used else 'PNULL'
    count = 2 if used else 1
    return [
        'S.TODO = (ACCESS_RESULT paccess) :: ptask_tail*',
        'paccess.MODE = ACCESS_SET',
        'paccess.TASK = KEY_WRITE_FINISH pkeywriter',
        'paccess.OBJECT = (n_child)',
        'paccess.SELECTED = VARIABLE $ptascii("rhsUnused309") z_rhs',
        'paccess.RHS = paccess.SELECTED',
        'paccess.VALUE = POBJECT n_payload',
        '$lookup(S.ENV, $ptascii("rhsUnused309")) = (n_rhs)',
        'S.STORE[n_rhs] = DEFINED (POBJECT n_payload)',
        '$heap_owners($heap_prune($heap_graph(S)), HOBJECT n_payload) = 1',
        *guards('S'),
        'PhpStep: S ~> S_raw',
        'S_raw.RESULT = KNOWN (POBJECT n_payload)',
        'S_raw.TODO = ptask_tail*',
        '$call_descriptors_valid(S_raw)', '$heap_valid($heap_graph(S_raw))',
        'S_budget = $drive_steps(S, 1)', 'S_budget.COMPLETION = BUDGET',
        'S_budget.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
        'pdestructionoperation.SOURCE = ACCESS_RESULT paccess',
        f'pdestructionoperation.VALUE = KNOWN ({value})',
        f'$heap_owners($heap_prune($heap_graph(S_budget)), HOBJECT n_payload) = {count}',
        '$destructor_operation_live(S_budget, pdestructionoperation)',
        *guards('S_budget'),
        'S_done = $drive(S_budget[.COMPLETION = NORMAL], 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        'S_done.DESTRUCTION.OPERATIONS = eps',
        '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_payload) <- S_done.ALLOCATIONS)',
        '$lookup(S_done.ENV, $ptascii("rhsUnused309")) = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]


CASES = [
    ('unused-returned-Set-normalizes-result-before-child-retirement',
     'returned-child-unused-CV-result-must-not-pin-payload', STAGE, checks(False)),
    ('used-returned-Set-keeps-result-through-child-retirement',
     'returned-child-used-CV-result-retains-payload', STAGE, checks(True)),
]
