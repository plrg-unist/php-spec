"""Reached ordinary recursion requests, real Error allocation and resumption."""
import json

from throwable_builtin_previous_protocol import PREFIX as PREVIOUS_PREFIX
from throwable_previous_graph_protocol import front as previous_front, trace

MESSAGE = 'Nesting level too deep - recursive dependency?'
# Frozen original-source observations; the rules do not consult native answers.
EXPECTED = {
    "std-error-origin-trace": "B|F|Error:Nesting level too deep - recursive dependency?:0:1:3:1|compare148:1:1|",
    "array-cycle-operators": "B|EEEEEEE|Nesting level too deep - recursive dependency?|W|1:E|",
    "inline-cycle-recovery": "B|E|Nesting level too deep - recursive dependency?|M|-1:1|I|1|W|1:1|",
    "aggregate-error-finally-cleanup": "B|F|D|E|Nesting level too deep - recursive dependency?|R|1|M|0|"
}
PREFIX = PREVIOUS_PREFIX + r'''
dec $trr_stage(pstate) : bool
def $trr_stage(S) = true
  -- if S.TODO = (BINARY_RIGHT pbin poperand z) :: ptask*
  -- if $comparison_operator(pbin)
def $trr_stage(S) = false -- otherwise
dec $trr_seek(pstate, nat) : pstate
def $trr_seek(S, n) = S -- if $trr_stage(S) \/ n = 0
def $trr_seek(S, n) = $trr_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if ~$trr_stage(S) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $trr_seek(S, n) = S -- otherwise
'''


def front(program, path):
    return [row.replace('$tbp_seek', '$trr_seek').replace('$tbp_stage', '$trr_stage')
            for row in previous_front(program, path)] + [
        'S.TODO = (BINARY_RIGHT pbin poperand z) :: ptask_tail*',
        '$value_order_effect(S,POBJECT n_a,POBJECT n_b,eps,z) = (S_effect,ORDERRECURSIVE)',
    ]


def captured(node, label, value):
    return trace('S', node, label, value)[:4]


def error_rows(temporary_arrays=False):
    """S_effect is the reached comparer state before the ordinary consumer."""
    budget_tail = [
        'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
        'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_operand_left),DESTRUCTION_VALUE (HARRAY n_operand_right)]',
        '$call_task_valid(S_one[.COMPLETION = NORMAL],DESTRUCTOR_RELEASE pdestructionrelease)',
        'pdestructionoperation.SOURCE = BINARY_RIGHT pbin poperand z',
        'pdestructionoperation.PENDING = (n_error)',
        'pdestructionoperation.COMPLETION = THROWING n_error',
        'pdestructionoperation.VALUE = KNOWN PNULL',
        'pdestructionoperation.NOGC = eps',
        r'pdestructionoperation.CALLER = S.CURRENT /\ pdestructionoperation.ORIGIN = S.ORIGIN',
        'S_one.DESTRUCTION.OPERATIONS = pdestructionoperation :: S_error.DESTRUCTION.OPERATIONS',
        'S_one.DESTRUCTION.RELEASES = pdestructionrelease :: S_error.DESTRUCTION.RELEASES',
    ] if temporary_arrays else [
        'S_one.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
    ]
    return [
        'S.TODO = (BINARY_RIGHT pbin poperand z) :: ptask_tail*',
        'S.ERRORORIGIN = eps',
        'S.ORIGIN = (porigin_site)',
        'S_effect.COMPLETION = NORMAL',
        'S_effect.OBJECTS = S.OBJECTS',
        'PhpStep: S ~> S_raw',
        'S_raw.COMPLETION = THROWN "Error" ($ptascii("' + MESSAGE + '")) z',
        'S_raw.TODO = ptask_tail*',
        r'S_raw.ARRAYS = S_effect.ARRAYS /\ S_raw.OBJECTTABLES = S_effect.OBJECTTABLES',
        r'S_raw.OBJECTPROPS = S_effect.OBJECTPROPS /\ S_raw.STORE = S_effect.STORE',
        'S_raw.ALLOCATIONS = S_effect.ALLOCATIONS',
        r'S_raw.OBJECTS = S.OBJECTS /\ S_raw.EVENTS = S.EVENTS',
        r'S_raw.CURRENT = S.CURRENT /\ S_raw.FRAMES = S.FRAMES',
        '$aggregate_compare_seen(S_raw) = eps',
        'S_error = $throwable_transition(S,S_raw)',
        'n_error = |S.OBJECTS|',
        'S_error.COMPLETION = THROWING n_error',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'S_error.OBJECTS = S.OBJECTS ++ [THROWABLE pthrowable_error]',
        'pthrowable_error.KIND = "Error"',
        r'pthrowable_error.ORIGIN = S.ORIGIN /\ pthrowable_error.FILEORIGIN = S.ORIGIN',
        '$throwable_object_image_valid(S_error,n_error)',
        '$throwable_field(S_error,n_error,"message") = PSTRING ($ptascii("' + MESSAGE + '"))',
        '$throwable_field(S_error,n_error,"code") = PINT 0',
        '$throwable_field(S_error,n_error,"line") = PINT z',
        '$throwable_field(S_error,n_error,"file") = PSTRING ($call_sourcefile(S.FILES,porigin_site))',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"string") = PSTRING eps',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_error_trace',
        'S_error.OBJECTTABLES = S_effect.OBJECTTABLES',
        'S_error.EVENTS = S.EVENTS',
        '$heap_owners($heap_prune($heap_graph(S_error)),HOBJECT n_error) = 1',
        '$drive_steps(S,0) = S[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S,1)',
        'S_one.COMPLETION = BUDGET',
        *budget_tail,
        r'S_one.OBJECTS = S_error.OBJECTS /\ S_one.ARRAYS = S_error.ARRAYS',
        'S_one.OBJECTTABLES = S_effect.OBJECTTABLES',
        'S_one.EVENTS = S.EVENTS',
        '(HOBJECT n_error) <- S_one.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_one)),HOBJECT n_error) = 1',
        '$aggregate_compare_seen(S_one) = eps',
    ]


