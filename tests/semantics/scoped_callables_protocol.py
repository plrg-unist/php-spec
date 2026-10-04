#!/usr/bin/env python3
"""Lexical method selection, producer permission and directory handler consumers."""
from pathlib import Path
import json

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('scoped_callables_cases.json')
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOGUE.read_text())}
VALID = ['$call_descriptors_valid(S)', '$class_state_valid(S)',
         '$closure_state_valid(S)', '$heap_valid($heap_graph(S))']
AFTER = ['$call_descriptors_valid(S_done)', '$class_state_valid(S_done)',
         '$closure_state_valid(S_done)', '$heap_valid($heap_graph(S_done))']

CASES = {
    'protected-prototype-direct-caller-scope': {
        'source': SOURCES['protected-prototype-ancestor-direct-selection'],
        'stage': ('S.TODO = (NAMED_ARGS (ARRAY_METHOD_TARGET pcalltarget parrayselection) '
                  'phpType7* 0 {SLOTS eps, NAMED eps} (porigin_site) z_call) :: ptask_tail*'),
        'checks': [
            'pcalltarget = SCOPE_METHOD_TARGET (METHOD_TARGET n_receiver porigin_run) pcallableaccess',
            'pcallableaccess.SITE = (porigin_site)',
            'pcallableaccess.SCOPE = (porigin_root)',
            'pcallableaccess.OBJECT',
            'pcallableaccess.CREATION = eps',
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.LEXICAL_CLASS = (porigin_root)',
            'pcallcontext.RECEIVER = (n_start)',
            'parrayselection.SITE = porigin_site',
            'parrayselection.REQUESTED = porigin_right',
            'parrayselection.NAME = $ptascii("run")',
            'parrayselection.LINE = z_call',
            'S.OBJECTS[n_start] = INSTANCE porigin_root',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_right',
            '$class_method_origin(S.CLASSES, porigin_run) = (pmethoddesc)',
            'pmethoddesc.OWNER = porigin_right',
            'pmethoddesc.VISIBILITY = PROPERTY_PROTECTED',
            '~pmethoddesc.STATIC',
            '$method_prototype(S, porigin_right, pmethoddesc.NAME, |S.CLASSES|) = porigin_root',
            '$method_accessible(S, pmethoddesc, (porigin_root))',
            '$method_accessible(S, pmethoddesc, (porigin_right))',
            '$method_site_scope(S, porigin_run, porigin_site) = (porigin_root)',
            '$scope_access_origin(S, pcallableaccess, porigin_run)',
            '$array_target_identity(S, pcalltarget, parrayselection)',
            '$call_selected_valid(S, ARRAY_METHOD_TARGET pcalltarget parrayselection, (porigin_site))',
            '$target_nodes(pcalltarget) = [HOBJECT n_receiver]',
            '$target_lexical_class(S, pcalltarget) = (porigin_right)',
            '$target_called_class(S, pcalltarget) = (porigin_right)',
            *VALID,
            '~$scope_target_valid(S, METHOD_TARGET n_receiver porigin_run, pcallableaccess[.SCOPE = (porigin_right)])',
            '~$array_target_identity(S, SCOPE_METHOD_TARGET (METHOD_TARGET n_receiver porigin_run) pcallableaccess[.OBJECT = false], parrayselection)',
            '~$array_target_identity(S, pcalltarget, parrayselection[.NAME = $ptascii("start")])',
            '~$call_task_valid(S, NAMED_ARGS (ARRAY_METHOD_TARGET pcalltarget parrayselection) phpType7* 0 {SLOTS eps, NAMED eps} (porigin_site) $(z_call + 100))',
            'S_done = $drive(S, 3000)',
            'S_done.COMPLETION = NORMAL',
            'S_done.EVENTS = [OUTPUT $ptascii("Right"), OUTPUT $ptascii("/"), OUTPUT $ptascii("Right"), OUTPUT $ptascii(":"), OUTPUT $ptascii("x")]',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_start) <- S_done.ALLOCATIONS)',
            *AFTER,
        ],
    },
    'private-fixed-string-producer-this-and-ref-clone': {
        'source': SOURCES['private-fixed-string-capture-ref-default-clone'],
        'stage': 'S.TODO = (STRING_CONVERT pcalltarget pstringselection) :: ptask_tail*',
        'checks': [
            'pcalltarget = SCOPE_METHOD_TARGET pcalltarget_base pcallableaccess',
            'pcalltarget_base = SCOPED_TARGET porigin_owner porigin_run porigin_child (n_receiver) (KNOWN (PSTRING $ptascii("Owner")))',
            'pcallableaccess.SITE = (pstringselection.SITE)',
            'pcallableaccess.SCOPE = (porigin_owner)',
            '~pcallableaccess.OBJECT',
            'pcallableaccess.CREATION = eps',
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.LEXICAL_CLASS = (porigin_owner)',
            'pcallcontext.CALLED_CLASS = (porigin_child)',
            'pcallcontext.RECEIVER = (n_receiver)',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_child',
            '$lookup(S.ENV, $ptascii("other")) = (n_other_cell)',
            'S.STORE[n_other_cell] = DEFINED (POBJECT n_other)',
            'n_other =/= n_receiver',
            'S.OBJECTS[n_other] = INSTANCE porigin_child',
            'pstringselection.ORIGINAL = $ptascii("Owner::run")',
            'pstringselection.REQUESTED = porigin_owner',
            '$dynamic_fixed_name(S, pstringselection.SITE) = ($ptascii("Owner::run"))',
            '$class_method_origin(S.CLASSES, porigin_run) = (pmethoddesc)',
            'pmethoddesc.OWNER = porigin_owner',
            'pmethoddesc.VISIBILITY = PROPERTY_PRIVATE',
            '~pmethoddesc.STATIC',
            '$string_target_identity(S, pcalltarget, pstringselection)',
            '$string_convert_valid(S, pcalltarget, pstringselection)',
            '$scope_capture_certificate(S, pstringselection.SITE, (porigin_owner), eps)',
            '$target_nodes(pcalltarget) = [HOBJECT n_receiver]',
            '$target_receiver(S, pcalltarget) = (n_receiver)',
            '$declaration_history_valid(S)',
            *VALID,
            '~$string_convert_valid(S, SCOPE_METHOD_TARGET pcalltarget_base pcallableaccess[.SCOPE = (porigin_child)], pstringselection)',
            '~$string_target_identity(S, SCOPE_METHOD_TARGET pcalltarget_base pcallableaccess[.OBJECT = true], pstringselection)',
            '~$string_convert_valid(S, pcalltarget, pstringselection[.LINE = $(pstringselection.LINE + 100)])',
            '~$string_convert_valid(S, pcalltarget, pstringselection[.ORIGINAL = $ptascii("Child::run")])',
            '$target_function(S, SCOPED_TARGET porigin_owner porigin_run porigin_child (n_other) (KNOWN (PSTRING $ptascii("Owner")))) = (pmethoddesc.FUNCTION)',
            '~$string_convert_valid(S, SCOPE_METHOD_TARGET (SCOPED_TARGET porigin_owner porigin_run porigin_child (n_other) (KNOWN (PSTRING $ptascii("Owner")))) pcallableaccess, pstringselection)',
            'n_capture = |S.OBJECTS|',
            'PhpStep: S ~> S_one',
            'S_one.COMPLETION = NORMAL',
            'S_one.OBJECTS[n_capture] = STRINGMETHODCLOSURE pcalltarget pstringselection',
            'S_one.RESULT = KNOWN (POBJECT n_capture)',
            '$node_children(S_one, HOBJECT n_capture) = [HOBJECT n_receiver]',
            '$closure_callable(S_one, n_capture)',
            '$typed_closure(S_one, n_capture)',
            '$closure_scope_at(S_one.CLOSURESCOPES, n_capture) = (pclosurescope)',
            'pclosurescope.LEXICAL = porigin_owner',
            'pclosurescope.CALLED = porigin_child',
            'pclosurescope.RECEIVER = (n_receiver)',
            '$closure_scope_row_valid(S_one, pclosurescope)',
            'S_done = $drive(S_one, 5000)',
            'S_done.COMPLETION = NORMAL',
            'S_done.EVENTS = [OUTPUT $ptascii("Owner"), OUTPUT $ptascii("/"), OUTPUT $ptascii("Child"), OUTPUT $ptascii(":"), OUTPUT $ptascii("d"), OUTPUT $ptascii(":"), OUTPUT $ptascii("1"), OUTPUT $ptascii(":"), OUTPUT $ptascii("xK"), OUTPUT $ptascii("|"), OUTPUT $ptascii("Owner"), OUTPUT $ptascii("/"), OUTPUT $ptascii("Child"), OUTPUT $ptascii(":"), OUTPUT $ptascii("y"), OUTPUT $ptascii(":"), OUTPUT $ptascii("2"), OUTPUT $ptascii(":"), OUTPUT $ptascii("xKK")]',
            'S_done.GLOBALTABLE = (psymboltable)',
            '$lookup(psymboltable.ENV, $ptascii("v")) = (n_v)',
            'S_done.STORE[n_v] = DEFINED (PSTRING $ptascii("xKK"))',
            '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_other) <- S_done.ALLOCATIONS)',
            '$declaration_history_valid(S_done)',
            *AFTER,
        ],
    },
    'protected-direct-error-before-cv-arguments': {
        'source': SOURCES['protected-denial-precedes-argument-effects'],
        'stage': 'S.TODO = (CALL_DYNAMIC porigin_site z_init z_call) :: ptask_tail*',
        'checks': [
            'S.ORIGIN = (porigin_site)',
            'S.RESULT = VARIABLE $ptascii("cb") z_read',
            '$dynamic_operand_valid(S, porigin_site)',
            '$lookup(S.ENV, $ptascii("cb")) = (n_cell)',
            'S.STORE[n_cell] = DEFINED (PARRAY n_array)',
            '$array_shape_error(S, n_array) = eps',
            'ptbytes_denied = $ptascii("Call to protected method Hidden::rUN() from global scope")',
            '$array_resolve(S, n_array, ARRAY_DISPATCH) = ARRAYINVALID ptbytes_denied',
            '$typed_callable(S, PARRAY n_array) = (false)',
            'S.EVENTS = eps',
            *VALID,
            'PhpStep: S ~> S_error',
            'S_error.COMPLETION = THROWN "Error" ptbytes_denied z_error',
            'z_error = z_init',
            'S_error.EVENTS = S.EVENTS',
            'S_error.STORE = S.STORE',
            'S_error.CURRENT = S.CURRENT',
            'S_error.FRAMES = S.FRAMES',
            'S_done = $drive(S_error, 3000)',
            'S_done.COMPLETION = NORMAL',
            'S_done.EVENTS = [OUTPUT ptbytes_denied]',
            *AFTER,
        ],
    },
}

