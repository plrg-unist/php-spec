#!/usr/bin/env python3
"""Paused value forwarding and isolated reference-cell ownership for Closure::call."""
from pathlib import Path
import closure_call_protocol as protocol

ALIAS_SOURCE = '<?php class A {} $c=function(&$x){$x=9;}; $a=1; $c->call(new A,(function() use (&$a){return $a;})());'
CASES = {
    'call-ref-capture-known': {
        'source': '<?php class A {} $c=function(&$x){}; $x=1; $c->call(new A,$x);',
        'stage': 'S.TODO = (CLOSURE_CALL_INVOKE pclosurecall) :: ptask_tail*',
        'checks': [
            'pclosurecall.RAW = [(KINT 1, KNOWN (PINT 1))]',
            'pclosurecall.SENT.SLOTS = [NAMED_SENT (KNOWN (PINT 1))]',
            '$call_task_valid(S, CLOSURE_CALL_INVOKE pclosurecall)',
            '$call_descriptors_valid(S)', '$closure_state_valid(S)',
            '$heap_valid($heap_graph(S))',
            '~$call_task_valid(S, CLOSURE_CALL_INVOKE pclosurecall[.RAW = [(KINT 1, REFERENCE 0)]])',
        ],
    },
    'call-ref-forward-caller-substitution': {
        'source': ALIAS_SOURCE,
        'stage': 'S.TODO = (CLOSURE_CALL_FORWARD pclosurecall 0 pnamedargs n_base) :: ptask_tail*',
        'checks': [
            'pnamedargs = {SLOTS eps, NAMED eps}',
            'n_base = |S.STORE|',
            'pclosurecall.RAW = [(KINT 1, KNOWN (PINT 1))]',
            '$lookup(S.ENV, $ptascii("a")) = (n_cell_a)',
            'S.STORE[n_cell_a] = DEFINED (PINT 1)',
            '$(n_cell_a + 1) = |S.STORE|',
            '$call_reference_operand_valid(S, REFERENCE n_cell_a)',
            '$call_task_valid(S, CLOSURE_CALL_FORWARD pclosurecall 0 pnamedargs n_base)',
            '$call_descriptors_valid(S)', '$closure_state_valid(S)',
            '$heap_valid($heap_graph(S))',
            'pnamedargs_bad = pnamedargs[.SLOTS = [NAMED_SENT (REFERENCE n_cell_a)]]',
            'S_bad = S[.TODO = (CLOSURE_CALL_FORWARD pclosurecall 1 pnamedargs_bad n_cell_a) :: ptask_tail*]',
            '~$call_task_valid(S_bad, CLOSURE_CALL_FORWARD pclosurecall 1 pnamedargs_bad n_cell_a)',
            '~$call_descriptors_valid(S_bad)',
            '~$closure_state_valid(S_bad)',
            '~$call_task_valid(S, CLOSURE_CALL_FORWARD pclosurecall[.LINE = $(pclosurecall.LINE + 100)] 0 pnamedargs n_base)',
        ],
    },
    'call-ref-forward-fresh-cell': {
        'source': ALIAS_SOURCE,
        'stage': 'S.TODO = (CLOSURE_CALL_FORWARD pclosurecall 1 pnamedargs n_base) :: ptask_tail*',
        'checks': [
            'pnamedargs.SLOTS = [NAMED_SENT (REFERENCE n_temp)]',
            'n_temp = n_base', '$(n_base + 1) = |S.STORE|',
            'S.STORE[n_temp] = DEFINED (PINT 1)',
            '$lookup(S.ENV, $ptascii("a")) = (n_cell_a)',
            'S.STORE[n_cell_a] = DEFINED (PINT 1)',
            '$call_reference_operand_valid(S, REFERENCE n_cell_a)',
            'n_temp =/= n_cell_a',
            '(HCELL n_temp) <- $task_nodes(CLOSURE_CALL_FORWARD pclosurecall 1 pnamedargs n_base)',
            '(HOBJECT pclosurecall.SOURCE) <- $task_nodes(CLOSURE_CALL_FORWARD pclosurecall 1 pnamedargs n_base)',
            '$call_task_valid(S, CLOSURE_CALL_FORWARD pclosurecall 1 pnamedargs n_base)',
            '$call_descriptors_valid(S)', '$closure_state_valid(S)', '$heap_valid($heap_graph(S))',
            'pnamedargs_bad = pnamedargs[.SLOTS = [NAMED_SENT (REFERENCE n_cell_a)]]',
            '~$call_task_valid(S, CLOSURE_CALL_FORWARD pclosurecall 1 pnamedargs_bad n_base)',
            '~$call_task_valid(S, CLOSURE_CALL_FORWARD pclosurecall 0 pnamedargs n_base)',
            '~$call_task_valid(S, CLOSURE_CALL_FORWARD pclosurecall 1 pnamedargs $(n_base + 1))',
        ],
    },
    'call-ref-forward-pending-error': {
        'source': '<?php class A {} $c=function(&$x){}; $c->call(new A,x:(function(){echo "E";return 1;})(),z:(function(){echo "L";return 2;})());',
        'stage': 'S.TODO = (CLOSURE_CALL_FORWARD pclosurecall 1 pnamedargs n_base) :: ptask_tail* -- if pclosurecall.ERROR = (preqbytes)',
        'checks': [
            'pclosurecall.SENT = {SLOTS eps, NAMED eps}',
            'pclosurecall.RAW = [(KSTRING $ptascii("x"), KNOWN (PINT 1)), (KSTRING $ptascii("z"), KNOWN (PINT 2))]',
            'pnamedargs.SLOTS = [NAMED_SENT (REFERENCE n_temp)]',
            'n_temp = n_base', 'S.STORE[n_temp] = DEFINED (PINT 1)',
            '$call_task_valid(S, CLOSURE_CALL_FORWARD pclosurecall 1 pnamedargs n_base)',
            '$call_descriptors_valid(S)', '$closure_state_valid(S)', '$heap_valid($heap_graph(S))',
            '~$call_task_valid(S, CLOSURE_CALL_FORWARD pclosurecall[.ERROR = eps] 1 pnamedargs n_base)',
            '~$call_task_valid(S, CLOSURE_CALL_FORWARD pclosurecall[.RAW = [(KSTRING $ptascii("x"), VARIABLE $ptascii("x") 1), pclosurecall.RAW[1]]] 1 pnamedargs n_base)',
            '~$call_task_valid(S, CLOSURE_CALL_FORWARD pclosurecall 2 pnamedargs n_base)',
        ],
    },
    'call-ref-forward-named-order': {
        'source': '<?php class A {} $c=function(&$x,&$y){echo $x.$y;}; $c->call(y:2,newThis:new A,x:1);',
        'stage': 'S.TODO = (CLOSURE_CALL_FORWARD pclosurecall 1 pnamedargs n_base) :: ptask_tail*',
        'checks': [
            'pclosurecall.RAW = [(KSTRING $ptascii("y"), KNOWN (PINT 2)), (KSTRING $ptascii("x"), KNOWN (PINT 1))]',
            'pnamedargs.SLOTS = [NAMED_HOLE, NAMED_SENT (REFERENCE n_y)]',
            'n_y = n_base', 'S.STORE[n_y] = DEFINED (PINT 2)', '|S.EVENTS| = 1',
            '$call_task_valid(S, CLOSURE_CALL_FORWARD pclosurecall 1 pnamedargs n_base)',
            '$call_descriptors_valid(S)', '$closure_state_valid(S)', '$heap_valid($heap_graph(S))',
            'S_after = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
            'S_after.TODO = (CLOSURE_CALL_FORWARD pclosurecall 2 pnamedargs_after n_base) :: ptask_tail*',
            'pnamedargs_after.SLOTS = [NAMED_SENT (REFERENCE n_x), NAMED_SENT (REFERENCE n_y)]',
            'n_x = $(n_base + 1)', 'S_after.STORE[n_x] = DEFINED (PINT 1)', '|S_after.EVENTS| = 2',
            '$call_descriptors_valid(S_after)', '$closure_state_valid(S_after)', '$heap_valid($heap_graph(S_after))',
        ],
    },
}

