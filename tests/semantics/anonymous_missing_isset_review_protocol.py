#!/usr/bin/env python3
"""Independent absent-isset history and empty-boundary checks (fixture AL)."""
import argparse
import hashlib
from pathlib import Path

import closure_call_protocol as protocol


SOURCE = ('<?php\n'
          '$o = new class { public function __isset(string $name): bool { '
          '$GLOBALS["o"] = null; echo "ISSET:", $name, ";"; return true; } };\n'
          '$result = isset($o->missing);\n'
          'echo $result ? "T;" : "F;";\n'
          'echo $o === null ? "NULL;" : "BAD;";\n')
assert hashlib.sha256(SOURCE.encode()).hexdigest() == (
    'a887ba18180dfbe443d32213ae2a36519e37059b7b2b1291e587a2105c74cc65')

REACHED = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.TARGET = PROPERTY_ISSET_TARGET ppropertyisset',
    'ppropertyisset.PROPERTY = eps',
    'ppropertyisset.NAME = $ptascii("missing")',
    'ppropertyisset.LINE = 3',
    'n_receiver = ppropertyisset.OBJECT',
    'S.OBJECTS[n_receiver] = INSTANCE ppropertyisset.CLASS',
    '(HOBJECT n_receiver) <- S.ALLOCATIONS',
    'S.FRAMES = [pframe]',
    'pframe.CONTEXT = eps',
    'pframe.TODO = (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*',
    '$property_isset_frame(S,pcallcontext,pframe,ppropertyisset)',
    '$property_isset_entered(S,S.CURRENT,S.FRAMES,ppropertyisset)',
    '$property_isset_context(S,pcallcontext)',
    '$property_isset_guard(S,S.CURRENT,S.FRAMES,n_receiver,ppropertyisset.NAME)',
    '$task_nodes(PROPERTY_ISSET_RESULT ppropertyisset) = [HOBJECT n_receiver]',
    '$target_nodes(pcallcontext.TARGET) = eps',
    '$target_instance(pcallcontext.TARGET) = eps',
    '$call_receiver_roots(pcallcontext) = eps',
    '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1',
    'S_caller = $constant_frame_scope(S,pframe,eps)',
    '$lookup(S_caller.ENV,$ptascii("o")) = (n_cell)',
    'S.STORE[n_cell] = DEFINED PNULL',
    '$property_isset_valid(S_caller,ppropertyisset)',
    '~$property_isset_capture(S_caller,ppropertyisset)',
    '$property_isset_tail(S_caller,ppropertyisset,S_caller.TODO)',
    '$property_isset_storage_capture(S_caller,ppropertyisset)',
    '$property_effective_desc(S,n_receiver,ppropertyisset.NAME) = eps',
    '$property_get_method(S,n_receiver) = eps',
    '$property_isset_method(S,n_receiver) = (pmethoddesc)',
    '$property_magic_method_source(S,pmethoddesc,"__isset")',
    '$property_isset_function(S,ppropertyisset) = (pmethoddesc.FUNCTION)',
    '$objectprops_at(S.OBJECTPROPS,n_receiver) = (eps)',
    '$call_current_valid(S)',
    '$call_frames_valid(S,S.FRAMES)',
    '$call_descriptors_valid(S)',
    '$property_state_valid(S)',
    '$heap_valid($heap_graph(S))',
]

