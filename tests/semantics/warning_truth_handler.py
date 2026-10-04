"""Inherited method handlers entered by original-null truth decisions."""
from error_handler_protocol import PREFIX
from warning_truth_protocol import GUARDS, FINISH

SOURCE = b"""<?php
error_reporting(0);
class TruthOwner209 {
    public static function normal($severity, $message, $file, $line) {
        echo 'A', func_num_args(), ':', __CLASS__, '/', static::class;
        $GLOBALS['arrayDecision209'] = 7;
        return true;
    }
    public static function fail($severity, $message, $file, $line) {
        echo ';S', func_num_args();
        $GLOBALS['stringDecision209'] = 8;
        throw new Error('truth-stop');
    }
}
class TruthChild209 extends TruthOwner209 {}
$arrayHandler209 = ['TruthChild209', 'normal'];
set_error_handler($arrayHandler209, 2);
if ($arrayDecision209) { echo 'T'; } else { echo 'F'; }
echo ':', $arrayDecision209, ':', get_error_handler() === $arrayHandler209 ? '1' : 'X';
restore_error_handler();
$stringHandler209 = 'TruthChild209::fail';
set_error_handler($stringHandler209, 2);
$destination209 = 'old';
try { $destination209 = true && $stringDecision209; echo 'BAD'; }
catch (Error $error209) {
    echo 'C:', $destination209, ':', $stringDecision209, ':', get_error_handler() === $stringHandler209 ? '1' : 'X';
}
restore_error_handler();
"""
EXPECTED = b'A4:TruthOwner209/TruthChild209F:7:1;S4C:old:8:1'
ID = 'array-normal-string-throw-truth'
STAGE = ('S.TODO = (ARGINFO_INVOKE pargcall) :: ptask_tail*'
         ' -- if S.CURRENT = (pcallcontext)'
         ' -- if pcallcontext.TARGET = HANDLER_METHOD_TARGET true porigin_requested ptbytes_method pcalltarget'
         ' -- if ptbytes_method = $ptascii("fail")')
