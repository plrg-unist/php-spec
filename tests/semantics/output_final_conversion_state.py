#!/usr/bin/env python3
"""Array Warning and retval authority during the real null-C FINAL drain."""
import os
from pathlib import Path
import output_deprecation_warning_review_state as runner
import output_final_conversion_sources as sources
ROOT = sources.ROOT
CASES = {'final-array-warning-null-c': sources.CASES['final-array-warning-null-c']}
PREFIX = runner.PREFIX.split('dec $dp_phase', 1)[0] + r'''
dec $dp_phase(pstate, nat) : bool
def $dp_phase(S, 0) = true -- if S.TODO = (OB_USER_ARRAY_WARN pobarrayreturn) :: ptask_tail*
def $dp_phase(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S, pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = OB_USER_ARRAY_RESULT pobarrayreturn
  -- if $lookup(S.ENV, ([108])) = (n_line)
  -- if S.STORE[n_line] = DEFINED (PINT 0)
def $dp_phase(S, 2) = true -- if S.TODO = (OB_USER_ARRAY_RESULT pobarrayreturn) :: ptask_tail*
def $dp_phase(S, 3) = true -- if S.TODO = (OB_USER_ARRAY_DONE pobarrayreturn) :: ptask_tail*
def $dp_phase(S, 4) = true -- if S.TODO = (OB_USER_ARRAY_COMMIT pobarrayreturn poboutput) :: ptask_tail*
def $dp_phase(S, n) = false -- otherwise
''' + 'dec $dp_seek' + runner.PREFIX.split('dec $dp_seek', 1)[1]

def fingerprint():
    inputs = sources.fingerprint()
    inputs['tests/semantics/output_final_conversion_state.py'] = sources.runner.common.sha(Path(__file__))
    inputs['tests/semantics/_build/default/numeric_runner.exe'] = sources.runner.common.sha(ROOT / 'tests/semantics/_build/default/numeric_runner.exe')
    return inputs

def seek(checks, old, new, phase):
    checks += [new + '_found = $dp_seek(' + old + ', ' + str(phase) + ', 2048)',
               new + r'_found.COMPLETION = NORMAL \/ ' + new + '_found.COMPLETION = BUDGET',
               new + ' = ' + new + '_found[.COMPLETION = NORMAL]', *runner.valid(new)]

def assertions(name, fixture, directory, path):
    checks = ['S_initial = $php_file_run(' + fixture + ', 0, ' + runner.bytes_expr(os.fsencode(path)) + ', ' + runner.bytes_expr(os.fsencode(directory)) + ')',
              'S_initial.COMPLETION = BUDGET']
    seek(checks, 'S_initial', 'S', 0)
    checks += [
        'S.TODO = (OB_USER_ARRAY_WARN pobarrayreturn) :: ptask_native*',
        'pobarrayreturn.INVOKE.CALL = OB_FINAL pobdrain',
        'pobarrayreturn.CALLER = eps', 'pobarrayreturn.PENDING = eps',
        'pobarrayreturn.TAIL = ptask_native*', 'pobarrayreturn.INVOKE.PHASE = 9',
        '$string_bytes(pobarrayreturn.INVOKE.INPUT) = ([65])',
        'S.CURRENT = eps', 'S.ORIGIN = ($ob_call_site(pobarrayreturn.INVOKE.CALL))',
        'S.DESTRUCTION.PHASE = DESTRUCTION_DONE', '$output_drain_active(S, pobdrain)',
        '$output_final_destructors(S)',
        '$heap_count(HARRAY pobarrayreturn.ARRAY, $task_nodes(OB_USER_ARRAY_WARN pobarrayreturn)) = 1',
        '~$call_task_valid(S, OB_USER_ARRAY_WARN pobarrayreturn[.ARRAY = 999999])',
        '~$call_task_valid(S, OB_USER_ARRAY_WARN pobarrayreturn[.TAIL = eps])',
        'S_budget = $drive_steps(S, 0)', 'S_budget.COMPLETION = BUDGET',
        'S_budget.TODO = S.TODO', 'S_budget.ALLOCATIONS = S.ALLOCATIONS',
        'S_budget.DESTRUCTION = S.DESTRUCTION', *runner.valid('S_budget'),
    ]
    seek(checks, 'S', 'S_error', 1)
    checks += [
        'S_error.CURRENT = (pcallcontext)',
        '$error_context_call(S_error, pcallcontext) = (perrorcall)',
        'perrorcall.RESUME = OB_USER_ARRAY_RESULT pobarrayreturn',
        'pcallcontext.ARGC = 4', 'perrorcall.LEVEL = 2', 'perrorcall.LINE = 0',
        'perrorcall.MESSAGE = $ptascii("Array to string conversion")',
        '$error_handler_file(S_error, perrorcall) = $ptascii("Unknown")',
        '$lookup(S_error.ENV, ([110])) = (n_level)', 'S_error.STORE[n_level] = DEFINED (PINT 2)',
        '$lookup(S_error.ENV, ([102])) = (n_file)', 'S_error.STORE[n_file] = DEFINED pvalue_file',
        '$string_bytes(pvalue_file) = ($ptascii("Unknown"))',
        '$lookup(S_error.ENV, ([108])) = (n_line)', 'S_error.STORE[n_line] = DEFINED (PINT 0)',
        '$output_final_destructors(S_error)',
        'S_pending = S_error[.COMPLETION = THROWN "Exception" ([69]) 0]',
        'S_blocked = $output_guard(S_pending)',
        'S_blocked.COMPLETION = UNSUPPORTED "pending FINAL Array/Object return conversion"',
        'S_blocked.TODO = S_pending.TODO', 'S_blocked.CURRENT = S_pending.CURRENT',
        'S_blocked.FRAMES = S_pending.FRAMES', 'S_blocked.ALLOCATIONS = S_pending.ALLOCATIONS',
        '$heap_count(HARRAY pobarrayreturn.ARRAY, $task_nodes(OB_USER_ARRAY_RESULT pobarrayreturn)) = 1',
    ]
    seek(checks, 'S_error', 'S_result', 2)
    checks += ['S_result.CURRENT = eps', '$ob_array_current(S_result, pobarrayreturn)']
    seek(checks, 'S_result', 'S_done', 3)
    checks += ['$heap_count(HARRAY pobarrayreturn.ARRAY, $task_nodes(OB_USER_ARRAY_DONE pobarrayreturn)) = 0']
    seek(checks, 'S_done', 'S_commit', 4)
    checks += [
        'S_commit.TODO = (OB_USER_ARRAY_COMMIT pobarrayreturn poboutput) :: ptask_native*',
        'poboutput.VALUE = PSTRING $ptascii("Array")', '~poboutput.FAILED',
        'S_final = $drive_steps(S_commit, 4096)',
        'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps',
        'S_final.CURRENT = eps', 'S_final.FRAMES = eps', 'S_final.OUTPUTBUFFERS = eps',
        '$dp_output(S_final.EVENTS) = ' + runner.bytes_expr(CASES[name][1]), *runner.valid('S_final'),
    ]
    return checks

if __name__ == '__main__':
    runner.ROOT = ROOT
    runner.CASES = CASES
    runner.PREFIX = PREFIX
    runner.fingerprint = fingerprint
    runner.assertions = assertions
    runner.main()