def checks(program, path, name):
    rows = front(program, path)
    if name == 'array-cycle-operators':
        rows += captured('n_p', 'p', 'PARRAY n_payload_p')
        rows += captured('n_q', 'q', 'PARRAY n_payload_q')
        rows += [
            'pbin = EQUAL',
            'z = 7',
            '$entry_lookup(S.ARRAYS[n_payload_p].ITEMS,KSTRING $ptascii("next")) = (ALIAS n_live_p)',
            '$entry_lookup(S.ARRAYS[n_payload_q].ITEMS,KSTRING $ptascii("next")) = (ALIAS n_live_q)',
            'S.STORE[n_live_p] = DEFINED (PARRAY n_array_p)',
            'S.STORE[n_live_q] = DEFINED (PARRAY n_array_q)',
            '$entry_lookup(S.ARRAYS[n_array_p].ITEMS,KSTRING $ptascii("next")) = (ALIAS n_live_p)',
            '$entry_lookup(S.ARRAYS[n_array_q].ITEMS,KSTRING $ptascii("next")) = (ALIAS n_live_q)',
            '$heap_subset([HCELL n_live_p,HCELL n_live_q,HARRAY n_array_p,HARRAY n_array_q],S.ALLOCATIONS)',
            'S_effect = S',
            '$trace_visit_array_effect(S,n_array_p,n_array_q,[HARRAY n_array_p],z) = (S,ORDERRECURSIVE)',
        ]
    else:
        assert name in ('std-error-origin-trace', 'inline-cycle-recovery',
                        'aggregate-error-finally-cleanup')
        rows += captured('n_p', 'p', 'POBJECT n_left')
        rows += captured('n_q', 'q', 'POBJECT n_right')
        rows += [
            'pbin = SPACESHIP',
            'n_left =/= n_right',
            '$objectprops_record_at(S.OBJECTPROPS,n_left) = (pobjectprops_left)',
            '$objectprops_record_at(S.OBJECTPROPS,n_right) = (pobjectprops_right)',
            '$property_slot_at(pobjectprops_left.SLOTS,$ptascii("next")) = (ppropertyslot_left)',
            '$property_slot_at(pobjectprops_right.SLOTS,$ptascii("next")) = (ppropertyslot_right)',
            'ppropertyslot_left.STATE = PROP_VALUE (DIRECT (POBJECT n_left))',
            'ppropertyslot_right.STATE = PROP_VALUE (DIRECT (POBJECT n_right))',
            '$object_table_at(S.OBJECTTABLES,n_left) = eps',
            '$object_table_at(S.OBJECTTABLES,n_right) = eps',
        ]
        if name == 'inline-cycle-recovery':
            rows += [
                'z = 8',
                'S.OBJECTS[n_left] = INSTANCE porigin_plain',
                'S.OBJECTS[n_right] = INSTANCE porigin_plain',
                '$aggregate_object_guard(S,n_left,n_right) = HOBJECT n_left',
                '$trace_visit_object_effect(S,n_left,n_right,[HOBJECT n_left],z) = (S,ORDERRECURSIVE)',
                'S_effect = S',
            ]
        else:
            rows += [
                'z = ' + ('3' if name == 'std-error-origin-trace' else '7'),
                r'S.OBJECTS[n_left] = STDINSTANCE /\ S.OBJECTS[n_right] = STDINSTANCE',
                'n_table_left = |S.ARRAYS|',
                'n_table_right = $(n_table_left + 1)',
                '$object_table_at(S_effect.OBJECTTABLES,n_left) = (n_table_left)',
                '$object_table_at(S_effect.OBJECTTABLES,n_right) = (n_table_right)',
                '|S_effect.ARRAYS| = $(|S.ARRAYS| + 2)',
                '$heap_owners($heap_prune($heap_graph(S_effect)),HARRAY n_table_left) = 1',
                '$heap_owners($heap_prune($heap_graph(S_effect)),HARRAY n_table_right) = 1',
            ]
        if name == 'aggregate-error-finally-cleanup':
            rows += [
                'poperand = KNOWN (PARRAY n_operand_left)',
                'S.RESULT = KNOWN (PARRAY n_operand_right)',
                'n_operand_left =/= n_operand_right',
                '|S.ARRAYS[n_operand_left].ITEMS| = 2',
                '|S.ARRAYS[n_operand_right].ITEMS| = 2',
                '$entry_lookup(S.ARRAYS[n_operand_left].ITEMS,KINT 0) = (DIRECT (POBJECT n_a))',
                '$entry_lookup(S.ARRAYS[n_operand_right].ITEMS,KINT 0) = (DIRECT (POBJECT n_b))',
                '$entry_lookup(S.ARRAYS[n_operand_left].ITEMS,KINT 1) = (DIRECT (POBJECT n_tail))',
                '$object_name(S,n_tail) = $ptascii("Tail148")',
                '$lookup(S.ENV,$ptascii("guard")) = (n_guardcv)',
                'S.STORE[n_guardcv] = DEFINED (POBJECT n_guard)',
                '$object_name(S,n_guard) = $ptascii("Guard148")',
                '$heap_owners($heap_prune($heap_graph(S)),HOBJECT n_guard) = 1',
            ]
    rows += error_rows(name == 'aggregate-error-finally-cleanup')
    if name in ('array-cycle-operators', 'inline-cycle-recovery'):
        rows += ['S_error.ARRAYS[n_error_trace].ITEMS = eps']
    else:
        rows += [
            '$entry_lookup(S_error.ARRAYS[n_error_trace].ITEMS,KINT 0) = (DIRECT (PARRAY n_error_frame))',
            '$trace_array_field(S_error,n_error_frame,$ptascii("function")) = PSTRING ($ptascii("compare148"))',
            '$trace_array_field(S_error,n_error_frame,$ptascii("line")) = PINT ' + ('8' if name == 'std-error-origin-trace' else '14'),
            '$trace_array_field(S_error,n_error_frame,$ptascii("args")) = PARRAY n_error_args',
            '$entry_lookup(S_error.ARRAYS[n_error_args].ITEMS,KINT 0) = (DIRECT (POBJECT n_a))',
            '$entry_lookup(S_error.ARRAYS[n_error_args].ITEMS,KINT 1) = (DIRECT (POBJECT n_b))',
        ]
    rows += [
        'S_done = $drive_steps(S_one[.COMPLETION = NORMAL],3000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tbp_output(S_done.EVENTS) = $ptascii(' + json.dumps(EXPECTED[name]) + ')',
    ]
    if name == 'aggregate-error-finally-cleanup':
        rows += [
            '~((HOBJECT n_guard) <- S_done.ALLOCATIONS)',
            '~((HARRAY n_operand_left) <- S_done.ALLOCATIONS)',
            '~((HARRAY n_operand_right) <- S_done.ALLOCATIONS)',
        ]
    return rows
