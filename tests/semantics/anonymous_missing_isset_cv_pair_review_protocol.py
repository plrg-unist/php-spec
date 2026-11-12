#!/usr/bin/env python3
"""Independent string-CV missing-isset captured-name and frame checks."""
import argparse
import hashlib
from pathlib import Path

import closure_call_protocol as protocol


SOURCE = '''<?php
$name = "missing";
$o = new class {
    public function __isset(string $incoming): bool {
        echo "I:", $incoming, ";";
        $incoming = "formal";
        $GLOBALS["name"] = "changed";
        $GLOBALS["o"] = null;
        return true;
    }
    public function __get($incoming) { echo "BAD-GET;"; return 0; }
    public function __destruct() { echo "D;"; }
};
echo isset($o->$name) ? "YES;" : "BAD;";
echo $name === "changed" ? "CHANGED;" : "BAD;";
echo $o === null ? "NULL;" : "BAD;";
'''
assert hashlib.sha256(SOURCE.encode()).hexdigest() == (
    '2074a30ee3080db6d1fa4ce664b9e0bda652dc8a6e20b2d577acda6371a98fe3')

REACHED = [
    'S.RESULT = KNOWN (PBOOL true)',
    '$call_task_valid(S,RETURN_VALUE z_return)',
    'ppropertyisset.PROPERTY = eps',
    'ppropertyisset.NAME = $ptascii("missing") /\\ ppropertyisset.LINE = 14',
    'n_receiver = ppropertyisset.OBJECT',
    'S.OBJECTS[n_receiver] = INSTANCE ppropertyisset.CLASS',
    '(HOBJECT n_receiver) <- S.ALLOCATIONS',
    '~$instance_storage_freeing(S,n_receiver)',
    'pframe.CONTEXT = eps /\\ pframe.ORIGIN = (ppropertyisset.SITE)',
    'pframe.TODO = (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*',
    '$property_isset_source(S,ppropertyisset)',
    '~$property_isset_empty(S,ppropertyisset)',
    '$property_isset_bool_pair(S,ppropertyisset)',
    '~$property_isset_untyped(S,ppropertyisset)',
    '$property_isset_frame(S,pcallcontext,pframe,ppropertyisset)',
    '$property_isset_entered(S,S.CURRENT,S.FRAMES,ppropertyisset)',
    '$property_isset_context(S,pcallcontext)',
    '$property_isset_guard(S,S.CURRENT,S.FRAMES,n_receiver,ppropertyisset.NAME)',
    '~$property_empty_get_active(S,n_receiver,ppropertyisset.NAME)',
    '~$property_get_guard_tasks(S.TODO,n_receiver,ppropertyisset.NAME)',
    '~$property_get_guard_frames(S.FRAMES,n_receiver,ppropertyisset.NAME)',
    '$task_nodes(PROPERTY_ISSET_RESULT ppropertyisset) = [HOBJECT n_receiver]',
    '$target_nodes(pcallcontext.TARGET) = eps /\\ $target_instance(pcallcontext.TARGET) = eps',
    '$call_receiver_roots(pcallcontext) = eps',
    '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1',
    '$lookup(S.ENV,$ptascii("incoming")) = (n_name)',
    'S.STORE[n_name] = DEFINED pvalue_name',
    '$string_bytes(pvalue_name) = ($ptascii("formal"))',
    '$property_isset_valid(S_caller,ppropertyisset)',
    '~$property_isset_capture(S_caller,ppropertyisset)',
    '$property_isset_tail(S_caller,ppropertyisset,S_caller.TODO)',
    '$property_isset_storage_capture(S_caller,ppropertyisset)',
    '$property_effective_desc(S,n_receiver,ppropertyisset.NAME) = eps',
    '$objectprops_at(S.OBJECTPROPS,n_receiver) = (eps)',
    '$property_isset_method(S,n_receiver) = (pmethoddesc_isset)',
    '$property_get_method(S,n_receiver) = (pmethoddesc_get)',
    'pmethoddesc_isset.OWNER = pmethoddesc_get.OWNER',
    '$property_magic_method_source(S,pmethoddesc_isset,"__isset")',
    '$property_empty_get_source(S,pmethoddesc_get)',
    '$property_isset_function(S,ppropertyisset) = (pmethoddesc_isset.FUNCTION)',
    '$target_function(S,METHOD_TARGET n_receiver pmethoddesc_get.FUNCTION.ORIGIN) = (pmethoddesc_get.FUNCTION)',
    '$call_current_valid(S) /\\ $call_frames_valid(S,S.FRAMES)',
    '$call_descriptors_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
    '$property_magic_cv_source(S,ppropertyisset.SITE,ppropertyisset.LINE)',
    '$property_isset_missing_source(S,ppropertyisset)',
    '$lookup(S_caller.ENV,$ptascii("name")) = (n_selector)',
    'S.STORE[n_selector] = DEFINED pvalue_selector',
    '$string_bytes(pvalue_selector) = ($ptascii("changed"))',
    '~$property_magic_name_capture(S_caller,ppropertyisset.SITE,ppropertyisset.LINE,ppropertyisset.NAME)',
    'S.HELD = eps',
]

