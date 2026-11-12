#!/usr/bin/env python3
"""Independent missing-unset capture, history, ownership and cache controls."""
import argparse
import hashlib
from pathlib import Path

import closure_call_protocol as protocol


SOURCE = ('<?php\n$o = new class {\n'
          '    public function __get($name) { echo "BAD_GET;"; return 7; }\n'
          '    public function __isset(string $name): bool { echo "BAD_ISSET;"; return true; }\n'
          '    public function __unset(string $name): void { $GLOBALS["o"] = null; echo "DROP:", $name, ";"; }\n'
          '};\nunset($o->missing);\necho $o === null ? "NULL;" : "BAD;";\n')
assert hashlib.sha256(SOURCE.encode()).hexdigest() == (
    '80fc35da30fc8fb298756e6433999f8a15087d8fa38d7b081bf7e0cad1349178')

REACHED = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.TARGET = PROPERTY_UNSET_TARGET ppropertyunset',
    'ppropertyunset.PROPERTY = eps',
    'ppropertyunset.NAME = $ptascii("missing") /\\ ppropertyunset.LINE = 7',
    'n_receiver = ppropertyunset.OBJECT',
    'S.OBJECTS[n_receiver] = INSTANCE ppropertyunset.CLASS',
    '(HOBJECT n_receiver) <- S.ALLOCATIONS',
    'S.FRAMES = [pframe]',
    'pframe.CONTEXT = eps',
    'pframe.TODO = (PROPERTY_UNSET_RESULT ppropertyunset) :: ptask_tail*',
    '$property_unset_frame(S,pcallcontext,pframe,ppropertyunset)',
    '$property_unset_context(S,pcallcontext)',
    '$property_unset_guard(S,S.CURRENT,S.FRAMES,n_receiver,ppropertyunset.NAME)',
    '$task_nodes(PROPERTY_UNSET_RESULT ppropertyunset) = [HOBJECT n_receiver]',
    '$target_nodes(pcallcontext.TARGET) = eps /\\ $target_instance(pcallcontext.TARGET) = eps',
    '$call_receiver_roots(pcallcontext) = eps',
    '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1',
    'S_caller = $constant_frame_scope(S,pframe,eps)',
    '$lookup(S_caller.ENV,$ptascii("o")) = (n_cell)',
    'S.STORE[n_cell] = DEFINED PNULL',
    '$property_unset_valid(S_caller,ppropertyunset)',
    '~$property_unset_capture(S_caller,ppropertyunset)',
    '$property_unset_tail(S_caller,ppropertyunset,S_caller.TODO)',
    '$property_unset_capture_state(S_caller,ppropertyunset)',
    '$property_effective_desc(S,n_receiver,ppropertyunset.NAME) = eps',
    '$property_get_method(S,n_receiver) = (pmethoddesc_get)',
    '$property_isset_method(S,n_receiver) = (pmethoddesc_isset)',
    '$property_unset_method(S,n_receiver) = (pmethoddesc_unset)',
    '$property_magic_method_source(S,pmethoddesc_unset,"__unset")',
    '$property_unset_function(S,ppropertyunset) = (pmethoddesc_unset.FUNCTION)',
    '$objectprops_at(S.OBJECTPROPS,n_receiver) = (eps)',
    '$object_table_at(S.OBJECTTABLES,n_receiver) = eps',
    '$call_current_valid(S) /\\ $call_frames_valid(S,S.FRAMES)',
    '$call_descriptors_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
]

