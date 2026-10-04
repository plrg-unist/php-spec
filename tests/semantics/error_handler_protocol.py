"""Source-reached pending, nested, fallback and temporary-reference handlers."""
from error_handler_cases import CASES as SOURCES

PREFIX = r'''
dec $stage(pstate) : bool
def $stage(S) = true -- if STAGE
def $stage(S) = false -- otherwise
dec $seek(pstate, nat) : pstate
def $seek(S, n) = S -- if $stage(S) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $seek(S, n) = $seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $seek(S, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $outputs(pevent*) : nat*
def $outputs(eps) = eps
def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)
def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)
def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)
def $outputs((WARNING_SOURCE n_unit n* z) :: pevent*) = $outputs(pevent*)
def $outputs((DIAGNOSTIC_SOURCE n_unit text n* z) :: pevent*) = $outputs(pevent*)
def $outputs((DIAGNOSTIC_STACK text n* z n_trace*) :: pevent*) = $outputs(pevent*)
def $outputs((DIAGNOSTIC_STACK_SOURCE n_unit text n* z n_trace*) :: pevent*) = $outputs(pevent*)
'''

GUARDS = ['$call_current_valid(S)', '$call_frames_valid(S, S.FRAMES)',
          '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
FINISH = [
    'S_done = $drive(S, 1500)', 'S_done.COMPLETION = NORMAL',
    'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.TRACE = eps',
    'S_done.ERRORHANDLER.CALLBACK = eps', 'S_done.ERRORHANDLERS = eps',
    '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    'S_done = $drive(S_initial[.COMPLETION = NORMAL], 1500)',
]

CASES = [
    ('pending-raw-callback', 'replacement-nested-and-throw',
     'S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*', [
         'S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
         'perrorcall.CALLBACK = POBJECT n_handler', 'perrorcall.TARGET = eps',
         'S.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)',
         'S.ERRORHANDLER.LEVELS = 512', 'perrorcall.LEVEL = 512',
         'perrorcall.MESSAGE = $ptascii("outer")',
         'perrorcall.RESUME = ERROR_TRIGGER_PHASE pconfigcall 2',
         '$error_call_valid(S, perrorcall)', '$call_task_valid(S, ERROR_HANDLER_INVOKE perrorcall)',
         '~$call_task_valid(S[.ERRORHANDLER.LEVELS = 0], ERROR_HANDLER_INVOKE perrorcall)',
         '~$call_task_valid(S, ERROR_HANDLER_INVOKE perrorcall[.LINE = 999])',
         '~$call_task_valid(S, ERROR_HANDLER_INVOKE perrorcall[.SITE = PORIGIN 999 eps])',
         '~$call_task_valid(S, ERROR_HANDLER_INVOKE perrorcall[.MESSAGE = $ptascii("forged")])',
         '$error_handler_target(S, perrorcall.CALLBACK) = (METHOD_TARGET n_handler porigin_method)',
         '$task_nodes(ERROR_HANDLER_INVOKE perrorcall) = [HOBJECT n_handler]',
         '$lookup(S.ENV, $ptascii("handler")) = eps',
         '$heap_owners($heap_graph(S), HOBJECT n_handler) = 2',
         *GUARDS, *FINISH,
     ]),
    ('nested-handler-saved-header', 'replacement-nested-and-throw',
     'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask_tail* -- if S.CURRENT = (pcallcontext) -- if pcallcontext.INSTANCE =/= eps', [
         'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask_tail*',
         'S.CURRENT = (pcallcontext)', 'pcallcontext.TARGET = CLOSURE_TARGET n_nested',
         'pcallcontext.INSTANCE = (n_nested)', 'pcallcontext.ARGC = 4',
         'S.FRAMES = pframe :: pframe_caller :: pframe_tail*',
         'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_saved*',
         'perrorcall.CALLBACK = POBJECT n_nested', 'perrorcall.MESSAGE = $ptascii("nested")',
         'pframe.CONTEXT = (pcallcontext_outer)',
         'pcallcontext_outer.TARGET = METHOD_TARGET n_outer porigin_method',
         'pcallcontext_outer.ARGC = 4',
         'pframe_caller.TODO = (ERROR_HANDLER_RESULT perrorcall_outer) :: ptask_caller*',
         'perrorcall_outer.CALLBACK = POBJECT n_outer',
         '$error_context_valid(S, pcallcontext)',
         '$call_saved_context_valid(S, pframe)',
         '~$call_saved_context_valid(S, pframe[.CONTEXT = (pcallcontext_outer[.ARGC = 0])])',
         '~$call_descriptors_valid(S[.FRAMES = pframe :: pframe_caller[.TODO = ptask_caller*] :: pframe_tail*])',
         '$target_function(S, pcallcontext.TARGET) = (pfunction)', 'S.CVS = pfunction.CVS',
         '$arginfo_values(S, pcallcontext) = $error_handler_values(S, perrorcall)',
         'S.ERRORHANDLER.CALLBACK = eps', *GUARDS, *FINISH,
     ]),
    ('exact-false-current-mask-fallback', 'mask-reporting-and-silence',
     'S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*', [
         'S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
         'S.RESULT = KNOWN (PBOOL false)', 'S.REPORTING = 0',
         'S.ERRORHANDLER.CALLBACK = eps', 'S.ERRORHANDLER.LEVELS = 512',
         '$call_task_valid(S, ERROR_HANDLER_RESULT perrorcall)',
         '~$call_task_valid(S, ERROR_HANDLER_RESULT perrorcall[.LEVEL = 1024])',
         'PhpStep: S ~> S_one', 'S_one.COMPLETION = NORMAL',
         'S_one.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)',
         'S_one.ERRORHANDLER.LEVELS = 512', 'S_one.EVENTS = S.EVENTS',
         'S_one.TODO = perrorcall.RESUME :: ptask_tail*',
         *GUARDS, *FINISH,
     ]),
    ('temporary-reference-default-live-args', 'temporary-reference-and-omitted-default',
     'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask_tail*', [
         'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask_tail*',
         'S.CURRENT = (pcallcontext)', 'pcallcontext.NAME = $ptascii("eh13ref")',
         'pcallcontext.ARGC = 4', 'pcallcontext.EXTRA = eps',
         'pcallcontext.PARAMS = [$ptascii("n"),$ptascii("m"),$ptascii("f"),$ptascii("l"),$ptascii("extra")]',
         '$target_function(S, pcallcontext.TARGET) = (pfunction)',
         'pfunction.SIGNATURE.PARAMETERS[0].BYREF',
         '$lookup(S.ENV, $ptascii("n")) = (n_cell)', 'S.STORE[n_cell] = DEFINED (PINT 999)',
         '$lookup(S.ENV, $ptascii("extra")) = (n_default)', 'S.STORE[n_default] = DEFINED (PINT 7)',
         '$error_context_valid(S, pcallcontext)', '$error_context_direct_trigger(S)',
         '~$typed_caller_strict(S)', 'S.FRAMES = pframe :: pframe_tail*',
         'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_saved*',
         'perrorcall.LEVEL = 512',
         '$arginfo_values(S, pcallcontext) = [PINT 999, PSTRING perrorcall.MESSAGE, PSTRING n_file*, PINT perrorcall.LINE]',
         *GUARDS, *FINISH,
     ]),
    ('named-handler-internal-trace', 'callback-finally-before-caller-catch',
     'S.TODO = (THROW_SEARCH n) :: (TRY_END porigin) :: ptask_tail* -- if S.CURRENT =/= eps', [
         'S.TODO = (THROW_SEARCH n) :: (TRY_END porigin) :: ptask_tail*',
         'S.CURRENT = (pcallcontext)', 'pcallcontext.NAME = $ptascii("eh13throw")',
         'pcallcontext.ARGC = 4', '$error_context_valid(S, pcallcontext)',
         '$error_context_direct_trigger(S)', 'S.ERRORHANDLER.CALLBACK = eps',
         'S.OBJECTS[n] = THROWABLE pthrowable', 'pthrowable.KIND = "Error"',
         '$throwable_field(S, n, "trace") = PARRAY n_trace',
         'S.ARRAYS[n_trace].ITEMS = (ENTRY (KINT 0) (DIRECT (PARRAY n_frame))) :: pentry_tail*',
         'parray_frame = S.ARRAYS[n_frame]',
         'parray_frame.ITEMS = [ENTRY (KSTRING $ptascii("function")) (DIRECT (PSTRING $ptascii("eh13throw"))), ENTRY (KSTRING $ptascii("args")) (DIRECT (PARRAY n_args))]',
         '$trace_graph_valid(S, n_trace)', '$throwable_live(S, n)',
         'S_missing = S[.ARRAYS = $array_replace(S.ARRAYS, n_frame, parray_frame[.ITEMS = [ENTRY (KSTRING $ptascii("args")) (DIRECT (PARRAY n_args))]])]',
         '~$trace_graph_valid(S_missing, n_trace)',
         'S_empty = S[.ARRAYS = $array_replace(S.ARRAYS, n_frame, parray_frame[.ITEMS = [ENTRY (KSTRING $ptascii("function")) (DIRECT (PSTRING eps)), ENTRY (KSTRING $ptascii("args")) (DIRECT (PARRAY n_args))]])]',
         '~$trace_graph_valid(S_empty, n_trace)',
         'S_self = S[.ARRAYS = $array_replace(S.ARRAYS, n_frame, parray_frame[.ITEMS = [ENTRY (KSTRING $ptascii("function")) (DIRECT (PSTRING $ptascii("eh13throw"))), ENTRY (KSTRING $ptascii("args")) (DIRECT (PARRAY n_frame))]])]',
         '~$trace_graph_valid(S_self, n_trace)',
         'S_outer = S[.ARRAYS = $array_replace(S.ARRAYS, n_frame, parray_frame[.ITEMS = [ENTRY (KSTRING $ptascii("function")) (DIRECT (PSTRING $ptascii("eh13throw"))), ENTRY (KSTRING $ptascii("args")) (DIRECT (PARRAY n_trace))]])]',
         '~$trace_graph_valid(S_outer, n_trace)',
         *GUARDS, *FINISH,
     ]),
    ('fatal-callback-captured-trace', 'user-fatal-false-callback-trace',
     'S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail* -- if perrorcall.LEVEL = 256', [
         'S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
         'S.RESULT = KNOWN (PBOOL false)', 'perrorcall.LEVEL = 256',
         'perrorcall.CALLBACK = PSTRING ($ptascii("eh13fataltrace"))',
         'perrorcall.RESUME = ERROR_TRIGGER_PHASE pconfigcall 2',
         '$call_task_valid(S, ERROR_HANDLER_RESULT perrorcall)',
         'S.REPORTING = 256', 'S.ERRORHANDLER.CALLBACK = eps',
         'S.ERRORFATALTRACE = [ptraceframe, ptraceframe_caller]',
         'ptraceframe.FILE = $call_sourcefile(S.FILES, pconfigcall.SITE)',
         'ptraceframe.LINE = pconfigcall.LINE',
         'ptraceframe.FUNCTION = $ptascii("trigger_error")',
         'ptraceframe.CLASS = eps', 'ptraceframe.TYPE = eps',
         'ptraceframe.ARGS = [(KINT 0, PSTRING ($ptascii("123"))), (KINT 1, PSTRING ($ptascii("256")))]',
         'ptraceframe.HASARGS',
         'ptraceframe_caller.FUNCTION = $ptascii("eh13cause")',
         'ptraceframe_caller.ARGS = [(KINT 0, PARRAY n_saved)]',
         '$lookup(S.ENV, $ptascii("v")) = (n_cell)',
         'S.STORE[n_cell] = DEFINED (PARRAY n_live)', 'n_live =/= n_saved',
         'S.ARRAYS[n_saved].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
         'S.ARRAYS[n_live].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]',
         '$heap_owners($heap_graph(S), HARRAY n_saved) = 1',
         '$heap_owners($heap_graph(S), HARRAY n_live) = 1', *GUARDS,
         'PhpStep: S ~> S_one',
         'S_one.COMPLETION = USERFATAL ($ptascii("123")) pconfigcall.LINE true',
         'S_one.TODO = eps', 'S_one.ERRORHANDLER.CALLBACK = eps',
         'S_one.ERRORFATALTRACE = eps', 'S_one.TRACE = S.ERRORFATALTRACE',
         'S_one.EVENTS = S.EVENTS', '$heap_valid($heap_graph(S_one))',
         'S_done = $drive(S_one, 1500)', 'S_done.COMPLETION = S_one.COMPLETION',
         'S_done.TRACE = S.ERRORFATALTRACE', 'S_done.ERRORFATALTRACE = eps',
         'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.TODO = eps',
         '$heap_valid($heap_graph(S_done))',
     ]),
    ('fatal-callback-cleared-trace', 'user-fatal-nested-warning-clears-trace',
     'S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail* -- if perrorcall.LEVEL = 256', [
         'S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
         'S.RESULT = KNOWN (PBOOL false)', 'perrorcall.LEVEL = 256',
         'perrorcall.CALLBACK = PSTRING ($ptascii("eh13fatalclear"))',
         'perrorcall.RESUME = ERROR_TRIGGER_PHASE pconfigcall 2',
         '$call_task_valid(S, ERROR_HANDLER_RESULT perrorcall)',
         'S.REPORTING = 256', 'S.ERRORHANDLER.CALLBACK = eps',
         'S.ERRORFATALTRACE = eps', *GUARDS,
         'PhpStep: S ~> S_one',
         'S_one.COMPLETION = USERFATAL ($ptascii("outer")) pconfigcall.LINE true',
         'S_one.TODO = eps', 'S_one.ERRORHANDLER.CALLBACK = eps',
         'S_one.ERRORFATALTRACE = eps', 'S_one.TRACE = eps',
         'S_one.EVENTS = S.EVENTS', '$heap_valid($heap_graph(S_one))', 'S_done = S_one',
     ]),
    ('fatal-direct-captured-trace', 'user-fatal-displayed-default',
     'S.TODO = (ERROR_TRIGGER_PHASE pconfigcall 1) :: ptask_tail* -- if $error_trigger_level(S[.COMPLETION = NORMAL], pconfigcall) = (256)', [
         'S.TODO = (ERROR_TRIGGER_PHASE pconfigcall 1) :: ptask_tail*',
         '$call_task_valid(S, ERROR_TRIGGER_PHASE pconfigcall 1)',
         'S.ERRORHANDLER.CALLBACK = eps', 'S.ERRORFATALTRACE = eps',
         'S.REPORTING = 256',
         'S_capture = $error_trace_capture(S, 256, ERROR_TRIGGER_PHASE pconfigcall 2)',
         'S_capture.ERRORFATALTRACE = [ptraceframe]',
         'ptraceframe.FILE = $call_sourcefile(S.FILES, pconfigcall.SITE)',
         'ptraceframe.LINE = pconfigcall.LINE',
         'ptraceframe.FUNCTION = $ptascii("trigger_error")',
         'ptraceframe.ARGS = [(KINT 0, PSTRING ($ptascii("fatal"))), (KINT 1, PINT 256)]',
         'ptraceframe.CLASS = eps', 'ptraceframe.TYPE = eps', 'ptraceframe.HASARGS',
         *GUARDS, 'PhpStep: S ~> S_one',
         'S_one.COMPLETION = USERFATAL ($ptascii("fatal")) pconfigcall.LINE true',
         'S_one.TODO = eps', 'S_one.ERRORFATALTRACE = eps',
         'S_one.TRACE = S_capture.ERRORFATALTRACE', 'S_one.EVENTS = S.EVENTS',
         '$heap_valid($heap_graph(S_one))', 'S_done = S_one',
     ]),
]

from reporting_protocol import CASE as REPORTING_CASE
CASES.append(REPORTING_CASE)
