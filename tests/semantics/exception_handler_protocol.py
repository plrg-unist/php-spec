"""Source-driven exception callback owners, current/saved frames and resume."""
import json
from pathlib import Path

SOURCES = {row['id']: row['source'] for row in json.loads(
    Path(__file__).with_name('exception_handler_cases.json').read_text())}
SOURCES['zero-formal'] = '<?php function h(){echo func_num_args();}set_exception_handler("h");throw new Exception;'
SOURCES['saved-call'] = '<?php function inner(){echo func_num_args();}function h($e){inner();}set_exception_handler("h");throw new Exception;'

PREFIX = r'''
dec $stage(pstate) : bool
def $stage(S) = true -- if STAGE
def $stage(S) = false -- otherwise
dec $seek(pstate, nat) : pstate
def $seek(S, n) = S -- if $stage(S)
def $seek(S, n) = $seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $seek(S, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $seek(S, 0) = S -- if ~$stage(S) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $event_output(pevent) : nat*
def $event_output(OUTPUT n*) = n*
def $event_output(pevent) = eps -- otherwise
dec $outputs(pevent*) : nat*
def $outputs(eps) = eps
def $outputs(pevent :: pevent_tail*) = $event_output(pevent) ++ $outputs(pevent_tail*)
'''

GUARDS = ['$call_current_valid(S)', '$call_frames_valid(S, S.FRAMES)',
          '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
FINISH = [
    'S_done = $drive(S, 1500)', 'S_done.COMPLETION = NORMAL',
    'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
    'S_done.TRACE = eps', '$call_descriptors_valid(S_done)',
    '$heap_valid($heap_graph(S_done))',
    'S_done = $drive(S_initial[.COMPLETION = NORMAL], 1500)',
    'S_paused = $drive_steps(S, 1)',
    r'S_paused.COMPLETION = BUDGET \/ S_paused.COMPLETION = NORMAL',
    'S_done = $drive(S_paused[.COMPLETION = NORMAL], 1500)',
]

CASES = [
    ('pending-raw-owners', 'static-object-detached',
     'S.TODO = (EXCEPTION_HANDLER_INVOKE pexceptioncall) :: ptask_tail*', 'H', [
         'S.TODO = (EXCEPTION_HANDLER_INVOKE pexceptioncall) :: ptask_tail*',
         'S.CURRENT = eps', 'S.FRAMES = eps', 'S.EXCEPTIONHANDLER = eps',
         'S.EXCEPTIONHANDLERS = (pexceptioncall.CALLBACK) :: (pvalue?)*',
         'pexceptioncall.CALLBACK = PARRAY n_array',
         'pexceptioncall.RAW = (S.ARRAYS[n_array])',
         'pexceptioncall.TARGET = eps', 'pexceptioncall.SENT = eps',
         '$task_nodes(EXCEPTION_HANDLER_INVOKE pexceptioncall) = [HOBJECT pexceptioncall.OBJECT]',
         '$heap_owners($heap_graph(S), HARRAY n_array) = 2',
         '$heap_owners($heap_graph(S), HOBJECT pexceptioncall.OBJECT) = 1',
         '$call_task_valid(S, EXCEPTION_HANDLER_INVOKE pexceptioncall)',
         '~$call_task_valid(S[.EXCEPTIONHANDLER = (pexceptioncall.CALLBACK)], EXCEPTION_HANDLER_INVOKE pexceptioncall)',
         '~$call_task_valid(S, EXCEPTION_HANDLER_INVOKE pexceptioncall[.SENT = (KNOWN PNULL)])',
         '~$call_task_valid(S, EXCEPTION_HANDLER_INVOKE pexceptioncall[.TARGET = (PORIGIN 999 eps)])',
         *GUARDS, *FINISH,
         '~((HOBJECT pexceptioncall.OBJECT) <- S_done.ALLOCATIONS)',
     ]),
    ('zero-formal-authentic-extra', 'zero-formal',
     'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask_tail*', '1', [
         'S.CURRENT = (pcallcontext)', 'pcallcontext.NAME = $ptascii("h")',
         'pcallcontext.ARGC = 1', 'pcallcontext.CALLSITE = eps', 'pcallcontext.LINE = $(-1)',
         'S.FRAMES = [pframe]',
         'pframe.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: ptask_saved*',
         'pexceptioncall.SENT = (KNOWN (POBJECT pexceptioncall.OBJECT))',
         'pcallcontext.EXTRA = [KNOWN (POBJECT pexceptioncall.OBJECT)]',
         '$exception_context_valid(S, pcallcontext)',
         '~$exception_context_valid(S, pcallcontext[.EXTRA = [KNOWN PNULL]])',
         '~$exception_context_valid(S, pcallcontext[.ARGC = 0])',
         '~$exception_context_valid(S, pcallcontext[.CALLSITE = (pcallcontext.FUNCTION)])',
         '~$exception_context_valid(S, pcallcontext[.LINE = 0])',
         '~$call_task_valid(S, EXCEPTION_HANDLER_RESULT pexceptioncall)',
         '$call_task_valid(S[.CURRENT = eps][.FRAMES = eps], EXCEPTION_HANDLER_RESULT pexceptioncall)',
         '$arginfo_values(S, pcallcontext) = [POBJECT pexceptioncall.OBJECT]',
         *GUARDS, *FINISH,
         '~((HOBJECT pexceptioncall.OBJECT) <- S_done.ALLOCATIONS)',
     ]),
    ('saved-user-callee-scope', 'saved-call',
     'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask_tail*', '0', [
         'S.CURRENT = (pcallcontext_inner)', 'pcallcontext_inner.NAME = $ptascii("inner")',
         'S.FRAMES = [pframe, pframe_caller]',
         'pframe.CONTEXT = (pcallcontext)', 'pcallcontext.NAME = $ptascii("h")',
         'pframe_caller.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: ptask_saved*',
         '$exception_context_valid(S, pcallcontext)',
         '~$exception_context_kind(S, pcallcontext_inner)',
         '$call_saved_context_valid(S, pframe)',
         '~$call_saved_context_valid(S, pframe[.CONTEXT = (pcallcontext[.ARGC = 2])])',
         '~$call_descriptors_valid(S[.FRAMES = [pframe, pframe_caller[.TODO = ptask_saved*]]])',
         *GUARDS, *FINISH,
         '~((HOBJECT pexceptioncall.OBJECT) <- S_done.ALLOCATIONS)',
     ]),
    ('byref-warning-internal-frame', 'byrefhandled',
     'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask_tail*', '2:Unknown:0:4:old', [
         'S.CURRENT = (pcallcontext)', 'pcallcontext.NAME = $ptascii("w")',
         'pcallcontext.ARGC = 4', 'pcallcontext.CALLSITE = eps',
         '$exception_warning_context(S, pcallcontext)',
         '$error_context_valid(S, pcallcontext)', '$error_context_direct_trigger(S)',
         'S.FRAMES = [pframe]',
         'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_saved*',
         'perrorcall.RESUME = EXCEPTION_HANDLER_ENTER pexceptioncall',
         'pexceptioncall.SENT = eps', 'S.EXCEPTIONHANDLER = eps',
         '$error_handler_values(S, perrorcall) = [PINT 2,PSTRING perrorcall.MESSAGE,PSTRING $ptascii("Unknown"),PINT 0]',
         *GUARDS, *FINISH,
         '~((HOBJECT pexceptioncall.OBJECT) <- S_done.ALLOCATIONS)',
     ]),
    ('detached-static-selection', 'static-object-detached',
     'S.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: ptask_tail*', 'H', [
         'S.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: ptask_tail*',
         'S.CURRENT = eps', 'S.FRAMES = eps', 'S.EXCEPTIONHANDLER = eps',
         'S.EXCEPTIONHANDLERS = eps', 'pexceptioncall.CALLBACK = PARRAY n_array',
         'pexceptioncall.RAW = (parray)',
         '$entry_lookup(parray.ITEMS, KINT 0) = (DIRECT (POBJECT n_selector))',
         '$entry_lookup(S.ARRAYS[n_array].ITEMS, KINT 0) = (DIRECT (PSTRING $ptascii("C")))',
         '~((HOBJECT n_selector) <- S.ALLOCATIONS)',
         '$heap_owners($heap_graph(S), HOBJECT n_selector) = 0',
         '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
         '$exception_result_valid(S, pexceptioncall)',
         '$task_nodes(EXCEPTION_HANDLER_RESULT pexceptioncall) = [HOBJECT pexceptioncall.OBJECT]',
         *GUARDS, *FINISH,
         '~((HOBJECT pexceptioncall.OBJECT) <- S_done.ALLOCATIONS)',
     ]),
    ('retired-byref-send-cell', 'byref',
     'S.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: ptask_tail*', 'old', [
         'S.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: ptask_tail*',
         'S.CURRENT = eps', 'S.FRAMES = eps',
         'pexceptioncall.SENT = (REFERENCE n_cell)',
         '~((HCELL n_cell) <- S.ALLOCATIONS)',
         '$exception_result_valid(S, pexceptioncall)',
         *GUARDS, *FINISH,
         '~((HOBJECT pexceptioncall.OBJECT) <- S_done.ALLOCATIONS)',
     ]),
]