DERIVED = [
    '~$property_unset_valid(S_caller,ppropertyunset[.PROPERTY = (pmethoddesc_get.FUNCTION.ORIGIN)])',
    '~$property_unset_valid(S_caller,ppropertyunset[.NAME = eps])',
    '~$property_unset_valid(S_caller,ppropertyunset[.NAME = ([0] ++ ppropertyunset.NAME)])',
    '~$property_unset_valid(S_caller,ppropertyunset[.LINE = 8])',
    '~$property_unset_valid(S_caller,ppropertyunset[.SITE = ppropertyunset.METHOD])',
    '~$property_unset_valid(S_caller,ppropertyunset[.METHOD = pmethoddesc_get.FUNCTION.ORIGIN])',
    '~$property_unset_valid(S_caller,ppropertyunset[.CLASS = ppropertyunset.SITE])',
    '~$property_unset_valid(S_caller,ppropertyunset[.OBJECT = (|S.OBJECTS|)])',
    '~$property_unset_valid(S_caller[.SOURCES = eps],ppropertyunset)',
    '~$property_unset_valid(S_caller[.CODE = eps],ppropertyunset)',
    '~$property_unset_context(S,pcallcontext[.LINE = 8])',
    '~$property_unset_frame(S,pcallcontext,pframe[.TODO = ptask_tail*],ppropertyunset)',
    'S_cached = $object_table_materialize(S,n_receiver)',
    'S_cached.COMPLETION = NORMAL',
    '$object_table_at(S_cached.OBJECTTABLES,n_receiver) = (n_table)',
    '$property_unset_valid(S_cached,ppropertyunset)',
    '$property_unset_frame(S_cached,pcallcontext,pframe,ppropertyunset)',
    '$property_unset_context(S_cached,pcallcontext)',
    '~$property_unset_capture_state(S_cached,ppropertyunset)',
    '$property_state_valid(S_cached) /\\ $object_tables_valid(S_cached) /\\ $heap_valid($heap_graph(S_cached))',
    'ppropertyslot_value = {DECL eps, NAME ppropertyunset.NAME, STATE (PROP_VALUE (DIRECT (PINT 9)))}',
    'S_value = $objectprops_mark(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_receiver,[ppropertyslot_value])],n_receiver)',
    '$property_unset_valid(S_value,ppropertyunset)',
    '$property_unset_context(S_value,pcallcontext)',
    '~$property_unset_capture_state(S_value,ppropertyunset)',
    '$property_state_valid(S_value) /\\ $heap_valid($heap_graph(S_value))',
    'S_result = $constant_frame_scope(S_value,pframe,eps)[.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    'PhpStep: S_result ~> S_after',
    'S_after.TODO = ptask_tail* /\\ S_after.RESULT = KNOWN PNULL',
    'S_after.OBJECTPROPS = S_result.OBJECTPROPS',
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
    'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("NULL;")]',
    '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
    '$call_descriptors_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
]

CASES = {
    'getters-stay-idle-after-globals-cv-clearing': {
        'source': SOURCE,
        'stage': ('S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.TARGET = PROPERTY_UNSET_TARGET ppropertyunset '
                  '-- if S.EVENTS = [OUTPUT $ptascii("DROP:"), '
                  'OUTPUT $ptascii("missing"), OUTPUT $ptascii(";")]'),
        'checks': REACHED + DERIVED + RESUME,
    },
    'source-cached-table-entry-remains-unsupported': {
        'source': '<?php\n$o = new class { public function __unset(string $name): void { echo "CALLED;"; } };\nforeach ($o as $key => $value) {}\n$copy = (array)$o;\nunset($o->missing);\necho "AFTER;";\n',
        'stage': ('S.CURRENT = eps -- if S.TODO = UNSET_ARRAY :: ptask_tail* '
                  '-- if S.BASE = BASE_PROPERTY_PENDING pbase (KNOWN (PSTRING ($ptascii("missing")))) z_receiver '
                  '-- if $property_unset_pending_receiver(S,pbase) = (n_receiver)'),
        'checks': [
            'S.ORIGIN = (porigin_site)',
            'S.RESULT = KNOWN PNULL',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_class',
            '$property_unset_method(S,n_receiver) = (pmethoddesc)',
            '$property_magic_method_source(S,pmethoddesc,"__unset")',
            '$property_effective_desc(S,n_receiver,$ptascii("missing")) = eps',
            '$property_unset_needed(S,n_receiver,$ptascii("missing"))',
            '$objectprops_at(S.OBJECTPROPS,n_receiver) = (eps)',
            '$object_table_at(S.OBJECTTABLES,n_receiver) = (n_table)',
            '$lookup(S.ENV,$ptascii("copy")) = (n_copy)',
            'S.STORE[n_copy] = DEFINED (PARRAY n_table)',
            '$heap_owners($heap_graph(S),HARRAY n_table) = 2',
            'ppropertyunset = {SITE porigin_site, NAME $ptascii("missing"), LINE 5, OBJECT n_receiver, CLASS porigin_class, METHOD pmethoddesc.FUNCTION.ORIGIN, PROPERTY eps}',
            '$property_unset_valid(S,ppropertyunset)',
            '~$property_unset_capture_state(S,ppropertyunset)',
            '~$property_unset_capture(S,ppropertyunset)',
            '$property_unset_absent_candidate(S) = eps',
            '$property_unset_plan(S) = eps',
            '$property_unset_absent_guarded_plan(S) = eps',
            '$property_unset_pending(S)',
            '$class_state_valid(S) /\\ $object_tables_valid(S) /\\ $heap_valid($heap_graph(S))',
            'S.EVENTS = eps',
            'PhpStep: S ~> S_stopped',
            'S_stopped.COMPLETION = UNSUPPORTED "magic unset source, function, or recursive access"',
            'S_stopped.EVENTS = eps',
            'S_stopped.OBJECTTABLES = S.OBJECTTABLES /\\ S_stopped.ARRAYS = S.ARRAYS',
        ],
    },
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items()
                  if not args.case or name in args.case}, (Path(__file__),))