CASES['call-ref-body-write-isolation'] = {
    'source': ALIAS_SOURCE,
    'stage': 'S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = CLOSURE_CALL_TARGET n_source n_receiver -- if $lookup(S.ENV, $ptascii("x")) = (n_temp) -- if S.STORE[n_temp] = DEFINED (PINT 9)',
    'checks': [
        'S.FRAMES[0] = pframe', 'pframe.LOCALS = eps', 'S.GLOBALTABLE = (psymboltable)',
        '$lookup(psymboltable.ENV, $ptascii("a")) = (n_cell_a)',
        'S.STORE[n_cell_a] = DEFINED (PINT 1)',
        '$call_reference_operand_valid(S, REFERENCE n_cell_a)',
        '$call_reference_operand_valid(S, REFERENCE n_temp)',
        'n_temp =/= n_cell_a',
        'pcallcontext.WRAPPER = (pnamedargs)',
        'pnamedargs.SLOTS = [NAMED_SENT (KNOWN (PINT 1))]',
        '$wrapper_context_valid(S, pcallcontext)',
        '$call_descriptors_valid(S)', '$closure_state_valid(S)', '$heap_valid($heap_graph(S))',
        '~$call_descriptors_valid(S[.CURRENT = (pcallcontext[.WRAPPER = eps])])',
    ],
}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__),))