DERIVED = [
    '~$property_isset_valid(S_caller,ppropertyisset[.PROPERTY = (ppropertyisset.METHOD)])',
    '~$property_isset_valid(S_caller,ppropertyisset[.NAME = eps])',
    '~$property_isset_valid(S_caller,ppropertyisset[.NAME = ([0] ++ ppropertyisset.NAME)])',
    '~$property_isset_valid(S_caller,ppropertyisset[.LINE = 4])',
    '~$property_isset_valid(S_caller,ppropertyisset[.SITE = ppropertyisset.METHOD])',
    '~$property_isset_valid(S_caller,ppropertyisset[.METHOD = ppropertyisset.SITE])',
    '~$property_isset_valid(S_caller,ppropertyisset[.CLASS = ppropertyisset.SITE])',
    '~$property_isset_valid(S_caller,ppropertyisset[.OBJECT = (|S.OBJECTS|)])',
    '~$property_isset_valid(S_caller[.SOURCES = eps],ppropertyisset)',
    '~$property_isset_valid(S_caller[.CODE = eps],ppropertyisset)',
    '~$property_isset_context(S,pcallcontext[.LINE = 4])',
    '~$property_isset_frame(S,pcallcontext,pframe[.TODO = ptask_tail*],ppropertyisset)',
    'ppropertyslot_dynamic = {DECL eps, NAME ppropertyisset.NAME, STATE (PROP_VALUE (DIRECT (PINT 7)))}',
    'S_history = $objectprops_mark(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_receiver,[ppropertyslot_dynamic])],n_receiver)',
    '$property_isset_valid(S_history,ppropertyisset)',
    '~$property_isset_storage_capture(S_history,ppropertyisset)',
    '$property_isset_frame(S_history,pcallcontext,pframe,ppropertyisset)',
    '$property_isset_context(S_history,pcallcontext)',
    '$call_current_valid(S_history)',
    '$call_frames_valid(S_history,S_history.FRAMES)',
    '$property_state_valid(S_history)',
    '$heap_owners($heap_graph(S_history),HOBJECT n_receiver) = 1',
    'S_history_caller = $constant_frame_scope(S_history,pframe,eps)',
    '$property_isset_tail(S_history_caller,ppropertyisset,S_history_caller.TODO)',
    '~$property_isset_capture(S_history_caller,ppropertyisset)',
    'S_result = S_history_caller[.RESULT = KNOWN (PBOOL true)][.BASE = BASE_VALUE (KNOWN PNULL)]',
    'PhpStep: S_result ~> S_result_after',
    'S_result_after.RESULT = KNOWN (PBOOL true)',
    'S_result_after.TODO = ptask_tail*',
    'S_result_after.BASE = BASE_VALUE (KNOWN PNULL)',
]

RESUME = [
    'S_zero = $drive_steps(S,0)',
    'S_zero.COMPLETION = BUDGET',
    'S_zero[.COMPLETION = NORMAL] = S',
    'S_one = $drive_steps(S,1)',
    'S_one.COMPLETION = BUDGET',
    'S_done = $drive_steps(S,4096)',
    '$drive_steps(S_one[.COMPLETION = NORMAL],4095) = S_done',
    '$drive_steps(S_zero[.COMPLETION = NORMAL],4096) = S_done',
    'S_done.COMPLETION = NORMAL',
    'S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.HELD = eps',
    'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("T;"), OUTPUT $ptascii("NULL;")]',
    '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
    '$call_descriptors_valid(S_done)',
    '$property_state_valid(S_done)',
    '$heap_valid($heap_graph(S_done))',
]

CASES = {
    'globals-removal-retains-selected-receiver': {
        'source': SOURCE,
        'stage': ('S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.TARGET = PROPERTY_ISSET_TARGET ppropertyisset '
                  '-- if S.EVENTS = [OUTPUT $ptascii("ISSET:"), '
                  'OUTPUT $ptascii("missing"), OUTPUT $ptascii(";")]'),
        'checks': REACHED + DERIVED + RESUME,
    },
    'absent-empty-remains-explicitly-unsupported': {
        'source': '<?php\n$o = new class { public function __isset(string $name): bool { echo "CALLED;"; return true; } };\n$result = empty($o->missing);\n',
        'stage': ('S.CURRENT = eps -- if S.TODO = (ISSET_RESULT true z) :: ptask_tail* '
                  '-- if S.BASE = BASE_PROPERTY (POBJECT n_receiver) ($ptascii("missing"))'),
        'checks': [
            'S.ORIGIN = (porigin_site)',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_class',
            '$property_isset_method(S,n_receiver) = (pmethoddesc)',
            '$property_magic_method_source(S,pmethoddesc,"__isset")',
            '$property_effective_desc(S,n_receiver,$ptascii("missing")) = eps',
            '$property_isset_needed(S,n_receiver,$ptascii("missing"))',
            'ppropertyisset = {SITE porigin_site, NAME $ptascii("missing"), LINE z, OBJECT n_receiver, CLASS porigin_class, METHOD pmethoddesc.FUNCTION.ORIGIN, PROPERTY eps}',
            '$property_isset_empty(S,ppropertyisset)',
            '$property_isset_source(S,ppropertyisset)',
            '~$property_isset_valid(S,ppropertyisset)',
            '~$property_isset_capture(S,ppropertyisset)',
            '$property_isset_plan(S) = eps',
            '$property_empty_pending(S)',
            '$property_empty_plan(S) = eps',
            'S.EVENTS = eps',
            'PhpStep: S ~> S_stopped',
            'S_stopped.COMPLETION = UNSUPPORTED "magic empty source, methods, or recursive access"',
            'S_stopped.EVENTS = eps',
        ],
    },
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items()
                  if not args.case or name in args.case}, (Path(__file__),))
