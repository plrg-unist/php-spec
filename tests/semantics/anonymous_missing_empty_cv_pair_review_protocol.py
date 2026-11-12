#!/usr/bin/env python3
"""Independent CV-name Empty handoff and captured-name checks."""
import argparse
import hashlib
from pathlib import Path

import closure_call_protocol as protocol


SOURCE = '''<?php
$name = "missing";
$o = new class {
    public function __isset(string $incoming): bool {
        echo "I:", $incoming, ";";
        $incoming = "isset-formal";
        $GLOBALS["name"] = "changed";
        $GLOBALS["o"] = null;
        return true;
    }
    public function __get($incoming) {
        echo "G:", $incoming, ";";
        $incoming = "get-formal";
        return 0;
    }
    public function __destruct() { echo "D;"; }
};
echo empty($o->$name) ? "EMPTY;" : "BAD;";
echo $name === "changed" ? "CHANGED;" : "BAD;";
echo $o === null ? "NULL;" : "BAD;";
'''
assert hashlib.sha256(SOURCE.encode()).hexdigest() == (
    'e67c41fe08e25c1524f541737c93551818b1c9328594e99776f91686ea9e9d09')

REACHED = [
    'S.RESULT = KNOWN (PINT 0) /\\ S.HELD = eps',
    '$call_task_valid(S,RETURN_VALUE z_return)',
    'ppropertyempty.PROPERTY = eps',
    'ppropertyempty.NAME = $ptascii("missing") /\\ ppropertyempty.LINE = 18',
    'n_receiver = ppropertyempty.OBJECT',
    'S.OBJECTS[n_receiver] = INSTANCE ppropertyempty.CLASS',
    '(HOBJECT n_receiver) <- S.ALLOCATIONS /\\ ~$instance_storage_freeing(S,n_receiver)',
    'S.FRAMES = [pframe]',
    'pframe.CONTEXT = eps /\\ pframe.ORIGIN = (ppropertyempty.SITE)',
    'pframe.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail*',
    '$property_empty_frame(S,pcallcontext,pframe,ppropertyempty,true)',
    '$property_empty_entered(S,S.CURRENT,S.FRAMES,ppropertyempty,true)',
    '$property_empty_context(S,pcallcontext)',
    '$property_empty_guard(S,n_receiver,ppropertyempty.NAME) /\\ $property_empty_get_active(S,n_receiver,ppropertyempty.NAME)',
    '$task_nodes(PROPERTY_EMPTY_RESULT ppropertyempty true) = [HOBJECT n_receiver]',
    '$target_nodes(pcallcontext.TARGET) = eps /\\ $target_instance(pcallcontext.TARGET) = eps /\\ $call_receiver_roots(pcallcontext) = eps',
    '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1',
    '$lookup(S.ENV,$ptascii("incoming")) = (n_formal)',
    'S.STORE[n_formal] = DEFINED pvalue_formal',
    '$string_bytes(pvalue_formal) = ($ptascii("get-formal"))',
    'S_caller = $constant_frame_scope(S,pframe,eps)',
    '$lookup(S_caller.ENV,$ptascii("o")) = (n_o)',
    'S.STORE[n_o] = DEFINED PNULL',
    '$lookup(S_caller.ENV,$ptascii("name")) = (n_selector)',
    'S.STORE[n_selector] = DEFINED pvalue_selector',
    '$string_bytes(pvalue_selector) = ($ptascii("changed"))',
    '$property_magic_cv_source(S,ppropertyempty.SITE,ppropertyempty.LINE)',
    '$property_empty_source(S,ppropertyempty.SITE,ppropertyempty.NAME,ppropertyempty.LINE)',
    '$property_empty_valid(S_caller,ppropertyempty) /\\ ~$property_empty_capture(S_caller,ppropertyempty)',
    '$property_empty_tail(S_caller,ppropertyempty,true,S_caller.TODO)',
    '$objectprops_at(S.OBJECTPROPS,n_receiver) = (eps) /\\ $property_empty_storage_capture(S,ppropertyempty)',
    'S.EVENTS = [OUTPUT $ptascii("I:"),OUTPUT $ptascii("missing"),OUTPUT $ptascii(";"),OUTPUT $ptascii("G:"),OUTPUT $ptascii("missing"),OUTPUT $ptascii(";")]',
    '$call_descriptors_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
]

