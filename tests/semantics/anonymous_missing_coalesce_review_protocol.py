#!/usr/bin/env python3
"""Independent missing-coalesce saved-name, receiver and fallback controls."""
import argparse
import hashlib
from pathlib import Path

import closure_call_protocol as protocol


SOURCE = '''<?php
function missing_fallback() { echo "F;"; return 23; }
$o = new class {
    public function __isset(string $name): bool {
        echo "I:", $name, ";";
        $name = "changed";
        $GLOBALS["o"] = null;
        return true;
    }
    public function __get($name) { echo "G:", $name, ";"; return null; }
    public function __destruct() { echo "D;"; }
};
$r = $o->missing ?? missing_fallback();
echo "R:", $r, ";";
echo $o === null ? "NULL;" : "BAD;";
'''
assert hashlib.sha256(SOURCE.encode()).hexdigest() == (
    '69bf532949c76382d150aaf60d4d150b86107ab1eb950fdaebbce40d842724b0')

REACHED = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.TARGET = PROPERTY_COALESCE_TARGET ppropertycoalesce true',
    'ppropertycoalesce.PROPERTY = eps',
    'ppropertycoalesce.NAME = $ptascii("missing") /\\ ppropertycoalesce.LINE = 13',
    'ppropertycoalesce.GET = (porigin_get)',
    'n_receiver = ppropertycoalesce.OBJECT',
    'S.OBJECTS[n_receiver] = INSTANCE ppropertycoalesce.CLASS',
    '(HOBJECT n_receiver) <- S.ALLOCATIONS',
    '~$instance_storage_freeing(S,n_receiver)',
    'S.FRAMES = [pframe]',
    'pframe.CONTEXT = eps',
    'pframe.ORIGIN = (ppropertycoalesce.SITE)',
    'pframe.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: ptask_tail*',
    '$property_coalesce_frame(S,pcallcontext,pframe,eps,ppropertycoalesce,true)',
    '$property_coalesce_entered(S,S.CURRENT,S.FRAMES,ppropertycoalesce,true)',
    '$property_coalesce_context(S,pcallcontext)',
    '$property_coalesce_active(S,S.CURRENT,S.FRAMES,n_receiver,ppropertycoalesce.NAME,true)',
    '~$property_coalesce_active(S,S.CURRENT,S.FRAMES,n_receiver,ppropertycoalesce.NAME,false)',
    '~$property_isset_guard(S,S.CURRENT,S.FRAMES,n_receiver,ppropertycoalesce.NAME)',
    '$property_empty_get_active(S,n_receiver,ppropertycoalesce.NAME)',
    '$task_nodes(PROPERTY_COALESCE_RESULT ppropertycoalesce true) = [HOBJECT n_receiver]',
    '$target_nodes(pcallcontext.TARGET) = eps /\\ $target_instance(pcallcontext.TARGET) = eps',
    '$call_receiver_roots(pcallcontext) = eps',
    '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1',
    '$lookup(S.ENV,$ptascii("name")) = (n_name)',
    'S.STORE[n_name] = DEFINED pvalue_name',
    '$string_bytes(pvalue_name) = (ppropertycoalesce.NAME)',
    'S_caller = $constant_frame_scope(S,pframe,eps)',
    '$lookup(S_caller.ENV,$ptascii("o")) = (n_o)',
    'S.STORE[n_o] = DEFINED PNULL',
    '$property_coalesce_valid(S_caller,ppropertycoalesce)',
    '~$property_coalesce_capture(S_caller,ppropertycoalesce)',
    '$property_coalesce_tail(S_caller,ppropertycoalesce,true,S_caller.TODO)',
    '$property_effective_desc(S,n_receiver,ppropertycoalesce.NAME) = eps',
    '$objectprops_at(S.OBJECTPROPS,n_receiver) = (eps)',
    '$property_coalesce_storage_capture(S,ppropertycoalesce)',
    '$property_empty_method(S,n_receiver,false) = (pmethoddesc_isset)',
    '$property_empty_method(S,n_receiver,true) = (pmethoddesc_get)',
    'pmethoddesc_isset.OWNER = pmethoddesc_get.OWNER',
    '$property_magic_method_source(S,pmethoddesc_isset,"__isset")',
    '$property_empty_get_source(S,pmethoddesc_get)',
    '$property_coalesce_function(S,ppropertycoalesce,false) = (pmethoddesc_isset.FUNCTION)',
    '$property_coalesce_function(S,ppropertycoalesce,true) = (pmethoddesc_get.FUNCTION)',
    '$call_current_valid(S) /\\ $call_frames_valid(S,S.FRAMES)',
    '$call_descriptors_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
]