DERIVED = [
    '~$property_isset_valid(S_caller,ppropertyisset[.PROPERTY = (ppropertyisset.METHOD)])',
    '~$property_isset_valid(S_caller,ppropertyisset[.NAME = eps])',
    '~$property_isset_valid(S_caller,ppropertyisset[.LINE = 15])',
    '~$property_isset_valid(S_caller,ppropertyisset[.SITE = ppropertyisset.METHOD])',
    '~$property_isset_valid(S_caller,ppropertyisset[.METHOD = pmethoddesc_get.FUNCTION.ORIGIN])',
    '~$property_isset_valid(S_caller,ppropertyisset[.CLASS = ppropertyisset.SITE])',
    '~$property_isset_valid(S_caller,ppropertyisset[.OBJECT = (|S.OBJECTS|)])',
    '~$property_isset_valid(S_caller[.SOURCES = eps],ppropertyisset)',
    '~$property_isset_valid(S_caller[.CODE = eps],ppropertyisset)',
    '~$property_isset_context(S,pcallcontext[.LINE = 15])',
    '~$property_isset_frame(S,pcallcontext,pframe[.TODO = ptask_tail*],ppropertyisset)',
    'ppropertyslot_value = {DECL eps, NAME ppropertyisset.NAME, STATE (PROP_VALUE (DIRECT (PINT 9)))}',
    'S_value = $objectprops_mark(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_receiver,[ppropertyslot_value])],n_receiver)',
    '$property_isset_context(S_value,pcallcontext)',
    '$property_isset_bool_pair(S_value,ppropertyisset)',
    '~$property_isset_storage_capture(S_value,ppropertyisset)',
    'S_value_caller = $constant_frame_scope(S_value,pframe,eps)[.STORE[n_o] = DEFINED (POBJECT n_receiver)][.STORE[n_selector] = DEFINED (PSTRING ($ptascii("missing")))]',
    '$property_isset_valid(S_value_caller,ppropertyisset)',
    '~$property_isset_capture(S_value_caller,ppropertyisset)',
    '$property_state_valid(S_value) /\\ $heap_valid($heap_graph(S_value))',
    'ppropertyisset_changed = ppropertyisset[.NAME = $ptascii("changed")]',
    '$property_isset_valid(S_caller,ppropertyisset_changed)',
    '~$property_isset_tail(S_caller,ppropertyisset_changed,S_caller.TODO)',
    'pcallcontext_changed = pcallcontext[.TARGET = PROPERTY_ISSET_TARGET ppropertyisset_changed]',
    '~$property_isset_context(S,pcallcontext_changed)',
    '~$property_isset_frame(S,pcallcontext_changed,pframe,ppropertyisset_changed)',
    'pframe_changed = pframe[.TODO = (PROPERTY_ISSET_RESULT ppropertyisset_changed) :: ptask_tail*]',
    '~$property_isset_frame(S,pcallcontext,pframe_changed,ppropertyisset)',
    '~$property_isset_context(S[.FRAMES = [pframe_changed]],pcallcontext)',
    'S_receiver_only = S_caller[.STORE[n_o] = DEFINED (POBJECT n_receiver)]',
    '~$property_isset_capture(S_receiver_only,ppropertyisset)',
    'S_name_only = S_caller[.STORE[n_selector] = DEFINED (PSTRING ($ptascii("missing")))]',
    '~$property_isset_capture(S_name_only,ppropertyisset)',
    'S_both = S_receiver_only[.STORE[n_selector] = DEFINED (PSTRING ($ptascii("missing")))]',
    '$property_magic_name_capture(S_both,ppropertyisset.SITE,ppropertyisset.LINE,ppropertyisset.NAME)',
    '$property_isset_capture(S_both,ppropertyisset)',
    '~$property_isset_capture(S_both,ppropertyisset_changed)',
    'S_pending = S_both[.TODO = (CALL_ARGS (PROPERTY_ISSET_TARGET ppropertyisset) eps 1 ([KNOWN (PSTRING ppropertyisset.NAME)]) (ppropertyisset.SITE) ppropertyisset.LINE) :: (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*]',
    '$property_isset_pending_call(S_pending,ppropertyisset)',
    'S_pending_changed = S_both[.TODO = (CALL_ARGS (PROPERTY_ISSET_TARGET ppropertyisset_changed) eps 1 ([KNOWN (PSTRING ppropertyisset_changed.NAME)]) (ppropertyisset_changed.SITE) ppropertyisset_changed.LINE) :: (PROPERTY_ISSET_RESULT ppropertyisset_changed) :: ptask_tail*]',
    '~$property_isset_pending_call(S_pending_changed,ppropertyisset_changed)',
    '~$call_selected_valid(S_pending_changed,PROPERTY_ISSET_TARGET ppropertyisset_changed,(ppropertyisset.SITE))',
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
    'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("D;"),OUTPUT $ptascii("YES;"),OUTPUT $ptascii("CHANGED;"),OUTPUT $ptascii("NULL;")]',
    '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
    '$call_descriptors_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
]

CASES = {
    'cv-name-keeps-history-after-selector-and-receiver-rebinding': {
        'source': SOURCE,
        'stage': ('S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.TARGET = PROPERTY_ISSET_TARGET ppropertyisset '
                  '-- if S.FRAMES = [pframe] '
                  '-- if S.EVENTS = [OUTPUT $ptascii("I:"),OUTPUT $ptascii("missing"),OUTPUT $ptascii(";")] '
                  '-- if S_caller = $constant_frame_scope(S,pframe,eps) '
                  '-- if $lookup(S_caller.ENV,$ptascii("o")) = (n_o) '
                  '-- if S.STORE[n_o] = DEFINED PNULL '
                  '-- if S.TODO = (RETURN_VALUE z_return) :: ptask_return*'),
        'checks': REACHED + DERIVED + RESUME,
    },
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items()
                  if not args.case or name in args.case}, (Path(__file__),))