CASES['private-literal-class-array-capture-kind'] = {
    'source': SOURCES['private-static-array-capture-clone-default-static'],
    'stage': 'S.TODO = (ARRAY_CONVERT pcalltarget parrayselection) :: ptask_tail*',
    'checks': [
        'pcalltarget = SCOPE_METHOD_TARGET (STATIC_METHOD_TARGET porigin_child porigin_run) pcallableaccess',
        'pcallableaccess.SITE = (parrayselection.SITE)',
        'pcallableaccess.SCOPE = (porigin_owner)',
        '~pcallableaccess.OBJECT',
        'pcallableaccess.CREATION = eps',
        'parrayselection.REQUESTED = porigin_child',
        'parrayselection.NAME = $ptascii("run")',
        '$class_method_origin(S.CLASSES, porigin_run) = (pmethoddesc)',
        'pmethoddesc.OWNER = porigin_owner',
        'pmethoddesc.VISIBILITY = PROPERTY_PRIVATE',
        'pmethoddesc.STATIC',
        '$scope_array_kind_valid(S, parrayselection.SITE, false)',
        '~$scope_array_kind_valid(S, parrayselection.SITE, true)',
        '$scope_identity(S, STATIC_METHOD_TARGET porigin_child porigin_run, porigin_child, $ptascii("run"), pcallableaccess[.OBJECT = true])',
        '~$array_target_identity(S, SCOPE_METHOD_TARGET (STATIC_METHOD_TARGET porigin_child porigin_run) pcallableaccess[.OBJECT = true], parrayselection)',
        '$array_convert_valid(S, pcalltarget, parrayselection)',
        '$target_nodes(pcalltarget) = eps',
        *VALID,
        'n_capture = |S.OBJECTS|',
        'PhpStep: S ~> S_one',
        'S_one.COMPLETION = NORMAL',
        'S_one.OBJECTS[n_capture] = ARRAYMETHODCLOSURE pcalltarget parrayselection eps',
        '$node_children(S_one, HOBJECT n_capture) = eps',
        '$closure_callable(S_one, n_capture)',
        '$typed_closure(S_one, n_capture)',
        'S_done = $drive(S_one, 4000)',
        'S_done.COMPLETION = NORMAL',
        'S_done.EVENTS = [OUTPUT $ptascii("Owner"), OUTPUT $ptascii("/"), OUTPUT $ptascii("Child"), OUTPUT $ptascii(":"), OUTPUT $ptascii("d"), OUTPUT $ptascii(":"), OUTPUT $ptascii("1"), OUTPUT $ptascii("Owner"), OUTPUT $ptascii("/"), OUTPUT $ptascii("Child"), OUTPUT $ptascii(":"), OUTPUT $ptascii("x"), OUTPUT $ptascii(":"), OUTPUT $ptascii("2")]',
        '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
        *AFTER,
    ],
}

