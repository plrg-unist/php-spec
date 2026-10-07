#!/usr/bin/env python3
"""Reached fast-source destructor and zero-argument keyword trace admission.

--prepare-only constructs checked source/file fixtures without model applications.
The ordinary file provider supplies paths and bytes, not execution answers.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HELPERS = {'fast': '\ndec $retirement_trace_review_reached(pstate) : bool\ndef $retirement_trace_review_reached(S) = true\n  -- if S.CURRENT = (pcallcontext)\n  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)\n  -- if pdestructorcall.OPERATION = (pdestructionoperation)\n  -- if pdestructionoperation.SOURCE = SOURCE_OPERAND_FAST psourceoperand n\ndef $retirement_trace_review_reached(S) = false -- otherwise\ndec $retirement_trace_review_seek(pstate, nat) : pstate\ndef $retirement_trace_review_seek(S, n) = S -- if $retirement_trace_review_reached(S)\ndef $retirement_trace_review_seek(S, n) = S\n  -- if ~$retirement_trace_review_reached(S)\n  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\ndef $retirement_trace_review_seek(S, 0) = S -- if ~$retirement_trace_review_reached(S)\ndef $retirement_trace_review_seek(S, n) = $retirement_trace_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))\n  -- if ~$retirement_trace_review_reached(S)\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $(n > 0)\n', 'helper': '\ndec $retirement_helper_review_reached(pstate) : bool\ndef $retirement_helper_review_reached(S) = true\n  -- if S.CURRENT = (pcallcontext)\n  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)\n  -- if pdestructorcall.OPERATION = (pdestructionoperation)\n  -- if pdestructionoperation.SOURCE = SOURCE_HELPER_RELEASE psourceoperand HELPER_EMPTY_EVAL\ndef $retirement_helper_review_reached(S) = false -- otherwise\ndec $retirement_helper_review_seek(pstate, nat) : pstate\ndef $retirement_helper_review_seek(S, n) = S -- if $retirement_helper_review_reached(S)\ndef $retirement_helper_review_seek(S, n) = S\n  -- if ~$retirement_helper_review_reached(S)\n  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\ndef $retirement_helper_review_seek(S, 0) = S -- if ~$retirement_helper_review_reached(S)\ndef $retirement_helper_review_seek(S, n) = $retirement_helper_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))\n  -- if ~$retirement_helper_review_reached(S)\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $(n > 0)\ndec $retirement_helper_review_replace(pstate, pframe, pdestructorcall, pdestructionoperation, pdestructionoperation) : pstate\ndef $retirement_helper_review_replace(S, pframe, pdestructorcall, pdestructionoperation, pdestructionoperation_new) = S[.DESTRUCTION.OPERATIONS = [pdestructionoperation_new]][.DESTRUCTION.CALLS = [pdestructorcall_new]][.FRAMES = [pframe[.TODO = (DESTRUCTOR_RESULT pdestructorcall_new) :: $destructor_operation_tasks(ptask_tail*, pdestructionoperation, pdestructionoperation_new)]]]\n  -- if pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail*\n  -- if pdestructorcall_new = pdestructorcall[.OPERATION = (pdestructionoperation_new)]\n'}
PREMISES = {'fast': ['',
          '  -- if S_open.COMPLETION = SOURCE_PENDING',
          '  -- if S_open.FILECONTEXTS = pfilecontext_open :: eps',
          '  -- if pfilecontext_open.PHASE = FILE_RESOLVE_WAIT',
          '',
          '  -- if S_parse.COMPLETION = SOURCE_PENDING',
          '  -- if S_parse.FILECONTEXTS = pfilecontext_parse :: eps',
          '  -- if pfilecontext_parse.UNIT = (n_unit)',
          '',
          '  -- if S_run.COMPLETION = NORMAL',
          '  -- if S_reached = $retirement_trace_review_seek(S_run, 2500)',
          '  -- if S_reached.COMPLETION = NORMAL \\/ S_reached.COMPLETION = BUDGET',
          '  -- if S = S_reached[.COMPLETION = NORMAL]',
          '  -- if S.CURRENT = (pcallcontext)',
          '  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)',
          '  -- if pdestructorcall.OPERATION = (pdestructionoperation)',
          '  -- if pdestructionoperation.SOURCE = SOURCE_OPERAND_FAST psourceoperand n_unit',
          '  -- if S.FRAMES = pframe :: eps',
          '  -- if pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail*',
          '  -- if S.FILECONTEXTS = pfilecontext :: eps',
          '  -- if pfilecontext.UNIT = (n_unit)',
          '  -- if ptraceframe = $file_trace_frame_before(S, pfilecontext, eps)',
          '  -- if S.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
          '  -- if S.DESTRUCTION.CALLS = [pdestructorcall]',
          '  -- if pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE '
          'pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (SOURCE_FAST_FINISH '
          'psourceoperand n_unit) :: (FILE_END n_unit) :: psourceoperand.TAIL',
          '  -- if S_scope = $constant_frame_scope(S, pframe, eps)',
          '  -- if S_tasks = '
          '$destructor_saved_frame_scope($api_saved_frame_scope($parameter_string_frame_scope(S_scope, '
          'pframe, eps), pframe, eps), pframe)',
          '  -- if S_result = $call_after_origin($call_after_origin(S_tasks, DESTRUCTOR_RESULT '
          'pdestructorcall), DESTRUCTOR_RELEASE pdestructionrelease)',
          '  -- if S_post_exit = $call_after_origin(S_result, DESTRUCTOR_OPERATION_EXIT '
          'pdestructionoperation)',
          '  -- if pdestructionoperation_value = pdestructionoperation[.VALUE = KNOWN (PINT 99)]',
          '  -- if pdestructorcall_value = pdestructorcall[.OPERATION = (pdestructionoperation_value)]',
          '  -- if S_value = S[.DESTRUCTION.OPERATIONS = [pdestructionoperation_value]][.DESTRUCTION.CALLS = '
          '[pdestructorcall_value]][.FRAMES = [pframe[.TODO = (DESTRUCTOR_RESULT pdestructorcall_value) :: '
          '(DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT '
          'pdestructionoperation_value) :: (SOURCE_FAST_FINISH psourceoperand n_unit) :: (FILE_END n_unit) '
          ':: psourceoperand.TAIL]]]',
          '  -- if pdestructorcall.RELEASE = (pdestructionrelease_before)',
          '  -- if pdestructionrelease_origin = pdestructionrelease[.ORIGIN = '
          '($source_operand_child(psourceoperand))]',
          '  -- if pdestructionrelease_call_origin = pdestructionrelease_before[.ORIGIN = '
          '($source_operand_child(psourceoperand))]',
          '  -- if pdestructionoperation_origin = pdestructionoperation[.ORIGIN = '
          '($source_operand_child(psourceoperand))]',
          '  -- if pdestructorcall_origin = pdestructorcall[.ORIGIN = '
          '($source_operand_child(psourceoperand))][.OPERATION = (pdestructionoperation_origin)][.RELEASE = '
          '(pdestructionrelease_call_origin)]',
          '  -- if S_origin = S[.DESTRUCTION.RELEASES = '
          '[pdestructionrelease_origin]][.DESTRUCTION.OPERATIONS = '
          '[pdestructionoperation_origin]][.DESTRUCTION.CALLS = [pdestructorcall_origin]][.FRAMES = '
          '[pframe[.ORIGIN = ($source_operand_child(psourceoperand))][.TODO = (DESTRUCTOR_RESULT '
          'pdestructorcall_origin) :: (DESTRUCTOR_RELEASE pdestructionrelease_origin) :: '
          '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_origin) :: (SOURCE_FAST_FINISH psourceoperand '
          'n_unit) :: (FILE_END n_unit) :: psourceoperand.TAIL]]]',
          '  -- if S_history = S[.DESTRUCTION.OPERATIONS = eps]',
          '  -- if S_suffix = S[.FRAMES = [pframe[.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: '
          '(DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: '
          '(FILE_END n_unit) :: psourceoperand.TAIL]]]',
          '  -- if S_owner = S[.FILECONTEXTS = [pfilecontext[.OWNER = $(pfilecontext.OWNER + 1)]]]',
          '  -- if S_matched = S_value[.RESULT = KNOWN (PINT 1)]',
          '  -- if $retirement_trace_review_reached(S)',
          '  -- if $call_descriptors_valid(S)',
          '  -- if $call_entry_check(S) = S',
          '  -- if $heap_valid($heap_graph(S))',
          '  -- if $destructor_call_live(S, pdestructorcall)',
          '  -- if $source_operand_fast_trace(S, pfilecontext)',
          '  -- if pdestructionoperation.VALUE = KNOWN (PINT 1)',
          '  -- if psourceoperand.OWNER = 0',
          '  -- if psourceoperand.LINE = 21',
          '  -- if $destructor_line(pdestructorcall) = 21',
          '  -- if ptraceframe.FUNCTION = $ptascii("include")',
          '  -- if ptraceframe.FILE = $call_sourcefile(S.FILES, psourceoperand.SITE)',
          '  -- if ptraceframe.LINE = 21',
          '  -- if ptraceframe.ARGS = eps /\\ ~ptraceframe.HASARGS',
          '  -- if $task_nodes(SOURCE_FAST_FINISH psourceoperand n_unit) = eps',
          '  -- if (HOBJECT pdestructorcall.OBJECT) <- S.ALLOCATIONS',
          '  -- if ~$source_operand_fast_trace(S, pfilecontext[.UNIT = eps])',
          '  -- if ~$source_operand_fast_trace(S, pfilecontext[.OWNER = $(pfilecontext.OWNER + 1)])',
          '  -- if ~$source_operand_fast_trace(S[.FILECONTEXTS = [pfilecontext[.PHASE = '
          'FILE_RESOLVE_WAIT]]], pfilecontext[.PHASE = FILE_RESOLVE_WAIT])',
          '  -- if ~$source_operand_fast_trace(S[.FRAMES = [pframe[.TODO = (DESTRUCTOR_RESULT '
          'pdestructorcall) :: eps]]], pfilecontext)',
          '  -- if ~$source_operand_fast_trace(S[.FILECONTEXTS = eps], pfilecontext)',
          '  -- if S.RESULT = KNOWN PNULL',
          '  -- if S_tasks.RESULT = KNOWN PNULL',
          '  -- if $eager_operation_validation_value(S_result, pdestructionoperation) = '
          'pdestructionoperation.VALUE',
          '  -- if S_post_exit.RESULT = pdestructionoperation.VALUE',
          '  -- if S_post_exit.DESTRUCTION.OPERATIONS = eps',
          '  -- if $call_task_valid(S_post_exit, SOURCE_FAST_FINISH psourceoperand n_unit)',
          '  -- if $machine_roots(S) = $machine_roots(S[.RESULT = '
          '$eager_operation_validation_value(S_result, pdestructionoperation)])',
          '  -- if $heap_valid($heap_graph(S_value))',
          '  -- if ~$call_descriptors_valid(S_value)',
          '  -- if $call_entry_check(S_value).COMPLETION = UNSUPPORTED "invalid compiled function '
          'descriptor"',
          '  -- if $heap_valid($heap_graph(S_origin))',
          '  -- if ~$call_descriptors_valid(S_origin)',
          '  -- if $call_entry_check(S_origin).COMPLETION = UNSUPPORTED "invalid compiled function '
          'descriptor"',
          '  -- if $heap_valid($heap_graph(S_history))',
          '  -- if ~$call_descriptors_valid(S_history)',
          '  -- if $call_entry_check(S_history).COMPLETION = UNSUPPORTED "invalid compiled function '
          'descriptor"',
          '  -- if $heap_valid($heap_graph(S_suffix))',
          '  -- if ~$call_descriptors_valid(S_suffix)',
          '  -- if $call_entry_check(S_suffix).COMPLETION = UNSUPPORTED "invalid compiled function '
          'descriptor"',
          '  -- if $heap_valid($heap_graph(S_owner))',
          '  -- if ~$call_descriptors_valid(S_owner)',
          '  -- if $call_entry_check(S_owner).COMPLETION = UNSUPPORTED "invalid compiled function '
          'descriptor"',
          '  -- if ~$source_operand_fast_trace(S_value, pfilecontext)',
          '  -- if ~$source_operand_fast_trace(S_origin, pfilecontext)',
          '  -- if ~$source_operand_fast_trace(S_history, pfilecontext)',
          '  -- if ~$source_operand_fast_trace(S_suffix, pfilecontext)',
          '  -- if ~$source_operand_fast_trace(S_owner, pfilecontext[.OWNER = $(pfilecontext.OWNER + 1)])',
          '  -- if $eager_operation_validation_value(S_result[.DESTRUCTION.OPERATIONS = '
          '[pdestructionoperation_value]], pdestructionoperation_value) = S_result.RESULT',
          '  -- if $eager_operation_validation_value(S_result[.DESTRUCTION.OPERATIONS = '
          '[pdestructionoperation_origin]][.ORIGIN = ($source_operand_child(psourceoperand))], '
          'pdestructionoperation_origin) = S_result.RESULT',
          '  -- if $eager_operation_validation_value(S_result[.DESTRUCTION.OPERATIONS = eps], '
          'pdestructionoperation) = S_result.RESULT',
          '  -- if $eager_operation_validation_value(S_result[.TODO = [DESTRUCTOR_OPERATION_EXIT '
          'pdestructionoperation]], pdestructionoperation) = S_result.RESULT',
          '  -- if $eager_operation_validation_value(S_result[.FILECONTEXTS = [pfilecontext[.OWNER = '
          '$(pfilecontext.OWNER + 1)]]], pdestructionoperation) = S_result.RESULT',
          '  -- if $heap_valid($heap_graph(S_matched))',
          '  -- if ~$call_descriptors_valid(S_matched)',
          '  -- if $call_entry_check(S_matched).COMPLETION = UNSUPPORTED "invalid compiled function '
          'descriptor"'],
 'helper': ['',
            '  -- if S_seed.COMPLETION = NORMAL \\/ S_seed.COMPLETION = BUDGET',
            '  -- if S_reached = $retirement_helper_review_seek(S_seed, 2500)',
            '  -- if S_reached.COMPLETION = NORMAL \\/ S_reached.COMPLETION = BUDGET',
            '  -- if S = S_reached[.COMPLETION = NORMAL]',
            '  -- if S.CURRENT = (pcallcontext)',
            '  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)',
            '  -- if pdestructorcall.OPERATION = (pdestructionoperation)',
            '  -- if pdestructionoperation.SOURCE = SOURCE_HELPER_RELEASE psourceoperand HELPER_EMPTY_EVAL',
            '  -- if S.FRAMES = pframe :: eps',
            '  -- if pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail*',
            '  -- if psourceoperand.TAIL = ptask_operand_tail*',
            '  -- if ptask_tail* = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT '
            'pdestructionoperation) :: (SOURCE_HELPER_FINISH psourceoperand HELPER_EMPTY_EVAL) :: '
            'ptask_operand_tail*',
            '  -- if S_owner = $constant_frame_scope(S, pframe, eps)',
            '  -- if S_fold = $call_after_origin(S_owner, DESTRUCTOR_OPERATION_EXIT pdestructionoperation)',
            '  -- if psourceoperand.INPUT = KNOWN (POBJECT n_input)',
            '  -- if S_bad_value = $retirement_helper_review_replace(S, pframe, pdestructorcall, '
            'pdestructionoperation, pdestructionoperation[.VALUE = KNOWN (PBOOL true)])',
            '  -- if S_bad_value_match = S_bad_value[.RESULT = KNOWN (PBOOL false)]',
            '  -- if pdestructionoperation_origin = pdestructionoperation[.ORIGIN = '
            '($source_operand_child(psourceoperand))]',
            '  -- if pdestructorcall_origin = pdestructorcall[.ORIGIN = '
            '($source_operand_child(psourceoperand))][.OPERATION = (pdestructionoperation_origin)]',
            '  -- if S_bad_origin = S[.DESTRUCTION.OPERATIONS = '
            '[pdestructionoperation_origin]][.DESTRUCTION.CALLS = [pdestructorcall_origin]][.FRAMES = '
            '[pframe[.ORIGIN = ($source_operand_child(psourceoperand))][.TODO = (DESTRUCTOR_RESULT '
            'pdestructorcall_origin) :: (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_origin) :: (SOURCE_HELPER_FINISH '
            'psourceoperand HELPER_EMPTY_EVAL) :: ptask_operand_tail*]]]',
            '  -- if S_bad_history = S[.DESTRUCTION.OPERATIONS = eps]',
            '  -- if S_bad_suffix = S[.FRAMES = [pframe[.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: '
            'eps]]]',
            '  -- if pdestructionoperation_bad = pdestructionoperation[.SOURCE = SOURCE_HELPER_RELEASE '
            'psourceoperand[.OWNER = 1] HELPER_EMPTY_EVAL]',
            '  -- if S_bad_owner = $retirement_helper_review_replace(S, pframe, pdestructorcall, '
            'pdestructionoperation, pdestructionoperation_bad)[.FRAMES = [pframe[.TODO = (DESTRUCTOR_RESULT '
            'pdestructorcall[.OPERATION = (pdestructionoperation_bad)]) :: (DESTRUCTOR_RELEASE '
            'pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_bad) :: '
            '(SOURCE_HELPER_FINISH psourceoperand[.OWNER = 1] HELPER_EMPTY_EVAL) :: ptask_operand_tail*]]]',
            '  -- if ptraceframe_helper* = $eval_trace_preparser(S, (pcallcontext), pframe)',
            '  -- if ptraceframe_helper* = [ptraceframe]',
            '  -- if $retirement_helper_review_reached(S)',
            '  -- if $call_descriptors_valid(S)',
            '  -- if $call_entry_check(S) = S',
            '  -- if $heap_valid($heap_graph(S))',
            '  -- if $destructor_call_live(S, pdestructorcall)',
            '  -- if $destructor_operation_valid(S_owner, pdestructionoperation)',
            '  -- if $source_release_operation_valid(S, pdestructionoperation)',
            '  -- if $eager_operation_source_guard(S, pdestructionoperation)',
            '  -- if $source_helper_context(S_owner, psourceoperand, HELPER_EMPTY_EVAL)',
            '  -- if pdestructionoperation.VALUE = KNOWN (PBOOL false)',
            '  -- if psourceoperand.KIND = 0',
            '  -- if psourceoperand.OWNER = 0',
            '  -- if psourceoperand.LINE = 17',
            '  -- if n_input = pdestructorcall.OBJECT',
            '  -- if S.FILECONTEXTS = eps',
            '  -- if S.EVALCONTEXTS = eps',
            '  -- if S.RESULT = KNOWN PNULL',
            '  -- if S_owner.RESULT = KNOWN PNULL',
            '  -- if $eager_operation_validation_value(S_owner, pdestructionoperation) = KNOWN (PBOOL false)',
            '  -- if S_fold.RESULT = KNOWN (PBOOL false)',
            '  -- if S_fold.TODO = S_owner.TODO',
            '  -- if $machine_roots(S_fold) = $machine_roots(S_owner)',
            '  -- if S_fold.DESTRUCTION.OPERATIONS = eps',
            '  -- if $task_nodes(SOURCE_HELPER_FINISH psourceoperand HELPER_EMPTY_EVAL) = eps',
            '  -- if (HOBJECT n_input) <- S.ALLOCATIONS',
            '  -- if ptraceframe.FUNCTION = $ptascii("eval")',
            '  -- if ptraceframe.FILE = $call_sourcefile(S.FILES, psourceoperand.SITE)',
            '  -- if ptraceframe.LINE = 17',
            '  -- if ptraceframe.ARGS = eps /\\ ~ptraceframe.HASARGS',
            '  -- if $heap_valid($heap_graph(S_bad_value))',
            '  -- if ~$call_descriptors_valid(S_bad_value)',
            '  -- if $call_entry_check(S_bad_value).COMPLETION = UNSUPPORTED "invalid compiled function '
            'descriptor"',
            '  -- if $heap_valid($heap_graph(S_bad_value_match))',
            '  -- if ~$call_descriptors_valid(S_bad_value_match)',
            '  -- if $call_entry_check(S_bad_value_match).COMPLETION = UNSUPPORTED "invalid compiled '
            'function descriptor"',
            '  -- if $heap_valid($heap_graph(S_bad_origin))',
            '  -- if ~$call_descriptors_valid(S_bad_origin)',
            '  -- if $call_entry_check(S_bad_origin).COMPLETION = UNSUPPORTED "invalid compiled function '
            'descriptor"',
            '  -- if $heap_valid($heap_graph(S_bad_history))',
            '  -- if ~$call_descriptors_valid(S_bad_history)',
            '  -- if $call_entry_check(S_bad_history).COMPLETION = UNSUPPORTED "invalid compiled function '
            'descriptor"',
            '  -- if $heap_valid($heap_graph(S_bad_owner))',
            '  -- if ~$call_descriptors_valid(S_bad_owner)',
            '  -- if $call_entry_check(S_bad_owner).COMPLETION = UNSUPPORTED "invalid compiled function '
            'descriptor"',
            '  -- if $eager_operation_validation_value($constant_frame_scope(S_bad_value, '
            'S_bad_value.FRAMES[0], eps), pdestructionoperation[.VALUE = KNOWN (PBOOL true)]) = KNOWN PNULL',
            '  -- if $eager_operation_validation_value(S_owner[.ORIGIN = '
            '($source_operand_child(psourceoperand))][.DESTRUCTION.OPERATIONS = '
            '[pdestructionoperation_origin]], pdestructionoperation_origin) = KNOWN PNULL',
            '  -- if $eager_operation_validation_value($constant_frame_scope(S_bad_history, pframe, eps), '
            'pdestructionoperation) = KNOWN PNULL',
            '  -- if $heap_valid($heap_graph(S_bad_suffix))',
            '  -- if ~$call_descriptors_valid(S_bad_suffix)',
            '  -- if $call_entry_check(S_bad_suffix).COMPLETION = UNSUPPORTED "invalid compiled function '
            'descriptor"',
            '  -- if $eager_operation_validation_value($constant_frame_scope(S_bad_suffix, '
            'S_bad_suffix.FRAMES[0], eps), pdestructionoperation) = KNOWN PNULL']}


HELPERS['entry'] = ''
PREMISES['entry'] = ['  -- if S_open = $php_file_startup_run($first_work_review_program(), 10000, eps, eps, {REPORTING '
 '($ptascii("30719")), INCLUDEPATH $ptascii(".:")})',
 '  -- if S_open.COMPLETION = SOURCE_PENDING',
 '  -- if S_open.FILECONTEXTS = pfilecontext_open :: eps',
 '  -- if pfilecontext_open.PHASE = FILE_RESOLVE_WAIT',
 '  -- if S_parse = $file_open_resume(S_open, (FILE_OPENED pfilecontext_open.NONCE eps eps eps eps eps))',
 '  -- if S_parse.COMPLETION = SOURCE_PENDING',
 '  -- if S_parse.FILECONTEXTS = pfilecontext_parse :: eps',
 '  -- if pfilecontext_parse.UNIT = (n_unit)',
 '  -- if S = $file_parse_resume(S_parse, (SOURCE_ACCEPT n_unit eps $first_work_review_child()))',
 '  -- if S.COMPLETION = NORMAL',
 '  -- if S.TODO = (SOURCE_OPERAND_ENTER psourceoperand n_unit) :: ptask_body*',
 '  -- if $source_unit(S.SOURCES, n_unit) = (pcunit)',
 '  -- if P = $declaration_compiler_state($eval_source_ppstate(S, pcunit))',
 '  -- if P.WORK = (PPCWORK pcpath_fn statement_fn plenv_fn n_fn) :: (PPCWORK pcpath_echo statement_echo '
 'plenv_echo n_echo) :: ppwork_tail*',
 '  -- if statement_echo = (NStmtEcho (SEQUENCE ([expression_echo])) metadata_echo)',
 '  -- if porigin_echo = PORIGIN n_unit (pcpath_echo ++ [PCFIELD 0, PCINDEX 0])',
 '  -- if S_no_code = S[.CODE = eps]',
 '  -- if S_no_exit = S[.DECLARATIONS = eps]',
 '  -- if S_bad_tail = S[.TODO = [SOURCE_OPERAND_ENTER psourceoperand n_unit]]',
 '  -- if S_bad_owner = S[.FILECONTEXTS = [S.FILECONTEXTS[0][.OWNER = 1]]]',
 '  -- if $source_operand_enter_valid(S, psourceoperand, n_unit)',
 '  -- if $call_descriptors_valid(S)',
 '  -- if $call_entry_check(S) = S',
 '  -- if $heap_valid($heap_graph(S))',
 '  -- if P.COMPLETION = PPCNORMAL /\\ $compilation_image_valid(S, pcunit, P)',
 '  -- if (PDEXIT n_unit PCSCOMPLETE) <- S.DECLARATIONS',
 '  -- if $source_fast_statement(S, n_unit, pcpath_fn, statement_fn)',
 '  -- if ~$source_fast_statement(S, n_unit, pcpath_echo, statement_echo)',
 '  -- if $source_first_work_origin(S, n_unit, P.WORK) = (porigin_echo)',
 '  -- if $source_operand_entry_origin(S, psourceoperand, n_unit) = (porigin_echo)',
 '  -- if $property_current_line(S[.ORIGIN = (porigin_echo)]) = 5',
 '  -- if $source_first_work_origin(S, n_unit, [PPCWORK pcpath_echo (NStmtEcho (SEQUENCE eps) metadata_echo) '
 'plenv_echo n_echo]) = eps',
 '  -- if $source_first_work_origin(S, n_unit, [PPCWORK pcpath_echo (NStmtExpression expression_echo '
 'metadata_echo) plenv_echo n_echo]) = eps',
 '  -- if $source_first_work_origin(S_no_code, n_unit, P.WORK) = eps',
 '  -- if $source_operand_entry_origin(S_no_code, psourceoperand, n_unit) = S_no_code.ORIGIN',
 '  -- if $source_operand_entry_origin(S_no_exit, psourceoperand, n_unit) = S_no_exit.ORIGIN',
 '  -- if $heap_valid($heap_graph(S_bad_tail))',
 '  -- if ~$source_operand_enter_valid(S_bad_tail, psourceoperand, n_unit)',
 '  -- if ~$call_descriptors_valid(S_bad_tail)',
 '  -- if $call_entry_check(S_bad_tail).COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
 '  -- if $source_operand_entry_origin(S_bad_tail, psourceoperand, n_unit) = S_bad_tail.ORIGIN',
 '  -- if $heap_valid($heap_graph(S_bad_owner))',
 '  -- if ~$source_operand_enter_valid(S_bad_owner, psourceoperand, n_unit)',
 '  -- if ~$call_descriptors_valid(S_bad_owner)',
 '  -- if $call_entry_check(S_bad_owner).COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
 '  -- if $source_operand_entry_origin(S_bad_owner, psourceoperand, n_unit) = S_bad_owner.ORIGIN']

HELPERS['composition'] = '\ndec $combined_review_reached(pstate) : bool\ndef $combined_review_reached(S) = true\n  -- if S.CURRENT = (pcallcontext)\n  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)\n  -- if pdestructorcall.OPERATION = (pdestructionoperation)\n  -- if pdestructionoperation.SOURCE = SOURCE_OPERAND_ENTER psourceoperand n\ndef $combined_review_reached(S) = false -- otherwise\ndec $combined_review_seek(pstate, nat) : pstate\ndef $combined_review_seek(S, n) = S -- if $combined_review_reached(S)\ndef $combined_review_seek(S, n) = S\n  -- if ~$combined_review_reached(S)\n  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\ndef $combined_review_seek(S, 0) = S -- if ~$combined_review_reached(S)\ndef $combined_review_seek(S, n) = $combined_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))\n  -- if ~$combined_review_reached(S)\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $(n > 0)\n\n'
PREMISES['composition'] = ['  -- if S_open = $php_file_startup_run($combined_review_program(), 10000, '
 '$base64("L2hvbWUvdXNlci93b3Jrc3BhY2UvcGhwLXNwZWMvLnRvb2xzL2luY2x1ZGUtZGV2LTE0LWFycmF5LWluZ3Jlc3MvLnRvb2xzL2luY2x1ZGUtY29tYmluZWQtMTYvZ2VuZXJhdG9yLXNvdXJjZS5waHA="), '
 '$base64("L2hvbWUvdXNlci93b3Jrc3BhY2UvcGhwLXNwZWMvLnRvb2xzL2luY2x1ZGUtZGV2LTE0LWFycmF5LWluZ3Jlc3M="), '
 '{REPORTING ($ptascii("30719")), INCLUDEPATH $ptascii(".:")})',
 '  -- if S_open.COMPLETION = SOURCE_PENDING',
 '  -- if S_open.FILECONTEXTS = pfilecontext_open :: eps',
 '  -- if pfilecontext_open.PHASE = FILE_RESOLVE_WAIT',
 '  -- if S_parse = $file_open_resume(S_open, (FILE_OPENED pfilecontext_open.NONCE ([47, 104, 111, '
 '109, 101, 47, 117, 115, 101, 114, 47, 119, 111, 114, 107, 115, 112, 97, 99, 101, 47, 112, 104, 112, '
 '45, 115, 112, 101, 99, 47, 46, 116, 111, 111, 108, 115, 47, 105, 110, 99, 108, 117, 100, 101, 45, '
 '100, 101, 118, 45, 49, 52, 45, 97, 114, 114, 97, 121, 45, 105, 110, 103, 114, 101, 115, 115, 47, 46, '
 '116, 111, 111, 108, 115, 47, 105, 110, 99, 108, 117, 100, 101, 45, 99, 111, 109, 98, 105, 110, 101, '
 '100, 45, 49, 54, 47, 103, 101, 110, 101, 114, 97, 116, 111, 114, 45, 115, 111, 117, 114, 99, 101, '
 '46, 112, 104, 112]) ([47, 104, 111, 109, 101, 47, 117, 115, 101, 114, 47, 119, 111, 114, 107, 115, '
 '112, 97, 99, 101, 47, 112, 104, 112, 45, 115, 112, 101, 99, 47, 46, 116, 111, 111, 108, 115, 47, '
 '105, 110, 99, 108, 117, 100, 101, 45, 100, 101, 118, 45, 49, 52, 45, 97, 114, 114, 97, 121, 45, 105, '
 '110, 103, 114, 101, 115, 115, 47, 46, 116, 111, 111, 108, 115, 47, 105, 110, 99, 108, 117, 100, 101, '
 '45, 99, 111, 109, 98, 105, 110, 101, 100, 45, 49, 54, 47, 103, 101, 110, 101, 114, 97, 116, 111, '
 '114, 45, 115, 111, 117, 114, 99, 101, 45, 99, 104, 105, 108, 100, 46, 112, 104, 112]) ([47, 104, '
 '111, 109, 101, 47, 117, 115, 101, 114, 47, 119, 111, 114, 107, 115, 112, 97, 99, 101, 47, 112, 104, '
 '112, 45, 115, 112, 101, 99, 47, 46, 116, 111, 111, 108, 115, 47, 105, 110, 99, 108, 117, 100, 101, '
 '45, 100, 101, 118, 45, 49, 52, 45, 97, 114, 114, 97, 121, 45, 105, 110, 103, 114, 101, 115, 115, 47, '
 '46, 116, 111, 111, 108, 115, 47, 105, 110, 99, 108, 117, 100, 101, 45, 99, 111, 109, 98, 105, 110, '
 '101, 100, 45, 49, 54, 47, 103, 101, 110, 101, 114, 97, 116, 111, 114, 45, 115, 111, 117, 114, 99, '
 '101, 45, 99, 104, 105, 108, 100, 46, 112, 104, 112]) ([47, 104, 111, 109, 101, 47, 117, 115, 101, '
 '114, 47, 119, 111, 114, 107, 115, 112, 97, 99, 101, 47, 112, 104, 112, 45, 115, 112, 101, 99, 47, '
 '46, 116, 111, 111, 108, 115, 47, 105, 110, 99, 108, 117, 100, 101, 45, 100, 101, 118, 45, 49, 52, '
 '45, 97, 114, 114, 97, 121, 45, 105, 110, 103, 114, 101, 115, 115, 47, 46, 116, 111, 111, 108, 115, '
 '47, 105, 110, 99, 108, 117, 100, 101, 45, 99, 111, 109, 98, 105, 110, 101, 100, 45, 49, 54, 47, 103, '
 '101, 110, 101, 114, 97, 116, 111, 114, 45, 115, 111, 117, 114, 99, 101, 45, 99, 104, 105, 108, 100, '
 '46, 112, 104, 112]) ([60, 63, 112, 104, 112, 10, 102, 117, 110, 99, 116, 105, 111, 110, 32, 99, 111, '
 '109, 98, 105, 110, 101, 100, 95, 99, 104, 105, 108, 100, 95, 114, 101, 97, 100, 121, 95, 49, 54, 40, '
 '41, 32, 123, 125, 10, 10, 101, 99, 104, 111, 10, 32, 32, 32, 32, 39, 112, 114, 111, 118, 105, 100, '
 '101, 114, 45, 98, 111, 100, 121, 39, 59, 10, 114, 101, 116, 117, 114, 110, 32, 53, 50, 59, 10])))',
 '  -- if S_parse.COMPLETION = SOURCE_PENDING',
 '  -- if S_parse.FILECONTEXTS = pfilecontext_parse :: eps',
 '  -- if pfilecontext_parse.UNIT = (n_unit)',
 '  -- if S_entry = $file_parse_resume(S_parse, (SOURCE_ACCEPT n_unit ([60, 63, 112, 104, 112, 10, '
 '102, 117, 110, 99, 116, 105, 111, 110, 32, 99, 111, 109, 98, 105, 110, 101, 100, 95, 99, 104, 105, '
 '108, 100, 95, 114, 101, 97, 100, 121, 95, 49, 54, 40, 41, 32, 123, 125, 10, 10, 101, 99, 104, 111, '
 '10, 32, 32, 32, 32, 39, 112, 114, 111, 118, 105, 100, 101, 114, 45, 98, 111, 100, 121, 39, 59, 10, '
 '114, 101, 116, 117, 114, 110, 32, 53, 50, 59, 10]) $combined_review_child()))',
 '  -- if S_entry.COMPLETION = NORMAL',
 '  -- if S_entry.TODO = (SOURCE_OPERAND_ENTER psourceoperand n_unit) :: ptask_body*',
 '  -- if S_entry.CURRENT = (pcallcontext_entry)',
 '  -- if $generator_context_operation(S_entry, pcallcontext_entry) = (pgeneratorop_entry)',
 '  -- if $operand_nodes(psourceoperand.INPUT) = [HOBJECT n_operand]',
 '  -- if $source_operand_entry_origin(S_entry, psourceoperand, n_unit) = (porigin_work)',
 '  -- if S_reached = $combined_review_seek(S_entry, 400)',
 '  -- if S_reached.COMPLETION = NORMAL \\/ S_reached.COMPLETION = BUDGET',
 '  -- if S = S_reached[.COMPLETION = NORMAL]',
 '  -- if S.CURRENT = (pcallcontext)',
 '  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)',
 '  -- if pdestructorcall.OPERATION = (pdestructionoperation)',
 '  -- if pdestructionoperation.SOURCE = SOURCE_OPERAND_ENTER psourceoperand n_unit',
 '  -- if S_owner = $source_string_owner_scope(S, psourceoperand.OWNER)',
 '  -- if S_bad_owner = S_entry[.FILECONTEXTS = [S_entry.FILECONTEXTS[0][.OWNER = '
 '$(psourceoperand.OWNER + 1)]]]',
 '  -- if S_bad_tail = S_entry[.TODO = [SOURCE_OPERAND_ENTER psourceoperand n_unit]]',
 '  -- if $call_descriptors_valid(S_entry)',
 '  -- if $call_entry_check(S_entry) = S_entry',
 '  -- if $heap_valid($heap_graph(S_entry))',
 '  -- if $generator_from_state_valid(S_entry)',
 '  -- if $(psourceoperand.OWNER > 0)',
 '  -- if $global_quiet_name(S_entry, $ptascii("combined_operand_16")).RESULT = KNOWN PNULL',
 '  -- if (HOBJECT n_operand) <- S_entry.ALLOCATIONS',
 '  -- if $source_operand_enter_valid(S_entry, psourceoperand, n_unit)',
 '  -- if $property_current_line(S_entry[.ORIGIN = (porigin_work)]) = 5',
 '  -- if $call_descriptors_valid(S)',
 '  -- if $call_entry_check(S) = S',
 '  -- if $heap_valid($heap_graph(S))',
 '  -- if $destructor_call_live(S, pdestructorcall)',
 '  -- if pdestructionoperation.ORIGIN = (porigin_work)',
 '  -- if pdestructionoperation.CALLER = S_entry.CURRENT /\\ S_owner.CURRENT = S_entry.CURRENT',
 '  -- if $generator_context_operation(S_owner, pcallcontext_entry) = (pgeneratorop_entry)',
 '  -- if $heap_valid($heap_graph(S_bad_owner))',
 '  -- if ~$source_operand_enter_valid(S_bad_owner, psourceoperand, n_unit)',
 '  -- if ~$call_descriptors_valid(S_bad_owner)',
 '  -- if $call_entry_check(S_bad_owner).COMPLETION = UNSUPPORTED "invalid compiled function '
 'descriptor"',
 '  -- if $heap_valid($heap_graph(S_bad_tail))',
 '  -- if ~$source_operand_enter_valid(S_bad_tail, psourceoperand, n_unit)',
 '  -- if ~$call_descriptors_valid(S_bad_tail)',
 '  -- if $call_entry_check(S_bad_tail).COMPLETION = UNSUPPORTED "invalid compiled function '
 'descriptor"']

def run_case(case, args):
    semantic = args.semantic_root.resolve()
    sys.path.insert(0, str(ROOT / 'tests/semantics'))
    import error_handler_run as recorder
    from recorded_worker import Worker
    recorder.ROOT = ROOT
    directory = ROOT / 'tests/semantics/source-stringable-retirement'
    source = directory / {'fast': 'fast.php', 'helper': 'empty-eval.php', 'entry': 'first-echo.php', 'composition': 'generator-source.php'}[case]
    child = directory / {'fast': 'deferred-compile-only.php', 'entry': 'first-echo-child.php', 'composition': 'generator-source-child.php'}[case] if case != 'helper' else None
    profile_file = ROOT / 'tests/semantics/profile.json'
    profile = dict(json.loads(profile_file.read_bytes()), include_path='.:', error_reporting='30719')
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    php = ROOT / '.tools/php/bin/php'
    bridge = ROOT / '.tools/php-file.so'
    adapter = ROOT / '_build/default/adapter/main.exe'
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    worker = ROOT / 'frontend/worker.php'
    b64 = lambda value: base64.b64encode(value).decode()
    seq = lambda value: '(' + str(list(value)) + ')'
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    watched = [source, Path(__file__), profile_file, php, bridge, adapter, worker,
               ROOT / 'frontend/target.php', ROOT / 'spec/schema.json',
               ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/error_handler_run.py']
    if child is not None:
        watched.append(child)
    modules = []
    if not args.prepare_only:
        manifest = semantic / 'spec/semantics/modules.json'
        modules = [semantic / name for name in json.loads(manifest.read_bytes())]
        assert any(path.name == '298-source-stringable-lifetime.watsup' for path in modules)
        watched += [manifest, *modules, runner]
    snapshot = lambda: {str(path): sha(path) for path in watched}
    before = snapshot()
    def git(*parts):
        result = subprocess.run(['git', *parts], cwd=ROOT, env=recorder.ENV,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode().strip() if result.returncode == 0 else None
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    out = Path(tempfile.mkdtemp(prefix='source-stringable-retirement-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    report = {'revision': revision, 'working_tree_status': status, 'inputs': before,
              'profile': profile, 'source': str(source), 'child': str(child) if child is not None else None, 'semantic_root': str(semantic),
              'mode': 'SL', 'cache': False, 'det': True,
              'compiler_pin': 'da36ac3c434cd291940293a63da64544307730a3',
              'selected': ('active Generator source entry and first regular operand destructor' if case == 'composition' else
                           'compile-complete source operand entry' if case == 'entry' else
                           'first actual fast/helper operand destructor, before trace-loop effects'),
              'case': case, 'binding_premises': {'fast': 42, 'helper': 27, 'entry': 20, 'composition': 25}[case],
              'selected_admission_premises': {'fast': 98, 'helper': 78, 'entry': 46, 'composition': 49}[case],
              'check_premises': {'fast': 56, 'helper': 51, 'entry': 26, 'composition': 24}[case],
              'source_agreements': 0, 'application_evaluations': 0, 'passed': False,
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent', 'jobs': 1}}
    try:
        frontend = Worker([str(php), '-n', *flags, '-d', 'extension=' + str(bridge), str(worker)], out / 'frontend')
        try:
            parsed = [frontend.request({'op': 'parse', 'source': b64(source.read_bytes())})]
            if child is not None:
                parsed.append(frontend.request({'op': 'parse-file', 'id': '0', 'mode': 'file',
                    'profile': 'cli-raw-85', 'requested': b64(bytes(child)), 'resolved': b64(bytes(child)),
                    'opened': b64(bytes(child)), 'source': b64(child.read_bytes())}))
            assert all(row['accepted'] for row in parsed)
        finally:
            frontend.close()
        checked_worker = Worker([str(adapter), str(ROOT)], out / 'adapter')
        try:
            checked = [checked_worker.request({'op': 'check', 'ast': row['ast'], 'fixture': True}) for row in parsed]
            assert all(row['ok'] for row in checked)
        finally:
            checked_worker.close()
        (out / 'checked.json').write_text(json.dumps(checked) + '\n')
        prefix = {'fast': 'retirement_trace_review', 'helper': 'retirement_helper_review',
                  'entry': 'first_work_review', 'composition': 'combined_review'}[case]
        start = ('$php_file_startup_run($' + prefix + '_program(), '
                 + ('1' if case == 'helper' else '10000') + ', $base64('
                 + json.dumps(b64(bytes(source))) + '), $base64(' + json.dumps(b64(bytes(ROOT)))
                 + '), {REPORTING ($ptascii("30719")), INCLUDEPATH $ptascii(".:")})')
        premises = list(PREMISES[case])
        premises[0] = '  -- if ' + ('S_seed' if case == 'helper' else 'S_open') + ' = ' + start
        fixture = ('dec $' + prefix + '_program() : program\ndef $' + prefix + '_program() = '
                   + checked[0]['fixture'] + '\n')
        if child is not None:
            opened = ('(FILE_OPENED pfilecontext_open.NONCE ' + seq(bytes(source)) + ' '
                      + seq(bytes(child)) + ' ' + seq(bytes(child)) + ' ' + seq(bytes(child))
                      + ' ' + seq(child.read_bytes()) + ')')
            accepted = '(SOURCE_ACCEPT n_unit ' + seq(child.read_bytes()) + ' $' + prefix + '_child())'
            premises[4] = '  -- if S_parse = $file_open_resume(S_open, ' + opened + ')'
            premises[8] = '  -- if ' + ('S' if case == 'entry' else 'S_entry' if case == 'composition' else 'S_run') + ' = $file_parse_resume(S_parse, ' + accepted + ')'
            fixture += ('dec $' + prefix + '_child() : program\ndef $' + prefix + '_child() = '
                        + checked[1]['fixture'] + '\n')
        fixture += HELPERS[case]
        fixture += '\ndec $main() : bool\ndef $main() = true\n' + '\n'.join(premises) + '\ndef $main() = false -- otherwise\n'
        test = out / 'admission.watsup'
        test.write_text(fixture)
        report.update(frontend_accepted=True, adapter_ok=True, fixture_sha256=sha(test))
        if args.prepare_only:
            report['passed'] = True
        else:
            process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(test)], out / 'admission', 90)
            stdout = (out / 'admission.stdout').read_bytes()
            stderr = (out / 'admission.stderr').read_bytes()
            report['application_evaluations'] = int(process['exit'] == 0 and stdout in (b'true\n', b'false\n'))
            report.update(process=process, observed=stdout.decode(errors='replace'), stderr=stderr.decode(errors='replace'))
            report['passed'] = (process['exit'] == 0 and not process['timeout'] and not stderr
                                and not process['group_after'] and stdout == b'true\n')
    finally:
        report['inputs_stable'] = before == snapshot()
        report['head_stable'] = revision == git('rev-parse', 'HEAD')
        report['status_stable'] = status == git('status', '--short')
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report, indent=2) + '\n')
    return all(report[key] for key in ('passed', 'inputs_stable', 'head_stable', 'status_stable'))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', choices=('fast', 'helper', 'entry', 'composition'))
    parser.add_argument('--semantic-root', type=Path, default=ROOT)
    args = parser.parse_args(argv)
    return all(run_case(case, args) for case in ((args.case,) if args.case else ('fast', 'helper')))


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
