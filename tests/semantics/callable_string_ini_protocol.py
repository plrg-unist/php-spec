#!/usr/bin/env python3
"""Live receiver and raw/effective INI boundary after callable reception."""
from callable_string_ini import CASES as SOURCES, CATALOGUE
import include_mutable_protocol
from pathlib import Path

CASES = [(
    'ini-prefix-callable-string-live-owner-set-result',
    SOURCES['weak-callable-string-named-raw-effective-ini'],
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*\n'
    '  -- if pconfigcall.KIND = INTRINSIC_SET_INCLUDE_PATH',
    [
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.KIND = INTRINSIC_SET_INCLUDE_PATH',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (PSTRING $ptascii("last")))]',
        'pconfigcall.OWNER = eps',
        'S.CURRENT = (pcallcontext)',
        'pcallcontext.RECEIVER = (n_receiver)',
        '$object_invoke_method(S,n_receiver) = (pmethoddesc)',
        'pcallcontext.FUNCTION = pmethoddesc.FUNCTION.ORIGIN',
        'pcallcontext.TARGET = METHOD_TARGET n_receiver pmethoddesc.FUNCTION.ORIGIN',
        'pcallcontext.LEXICAL_CLASS = (pmethoddesc.OWNER)',
        'pcallcontext.CALLED_CLASS = (porigin_called)',
        'pcallcontext.INSTANCE = eps',
        'S.OBJECTS[n_receiver] = INSTANCE porigin_called',
        '(HOBJECT n_receiver) <- S.ALLOCATIONS',
        '(HOBJECT n_receiver) <- $machine_roots(S)',
        '$(|S.FRAMES| > 0)',
        '$typed_callable(S,POBJECT n_receiver) = (true)',
        'S.FILEINCLUDEPATH = ($ptascii("first") ++ [0] ++ $ptascii("tail"))',
        '$outputs(S.EVENTS) = $ptascii("R:")',
        '$config_invoke_valid(S,pconfigcall)',
        '$call_descriptors_valid(S)',
        '~$config_call_valid(S,pconfigcall[.LINE = 999])',
        '~$config_call_valid(S,pconfigcall[.SITE = pcallcontext.FUNCTION])',
        '~$config_selected_valid(S,pconfigcall[.OWNER = (999)])',
        '~$call_descriptors_valid(S[.CURRENT = (pcallcontext[.RECEIVER = eps])])',
        '~$call_descriptors_valid(S[.CURRENT = (pcallcontext[.LEXICAL_CLASS = eps])])',
        'S_ready = $config_receive(S,pconfigcall)',
        'S_ready.COMPLETION = NORMAL',
        'S_ready.TODO = ptask_tail*',
        'S_ready.RESULT = KNOWN (PSTRING $ptascii("first"))',
        'S_ready.FILEINCLUDEPATH = ($ptascii("last"))',
        'S_ready.FILECWD = S.FILECWD',
        'S_ready.CURRENT = S.CURRENT',
        'S_ready.FRAMES = S.FRAMES',
        'S_ready.STORE = S.STORE',
        'S_ready.OBJECTS = S.OBJECTS',
        'S_ready.ALLOCATIONS = S.ALLOCATIONS',
        'S_ready.EVENTS = S.EVENTS',
        '$call_descriptors_valid(S_ready)',
        'S_done = $drive_steps(S_ready,1000)',
        'S_done.COMPLETION = NORMAL',
        'S_done.FILEINCLUDEPATH = ($ptascii("last"))',
        '$outputs(S_done.EVENTS) = $ptascii("R:first")',
        '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
    ],
)]

def main():
    include_mutable_protocol.main(CASES, (Path(__file__), CATALOGUE))

if __name__ == '__main__':
    main()
