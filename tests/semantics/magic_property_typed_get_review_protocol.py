#!/usr/bin/env python3
"""Independent typed-Get reception and saved history in fixture SL_mode."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol


CATALOGUE = Path(__file__).with_name('magic_property_typed_get_review_cases.json')
row = next(row for row in json.loads(CATALOGUE.read_text())['cases']
           if row['id'] == 'typed-get-reception-keeps-empty-name-after-rebinding')
SOURCE = row['source']
assert hashlib.sha256(SOURCE.encode()).hexdigest() == (
    '7c1a8bb427ed6f0cf18017f05b8c98e1039c14e0ec912f0bf6fe3e43a274cb94')


REACHED = [
    'S.RESULT = KNOWN (PINT 0) /\\ S.HELD = eps',
    '$call_task_valid(S,RETURN_VALUE z_return)',
    'ppropertycoalesce.PROPERTY = eps',
    'ppropertycoalesce.NAME = eps /\\ ppropertycoalesce.LINE = 19',
    'ppropertycoalesce.GET = (porigin_get)',
    'n_receiver = ppropertycoalesce.OBJECT',
    'S.OBJECTS[n_receiver] = INSTANCE ppropertycoalesce.CLASS',
    '$class_at(S.CLASSES,ppropertycoalesce.CLASS) = (pclassdesc)',
    'pclassdesc.NAME = $ptascii("TypedGetReceptionHistory") /\\ pclassdesc.PARENT = eps',
    '$property_get_method(S,n_receiver) = (pmethoddesc_get)',
    'pmethoddesc_get.FUNCTION.ORIGIN = porigin_get',
    'pmethoddesc_get.FUNCTION.SIGNATURE.PARAMETERS = [psparam_name]',
    'psparam_name.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))] /\\ psparam_name.NAME = $ptascii("incoming")',
    '$ppmethod_get_declaration_signature(pmethoddesc_get.FUNCTION.SIGNATURE) /\\ ~$ppmethod_get_signature(pmethoddesc_get.FUNCTION.SIGNATURE)',
    '$property_empty_get_source(S,pmethoddesc_get)',
    '(HOBJECT n_receiver) <- S.ALLOCATIONS /\\ ~$instance_storage_freeing(S,n_receiver)',
    'S.FRAMES = [pframe]',
    'pframe.CONTEXT = eps /\\ pframe.ORIGIN = (ppropertycoalesce.SITE)',
    'pframe.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: ptask_tail*',
    '$property_coalesce_frame(S,pcallcontext,pframe,eps,ppropertycoalesce,true)',
    '$property_coalesce_entered(S,S.CURRENT,S.FRAMES,ppropertycoalesce,true)',
    '$property_coalesce_context(S,pcallcontext)',
    '$property_coalesce_active(S,S.CURRENT,S.FRAMES,n_receiver,ppropertycoalesce.NAME,true)',
    '~$property_coalesce_active(S,S.CURRENT,S.FRAMES,n_receiver,ppropertycoalesce.NAME,false)',
    '~$property_isset_guard(S,S.CURRENT,S.FRAMES,n_receiver,ppropertycoalesce.NAME)',
    '$property_empty_get_active(S,n_receiver,ppropertycoalesce.NAME)',
    '$task_nodes(PROPERTY_COALESCE_RESULT ppropertycoalesce true) = [HOBJECT n_receiver]',
    '$target_nodes(pcallcontext.TARGET) = eps /\\ $target_instance(pcallcontext.TARGET) = eps /\\ $call_receiver_roots(pcallcontext) = eps',
    '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1',
    '$lookup(S.ENV,$ptascii("incoming")) = (n_formal)',
    'S.STORE[n_formal] = DEFINED pvalue_formal',
    'pvalue_formal = PINT 9',
    'S_caller = $constant_frame_scope(S,pframe,eps)',
    '$lookup(S_caller.ENV,$ptascii("o")) = (n_o)',
    'S.STORE[n_o] = DEFINED PNULL',
    '$lookup(S_caller.ENV,$ptascii("name")) = (n_selector)',
    'S.STORE[n_selector] = DEFINED pvalue_selector',
    '$string_bytes(pvalue_selector) = ($ptascii("changed"))',
    '$property_magic_cv_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
    '$property_coalesce_source(S,ppropertycoalesce)',
    '$property_coalesce_valid(S_caller,ppropertycoalesce) /\\ ~$property_coalesce_capture(S_caller,ppropertycoalesce)',
    '$property_coalesce_tail(S_caller,ppropertycoalesce,true,S_caller.TODO)',
    '$objectprops_at(S.OBJECTPROPS,n_receiver) = (eps) /\\ $property_coalesce_storage_capture(S,ppropertycoalesce)',
    '$property_magic_cv_result_supported(S_caller,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S.RESULT)',
    'S.EVENTS = [OUTPUT $ptascii("I:"),OUTPUT eps,OUTPUT $ptascii(";"),OUTPUT $ptascii("G:"),OUTPUT eps,OUTPUT $ptascii(";")]',
    '$call_descriptors_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
]

DERIVED = [
    '~$property_coalesce_valid(S_caller,ppropertycoalesce[.PROPERTY = (porigin_get)])',
    '~$property_coalesce_descriptor(S_caller,ppropertycoalesce[.NAME = (0 :: eps)])',
    '~$property_coalesce_valid(S_caller,ppropertycoalesce[.LINE = 20])',
    '~$property_coalesce_valid(S_caller,ppropertycoalesce[.SITE = porigin_get])',
    '~$property_coalesce_valid(S_caller,ppropertycoalesce[.ISSET = porigin_get])',
    '~$property_coalesce_valid(S_caller,ppropertycoalesce[.GET = (ppropertycoalesce.ISSET)])',
    '~$property_coalesce_valid(S_caller,ppropertycoalesce[.CLASS = ppropertycoalesce.SITE])',
    '~$property_coalesce_valid(S_caller,ppropertycoalesce[.OBJECT = (|S.OBJECTS|)])',
    '~$property_coalesce_valid(S_caller[.SOURCES = eps],ppropertycoalesce)',
    '~$property_coalesce_valid(S_caller[.CODE = eps],ppropertycoalesce)',
    'ppropertycoalesce_changed = ppropertycoalesce[.NAME = $ptascii("changed")]',
    '$property_coalesce_descriptor(S_caller,ppropertycoalesce_changed)',
    '~$property_coalesce_tail(S_caller,ppropertycoalesce_changed,true,S_caller.TODO)',
    '~$property_coalesce_context(S,pcallcontext[.TARGET = PROPERTY_COALESCE_TARGET ppropertycoalesce_changed true])',
    'pframe_changed = pframe[.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce_changed true) :: ptask_tail*]',
    '~$property_coalesce_frame(S,pcallcontext,pframe_changed,eps,ppropertycoalesce,true)',
    'S_pending_get = S_caller[.TODO = (CALL_ARGS (PROPERTY_COALESCE_TARGET ppropertycoalesce true) eps 1 ([KNOWN (PSTRING ppropertycoalesce.NAME)]) (ppropertycoalesce.SITE) ppropertycoalesce.LINE) :: (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    '$property_coalesce_pending_call(S_pending_get,ppropertycoalesce,true)',
    'S_pending_isset = S_caller[.TODO = (CALL_ARGS (PROPERTY_COALESCE_TARGET ppropertycoalesce false) eps 1 ([KNOWN (PSTRING ppropertycoalesce.NAME)]) (ppropertycoalesce.SITE) ppropertycoalesce.LINE) :: (PROPERTY_COALESCE_RESULT ppropertycoalesce false) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    '~$property_coalesce_pending_call(S_pending_isset,ppropertycoalesce,false)',
    'S_receiver_only = S_caller[.STORE[n_o] = DEFINED (POBJECT n_receiver)]',
    '~$property_coalesce_capture(S_receiver_only,ppropertycoalesce)',
    'S_name_only = S_caller[.STORE[n_selector] = DEFINED (PSTRING eps)]',
    '~$property_coalesce_capture(S_name_only,ppropertycoalesce)',
    'S_both = S_receiver_only[.STORE[n_selector] = DEFINED (PSTRING eps)]',
    '$property_coalesce_capture(S_both,ppropertycoalesce) /\\ ~$property_coalesce_capture(S_both,ppropertycoalesce_changed)',
    '$property_coalesce_pending_call(S_pending_isset[.STORE = S_both.STORE],ppropertycoalesce,false)',
    'S_pending_forged = S_both[.TODO = (CALL_ARGS (PROPERTY_COALESCE_TARGET ppropertycoalesce_changed false) eps 1 ([KNOWN (PSTRING ppropertycoalesce_changed.NAME)]) (ppropertycoalesce_changed.SITE) ppropertycoalesce_changed.LINE) :: (PROPERTY_COALESCE_RESULT ppropertycoalesce_changed false) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    '~$property_coalesce_pending_call(S_pending_forged,ppropertycoalesce_changed,false)',
    'ppropertyslot_value = {DECL eps, NAME ppropertycoalesce.NAME, STATE (PROP_VALUE (DIRECT (PINT 9)))}',
    'S_value = $objectprops_mark(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_receiver,[ppropertyslot_value])],n_receiver)',
    '$property_coalesce_context(S_value,pcallcontext) /\\ ~$property_coalesce_storage_capture(S_value,ppropertycoalesce)',
    'S_value_caller = $constant_frame_scope(S_value,pframe,eps)[.STORE = S_both.STORE]',
    '~$property_coalesce_capture(S_value_caller,ppropertycoalesce)',
    '$property_state_valid(S_value) /\\ $heap_valid($heap_graph(S_value))',
    '~$property_magic_cv_result_supported(S_caller,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,KNOWN PNULL)',
    '~$property_magic_cv_result_supported(S_caller,ppropertycoalesce.SITE,ppropertycoalesce.LINE,false,KNOWN (PINT 0))',
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
    'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("D;"),OUTPUT $ptascii("ZERO;"),OUTPUT $ptascii("CHANGED;"),OUTPUT $ptascii("NULL;")]',
    '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
    '$call_descriptors_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
]

CASES = {
    'typed-get-reception-keeps-empty-name-after-rebinding': {
        'source': SOURCE,
        'stage': ('S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.TARGET = PROPERTY_COALESCE_TARGET ppropertycoalesce true '
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
                  if not args.case or name in args.case}, (Path(__file__), CATALOGUE),
                 runner_flags=('--sl',))
