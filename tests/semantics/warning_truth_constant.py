"""Deferred array cache inside an original-null warning-truth callback."""
from error_handler_protocol import PREFIX
from warning_truth_protocol import GUARDS, FINISH

SOURCE = b"""<?php
error_reporting(0);
class TruthConstant209 { const X = [TRUTH_VALUE209]; }
const TRUTH_VALUE209 = 7;
$handler = function($severity, $message, $file, $line) {
    echo 'H', func_num_args();
    $copy = TruthConstant209::X;
    $copy[0] = 9;
    $GLOBALS['decision209'] = 7;
    echo ':', $copy[0];
    return true;
};
set_error_handler($handler, 2);
if ($decision209) { echo 'T'; } else { echo 'F'; }
echo ':', $decision209, ':', TruthConstant209::X[0], ':', get_error_handler() === $handler ? '1' : 'X';
restore_error_handler();
"""
EXPECTED = b'H4:9F:7:7:1'
ID = 'truth-handler-deferred-array-cache'
STAGE = ('S.TODO = (CLASS_CONST_BIND porigin_x) :: ptask_tail*'
         ' -- if S.CURRENT = (pcallcontext)'
         ' -- if pcallcontext.TARGET = CLOSURE_TARGET n_handler')
CHECKS = [
    'S.TODO = (CLASS_CONST_BIND porigin_x) :: ptask_tail*',
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.TARGET = CLOSURE_TARGET n_handler',
    'pcallcontext.INSTANCE = (n_handler)',
    'pcallcontext.ARGC = 4',
    '$target_function(S, pcallcontext.TARGET) = (pfunction)',
    'S.CVS = pfunction.CVS',
    'S.BORROWEDREAD = eps',
    'S.ERRORHANDLER.CALLBACK = eps',
    'S.FRAMES = [pframe]',
    'pframe.CONTEXT = eps',
    'pframe.LOCALS = eps',
    'pframe.BORROWEDREAD = eps',
    'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_saved*',
    'perrorcall.CALLBACK = POBJECT n_handler',
    'perrorcall.TARGET = (pcallcontext.TARGET)',
    'perrorcall.LEVEL = 2',
    'perrorcall.RESUME = ERROR_READ_RESULT perrorread',
    'perrorread.NAME = $ptascii("decision209")',
    'perrorread.RESULT = KNOWN PNULL',
    'perrorread.TASK = perrorread.ORIGINAL',
    'perrorread.ORIGINAL = CHOOSE ptask_true* ptask_false* z',
    'S_caller = S[.CURRENT = eps][.FRAMES = eps][.ORIGIN = pframe.ORIGIN][.TODO = pframe.TODO][.BORROWEDREAD = pframe.BORROWEDREAD]',
    'S_caller.ORIGIN = (porigin_if)',
    '$origin_node(S.SOURCES, porigin_if) = (NStmtIf expression (SEQUENCE statement*) (SEQUENCE phpType54*) phpType55 metadata)',
    '$error_variable_source(S_caller, S_caller.ORIGIN, [PCFIELD 0], perrorread.NAME)',
    '$error_read_valid(S_caller, perrorread)',
    '$error_entered_call_valid(S_caller, perrorcall)',
    '$error_context_valid(S, pcallcontext)',
    '$arginfo_values(S, pcallcontext) = $error_handler_values(S, perrorcall)',
    'S.CLASSCONSTANTINIT = [pclassconstantcontext]',
    'pclassconstantcontext.DECL = porigin_x',
    'pclassconstantcontext.PREVIOUS = eps',
    'pclassconstantcontext.ORIGIN = (porigin_fetch)',
    'S.CONSTCONTEXT = (pconstantcontext)',
    'pconstantcontext.ORIGIN = porigin_x',
    'pconstantcontext.LINE = pclassconstantcontext.LINE',
    '$class_constant_origin(S.CLASSES, porigin_x) = (pclassconstantdesc)',
    'pclassconstantdesc.OWNERNAME = $ptascii("TruthConstant209")',
    'pclassconstantdesc.NAME = $ptascii("X")',
    '~pclassconstantdesc.FOLDED',
    '$origin_node(S.SOURCES, pclassconstantdesc.INITIALIZER) = (NExprArray phpType12 metadata_array)',
    '$default_cache_at(S.CLASSCONSTANTCACHE, porigin_x) = eps',
    '$class_constant_state_valid(S)',
    'S_value = $resolve_at(S, S.RESULT, pconstantcontext.LINE)',
    'S_value.COMPLETION = NORMAL',
    'S_value.RESULT = KNOWN (PARRAY n_array)',
    'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
    '~$class_constant_state_valid(S[.CLASSCONSTANTINIT = eps])',
    '~$class_constant_state_valid(S[.TODO = ptask_tail*])',
    '~$class_constant_state_valid(S[.CLASSCONSTANTINIT = [pclassconstantcontext[.LINE = 999]]])',
    '~$class_constant_state_valid(S[.CONSTCONTEXT = (pconstantcontext[.ORIGIN = porigin_fetch])])',
    '~$call_current_valid(S[.CURRENT = (pcallcontext[.ARGC = 0])])',
    '~$call_current_valid(S[.CVS = eps])',
    '~$call_frames_valid(S, [pframe[.TODO = (ERROR_HANDLER_RESULT perrorcall[.RESUME = ERROR_READ_RESULT perrorread[.RESULT = KNOWN (PINT 7)]]) :: ptask_saved*]])',
    'PhpStep: S ~> S_bound',
    'S_bound.COMPLETION = NORMAL',
    'S_bound.CLASSCONSTANTINIT = eps',
    'S_bound.CONSTCONTEXT = eps',
    'S_bound.CURRENT = S.CURRENT',
    'S_bound.FRAMES = S.FRAMES',
    'S_bound.ORIGIN = (porigin_fetch)',
    '$default_cache_at(S_bound.CLASSCONSTANTCACHE, porigin_x) = (pdefaultcache)',
    'pdefaultcache.VALUE = PARRAY n_array',
    '(HARRAY n_array) <- $class_constant_roots(S_bound.CLASSCONSTANTCACHE)',
    '$class_constant_state_valid(S_bound)',
    '$heap_owners($heap_graph(S_bound), HARRAY n_array) = 2',
    *GUARDS,
    *FINISH,
    'S_done.CLASSCONSTANTINIT = eps',
    'S_done.CONSTCONTEXT = eps',
    '$default_cache_at(S_done.CLASSCONSTANTCACHE, porigin_x) = (pdefaultcache)',
    'S_done.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
    '$heap_owners($heap_graph(S_done), HARRAY n_array) = 1',
    '$class_constant_state_valid(S_done)',
]
SOURCES = [(ID, SOURCE, EXPECTED, 'normal')]
CASES = [('truth-handler-constant-context', ID, STAGE, CHECKS)]
