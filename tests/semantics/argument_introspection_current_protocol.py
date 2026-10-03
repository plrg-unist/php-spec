#!/usr/bin/env python3
"""Argument views inside installed method capture and CONFIG callbacks."""
from pathlib import Path
import argparse

import argument_introspection_protocol as arguments
import include_mutable_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
SENDER = '''
dec $current_saved_arginfo_sender(pstate, ptask*) : pstate?
def $current_saved_arginfo_sender(S, eps) = eps
def $current_saved_arginfo_sender(S, (ARGINFO_SEND pargcall) :: ptask_tail*) = (S[.TODO = (ARGINFO_SEND pargcall) :: ptask_tail*])
def $current_saved_arginfo_sender(S, ptask :: ptask_tail*) = $current_saved_arginfo_sender($call_after_origin(S, ptask), ptask_tail*)
  -- if ~$saved_arginfo_head(ptask)
'''
FINISH = [
    'S_done = $drive(S, 1000)',
    'S_done.COMPLETION = NORMAL',
    'S_done.TODO = eps',
    'S_done.FRAMES = eps',
    'S_done.TRACE = eps',
    '$heap_valid($heap_graph(S_done))',
    'S_done = $drive(S_initial[.COMPLETION = NORMAL], 1000)',
]
CASES = [
    ('static-dispatch-live-arguments',
     b'<?php class C {static function m($x){echo func_num_args(),func_get_arg(0);}}C::m(7);',
     'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask*', [
         'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask*',
         'pargcall.KIND = INTRINSIC_FUNC_NUM_ARGS',
         'S.CURRENT = (pcallcontext)',
         'pcallcontext.TARGET = SCOPED_TARGET porigin_class porigin_method porigin_called eps poperand_selector',
         'pcallcontext.INSTANCE = eps',
         'pcallcontext.RECEIVER = eps',
         'pcallcontext.ARGC = 1',
         'pcallcontext.PARAMS = [$ptascii("x")]',
         '$arginfo_values(S, pcallcontext) = [PINT 7]',
         '$call_task_valid(S, ARGINFO_INVOKE pargcall)',
         '$call_current_valid(S)',
         '$call_descriptors_valid(S)',
         '$heap_valid($heap_graph(S))',
         '~$call_current_valid(S[.CURRENT = (pcallcontext[.INSTANCE = (999)])])',
         '~$call_current_valid(S[.CURRENT = (pcallcontext[.RECEIVER = (999)])])',
         *FINISH,
         '$outputs(S_done.EVENTS) = $ptascii("17")',
     ]),
    ('captured-static-saved-arguments',
     b'<?php function argpos13(){return 0;}class P {protected static function m($x){echo func_num_args(),func_get_arg(argpos13());return func_get_args();}}class A extends P {}$f=(function(){return A::m(...);})->call(new A);$a=$f(7);echo $a[0];',
     '$saved_arginfo_stage(S)', [
         'S.FRAMES = pframe :: pframe_tail*',
         '$saved_arginfo(pframe.TODO) = (pargcall)',
         'S.CURRENT = (pcallcontext)',
         'pcallcontext.NAME = $ptascii("argpos13")',
         'pcallcontext.INSTANCE = eps',
         'pcallcontext.ARGC = 0',
         'pcallcontext.PARAMS = eps',
         'S.CVS = eps',
         '$arginfo_values(S, pcallcontext) = eps',
         'pframe.CONTEXT = (pcallcontext_saved)',
         'pcallcontext_saved.TARGET = CLOSURE_TARGET n_capture',
         'pcallcontext_saved.INSTANCE = (n_capture)',
         'pcallcontext_saved.RECEIVER = eps',
         'pcallcontext_saved.ARGC = 1',
         'pcallcontext_saved.PARAMS = [$ptascii("x")]',
         'pframe.LOCALS = (psymboltable)',
         'psymboltable.CVS = [$ptascii("x")]',
         'S.OBJECTS[n_capture] = METHODCLOSURE porigin_method porigin_site porigin_class (pmethodcapture)',
         '$class_method_origin(S.CLASSES, porigin_method) = (pmethoddesc)',
         'pmethoddesc.STATIC',
         'pmethoddesc.VISIBILITY = PROPERTY_PROTECTED',
         '$closure_scope_at(S.CLOSURESCOPES, n_capture) = (pclosurescope)',
         '$method_capture_authorized(S, pmethoddesc, porigin_site, porigin_class, pclosurescope, (pmethodcapture))',
         '$call_current_valid(S)',
         '$call_saved_context_valid(S, pframe)',
         '$call_frames_valid(S, S.FRAMES)',
         '$call_descriptors_valid(S)',
         '$closure_state_valid(S)',
         '$heap_valid($heap_graph(S))',
         'S_saved = S[.CURRENT = pframe.CONTEXT][.ORIGIN = pframe.ORIGIN][.TODO = pframe.TODO][.ENV = psymboltable.ENV][.CVS = psymboltable.CVS][.SYMBOLS = psymboltable.SYMBOLS]',
         '$arginfo_values(S_saved, pcallcontext_saved) = [PINT 7]',
         '$current_saved_arginfo_sender(S_saved, pframe.TODO) = (S_send)',
         'S_send.ORIGIN = (pargcall.SITE)',
         '$call_task_valid(S_send, ARGINFO_SEND pargcall)',
         '~$call_current_valid(S[.CURRENT = (pcallcontext[.INSTANCE = (n_capture)])])',
         '~$call_saved_context_valid(S, pframe[.CONTEXT = (pcallcontext_saved[.INSTANCE = (999)])])',
         '~$call_saved_context_valid(S, pframe[.CONTEXT = (pcallcontext_saved[.PARAMS = eps])])',
         '~$call_saved_context_valid(S, pframe[.LOCALS = (psymboltable[.CVS = eps])])',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.CONTEXT = (pcallcontext_saved[.INSTANCE = (999)])] :: pframe_tail*])',
         '~$call_task_valid(S_send, ARGINFO_SEND pargcall[.LINE = 999])',
         *FINISH,
         '$outputs(S_done.EVENTS) = $ptascii("177")',
     ]),
    ('set-named-unpack-callback-arguments',
     b"<?php declare(strict_types=1);class O {function __toString():string {echo func_num_args();$a=func_get_args();echo $a===[]?'T':'F';return 'outer';}}$f=set_include_path(...);echo $f->__invoke(...['include_path'=>new O]);",
     'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask*', [
         'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask*',
         'pargcall.KIND = INTRINSIC_FUNC_NUM_ARGS',
         '$call_task_valid(S, ARGINFO_INVOKE pargcall)',
         '$task_nodes(ARGINFO_INVOKE pargcall) = eps',
         'S.CURRENT = (pcallcontext)',
         'pcallcontext.ARGC = 0',
         'pcallcontext.PARAMS = eps',
         '$arginfo_values(S, pcallcontext) = eps',
         '$config_string_trace_context(S, pcallcontext)',
         'S.FRAMES = pframe :: pframe_tail*',
         'pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*',
         'pconfigcall.KIND = INTRINSIC_SET_INCLUDE_PATH',
         'pconfigcall.NAMED',
         'pconfigcall.OWNER = (n_owner)',
         'pconfigcall.SELECTION = eps',
         'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_object))]',
         'pconfigcall.PACKS = [pconfigpack]',
         'pconfigpack.ITEMS = [ENTRY (KSTRING $ptascii("include_path")) (DIRECT (POBJECT n_object))]',
         'S.CODE = [pcode]',
         'pcode.STRICT',
         '~$config_strict(S, pconfigcall)',
         '$config_string_site_valid(S, pconfigcall, n_object, porigin_child, z_child, z_call)',
         '$config_nodes(pconfigcall) = [HOBJECT n_owner, HOBJECT n_object]',
         '$task_nodes(CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) = [HOBJECT n_object, HOBJECT n_owner, HOBJECT n_object]',
         '~((HARRAY pconfigpack.ARRAY) <- $config_nodes(pconfigcall))',
         '$call_descriptors_valid(S)',
         '$call_frames_valid(S, S.FRAMES)',
         '$heap_valid($heap_graph(S))',
         '~$config_string_site_valid(S, pconfigcall[.PACKS = eps], n_object, porigin_child, z_child, z_call)',
         '~$config_string_site_valid(S, pconfigcall[.PACKS = [pconfigpack[.INDEX = 999]]], n_object, porigin_child, z_child, z_call)',
         '~$config_string_site_valid(S, pconfigcall[.PACKS = [pconfigpack[.ITEMS = [ENTRY (KSTRING $ptascii("directory")) (DIRECT (POBJECT n_object))]]]], n_object, porigin_child, z_child, z_call)',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall[.PACKS = eps] n_object porigin_child z_child z_call) :: ptask_tail*] :: pframe_tail*])',
         '~$call_descriptors_valid(S[.ALLOCATIONS = $call_remove_owner(S.ALLOCATIONS, HOBJECT n_owner)])',
         '~$call_descriptors_valid(S[.ALLOCATIONS = $call_remove_owner(S.ALLOCATIONS, HOBJECT n_object)])',
         '~$call_current_valid(S[.CURRENT = (pcallcontext[.INSTANCE = (n_owner)])])',
         *FINISH,
         'S_done.FILEINCLUDEPATH = ($ptascii("outer"))',
         '$outputs(S_done.EVENTS) = $ptascii("0T.:")',
     ]),
]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--retained', action='store_true')
    options = parser.parse_args()
    if options.retained:
        arguments.CASES = [case for case in arguments.CASES
                           if case[0] != 'language-engine-defect-model-only']
        raise SystemExit(0 if arguments.main('') else 1)
    protocol.PREFIX = arguments.SAVED + SENDER + protocol.PREFIX
    protocol.main(CASES, extra_inputs=(Path(__file__), ROOT / 'tests/semantics/argument_introspection_protocol.py'))
