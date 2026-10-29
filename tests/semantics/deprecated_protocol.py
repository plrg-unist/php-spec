#!/usr/bin/env python3
"""Reached Deprecated/NoDiscard handoff, selected cells and abrupt owners."""
import base64
import hashlib
from pathlib import Path

import deprecated_cases as authored
import deprecated_review_cases as reviewed
import nodiscard_protocol as runner

CASES = (
    'deprecated-before-nodiscard-before-type-recv',
    'deprecated-throw-cancels-nodiscard-and-recv',
    'inherited-reference-receiver-through-both-warnings',
    'handler-replacement-retires-before-second-warning',
)
EXPECTED = {**authored.EXPECTED_STDOUT, **reviewed.EXPECTED_STDOUT}
HELPERS = runner.HELPERS + r'''
dec $deprecated_test_front(pstate, nat) : bool
def $deprecated_test_front(S, 0) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = NODISCARD_RESUME pframe
  -- if perrorcall.LEVEL = 16384
def $deprecated_test_front(S, 1) = true
  -- if S.TODO = (NODISCARD_RESUME pframe) :: ptask_tail*
  -- if pframe.TODO = [DEPRECATED_RECEIVE porigin]
def $deprecated_test_front(S, 2) = true
  -- if S.TODO = (THROW_SEARCH n) :: (NODISCARD_RESUME pframe) :: ptask_tail*
  -- if pframe.TODO = [DEPRECATED_RECEIVE porigin]
def $deprecated_test_front(S, 3) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = NODISCARD_RESUME pframe
  -- if perrorcall.LEVEL = 512
def $deprecated_test_front(S, 4) = true
  -- if S.TODO = (NODISCARD_RESUME pframe) :: ptask_tail*
  -- if pframe.TODO = [NODISCARD_RECEIVE porigin]
def $deprecated_test_front(S, n) = false -- otherwise
dec $deprecated_test_seek(pstate, nat, nat) : pstate
def $deprecated_test_seek(S, n_stage, n) = S -- if $deprecated_test_front(S, n_stage)
def $deprecated_test_seek(S, n_stage, 0) = S -- if ~$deprecated_test_front(S, n_stage)
def $deprecated_test_seek(S, n_stage, n) = $deprecated_test_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$deprecated_test_front(S, n_stage) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $deprecated_test_seek(S, n_stage, n) = S
  -- if ~$deprecated_test_front(S, n_stage) /\ $(n > 0)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''


def conditions(name, program, path):
    throws = 'throw' in name
    method = name.startswith('inherited-')
    replacement = name.startswith('handler-replacement-')
    checks = [
        'S_initial = $php_run(' + program + ', 0, "' + base64.b64encode(bytes(path)).decode() + '")',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, prior, stage):
        checks.extend([
            f'{state}_found = $deprecated_test_seek({prior}, {stage}, 3000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$deprecated_test_front({state}, {stage})',
        ])

    seek('S_dispatch', 'S_initial', 0)
    checks += [
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_caller*',
        'perrorcall.RESUME = NODISCARD_RESUME pframe',
        'pframe.CONTEXT = (pcallcontext)', 'pframe.LOCALS = (psymboltable)',
        'pframe.TODO = [DEPRECATED_RECEIVE pcallcontext.FUNCTION]',
        'S_dispatch.CURRENT = eps', 'S_dispatch.FRAMES = eps',
        'S_dispatch.HELD = eps', 'S_dispatch.GLOBALTABLE = eps',
        'perrorcall.LEVEL = 16384', 'perrorcall.LINE = pcallcontext.LINE',
        'pcallcontext.CALLSITE = (perrorcall.SITE)',
        '$nodiscard_frame_valid(S_dispatch, pframe)', '$error_call_valid(S_dispatch, perrorcall)',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        '$function_at($all_functions(S_dispatch), pcallcontext.FUNCTION) = (pfunction)',
        '$function_deprecated(S_dispatch, pfunction) = DEPRECATED_ATTRIBUTE ptbytes_message ptbytes_since',
        '$task_nodes(perrorcall.RESUME) = $nodiscard_frame_nodes(pframe)',
        # Six derived negative assertions; none is an additional reached source.
        '~$nodiscard_frame_valid(S_dispatch, pframe[.ORIGIN = eps])',
        '~$nodiscard_frame_valid(S_dispatch, pframe[.CONTEXT = (pcallcontext[.CALLSITE = eps])])',
        '~$nodiscard_frame_valid(S_dispatch, pframe[.CONTEXT = (pcallcontext[.LINE = $(pcallcontext.LINE + 1)])])',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 512])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
        '~$deprecated_api_allowed(S_dispatch, pfunction)',
    ]
    if method:
        checks += [
            '$lookup(S_dispatch.ENV, $ptascii("arg")) = (n_old)',
            '$lookup(S_dispatch.ENV, $ptascii("outside")) = (n_old)',
            '$lookup(psymboltable.ENV, $ptascii("slot")) = (n_old)',
            'S_dispatch.STORE[n_old] = DEFINED (PINT 5)',
            'pcallcontext.RECEIVER = (n_receiver)',
            '$heap_owners($heap_prune($heap_graph(S_dispatch)), HCELL n_old) = 3',
            '$heap_owners($heap_prune($heap_graph(S_dispatch)), HOBJECT n_receiver) = 2',
            '$nodiscard_frame_nodes(pframe) = [HCELL n_old, HOBJECT n_receiver]',
        ]
    elif replacement:
        checks += [
            'perrorcall.CALLBACK = POBJECT n_handler',
            '$nodiscard_frame_nodes(pframe) = eps',
            '$heap_owners($heap_prune($heap_graph(S_dispatch)), HOBJECT n_handler) = 2',
        ]
    else:
        checks += [
            '$lookup(psymboltable.ENV, $ptascii("value")) = (n_sent)',
            '$lookup(S_dispatch.ENV, $ptascii("arg")) = (n_arg)',
            'n_sent =/= n_arg',
        ]
        if throws:
            checks += [
                'S_dispatch.STORE[n_sent] = DEFINED (POBJECT n_token)',
                'S_dispatch.STORE[n_arg] = DEFINED (POBJECT n_token)',
                '$heap_owners($heap_prune($heap_graph(S_dispatch)), HOBJECT n_token) = 2',
            ]
        else:
            checks += [
                'S_dispatch.STORE[n_sent] = DEFINED (PSTRING ($ptascii("bad")))',
                'S_dispatch.STORE[n_arg] = DEFINED (PSTRING ($ptascii("bad")))',
            ]

    seek('S_after', 'S_dispatch', 2 if throws else 1)
    if throws:
        checks += [
            'S_after.TODO = (THROW_SEARCH n_failure) :: (NODISCARD_RESUME pframe) :: ptask_caller*',
            'S_after.STORE[n_arg] = DEFINED PNULL',
            '$heap_owners($heap_prune($heap_graph(S_after)), HOBJECT n_token) = 1',
            '$nodiscard_frame_valid(S_after, pframe)',
            '$lookup(S_after.ENV, $ptascii("saved")) = (n_saved)',
            'S_after.STORE[n_saved] = DEFINED (POBJECT n_failure)',
        ]
    else:
        checks += [
            'S_after.TODO = (NODISCARD_RESUME pframe) :: ptask_caller*',
            'PhpStep: S_after ~> S_receive',
            'S_receive.TODO = [DEPRECATED_RECEIVE pcallcontext.FUNCTION]',
            'S_receive.CURRENT = (pcallcontext)', '$active_table(S_receive) = psymboltable',
            'S_receive.STORE = S_after.STORE', 'S_receive.EVENTS = S_after.EVENTS',
            'S_receive.ALLOCATIONS = S_after.ALLOCATIONS',
            '$call_task_valid(S_receive, DEPRECATED_RECEIVE pcallcontext.FUNCTION)',
            '$call_descriptors_valid(S_receive)',
            # Derived API projection retains the reached data and emits nothing.
            'S_api = $call_arity(S_receive, pfunction, pcallcontext.ARGC, pcallcontext.CALLSITE, pcallcontext.LINE)',
            'S_api.COMPLETION = UNSUPPORTED "Deprecated internal API timing"',
            'S_api.EVENTS = S_receive.EVENTS', 'S_api.STORE = S_receive.STORE',
            'PhpStep: S_receive ~> S_second',
            '$deprecated_test_front(S_second, 3)',
            'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_caller*',
            'perrorcall_second.RESUME = NODISCARD_RESUME pframe_second',
            'pframe_second.CONTEXT = pframe.CONTEXT', 'pframe_second.LOCALS = pframe.LOCALS',
            'pframe_second.TODO = [NODISCARD_RECEIVE pcallcontext.FUNCTION]',
            '$nodiscard_frame_nodes(pframe_second) = $nodiscard_frame_nodes(pframe)',
            '$error_call_valid(S_second, perrorcall_second)',
        ]
        if replacement:
            checks += [
                '$heap_owners($heap_prune($heap_graph(S_after)), HOBJECT n_handler) = 0',
                '$nodiscard_test_output(S_after.EVENTS) = [' + ','.join(map(str, b'D:1:1:1;X:1;')) + ']',
                '$lookup(S_after.ENV, $ptascii("retired")) = (n_retired)',
                '$lookup(S_after.ENV, $ptascii("body")) = (n_body)',
                'S_after.STORE[n_retired] = DEFINED (PINT 1)',
                'S_after.STORE[n_body] = DEFINED (PINT 0)',
                'perrorcall_second.CALLBACK = PSTRING ($ptascii("next_notice"))',
                '$heap_owners($heap_prune($heap_graph(S_second)), HOBJECT n_handler) = 0',
            ]
        if method:
            checks += [
                '$lookup(S_second.ENV, $ptascii("arg")) = (n_new)', 'n_new =/= n_old',
                'S_second.STORE[n_old] = DEFINED (PINT 9)',
                'S_second.STORE[n_new] = DEFINED (PINT 33)',
                '$heap_owners($heap_prune($heap_graph(S_second)), HCELL n_old) = 2',
                '$heap_owners($heap_prune($heap_graph(S_second)), HOBJECT n_receiver) = 1',
            ]
        elif not replacement:
            checks += [
                'S_second.STORE[n_sent] = DEFINED (PSTRING ($ptascii("bad")))',
                'S_second.STORE[n_arg] = DEFINED (PINT 7)',
            ]
        seek('S_final_warning', 'S_second', 4)
        checks += [
            'S_final_warning.TODO = (NODISCARD_RESUME pframe_second) :: ptask_caller*',
            '$nodiscard_frame_valid(S_final_warning, pframe_second)',
        ]
        if method:
            checks += [
                'S_final_warning.STORE[n_old] = DEFINED (PINT 20)',
                'S_final_warning.STORE[n_new] = DEFINED (PINT 33)',
            ]
    checks += [
        '$call_descriptors_valid(S_after)', '$heap_valid($heap_graph(S_after))',
        'S_done = $drive_steps(S_after, 3000)', 'S_done.COMPLETION = NORMAL',
        '$nodiscard_test_output(S_done.EVENTS) = [' + ','.join(map(str, EXPECTED[name])) + ']',
        'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return checks


def main():
    watched = (Path(__file__), Path(authored.__file__), Path(reviewed.__file__))
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    runner.authored, runner.reviewed = authored, reviewed
    runner.CASES = CASES
    runner.SOURCES = {**authored.CASES, **reviewed.CASES}
    runner.EXPECTED = EXPECTED
    runner.HELPERS, runner.conditions = HELPERS, conditions
    passed = runner.main()
    assert before == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
