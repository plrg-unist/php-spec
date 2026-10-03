"""One reached handler/Stringable property conversion and its trace readback."""
from error_handler_protocol import PREFIX

SOURCE = b'''<?php
class HandlerHolder13 {public static string $text='old';}
class HandlerText13 implements Stringable {
 public function __toString():string {echo func_num_args();throw new Error('conversion');}
}
function eh13typed($n,$m,$f,$l) {echo func_num_args();HandlerHolder13::$text=new HandlerText13;}
set_error_handler('eh13typed',512);
try {trigger_error('warning',512);} catch (Error $e) {
 echo ':',HandlerHolder13::$text,':',$e->getTraceAsString(),':',get_error_handler()==='eh13typed';
}
restore_error_handler();
'''


def trace_bytes(path):
    name = str(path).encode()
    return (b'#0 ' + name + b'(6): HandlerText13->__toString()\n'
            b'#1 [internal function]: eh13typed(512, \'warning\', \'' + name[:15]
            + b'...\', 8)\n#2 ' + name + b'(8): trigger_error(\'warning\', 512)\n#3 {main}')


def expected_stdout(path):
    return b'40:old:' + trace_bytes(path) + b':1'


STAGE = 'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask_tail* -- if S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 0'

CHECKS = [
    'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask_tail*',
    'S.CURRENT = (pcallcontext)', 'pcallcontext.TARGET = METHOD_TARGET n_text porigin_method',
    'pcallcontext.RECEIVER = (n_text)', 'pcallcontext.INSTANCE = eps',
    'pcallcontext.ARGC = 0', '$arginfo_values(S, pcallcontext) = eps',
    '$target_function(S, pcallcontext.TARGET) = (pfunction)', 'S.CVS = pfunction.CVS',
    'S.FRAMES = pframe_handler :: pframe_emitter :: pframe_tail*',
    'pframe_handler.TODO = (STRINGIFY_RESULT n_text porigin_string z_string) :: (STATIC_STRING_RESULT pstaticstring) :: (STATIC_STRING_CAPTURE pstaticstring) :: ptask_saved*',
    'pstaticstring.OBJECT = n_text', 'pstaticstring.SITE = porigin_string', 'pstaticstring.LINE = z_string',
    '$static_string_record_valid(S, pstaticstring)', '$stringify_context(S, pcallcontext)',
    'pframe_handler.CONTEXT = (pcallcontext_handler)',
    'pcallcontext_handler.NAME = $ptascii("eh13typed")', 'pcallcontext_handler.ARGC = 4',
    '$target_function(S, pcallcontext_handler.TARGET) = (pfunction_handler)',
    'pframe_handler.LOCALS = (psymboltable_handler)', 'psymboltable_handler.CVS = pfunction_handler.CVS',
    'pframe_emitter.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_emitter*',
    'perrorcall.CALLBACK = PSTRING ($ptascii("eh13typed"))',
    'perrorcall.LEVEL = 512', 'perrorcall.MESSAGE = $ptascii("warning")',
    'perrorcall.TARGET = (pcallcontext_handler.TARGET)',
    '$error_context_valid(S, pcallcontext_handler)', '$call_saved_context_valid(S, pframe_handler)',
    '~$call_saved_context_valid(S, pframe_handler[.CONTEXT = (pcallcontext_handler[.ARGC = 0])])',
    '~$call_saved_context_valid(S, pframe_handler[.LOCALS = (psymboltable_handler[.CVS = eps])])',
    '~$call_descriptors_valid(S[.FRAMES = pframe_handler :: pframe_emitter[.TODO = ptask_emitter*] :: pframe_tail*])',
    '~$call_current_valid(S[.CURRENT = (pcallcontext[.INSTANCE = (n_text)])])',
    'S.ERRORHANDLER.CALLBACK = eps',
    '$class_static_at(S.CLASSSTATICS, pstaticstring.DECL) = (pclassstatic)',
    'pclassstatic.STATE = PROP_VALUE pitem_old', '$entry_value(S, pitem_old) = PSTRING ($ptascii("old"))',
    '$call_current_valid(S)', '$call_frames_valid(S, S.FRAMES)', '$call_descriptors_valid(S)',
    '$heap_valid($heap_graph(S))', '$outputs(S.EVENTS) = [52]',
    'S_done = $drive(S, 1500)', 'S_done.COMPLETION = NORMAL',
    'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps',
    'S_done.TRACE = eps', 'S_done.ERRORHANDLER.CALLBACK = eps', 'S_done.ERRORHANDLERS = eps',
    '$class_static_at(S_done.CLASSSTATICS, pstaticstring.DECL) = (pclassstatic_done)',
    'pclassstatic_done.STATE = PROP_VALUE pitem_done', '$entry_value(S_done, pitem_done) = PSTRING ($ptascii("old"))',
    '$lookup(S_done.ENV, $ptascii("e")) = (n_error_cell)', 'S_done.STORE[n_error_cell] = DEFINED (POBJECT n_error)',
    '$throwable_field(S_done, n_error, "trace") = PARRAY n_trace', '$trace_graph_valid(S_done, n_trace)',
    'S_done.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_string_frame)), ENTRY (KINT 1) (DIRECT (PARRAY n_handler_frame)), ENTRY (KINT 2) (DIRECT (PARRAY n_trigger_frame))]',
    '$trace_array_field(S_done, n_string_frame, $ptascii("function")) = PSTRING ($ptascii("__toString"))',
    '$trace_array_field(S_done, n_string_frame, $ptascii("line")) = PINT 6',
    '$trace_array_field(S_done, n_handler_frame, $ptascii("function")) = PSTRING ($ptascii("eh13typed"))',
    '$entry_lookup(S_done.ARRAYS[n_handler_frame].ITEMS, KSTRING ($ptascii("file"))) = eps',
    '$entry_lookup(S_done.ARRAYS[n_handler_frame].ITEMS, KSTRING ($ptascii("line"))) = eps',
    '$trace_array_field(S_done, n_handler_frame, $ptascii("args")) = PARRAY n_handler_args',
    '|S_done.ARRAYS[n_handler_args].ITEMS| = 4',
    '$trace_array_field(S_done, n_trigger_frame, $ptascii("function")) = PSTRING ($ptascii("trigger_error"))',
    '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    'S_done = $drive(S_initial[.COMPLETION = NORMAL], 1500)',
]