CHECKS = [
    'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask_tail*',
    'pargcall.KIND = INTRINSIC_FUNC_NUM_ARGS',
    '$call_task_valid(S, ARGINFO_INVOKE pargcall)',
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.TARGET = HANDLER_METHOD_TARGET true porigin_requested $ptascii("fail") pcalltarget',
    'pcalltarget = SCOPED_TARGET porigin_requested porigin_method porigin_requested eps (KNOWN (PSTRING $ptascii("TruthChild209")))',
    'pcallcontext.FUNCTION = porigin_method',
    'pcallcontext.LEXICAL_CLASS = (porigin_owner)',
    'porigin_owner =/= porigin_requested',
    'pcallcontext.CALLED_CLASS = (porigin_requested)',
    'pcallcontext.RECEIVER = eps',
    'pcallcontext.INSTANCE = eps',
    'pcallcontext.ARGC = 4',
    '$class_at(S.CLASSES, porigin_requested) = (pclassdesc)',
    'pclassdesc.NAME = $ptascii("TruthChild209")',
    '$class_at(S.CLASSES, porigin_owner) = (pclassdesc_owner)',
    'pclassdesc_owner.NAME = $ptascii("TruthOwner209")',
    '$class_method_origin(S.CLASSES, porigin_method) = (pmethoddesc)',
    'pmethoddesc.OWNER = porigin_owner',
    'pmethoddesc.STATIC',
    '$target_function(S, pcallcontext.TARGET) = (pfunction)',
    'S.CVS = pfunction.CVS',
    'S.BORROWEDREAD = eps',
    'S.ERRORHANDLER.CALLBACK = eps',
    'S.FRAMES = [pframe]',
    'pframe.CONTEXT = eps',
    'pframe.LOCALS = eps',
    'pframe.BORROWEDREAD = eps',
    'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_saved*',
    'perrorcall.CALLBACK = PSTRING $ptascii("TruthChild209::fail")',
    'perrorcall.TARGET = (pcallcontext.TARGET)',
    'perrorcall.LEVEL = 2',
    'perrorcall.RESUME = ERROR_READ_RESULT perrorread',
    'perrorread.NAME = $ptascii("stringDecision209")',
    'perrorread.INPUT = VARIABLE perrorread.NAME z_variable',
    'perrorread.RESULT = KNOWN PNULL',
    'perrorread.TASK = perrorread.ORIGINAL',
    'perrorread.ORIGINAL = TRUTH_RESULT false z',
    'perrorread.LINE = z',
    'S_caller = S[.CURRENT = eps][.FRAMES = eps][.ORIGIN = pframe.ORIGIN][.TODO = pframe.TODO][.BORROWEDREAD = pframe.BORROWEDREAD]',
    'S_caller.ORIGIN = (porigin_truth)',
    '$compiled_redirect(S_caller, porigin_truth) = ((porigin_variable, expression_variable, true, z))',
    '$error_variable_source(S_caller, (porigin_variable), eps, perrorread.NAME)',
    '$error_read_valid(S_caller, perrorread)',
    '$error_entered_call_valid(S_caller, perrorcall)',
    '$error_context_valid(S, pcallcontext)',
    '$arginfo_values(S, pcallcontext) = $error_handler_values(S, perrorcall)',
    '$arginfo_values(S, pcallcontext) = [PINT 2, PSTRING ($ptascii("Undefined variable $stringDecision209")), PSTRING ptbytes_file, PINT z]',
    '$target_nodes(pcallcontext.TARGET) = eps',
    '$error_selected_roots(perrorcall.TARGET) = eps',
    'S_global = $global_table_view(S)',
    '$lookup(S_global.ENV, $ptascii("arrayDecision209")) = (n_array_live)',
    'S.STORE[n_array_live] = DEFINED (PINT 7)',
    '$error_missing_operand(S_global, perrorread.INPUT)',
    '$lookup(S_global.ENV, $ptascii("destination209")) = (n_destination)',
    'S.STORE[n_destination] = DEFINED (PSTRING $ptascii("old"))',
    '~$error_handler_selected(S, PSTRING $ptascii("TruthOwner209::fail"), pcallcontext.TARGET)',
    '~$error_handler_selected(S, perrorcall.CALLBACK, HANDLER_METHOD_TARGET false porigin_requested $ptascii("fail") pcalltarget)',
    '~$error_entered_call_valid(S_caller, perrorcall[.TARGET = (HANDLER_METHOD_TARGET true porigin_requested $ptascii("fail") (SCOPED_TARGET porigin_requested porigin_method porigin_owner eps (KNOWN (PSTRING $ptascii("TruthChild209")))))])',
    '~$error_context_valid(S, pcallcontext[.CALLSITE = (porigin_method)])',
    '~$error_context_valid(S, pcallcontext[.LINE = $(perrorcall.LINE + 1)])',
    '~$call_current_valid(S[.CURRENT = (pcallcontext[.ARGC = 0])])',
    '~$call_current_valid(S[.CVS = eps])',
    '~$error_read_valid(S_caller, perrorread[.RESULT = KNOWN (PINT 8)])',
    '~$error_read_valid(S_caller, perrorread[.NAME = $ptascii("arrayDecision209")])',
    '~$error_read_valid(S_caller, perrorread[.ORIGINAL = TRUTH_RESULT true z][.TASK = TRUTH_RESULT true z])',
    '~$call_frames_valid(S, [pframe[.TODO = (ERROR_HANDLER_RESULT perrorcall[.RESUME = ERROR_READ_RESULT perrorread[.RESULT = KNOWN (PINT 8)]]) :: ptask_saved*]])',
    *GUARDS,
    *FINISH,
    'S_done.STORE[n_array_live] = DEFINED (PINT 7)',
    'S_done.STORE[n_destination] = DEFINED (PSTRING $ptascii("old"))',
    '$lookup(S_done.ENV, $ptascii("stringDecision209")) = (n_string_live)',
    'S_done.STORE[n_string_live] = DEFINED (PINT 8)',
]
SOURCES = [(ID, SOURCE, EXPECTED, 'normal')]
CASES = [('method-handler-folded-truth-context', ID, STAGE, CHECKS)]
