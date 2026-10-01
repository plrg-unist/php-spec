#!/usr/bin/env python3
"""Focused forwarding ownership checks after the exit-cleanup projection."""
from pathlib import Path
import closure_call_protocol as protocol
import closure_call_reference_formal_protocol as formals

CASES = {name: formals.CASES[name] for name in (
    'call-ref-forward-caller-substitution',
)}
CASES['call-ref-exit-origin-cleanup'] = {
    'source': '<?php class A {} $a="1"; $c=function(int &$x){$x=9;echo $x;exit(7);}; try{foreach([0] as $k){$c->call(x:$a,newThis:new A);}}finally{echo "F";} echo "T";',
    'stage': 'S.TODO = [EXIT_UNWIND 7] -- if S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = CLOSURE_CALL_TARGET n_source n_receiver',
    'checks': [
        'S.ORIGIN = eps', 'S.CONSTCONTEXT = eps',
        'S.TRACE = eps', 'S.ERRORORIGIN = eps',
        '$task_nodes(EXIT_UNWIND 7) = eps',
        '$lookup(S.ENV, $ptascii("x")) = (n_temp)',
        'S.STORE[n_temp] = DEFINED (PINT 9)',
        'S.GLOBALTABLE = (psymboltable)',
        '$lookup(psymboltable.ENV, $ptascii("a")) = (n_caller)',
        'S.STORE[n_caller] = DEFINED (PSTRING $ptascii("1"))',
        'n_temp =/= n_caller',
        'pcallcontext.WRAPPER = (pnamedargs)',
        'pnamedargs.SLOTS = eps',
        'pnamedargs.NAMED = [($ptascii("x"), KNOWN (PSTRING $ptascii("1")))]',
        '$wrapper_context_valid(S, pcallcontext)',
        '$call_task_valid(S, EXIT_UNWIND 7)',
        '$call_descriptors_valid(S)', '$closure_state_valid(S)', '$heap_valid($heap_graph(S))',
        '~$call_task_valid(S[.ORIGIN = (pcallcontext.FUNCTION)], EXIT_UNWIND 7)',
        '~$call_descriptors_valid(S[.ORIGIN = (pcallcontext.FUNCTION)])',
        '~$call_descriptors_valid(S[.CURRENT = (pcallcontext[.WRAPPER = eps])])',
        'S_done = $drive(S[.COMPLETION = NORMAL], 1000)',
        'S_done.COMPLETION = EXITED 7', 'S_done.ORIGIN = eps',
        'S_done.CURRENT = eps', 'S_done.FRAMES = eps', 'S_done.TODO = eps',
        'S_done.ITERATORS = eps', 'S_done.SILENCES = eps',
        'S_done.EVENTS = S.EVENTS',
        '$lookup(S_done.ENV, $ptascii("a")) = (n_caller)',
        'S_done.STORE[n_caller] = DEFINED (PSTRING $ptascii("1"))',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ],
}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__), Path(formals.__file__)))
