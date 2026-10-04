#!/usr/bin/env python3
"""Genuine file-operand ownership, warning phases and shutdown retirement controls."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile
import textwrap

from error_handler_run import recorded
from recorded_worker import Worker

R = Path(__file__).resolve().parents[2]
C = R
SOURCES = Path(__file__).with_name('file_operands')
b64 = lambda value: base64.b64encode(value).decode()
text = lambda value: '$base64(' + json.dumps(b64(value)) + ')'
term = text


def render_owner(fixtures, source, throw_source):
    helpers=r'''
    dec $file_operand_stage(pstate, int) : bool
    def $file_operand_stage(S, 0) = true
      -- if S.TODO = (FILE_REQUEST porigin_parent z n_kind) :: (ORIGIN_RETURN (porigin_parent)) :: ptask_tail*
      -- if $eval_callback_ready(S[.COMPLETION = NORMAL], z)
    def $file_operand_stage(S, 1) = true
      -- if S.TODO = (CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_child) z) :: (STRINGIFY_RESULT n porigin_child z) :: (FILE_REQUEST porigin_parent z n_kind) :: (ORIGIN_RETURN (porigin_parent)) :: ptask_tail*
    def $file_operand_stage(S, 2) = true
      -- if S.CURRENT = (pcallcontext)
      -- if pcallcontext.CALLSITE = (porigin_child)
      -- if S.FRAMES = pframe :: pframe_tail*
      -- if pframe.TODO = (STRINGIFY_RESULT n porigin_child z) :: (FILE_REQUEST porigin_parent z n_kind) :: (ORIGIN_RETURN (porigin_parent)) :: ptask_tail*
    def $file_operand_stage(S, 3) = true
      -- if S.CURRENT = eps
      -- if S.TODO = (STRINGIFY_RESULT n porigin_child z) :: (FILE_REQUEST porigin_parent z n_kind) :: (ORIGIN_RETURN (porigin_parent)) :: ptask_tail*
      -- if S.RESULT = KNOWN (PSTRING n_value*)
    def $file_operand_stage(S, 4) = true
      -- if S.COMPLETION = SOURCE_PENDING
      -- if S.FILECONTEXTS = pfilecontext :: pfilecontext_tail*
      -- if S.TODO = (FILE_RESOLVE_AWAIT pfilecontext.NONCE) :: (ORIGIN_RETURN (pfilecontext.SITE)) :: ptask_tail*
    def $file_operand_stage(S, z) = false -- otherwise
    '''
    helpers+=r'''
    dec $file_operand_seek(pstate, int, nat) : pstate
    def $file_operand_seek(S, z, n) = S -- if $file_operand_stage(S, z)
    def $file_operand_seek(S, z, n) = S
      -- if ~$file_operand_stage(S, z)
      -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
    def $file_operand_seek(S, z, 0) = S
      -- if ~$file_operand_stage(S, z)
      -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
    def $file_operand_seek(S, z, n) = $file_operand_seek($drive_steps(S[.COMPLETION = NORMAL], 1), z, $nabs($(n - 1)))
      -- if ~$file_operand_stage(S, z)
      -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
      -- if $(n > 0)
    '''
    text=lambda b:'$base64('+json.dumps(b64(b))+')'
    checks=[
        'pstartup = {REPORTING ($ptascii("30719")), INCLUDEPATH $ptascii(".:")}',
        'S_initial = $php_file_startup_run($file_operand_program(), 0, '+text(bytes(source))+', '+text(bytes(C))+', pstartup)',
        '$call_descriptors_valid(S_initial)',
        'S_before = $file_operand_seek(S_initial, 0, 1000)', '$file_operand_stage(S_before, 0)',
        '$call_descriptors_valid(S_before)',
        'S_before.TODO = (FILE_REQUEST porigin_parent z 1) :: (ORIGIN_RETURN (porigin_parent)) :: ptask_tail*',
        'S_before.ORIGIN = (porigin_child)', '$file_operand_site_valid(S_before, porigin_parent, porigin_child, z, 1)',
        'S_before.FILESEQ = 0', 'S_before.FILECONTEXTS = eps',
        '~$call_descriptors_valid(S_before[.ORIGIN = (porigin_parent)])',
        '~$call_descriptors_valid(S_before[.TODO = (FILE_REQUEST porigin_parent z 1) :: ptask_tail*])',
        '~$call_descriptors_valid(S_before[.TODO = (FILE_REQUEST porigin_parent z 2) :: (ORIGIN_RETURN (porigin_parent)) :: ptask_tail*])',
        'S_pending = $file_operand_seek(S_initial, 1, 1000)', '$file_operand_stage(S_pending, 1)',
        '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
        'S_pending.TODO = (CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_child) z) :: (STRINGIFY_RESULT n porigin_child z) :: (FILE_REQUEST porigin_parent z 1) :: (ORIGIN_RETURN (porigin_parent)) :: ptask_tail*',
        '$stringify_pending(S_pending, METHOD_TARGET n porigin_method, porigin_child)',
        'S_pending.FILESEQ = 0', 'S_pending.FILECONTEXTS = eps',
        '~$call_descriptors_valid(S_pending[.TODO = (CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_child) z) :: (STRINGIFY_RESULT n porigin_child z) :: (FILE_REQUEST porigin_parent z 1) :: (ORIGIN_RETURN (porigin_child)) :: ptask_tail*])',
        '~$call_descriptors_valid(S_pending[.TODO = (CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_child) z) :: (STRINGIFY_RESULT n porigin_child z) :: (FILE_REQUEST porigin_parent $(z + 1) 1) :: (ORIGIN_RETURN (porigin_parent)) :: ptask_tail*])',
        'S_entered = $file_operand_seek(S_initial, 2, 1000)', '$file_operand_stage(S_entered, 2)',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
        'S_entered.CURRENT = (pcallcontext)', 'S_entered.FRAMES = pframe :: pframe_tail*',
        'pcallcontext.CALLSITE = (porigin_child)', '$stringify_context_frame_valid(S_entered, pcallcontext, pframe)',
        '$eval_trace_preparser(S_entered, S_entered.CURRENT, pframe) = [ptraceframe]',
        'ptraceframe.FILE = '+text(bytes(source)), 'ptraceframe.LINE = z', 'ptraceframe.FUNCTION = $ptascii("include")',
        'ptraceframe.ARGS = eps', '~ptraceframe.HASARGS',
        '$eval_trace_preparser(S_entered, (pcallcontext[.CALLSITE = eps]), pframe) = eps',
        '~$call_descriptors_valid(S_entered[.CURRENT = (pcallcontext[.LINE = $(z + 1)])])',
        '~$call_descriptors_valid(S_entered[.CURRENT = (pcallcontext[.RECEIVER = ($(n + 1))])])',
        '~$call_descriptors_valid(S_entered[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n porigin_child z) :: (FILE_REQUEST porigin_parent z 1) :: ptask_tail*] :: pframe_tail*])',
        'S_result = $file_operand_seek(S_initial, 3, 1000)', '$file_operand_stage(S_result, 3)',
        '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
        'S_result.TODO = (STRINGIFY_RESULT n porigin_child z) :: (FILE_REQUEST porigin_parent z 1) :: (ORIGIN_RETURN (porigin_parent)) :: ptask_tail*',
        'S_result.RESULT = KNOWN (PSTRING $ptascii("selected.php"))',
        'S_result.FILEINCLUDEPATH = ($ptascii("/live-path"))', 'S_result.FILESEQ = 0', 'S_result.FILECONTEXTS = eps',
        '(HOBJECT n) <- $heap_graph(S_result).ROOTS',
        '~$call_descriptors_valid(S_result[.ALLOCATIONS = $call_remove_owner(S_result.ALLOCATIONS, HOBJECT n)])',
        '~$call_descriptors_valid(S_result[.TODO = (STRINGIFY_RESULT $(n + 1) porigin_child z) :: (FILE_REQUEST porigin_parent z 1) :: (ORIGIN_RETURN (porigin_parent)) :: ptask_tail*])',
        'S_wait = $file_operand_seek(S_initial, 4, 1000)', '$file_operand_stage(S_wait, 4)',
        '$call_descriptors_valid(S_wait)', '$file_pending_state_valid(S_wait)',
        'S_wait.FILECONTEXTS = pfilecontext :: pfilecontext_tail*', 'pfilecontext.NONCE = 0', 'S_wait.FILESEQ = 1',
        'pfilecontext.SITE = porigin_parent', 'S_wait.ORIGIN = (porigin_parent)',
        'pfilecontext.REQUESTED = $ptascii("selected.php")', 'pfilecontext.INCLUDEPATH = $ptascii("/live-path")',
        'pfilecontext.CWD = '+text(bytes(C)), 'pfilecontext.OWNER = 0', 'pfilecontext.LEXICAL_CLASS = eps',
        '~$file_pending_state_valid(S_wait[.FILEINCLUDEPATH = ($ptascii(".:"))])',
        '~$file_pending_state_valid(S_wait[.FILESEQ = 2])',
        '~((HOBJECT n) <- S_wait.ALLOCATIONS)',
        '~((HOBJECT n) <- $heap_graph(S_wait).ROOTS)',
        '~$call_descriptors_valid(S_wait[.ORIGIN = (porigin_child)])',
        'S_throw = $php_startup_run($file_operand_throw_program(), 2000, '+json.dumps(b64(bytes(throw_source)))+', pstartup)',
        'S_throw.COMPLETION = NORMAL', '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))', 'S_throw.FILECWD = eps',
        'S_throw.FILESEQ = 0', 'S_throw.FILECONTEXTS = eps', 'S_throw.FILEBINDINGS = eps',
    ]
    helpers = textwrap.dedent(helpers)
    rendered='dec $file_operand_program() : program\ndef $file_operand_program() = '+fixtures['owner']+'\n'
    rendered+='dec $file_operand_throw_program() : program\ndef $file_operand_throw_program() = '+fixtures['owner_throw']+'\n'+helpers
    rendered+='\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+check+'\n' for check in checks)+'def $main() = false -- otherwise\n'
    assert len(checks) == 81
    return rendered, checks


def render_warning(fixtures, P):
    setup = ''.join('dec $file_warning_' + name.replace('-', '_') + '_program() : program\ndef $file_warning_'
                    + name.replace('-', '_') + '_program() = ' + fixture + '\n' for name, fixture in fixtures.items())
    helpers = r'''
    dec $file_warning_ready(pstate, nat) : bool
    def $file_warning_ready(S, n_phase) = true
      -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
      -- if perrorcall.RESUME = FILE_WARNING_PHASE n_nonce n_phase
    def $file_warning_ready(S, 4) = true
      -- if S.TODO = [EXIT_UNWIND 0]
      -- if |S.FRAMES| = 1
    def $file_warning_ready(S, 5) = true
      -- if S.TODO = [ERROR_UNWIND pcompletion]
      -- if |S.FRAMES| = 1
    def $file_warning_ready(S, n_phase) = false -- otherwise
    dec $file_warning_seek(pstate, nat, nat) : pstate
    def $file_warning_seek(S, n_phase, n) = S -- if $file_warning_ready(S, n_phase)
    def $file_warning_seek(S, n_phase, n) = S
      -- if ~$file_warning_ready(S, n_phase)
      -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
    def $file_warning_seek(S, n_phase, 0) = S
      -- if ~$file_warning_ready(S, n_phase)
      -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
    def $file_warning_seek(S, n_phase, n) = $file_warning_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
      -- if ~$file_warning_ready(S, n_phase)
      -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
      -- if $(n > 0)
    '''
    start = lambda name: '$php_file_startup_run($file_warning_' + name.replace('-', '_') + '_program(), 2000, ' + term(bytes(P / (name + '.php'))) + ', ' + term(bytes(C)) + ', pstartup)'
    missing = lambda nonce, name, request: 'FILE_MISSING ' + str(nonce) + ' ' + term(bytes(P / (name + '.php'))) + ' $ptascii(' + json.dumps(request) + ') $ptascii("No such file or directory")'
    checks = [
        'pstartup = {REPORTING ($ptascii("30719")), INCLUDEPATH $ptascii(".:")}',
        'S_wait = ' + start('live'), 'S_wait.COMPLETION = SOURCE_PENDING', '$call_descriptors_valid(S_wait)',
        'S_wait.FILECONTEXTS = pfilecontext_wait :: eps', 'pfilecontext_wait.NONCE = 0',
        'pfilecontext_wait.INCLUDEPATH = $ptascii("provider-path")',
        '$file_open_response_valid(S_wait, ' + missing(0, 'live', 'warning-missing.php') + ')',
        'S_stream = $file_open_resume(S_wait, ' + missing(0, 'live', 'warning-missing.php') + ')',
        'S_stream.COMPLETION = NORMAL', 'S_stream.FILECONTEXTS = pfilecontext_stream :: eps',
        'pfilecontext_stream.PHASE = FILE_WARNING_STREAM $ptascii("warning-missing.php") $ptascii("No such file or directory")',
        '$call_descriptors_valid(S_stream)', '$file_warning_task_valid(S_stream, 0, 0)',
        '~$file_warning_task_valid(S_stream, 0, 2)', '~$file_warning_task_valid(S_stream, 1, 0)',
        'S_dispatch = $drive_steps(S_stream, 1)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: pfilecontext_stream.TAIL',
        '$error_call_valid(S_dispatch, perrorcall_first)', 'perrorcall_first.RESUME = FILE_WARNING_PHASE 0 1',
        '~$error_call_valid(S_dispatch, perrorcall_first[.LEVEL = 8])',
        '~$error_call_valid(S_dispatch, perrorcall_first[.LINE = $(perrorcall_first.LINE + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall_first[.MESSAGE = $ptascii("forged")])',
        '~$call_descriptors_valid(S_dispatch[.CODE = eps])',
        '~$call_descriptors_valid(S_stream[.FILECONTEXTS = pfilecontext_stream[.OWNER = 1] :: eps])',
        '~$call_descriptors_valid(S_stream[.FILECONTEXTS = pfilecontext_stream[.KIND = 2] :: eps])',
        '~$call_descriptors_valid(S_stream[.FILECONTEXTS = pfilecontext_stream[.TAIL = eps] :: eps])',
        '~$call_descriptors_valid(S_stream[.TODO = [FILE_WARNING_PHASE 0 0, FILE_WARNING_PHASE 0 1] ++ pfilecontext_stream.TAIL])',
        'S_inner = $drive_steps(S_dispatch[.COMPLETION = NORMAL], 2000)', 'S_inner.COMPLETION = SOURCE_PENDING',
        'S_inner.FILECONTEXTS = pfilecontext_inner :: pfilecontext_outer :: eps',
        'pfilecontext_outer = pfilecontext_stream', 'pfilecontext_inner.NONCE = 1',
        'pfilecontext_inner.INCLUDEPATH = $ptascii("after-first")', 'S_inner.FILEINCLUDEPATH = ($ptascii("after-first"))',
        'S_inner.FRAMES = pframe_main :: eps',
        'pframe_main.TODO = (ERROR_HANDLER_RESULT perrorcall_saved) :: pfilecontext_outer.TAIL',
        '$file_warning_owner_valid(S_inner, pfilecontext_outer)', '$file_marker_match(pfilecontext_outer, ERROR_HANDLER_RESULT perrorcall_saved)',
        '$file_marker_count($file_owner_tasks(S_inner, pfilecontext_outer), pfilecontext_outer) = 1',
        '$file_marker_suffix_valid($file_owner_tasks(S_inner, pfilecontext_outer), pfilecontext_outer)',
        '$call_descriptors_valid(S_inner)', '$heap_valid($heap_graph(S_inner))',
        '~$call_descriptors_valid(S_inner[.FRAMES = pframe_main[.TODO = (ERROR_HANDLER_RESULT perrorcall_saved[.RESUME = FILE_WARNING_PHASE 1 1]) :: pfilecontext_outer.TAIL] :: eps])',
        'S_parse = $file_open_resume(S_inner, FILE_OPENED 1 ' + term(bytes(P / 'live.php')) + ' $ptascii("nested-target.php") ' + term(bytes(P / 'nested-target.php')) + ' ' + term(bytes(P / 'nested-target.php')) + ' ' + term((P / 'nested-target.php').read_bytes()) + ')',
        'S_parse.COMPLETION = SOURCE_PENDING', '$call_descriptors_valid(S_parse)',
        'S_nested = $file_parse_resume(S_parse, SOURCE_ACCEPT 1 ' + term((P / 'nested-target.php').read_bytes()) + ' $file_warning_nested_target_program())',
        'S_first_result = $file_warning_seek(S_nested, 1, 2000)', '$file_warning_ready(S_first_result, 1)',
        'S_first_result.RESULT = KNOWN (PBOOL false)', '$call_descriptors_valid(S_first_result)',
        'S_first_result.FILEINCLUDEPATH = ($ptascii("after-first"))',
        'S_open_prepare = $drive_steps(S_first_result[.COMPLETION = NORMAL], 1)',
        'S_open_prepare.TODO = (FILE_WARNING_PHASE 0 1) :: pfilecontext_stream.TAIL',
        'S_open = $drive_steps(S_open_prepare[.COMPLETION = NORMAL], 1)',
        'S_open.FILECONTEXTS = pfilecontext_open :: eps', 'pfilecontext_open.PHASE = FILE_WARNING_OPEN $ptascii("after-first")',
        'S_open.TODO = (FILE_WARNING_PHASE 0 2) :: pfilecontext_open.TAIL', '$call_descriptors_valid(S_open)',
        '~$file_warning_payload_valid(pfilecontext_open[.PHASE = FILE_WARNING_OPEN ([256])])',
        '~$file_warning_payload_valid(pfilecontext_open[.PHASE = FILE_WARNING_OPEN $base64("AEE=")])',
        'S_second_dispatch = $drive_steps(S_open[.COMPLETION = NORMAL], 1)',
        'S_second_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: pfilecontext_open.TAIL',
        '$error_call_valid(S_second_dispatch, perrorcall_second)', 'perrorcall_second.RESUME = FILE_WARNING_PHASE 0 3',
        'S_second_result = $file_warning_seek(S_second_dispatch[.COMPLETION = NORMAL], 3, 2000)',
        '$file_warning_ready(S_second_result, 3)', 'S_second_result.FILEINCLUDEPATH = ($ptascii("after-second"))',
        'S_second_result.FILECONTEXTS = pfilecontext_open :: eps', '$call_descriptors_valid(S_second_result)',
        'S_second_result.TODO = (ERROR_HANDLER_RESULT perrorcall_second_entered) :: pfilecontext_open.TAIL',
        '$error_call_valid(S_second_result, perrorcall_second_entered)',
        '~$error_call_valid(S_second_result, perrorcall_second_entered[.MESSAGE = $file_warning_open_message(pfilecontext_open, $ptascii("after-second"))])',
        'S_done = $drive_steps(S_second_result[.COMPLETION = NORMAL], 2000)', 'S_done.COMPLETION = NORMAL',
        'S_done.FILECONTEXTS = eps', 'S_done.FILESEQ = 2', '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        'S_throw_wait = ' + start('throw'), 'S_throw_wait.COMPLETION = SOURCE_PENDING',
        'S_throw_again = $file_open_continue(S_throw_wait, ' + missing(0, 'throw', 'throw-missing.php') + ')',
        'S_throw_again.COMPLETION = SOURCE_PENDING', 'S_throw_again.FILECONTEXTS = pfilecontext_throw_again :: eps',
        'pfilecontext_throw_again.NONCE = 1', 'pfilecontext_throw_again.PHASE = FILE_RESOLVE_WAIT',
        'S_throw_done = $file_open_continue(S_throw_again, ' + missing(1, 'throw', 'throw-again.php') + ')',
        'S_throw_done.COMPLETION = NORMAL', 'S_throw_done.FILECONTEXTS = eps', '$call_descriptors_valid(S_throw_done)', '$heap_valid($heap_graph(S_throw_done))',
    ]
    for name, stage in [('exit', 4), ('fatal', 5)]:
        prefix = 'S_' + name
        checks += [prefix + '_wait = ' + start(name), prefix + '_wait.COMPLETION = SOURCE_PENDING',
                   prefix + '_stream = $file_open_resume(' + prefix + '_wait, ' + missing(0, name, name + '-missing.php') + ')',
                   prefix + '_before = $file_warning_seek(' + prefix + '_stream, ' + str(stage) + ', 2000)',
                   '$file_warning_ready(' + prefix + '_before, ' + str(stage) + ')',
                   prefix + '_before.FILECONTEXTS = pfilecontext_' + name + ' :: eps',
                   'pfilecontext_' + name + '.OWNER = 0', '|' + prefix + '_before.FRAMES| = 1',
                   '$file_warning_owner_valid(' + prefix + '_before, pfilecontext_' + name + ')',
                   prefix + '_zero = $drive_steps(' + prefix + '_before, 0)', prefix + '_zero.COMPLETION = BUDGET',
                   prefix + '_zero.FILECONTEXTS = ' + prefix + '_before.FILECONTEXTS',
                   '$call_descriptors_valid(' + prefix + '_zero)',
                   prefix + '_one = $drive_steps(' + prefix + '_zero[.COMPLETION = NORMAL], 1)',
                   prefix + '_one.COMPLETION = BUDGET', prefix + '_one.FILECONTEXTS = eps',
                   prefix + '_one.FRAMES = eps', '$call_descriptors_valid(' + prefix + '_one)',
                   prefix + '_done = $drive_steps(' + prefix + '_one[.COMPLETION = NORMAL], 1)',
                   prefix + '_done.FILECONTEXTS = eps', '$call_descriptors_valid(' + prefix + '_done)',
                   '$heap_valid($heap_graph(' + prefix + '_done))']
    checks += ['S_exit_done.COMPLETION = EXITED 0', 'S_fatal_before.TODO = [ERROR_UNWIND pcompletion_fatal]', 'S_fatal_done.COMPLETION = pcompletion_fatal',
               'S_fatal_before.TRACE = ptraceframe_fatal :: ptraceframe_handler :: ptraceframe_include :: eps',
               'ptraceframe_include.FUNCTION = $ptascii("include")', 'ptraceframe_include.FILE = ' + term(bytes(P / 'fatal.php')),
               'ptraceframe_include.LINE = 8', 'ptraceframe_include.ARGS = eps', '~ptraceframe_include.HASARGS',
               'S_fatal_zero.TRACE = S_fatal_before.TRACE', 'S_fatal_one.TRACE = S_fatal_before.TRACE', 'S_fatal_done.TRACE = S_fatal_before.TRACE']
    assert len(checks) == 148
    prefix = setup + textwrap.dedent(helpers)
    return prefix, checks


def render_shutdown(fixtures, P):
    main = P / 'main.php'
    bad = P / 'compile-bad.php'
    checks = [
        'pstartup = {REPORTING ($ptascii("30719")), INCLUDEPATH $ptascii(".:")}',
        'S_wait = $php_file_startup_run($warning_shutdown_main_program(), 2000, ' + term(bytes(main)) + ', ' + term(bytes(C)) + ', pstartup)',
        'S_wait.COMPLETION = SOURCE_PENDING', '$call_descriptors_valid(S_wait)',
        'S_inner = $file_open_continue(S_wait, FILE_MISSING 0 ' + term(bytes(main)) + ' $ptascii("shutdown-missing.php") $ptascii("No such file or directory"))',
        'S_inner.COMPLETION = SOURCE_PENDING', '$call_descriptors_valid(S_inner)',
        'S_inner.FILECONTEXTS = pfilecontext_inner :: pfilecontext_outer :: eps',
        'pfilecontext_outer.NONCE = 0', 'pfilecontext_outer.OWNER = 0',
        'pfilecontext_outer.PHASE = FILE_WARNING_STREAM $ptascii("shutdown-missing.php") $ptascii("No such file or directory")',
        '$file_warning_owner_valid(S_inner, pfilecontext_outer)',
        'S_parse = $file_open_continue(S_inner, FILE_OPENED 1 ' + term(bytes(main)) + ' ' + term(bytes(bad)) + ' ' + term(bytes(bad)) + ' ' + term(bytes(bad)) + ' ' + term(bad.read_bytes()) + ')',
        'S_parse.COMPLETION = SOURCE_PENDING', '$call_descriptors_valid(S_parse)',
        'S_failed = $file_parse_resume(S_parse, SOURCE_ACCEPT 1 ' + term(bad.read_bytes()) + ' $warning_shutdown_bad_program())',
        'S_failed.COMPILESTOP', '$shutdown_ready(S_failed)',
        'S_failed.FILECONTEXTS = pfilecontext_outer :: eps', '|S_failed.FRAMES| = 1',
        '$file_warning_owner_valid(S_failed, pfilecontext_outer)',
        'S_failed.TRACE = ptraceframe_handler :: ptraceframe_include :: eps',
        'ptraceframe_include.FUNCTION = $ptascii("include")', 'ptraceframe_include.ARGS = eps', '~ptraceframe_include.HASARGS',
        'S_budget = $drive_steps(S_failed, 0)', 'S_budget.COMPLETION = BUDGET',
        'S_budget.SHUTDOWN.PHASE = SHUTDOWN_RUNNING', 'S_budget.FILECONTEXTS = eps',
        'S_budget.FRAMES = eps', 'S_budget.CURRENT = eps', '$call_descriptors_valid(S_budget)', '$heap_valid($heap_graph(S_budget))',
        '~$file_context_valid(S_budget, pfilecontext_outer)',
        'S_budget.EVENTS = (OUTPUT $ptascii("H:14|")) :: (DISPLAY_STDOUT (STDERR ptbytes_frozen)) :: eps',
        'S_done = $drive_steps(S_budget[.COMPLETION = NORMAL], 2000)',
        'S_done.FILECONTEXTS = eps', 'S_done.FRAMES = eps', 'S_done.SHUTDOWN.PHASE = SHUTDOWN_DONE',
        'S_done.EVENTS = S_budget.EVENTS ++ [OUTPUT $ptascii("Q:callback-path|")]', '$display_state_mode(S_done) = 0',
        'S_done.COMPLETION = S_budget.SHUTDOWN.COMPLETION', '$shutdown_frozen(S_done.COMPLETION)',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    fixture = 'dec $warning_shutdown_main_program() : program\ndef $warning_shutdown_main_program() = ' + fixtures['main'] + '\n'
    fixture += 'dec $warning_shutdown_bad_program() : program\ndef $warning_shutdown_bad_program() = ' + fixtures['compile-bad'] + '\n'
    fixture += 'dec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks) + 'def $main() = false -- otherwise\n'
    assert len(checks) == 45
    return fixture, checks


def prepare(out):
    sources = {'owner': SOURCES / 'owner-control.php', 'owner_throw': SOURCES / 'convert/throw.php'}
    sources.update({name: SOURCES / 'warning' / (name + '.php') for name in ('live', 'nested-target', 'throw', 'exit', 'fatal')})
    sources.update({name: SOURCES / 'shutdown' / (name + '.php') for name in ('main', 'compile-bad')})
    profile = json.loads((R / 'tests/semantics/profile.json').read_bytes())
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    frontend = Worker([str(R / '.tools/php/bin/php'), '-n', *flags, '-d', 'extension=' + str(R / '.tools/php-file.so'), str(R / 'frontend/worker.php')], out / 'frontend')
    try:
        parsed = {name: frontend.request({'op': 'parse', 'source': b64(source.read_bytes())}) for name, source in sources.items()}
        assert all(row['accepted'] for row in parsed.values())
    finally:
        frontend.close()
    adapter = Worker([str(R / '_build/default/adapter/main.exe'), str(R)], out / 'syntax-adapter')
    try:
        fixtures = {name: adapter.request({'op': 'check', 'ast': row['ast'], 'fixture': True})['fixture'] for name, row in parsed.items()}
    finally:
        adapter.close()
    owner, owner_checks = render_owner(fixtures, sources['owner'], sources['owner_throw'])
    prefix, warning_checks = render_warning({name: fixtures[name] for name in ('live', 'nested-target', 'throw', 'exit', 'fatal')}, SOURCES / 'warning')
    shutdown, shutdown_checks = render_shutdown(fixtures, SOURCES / 'shutdown')
    rows = [('owner', owner, owner_checks, len(owner_checks)), ('shutdown', shutdown, shutdown_checks, len(shutdown_checks))]
    groups = {'live': list(range(1, 81)), 'throw': list(range(81, 93)),
              'exit': [*range(93, 115), 137], 'fatal': [*range(115, 137), *range(138, 149)]}
    assert sorted(i for ids in groups.values() for i in ids) == list(range(1, 149))
    for name, ids in groups.items():
        checks = [warning_checks[i - 1] for i in ids]
        if name != 'live':
            checks.insert(0, warning_checks[0])
        fixture = prefix + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks) + 'def $main() = false -- otherwise\n'
        rows.append((name, fixture, checks, len(ids)))
    records = []
    for name, fixture, checks, count in rows:
        path = out / (name + '.watsup'); path.write_text(fixture)
        records.append({'id': name, 'fixture': str(path), 'conditions': count, 'main_checks': checks})
    (out / 'prepared.json').write_text(json.dumps({'records': records, 'sources': {name: str(path) for name, path in sources.items()}}, indent=2) + '\n')
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=('owner', 'live', 'throw', 'exit', 'fatal', 'shutdown'))
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out = Path(tempfile.mkdtemp(prefix='file-operand-protocol-', dir=R / '.tools')); print(out, flush=True)
    records = prepare(out)
    if args.prepare_only:
        return True
    modules = [R / name for name in json.loads((R / 'spec/semantics/modules.json').read_bytes())]
    runner = R / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*modules, R / 'spec/semantics/modules.json', runner, Path(__file__),
               R / '.tools/php/bin/php', R / '_build/default/adapter/main.exe',
               R / 'tests/semantics/error_handler_run.py', *sorted(SOURCES.rglob('*.php'))]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path.relative_to(R)): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    rows = []
    for record in records:
        if args.group and record['id'] != args.group:
            continue
        stem = out / record['id']
        result = recorded([str(runner), *map(str, modules), record['fixture']], stem, 90)
        passed = result['exit'] == 0 and not result['timeout'] and stem.with_suffix('.stdout').read_bytes() == b'true\n' and not stem.with_suffix('.stderr').read_bytes()
        rows.append({'id': record['id'], 'conditions': record['conditions'], 'pass': passed, 'process': result})
        print(record['id'], passed, flush=True)
    assert before == {str(path.relative_to(R)): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'inputs': before, 'rows': rows,
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent'},
        'scope': '81 owner,148 warning and45 shutdown conditions; three warning groups repeat startup setup only.'}, indent=2) + '\n')
    return all(row['pass'] for row in rows)


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
