"""Held PIPE value and original-null selection across a source warning handler."""
from error_handler_protocol import PREFIX
from warning_truth_protocol import NULL_READ, GUARDS, FINISH

SOURCE = b'''<?php
error_reporting(0);
ini_set('include_path', "before\\0tail");
class TruthPipeValue209 {
    function __toString(): string {
        echo 'C', func_num_args(), func_get_args() === [] ? 'Z' : 'X', $GLOBALS['left209'] === null ? 'N' : 'X';
        return 'after';
    }
}
$handler = function($severity, $message, $file, $line) {
    echo 'H', func_num_args();
    $GLOBALS['condition209'] = 7;
    $GLOBALS['left209'] = null;
    ini_set('include_path', "inner\\0tail");
};
set_error_handler($handler, 2);
$left209 = new TruthPipeValue209;
$old = $left209 |> ($condition209 ? ini_restore(...) : set_include_path(...));
echo '|', $old, '|', get_include_path(), '|', $condition209, ':', get_error_handler() === $handler ? '1' : 'X';
restore_error_handler();
'''
EXPECTED = b'H4C0ZN|inner|after|7:1'
ID = 'pipe-original-null-held-value'
STAGE = 'S.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*'
PREFIX += r'''
dec $held_pipe_task(ptask) : bool
def $held_pipe_task(PIPE_APPLY porigin poperand z_send z_call) = true
def $held_pipe_task(ptask) = false -- otherwise
dec $held_pipe(ptask*) : (porigin, poperand, int, int)?
def $held_pipe(eps) = eps
def $held_pipe((PIPE_APPLY porigin poperand z_send z_call) :: ptask*) = ((porigin, poperand, z_send, z_call))
def $held_pipe(ptask :: ptask_tail*) = $held_pipe(ptask_tail*) -- if ~$held_pipe_task(ptask)
'''
CHECKS = [
    *NULL_READ,
    'perrorread.NAME = $ptascii("condition209")',
    'perrorread.ORIGINAL = SELECT_VALUE expression_true expression_false z_cond z_true z_false',
    'perrorread.LINE = z_cond', 'S.ORIGIN = (porigin)',
    '$origin_node(S.SOURCES, porigin) = (NExprTernary expression_cond expression_true expression_false metadata)',
    '$error_variable_source(S, S.ORIGIN, [PCFIELD 0], perrorread.NAME)',
    '$held_pipe(ptask_tail*) = ((porigin_pipe, KNOWN (POBJECT n_object), z_send, z_call))',
    '$origin_child((porigin_pipe), [PCFIELD 1]) = (porigin)',
    '$origin_node(S.SOURCES, porigin_pipe) = (NExprBinaryOpPipe expression_left expression_right metadata_pipe)',
    'expression_right = NExprTernary expression_cond expression_true expression_false metadata',
    '~$pppipe_optimized(expression_right)',
    '$pipe_fixed_name(S, porigin_pipe) = eps',
    '$call_task_valid(S[.ORIGIN = (porigin_pipe)], PIPE_APPLY porigin_pipe (KNOWN (POBJECT n_object)) z_send z_call)',
    '(HOBJECT n_object) <- $task_nodes(PIPE_APPLY porigin_pipe (KNOWN (POBJECT n_object)) z_send z_call)',
    '$getclass_live_object(S, n_object)',
    '$heap_owners($heap_graph(S), HOBJECT n_object) = 1',
    '$lookup(S.ENV, $ptascii("left209")) = (n_left_slot)',
    'S.STORE[n_left_slot] = DEFINED PNULL',
    'S.FILEINCLUDEPATH = ($ptascii("inner") ++ [0] ++ $ptascii("tail"))',
    '~$call_task_valid(S[.ORIGIN = (porigin_pipe)], PIPE_APPLY porigin_pipe (KNOWN (POBJECT n_object)) 999 z_call)',
    '~$call_task_valid(S[.ORIGIN = (porigin_pipe)], PIPE_APPLY porigin_pipe (KNOWN (POBJECT n_object)) z_send 999)',
    '~$call_task_valid(S[.ORIGIN = (porigin)], PIPE_APPLY porigin_pipe (KNOWN (POBJECT n_object)) z_send z_call)',
    '~$error_read_valid(S, perrorread[.ORIGINAL = SELECT_VALUE expression_false expression_true z_cond z_true z_false][.TASK = SELECT_VALUE expression_false expression_true z_cond z_true z_false])',
    'PhpStep: S_resume ~> S_chosen',
    'S_chosen.TODO = [$at_task($origin_child(S.ORIGIN, [PCFIELD 2]), EVAL expression_false), VALUE_COPY z_false] ++ ptask_tail*',
    'S_chosen.RESULT = KNOWN PNULL', 'S_chosen.STORE[n_live] = DEFINED (PINT 7)',
    *GUARDS, *FINISH,
    'S_done.FILEINCLUDEPATH = ($ptascii("after"))',
]

SOURCES = [(ID, SOURCE, EXPECTED, "normal")]
CASES = [("pipe-held-value-source-certificate", ID, STAGE, CHECKS)]
