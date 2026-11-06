#!/usr/bin/env python3
"""Real null-C FINAL method entry, documentary registration and returned owners."""
import os

import output_deprecation_warning_review_state as runner
import output_final_conversion_review_sources as sources

ROOT = sources.ROOT
CASES = sources.CASES
PREFIX = runner.PREFIX.split('dec $dp_phase', 1)[0] + r'''
dec $dp_phase(pstate, nat) : bool
def $dp_phase(S, 0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $ob_object_context(S, pcallcontext) = (pobobjectreturn)
  -- if pobobjectreturn.INVOKE.CALL = OB_FINAL pobdrain
def $dp_phase(S, n) = false -- otherwise
''' + 'dec $dp_seek' + runner.PREFIX.split('dec $dp_seek', 1)[1]


def fingerprint():
    inputs = sources.fingerprint()
    for name in ('tests/semantics/output_final_conversion_review_state.py',
                 'tests/semantics/output_deprecation_warning_review_state.py',
                 'tests/semantics/_build/default/numeric_runner.exe'):
        inputs[name] = sources.runner.common.sha(ROOT / name)
    return inputs


def assertions(name, fixture, directory, path):
    return [
        'S_initial = $php_file_run(' + fixture + ', 0, ' + runner.bytes_expr(os.fsencode(path)) + ', ' + runner.bytes_expr(os.fsencode(directory)) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $dp_seek(S_initial, 0, 1024)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$dp_phase(S, 0)', *runner.valid('S'),
        'S.CURRENT = (pcallcontext)',
        '$ob_object_context(S, pcallcontext) = (pobobjectreturn)',
        'pobobjectreturn.INVOKE.CALL = OB_FINAL pobdrain',
        'pobobjectreturn.INVOKE.PHASE = 9', 'pobobjectreturn.PENDING = eps',
        'pobobjectreturn.CALLER = eps', 'pobobjectreturn.RETURNED = eps',
        'n_object = pobobjectreturn.OBJECT',
        'pcallcontext.TARGET = METHOD_TARGET n_object porigin_method',
        r'pcallcontext.CALLSITE = eps /\ pcallcontext.LINE = $(-1)',
        r'pcallcontext.ARGC = 0 /\ pcallcontext.EXTRA = eps /\ pcallcontext.NAMED = eps',
        r'pcallcontext.WRAPPER = eps /\ pcallcontext.HOLES = eps',
        'S.FRAMES = pframe :: pframe_tail*',
        'pframe.CONTEXT = eps',
        'porigin_registration = $ob_call_site(pobobjectreturn.INVOKE.CALL)',
        'pframe.ORIGIN = (porigin_registration)',
        'pframe.TODO = (STRINGIFY_RESULT n_object porigin_registration 0) :: (OB_USER_OBJECT_STRING pobobjectreturn) :: pobobjectreturn.TAIL',
        '$call_task_valid(S, OB_USER_OBJECT_STRING pobobjectreturn)',
        '$stringify_native_context_kind(S, pcallcontext)',
        '$stringify_context_frame_valid(S, pcallcontext, pframe)',
        '$reference_callback_used(S, pcallcontext) = (true)',
        '$heap_count(HOBJECT n_object, $machine_roots(S)) = 2',
        '$heap_count(HOBJECT n_object, $task_nodes(STRINGIFY_RESULT n_object porigin_registration 0)) = 1',
        '$task_nodes(OB_USER_OBJECT_STRING pobobjectreturn) = eps',
        '$output_drain_active(S, pobdrain)',
        'S.SHUTDOWN.PHASE = SHUTDOWN_DONE', 'S.DESTRUCTION.PHASE = DESTRUCTION_DONE',
        'S.OUTPUTBUFFERS = [poutputbuffer]',
        r'poutputbuffer.FLAGS = 113 /\ poutputbuffer.BYTES = ([65])',
        '$dp_output(S.EVENTS) = ([80])',
        '$trace_context(S, S.ENV, (pcallcontext)) = [ptraceframe]',
        r'ptraceframe.FILE = eps /\ ptraceframe.LINE = $(-1)',
        'ptraceframe.FUNCTION = $ptascii("__toString")',
        'ptraceframe.CLASS = ($ptascii("T"))',
        r'ptraceframe.ARGS = eps /\ ptraceframe.HASARGS',
        'pcallcontext_bad = pcallcontext[.CALLSITE = (porigin_registration)][.LINE = 0]',
        'S_bad = S[.CURRENT = (pcallcontext_bad)]',
        '$stringify_native_context_kind(S_bad, pcallcontext_bad)',
        '~$stringify_context_frame_valid(S_bad, pcallcontext_bad, pframe)',
        '$ob_object_context(S_bad, pcallcontext_bad) = eps',
        '~$call_descriptors_valid(S_bad)',
        'pframe_nested = pframe[.CONTEXT = (pcallcontext)][.TODO = eps]',
        'S_nested = S[.CURRENT = (pcallcontext_bad)][.FRAMES = pframe_nested :: S.FRAMES]',
        '$ob_object_final_domain(S_nested, pcallcontext_bad) = eps',
        '~$stringify_native_context_kind(S_nested, pcallcontext_bad)',
        'S_budget = $drive_steps(S, 0)', 'S_budget.COMPLETION = BUDGET',
        r'S_budget.CURRENT = S.CURRENT /\ S_budget.FRAMES = S.FRAMES /\ S_budget.TODO = S.TODO',
        r'S_budget.ALLOCATIONS = S.ALLOCATIONS /\ S_budget.OUTPUTBUFFERS = S.OUTPUTBUFFERS',
        *runner.valid('S_budget'),
        'S_done = $drive_steps(S_budget[.COMPLETION = NORMAL], 2048)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        'S_done.OUTPUTBUFFERS = eps',
        '~((HOBJECT n_object) <- S_done.ALLOCATIONS)',
        '$dp_output(S_done.EVENTS) = ' + runner.bytes_expr(CASES[name][1]),
        *runner.valid('S_done'),
    ]


if __name__ == '__main__':
    runner.ROOT = ROOT
    runner.CASES = CASES
    runner.PREFIX = PREFIX
    runner.assertions = assertions
    runner.fingerprint = fingerprint
    runner.main()