DIR_PREFIX = '''
dec $scoped_dir_stage(pstate) : bool
def $scoped_dir_stage(S) = true
  -- if S.TODO = (ARGINFO_INVOKE pargcall) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = HANDLER_METHOD_TARGET true porigin_owner ptbytes pcalltarget
def $scoped_dir_stage(S) = false -- otherwise
dec $scoped_dir_seek(pstate, nat) : pstate
def $scoped_dir_seek(S, n) = S -- if $scoped_dir_stage(S)
def $scoped_dir_seek(S, n) = $scoped_dir_seek($throwable_begin(S), $nabs($(n - 1)))
  -- if ~$scoped_dir_stage(S)
  -- if $throwable_pending(S.COMPLETION)
  -- if ~S.COMPILESTOP
  -- if $(n > 0)
def $scoped_dir_seek(S, n) = $scoped_dir_seek($prune_allocations($throwable_transition(S, S_next)), $nabs($(n - 1)))
  -- if ~$scoped_dir_stage(S)
  -- if S.COMPLETION = NORMAL
  -- if ~S.COMPILESTOP
  -- if ~$error_read_pending(S)
  -- if $(n > 0)
  -- PhpStep: S ~> S_next
'''

FILE_CASES = [(
    'scoped-private-static-handler-dir-warning',
    SOURCES['private-static-handler-current-dir-warning'].encode(),
    'true',
    [
        'S_wait = $drive_steps(S, 3000)',
        'S_wait.COMPLETION = SOURCE_PENDING',
        'S_wait.DIRCONTEXT = (pdircontext)',
        'pdircontext.NONCE = 0',
        'pdircontext.REQUESTED = $ptascii("missing")',
        'pdircontext.CALL.KIND = INTRINSIC_CHDIR',
        '$dir_pending_state_valid(S_wait)',
        '$call_descriptors_valid(S_wait)',
        '$dir_response_valid(S_wait, DIR_FAILED 0 pdircontext.CWD $ptascii("missing") $ptascii("No such file or directory") 2)',
        '~$dir_response_valid(S_wait, DIR_FAILED 1 pdircontext.CWD $ptascii("missing") $ptascii("No such file or directory") 2)',
        '~$dir_response_valid(S_wait, DIR_FAILED 0 pdircontext.CWD $ptascii("other") $ptascii("No such file or directory") 2)',
        'S_dispatch = $dir_resume(S_wait, DIR_FAILED 0 pdircontext.CWD $ptascii("missing") $ptascii("No such file or directory") 2)',
        'S_dispatch.COMPLETION = NORMAL',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_emitter*',
        'perrorcall.LEVEL = 2',
        'perrorcall.RESUME = CHDIR_WARNING_RESULT pdircontext $ptascii("No such file or directory") 2',
        'S_entered = $scoped_dir_seek(S_dispatch, 400)',
        'S_entered.CURRENT = (pcallcontext)',
        'S_entered.TODO = (ARGINFO_INVOKE pargcall) :: ptask_handler*',
        'S_entered.FRAMES = pframe_emitter :: pframe_tail*',
        'pframe_emitter.CONTEXT = (pcallcontext_emitter)',
        'pframe_emitter.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_emitter*',
        'pcallcontext.TARGET = HANDLER_METHOD_TARGET true porigin_owner $ptascii("handle") pcalltarget',
        'pcalltarget = SCOPE_METHOD_TARGET pcalltarget_base pcallableaccess',
        'pcalltarget_base = SCOPED_TARGET porigin_owner porigin_handle porigin_child eps (KNOWN (PSTRING $ptascii("Owner")))',
        'pcallableaccess.SITE = eps',
        'pcallableaccess.SCOPE = (porigin_owner)',
        '~pcallableaccess.OBJECT',
        'pcallableaccess.CREATION = eps',
        'pcallcontext.LEXICAL_CLASS = (porigin_owner)',
        'pcallcontext.CALLED_CLASS = (porigin_child)',
        'pcallcontext.RECEIVER = eps',
        'pcallcontext.ARGC = 4',
        '$arginfo_values(S_entered, pcallcontext) = [PSTRING $ptascii("2"), PSTRING perrorcall.MESSAGE, PSTRING ptbytes_file, PINT perrorcall.LINE]',
        'pcallcontext_emitter.LEXICAL_CLASS = (porigin_owner)',
        'pcallcontext_emitter.CALLED_CLASS = (porigin_child)',
        'pcallcontext_emitter.RECEIVER = (n_receiver)',
        'pcallcontext_emitter.ARGC = 1',
        'S_entered.OBJECTS[n_receiver] = INSTANCE porigin_child',
        'pframe_emitter.LOCALS = (psymboltable_emitter)',
        '$arginfo_values(S_entered[.ENV = psymboltable_emitter.ENV], pcallcontext_emitter) = [PSTRING $ptascii("x")]',
        'perrorcall_entered.TARGET = (pcallcontext.TARGET)',
        'perrorcall_entered.CALLBACK = PSTRING $ptascii("Owner::handle")',
        'S_emitter = S_entered[.CURRENT = pframe_emitter.CONTEXT][.FRAMES = pframe_tail*][.ORIGIN = pframe_emitter.ORIGIN][.TODO = pframe_emitter.TODO][.BORROWEDREAD = pframe_emitter.BORROWEDREAD]',
        '$error_entered_call_valid(S_emitter, perrorcall_entered)',
        '$error_context_valid(S_entered, pcallcontext)',
        '$error_context_trigger(S_entered, pcallcontext) = (pdircontext.CALL)',
        '$error_handler_trace_values(S_entered, pcallcontext, pdircontext.CALL) = [PSTRING $ptascii("missing")]',
        '$target_nodes(pcallcontext.TARGET) = eps',
        '$trace_context_class(S_entered, pcallcontext) = ($ptascii("Owner"))',
        '$trace_context_type(S_entered, pcallcontext) = ($ptascii("::"))',
        '$call_descriptors_valid(S_entered)',
        '$class_state_valid(S_entered)',
        '$closure_state_valid(S_entered)',
        '$heap_valid($heap_graph(S_entered))',
        '~$handler_emitter_valid(S_emitter, HANDLER_METHOD_TARGET true porigin_owner $ptascii("handle") (SCOPE_METHOD_TARGET pcalltarget_base pcallableaccess[.SCOPE = (porigin_child)]))',
        '~$handler_emitter_valid(S_emitter, HANDLER_METHOD_TARGET true porigin_owner $ptascii("handle") (SCOPE_METHOD_TARGET (SCOPED_TARGET porigin_owner porigin_handle porigin_owner eps (KNOWN (PSTRING $ptascii("Owner")))) pcallableaccess))',
        '~$error_entered_call_valid(S_emitter, perrorcall_entered[.LINE = $(perrorcall_entered.LINE + 100)])',
        '~$error_entered_call_valid(S_emitter, perrorcall_entered[.RESUME = CHDIR_WARNING_RESULT pdircontext[.REQUESTED = $ptascii("other")] $ptascii("No such file or directory") 2])',
        'S_done = $drive(S_entered, 3000)',
        'S_done.COMPLETION = NORMAL',
        '$outputs(S_done.EVENTS) = $ptascii("Owner/Child:1:x|H4:2:Owner/Child|E|1:x")',
        'S_done.CURRENT = eps',
        'S_done.FRAMES = eps',
        'S_done.ERRORHANDLER.CALLBACK = eps',
        'S_done.ERRORHANDLERS = eps',
        'S_done.DIRCONTEXT = eps',
        'S_done.FILECWD = S_wait.FILECWD',
        '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        *AFTER,
    ],
)]


def main():
    protocol.run(CASES, extra_inputs=[Path(__file__), CATALOGUE])
    import include_mutable_protocol
    include_mutable_protocol.PREFIX += DIR_PREFIX
    include_mutable_protocol.main(FILE_CASES, extra_inputs=[Path(__file__), CATALOGUE])


if __name__ == '__main__':
    main()