DERIVED = [
    '~$property_empty_valid(S_caller,ppropertyempty[.PROPERTY = (ppropertyempty.GET)])',
    '~$property_empty_valid(S_caller,ppropertyempty[.NAME = eps])',
    '~$property_empty_valid(S_caller,ppropertyempty[.LINE = 19])',
    '~$property_empty_valid(S_caller,ppropertyempty[.SITE = ppropertyempty.GET])',
    '~$property_empty_valid(S_caller,ppropertyempty[.ISSET = ppropertyempty.GET])',
    '~$property_empty_valid(S_caller,ppropertyempty[.GET = ppropertyempty.ISSET])',
    '~$property_empty_valid(S_caller,ppropertyempty[.CLASS = ppropertyempty.SITE])',
    '~$property_empty_valid(S_caller,ppropertyempty[.OBJECT = (|S.OBJECTS|)])',
    '~$property_empty_valid(S_caller[.SOURCES = eps],ppropertyempty)',
    '~$property_empty_valid(S_caller[.CODE = eps],ppropertyempty)',
    'ppropertyempty_changed = ppropertyempty[.NAME = $ptascii("changed")]',
    '$property_empty_valid(S_caller,ppropertyempty_changed)',
    '~$property_empty_tail(S_caller,ppropertyempty_changed,true,S_caller.TODO)',
    '~$property_empty_context(S,pcallcontext[.TARGET = PROPERTY_EMPTY_TARGET ppropertyempty_changed true])',
    'pframe_changed = pframe[.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty_changed true) :: ptask_tail*]',
    '~$property_empty_frame(S,pcallcontext,pframe_changed,ppropertyempty,true)',
    'S_pending_get = S_caller[.TODO = (CALL_ARGS (PROPERTY_EMPTY_TARGET ppropertyempty true) eps 1 ([KNOWN (PSTRING ppropertyempty.NAME)]) (ppropertyempty.SITE) ppropertyempty.LINE) :: (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    '$property_empty_pending_call(S_pending_get,ppropertyempty,true)',
    'S_pending_isset = S_caller[.TODO = (CALL_ARGS (PROPERTY_EMPTY_TARGET ppropertyempty false) eps 1 ([KNOWN (PSTRING ppropertyempty.NAME)]) (ppropertyempty.SITE) ppropertyempty.LINE) :: (PROPERTY_EMPTY_RESULT ppropertyempty false) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    '~$property_empty_pending_call(S_pending_isset,ppropertyempty,false)',
    'S_receiver_only = S_caller[.STORE[n_o] = DEFINED (POBJECT n_receiver)]',
    '~$property_empty_capture(S_receiver_only,ppropertyempty)',
    'S_name_only = S_caller[.STORE[n_selector] = DEFINED (PSTRING ($ptascii("missing")))]',
    '~$property_empty_capture(S_name_only,ppropertyempty)',
    'S_both = S_receiver_only[.STORE[n_selector] = DEFINED (PSTRING ($ptascii("missing")))]',
    '$property_empty_capture(S_both,ppropertyempty) /\\ ~$property_empty_capture(S_both,ppropertyempty_changed)',
    '$property_empty_pending_call(S_pending_isset[.STORE = S_both.STORE],ppropertyempty,false)',
    'S_pending_forged = S_both[.TODO = (CALL_ARGS (PROPERTY_EMPTY_TARGET ppropertyempty_changed false) eps 1 ([KNOWN (PSTRING ppropertyempty_changed.NAME)]) (ppropertyempty_changed.SITE) ppropertyempty_changed.LINE) :: (PROPERTY_EMPTY_RESULT ppropertyempty_changed false) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    '~$property_empty_pending_call(S_pending_forged,ppropertyempty_changed,false)',
    'ppropertyslot_value = {DECL eps, NAME ppropertyempty.NAME, STATE (PROP_VALUE (DIRECT (PINT 9)))}',
    'S_value = $objectprops_mark(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_receiver,[ppropertyslot_value])],n_receiver)',
    '$property_empty_context(S_value,pcallcontext) /\\ ~$property_empty_storage_capture(S_value,ppropertyempty)',
    'S_value_caller = $constant_frame_scope(S_value,pframe,eps)[.STORE = S_both.STORE]',
    '~$property_empty_capture(S_value_caller,ppropertyempty)',
    '$property_state_valid(S_value) /\\ $heap_valid($heap_graph(S_value))',
]

RESUME = [
    'S_zero = $drive_steps(S,0)',
    'S_zero.COMPLETION = BUDGET /\\ S_zero[.COMPLETION = NORMAL] = S',
    'S_one = $drive_steps(S,1)',
    'S_one.COMPLETION = BUDGET',
    'S_done = $drive_steps(S,4096)',
    '$drive_steps(S_one[.COMPLETION = NORMAL],4095) = S_done',
    '$drive_steps(S_zero[.COMPLETION = NORMAL],4096) = S_done',
    'S_done.COMPLETION = NORMAL',
    'S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.HELD = eps',
    'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("D;"),OUTPUT $ptascii("EMPTY;"),OUTPUT $ptascii("CHANGED;"),OUTPUT $ptascii("NULL;")]',
    '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
    '$call_descriptors_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
]

CASES = {
    'cv-empty-get-retains-name-after-both-selectors-change': {
        'source': SOURCE,
        'stage': ('S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.TARGET = PROPERTY_EMPTY_TARGET ppropertyempty true '
                  '-- if S.TODO = (RETURN_VALUE z_return) :: ptask_return* '
                  '-- if S.RESULT = KNOWN (PINT 0)'),
        'checks': REACHED + DERIVED + RESUME,
    },
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items()
                  if not args.case or name in args.case}, (Path(__file__),))