DERIVED = [
    '~$property_coalesce_valid(S_caller,ppropertycoalesce[.PROPERTY = (porigin_get)])',
    '~$property_coalesce_valid(S_caller,ppropertycoalesce[.NAME = $ptascii("changed")])',
    '~$property_coalesce_valid(S_caller,ppropertycoalesce[.NAME = eps])',
    '~$property_coalesce_valid(S_caller,ppropertycoalesce[.LINE = 14])',
    '~$property_coalesce_valid(S_caller,ppropertycoalesce[.SITE = porigin_get])',
    '~$property_coalesce_valid(S_caller,ppropertycoalesce[.ISSET = porigin_get])',
    '~$property_coalesce_valid(S_caller,ppropertycoalesce[.GET = (ppropertycoalesce.ISSET)])',
    '~$property_coalesce_valid(S_caller,ppropertycoalesce[.CLASS = ppropertycoalesce.SITE])',
    '~$property_coalesce_valid(S_caller,ppropertycoalesce[.OBJECT = (|S.OBJECTS|)])',
    '~$property_coalesce_valid(S_caller[.SOURCES = eps],ppropertycoalesce)',
    '~$property_coalesce_valid(S_caller[.CODE = eps],ppropertycoalesce)',
    '~$property_coalesce_valid(S_caller,ppropertycoalesce[.TAIL = eps])',
    '~$property_coalesce_context(S,pcallcontext[.LINE = 14])',
    '~$property_coalesce_frame(S,pcallcontext,pframe[.TODO = ptask_tail*],eps,ppropertycoalesce,true)',
    'S_pending_get = S_caller[.TODO = (CALL_ARGS (PROPERTY_COALESCE_TARGET ppropertycoalesce true) eps 1 ([KNOWN (PSTRING ppropertycoalesce.NAME)]) (ppropertycoalesce.SITE) ppropertycoalesce.LINE) :: (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    '$property_coalesce_pending_call(S_pending_get,ppropertycoalesce,true)',
    'S_pending_isset = S_caller[.TODO = (CALL_ARGS (PROPERTY_COALESCE_TARGET ppropertycoalesce false) eps 1 ([KNOWN (PSTRING ppropertycoalesce.NAME)]) (ppropertycoalesce.SITE) ppropertycoalesce.LINE) :: (PROPERTY_COALESCE_RESULT ppropertycoalesce false) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    '~$property_coalesce_pending_call(S_pending_isset,ppropertycoalesce,false)',
    'S_fresh = S_caller[.STORE[n_o] = DEFINED (POBJECT n_receiver)]',
    '$property_coalesce_capture(S_fresh,ppropertycoalesce)',
    'ppropertyslot_value = {DECL eps, NAME ppropertycoalesce.NAME, STATE (PROP_VALUE (DIRECT (PINT 9)))}',
    'S_value = $objectprops_mark(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_receiver,[ppropertyslot_value])],n_receiver)',
    '$property_coalesce_context(S_value,pcallcontext)',
    '~$property_coalesce_storage_capture(S_value,ppropertycoalesce)',
    'S_value_caller = $constant_frame_scope(S_value,pframe,eps)[.STORE[n_o] = DEFINED (POBJECT n_receiver)]',
    '$property_coalesce_valid(S_value_caller,ppropertycoalesce)',
    '~$property_coalesce_capture(S_value_caller,ppropertycoalesce)',
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
    'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("D;"),OUTPUT $ptascii("F;"),OUTPUT $ptascii("R:"),OUTPUT $ptascii("23"),OUTPUT $ptascii(";"),OUTPUT $ptascii("NULL;")]',
    '$lookup(S_done.ENV,$ptascii("r")) = (n_result)',
    'S_done.STORE[n_result] = DEFINED (PINT 23)',
    '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
    '$call_descriptors_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
]

CASES = {
    'get-keeps-original-name-and-sole-receiver-before-fallback': {
        'source': SOURCE,
        'stage': ('S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.TARGET = PROPERTY_COALESCE_TARGET ppropertycoalesce true '
                  '-- if S.EVENTS = [OUTPUT $ptascii("I:"),OUTPUT $ptascii("missing"),'
                  'OUTPUT $ptascii(";"),OUTPUT $ptascii("G:"),OUTPUT $ptascii("missing"),'
                  'OUTPUT $ptascii(";")]'),
        'checks': REACHED + DERIVED + RESUME,
    },
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items()
                  if not args.case or name in args.case}, (Path(__file__),))
