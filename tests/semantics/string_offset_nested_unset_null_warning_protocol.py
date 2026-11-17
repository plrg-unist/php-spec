#!/usr/bin/env python3
"""Genuine NULL-unset callback entry, restoration, throw discard and budgets."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_terminal_unset_protocol as prior
import string_offset_nested_unset_null_warning_cases as cases

INDEX = 0
recorded_prior = prior.recorded
PREFIX = prior.PREFIX + r'''
dec $null_unset_front(pstate, nat) : bool
def $null_unset_front(S, 0) = true -- if S.TODO = UNSET_ARRAY :: ptask_tail*
def $null_unset_front(S, 1) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = STRING_UNSET_WARNING_RESULT porigin z
def $null_unset_front(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = STRING_UNSET_WARNING_RESULT porigin z
def $null_unset_front(S, 3) = true
  -- if S.TODO = (STRING_UNSET_WARNING_RESULT porigin z) :: ptask_tail*
def $null_unset_front(S, 4) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = STRING_UNSET_WARNING_RESULT porigin z
def $null_unset_front(S, n) = false -- otherwise
dec $null_unset_seek(pstate, nat, nat) : pstate
def $null_unset_seek(S, n_stage, 0) = S
def $null_unset_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $null_unset_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $null_unset_seek(S, n_stage, n) = $null_unset_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$null_unset_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def recorded(command, stem, cap):
    runner = str(prior.ROOT / 'tests/semantics/_build/default/numeric_runner.exe')
    if command[0] == runner:
        command = [command[0], '--sl', *command[1:]]
    return recorded_prior(command, stem, cap)


def seek(start, stage, target):
    return [f'{target}_found = $null_unset_seek({start}, {stage}, 2000)',
            f'$null_unset_front({target}_found, {stage})',
            f'{target} = {target}_found[.COMPLETION = NORMAL]']


def conditions(program, path):
    encoded = json.dumps(base64.b64encode(bytes(path)).decode())
    base = ('PSTRING_CARRIER INTERNED_STRING ($ptascii("ab"))',
            'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abcd"))')[INDEX]
    checks = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S')
    checks += prior.lines(r'''
S.TODO = UNSET_ARRAY :: ptask_tail*
S.BASE = BASE_DIM (BASE_DIM (BASE_VALUE (VARIABLE ($ptascii("base")) 5)) (KNOWN PNULL) 5) (KNOWN (PINT 7)) 5
S.ORIGIN = (porigin_site)
$string_unset_warning_source(S, porigin_site, 5) = (($ptascii("base"), 5))
$string_unset_warning_plan(S) = ((porigin_site, 5))
$string_unset_warning_pending(S)
S.CURRENT = eps /\ S.FRAMES = eps /\ S.HELD = eps /\ S.EVENTS = eps
$lookup(S.ENV, $ptascii("base")) = (n_base)
$lookup(S.ENV, $ptascii("last")) = (n_last)
S.STORE[n_base] = DEFINED pvalue_base
S.STORE[n_last] = DEFINED (PINT 7)
S.ERRORHANDLER.CALLBACK = (pvalue_callback)
$hold_task_inputs(S) = S[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]
$task_nodes(STRING_UNSET_WARNING_RESULT porigin_site 5) = eps
PhpStep: S ~> S_dispatch
S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
S_dispatch = S[.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.ERRORFATALTRACE = eps]
perrorcall.SITE = porigin_site /\ perrorcall.LINE = 5 /\ perrorcall.LEVEL = 2
perrorcall.MESSAGE = $ptascii("String offset cast occurred")
perrorcall.EVENT = DIAGNOSTIC "Warning" ($ptascii("String offset cast occurred")) 5
perrorcall.CALLBACK = pvalue_callback /\ perrorcall.TARGET = eps
perrorcall.RESUME = STRING_UNSET_WARNING_RESULT porigin_site 5
$error_call_valid(S_dispatch, perrorcall)
$call_task_valid(S_dispatch, ERROR_HANDLER_INVOKE perrorcall)
$error_handler_values(S_dispatch, perrorcall) = [pvalue_level, pvalue_message, pvalue_file, pvalue_line]
pvalue_level = PINT 2 /\ pvalue_line = PINT 5
$string_bytes(pvalue_message) = ($ptascii("String offset cast occurred"))
$string_bytes(pvalue_file) = ($base64(FILE))
$heap_graph(S_dispatch) = $heap_graph(S[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
$drive_steps(S, 0) = S[.COMPLETION = BUDGET]
$drive_steps(S, 1) = S_dispatch[.COMPLETION = BUDGET]
'''.replace('FILE', encoded))
    at = checks.index('S.STORE[n_base] = DEFINED pvalue_base')
    checks[at:at] = ['pvalue_base = ' + base]
    checks += seek('S_dispatch', 1, 'S_entered') + prior.lines(r'''
S_entered.FRAMES = pframe :: pframe_tail*
pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*
pframe.ORIGIN = (porigin_site)
perrorcall_entered.RESUME = perrorcall.RESUME
perrorcall_entered.CALLBACK = pvalue_callback
perrorcall_entered.TARGET = (pcalltarget)
S_entered.CURRENT = (pcallcontext)
S_entered.ERRORHANDLER.CALLBACK = eps
$error_context_anchor(S_entered, pcallcontext, (pcallcontext), S_entered.FRAMES)
$heap_valid($heap_graph(S_entered)) /\ $call_descriptors_valid(S_entered)
''')
    if INDEX == 0:
        checks += seek('S_entered', 2, 'S_returned') + prior.lines(r'''
S_returned.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*
S_returned.RESULT = KNOWN (PBOOL true)
S_returned.ERRORHANDLER.CALLBACK = eps
S_returned.CURRENT = eps /\ S_returned.FRAMES = eps
''') + seek('S_returned', 3, 'S_resumed') + prior.lines(r'''
S_resumed.TODO = (STRING_UNSET_WARNING_RESULT porigin_site 5) :: ptask_tail*
S_resumed.ORIGIN = (porigin_site)
S_resumed.ERRORHANDLER = S.ERRORHANDLER
S_resumed.HELD = eps
$call_task_valid(S_resumed, STRING_UNSET_WARNING_RESULT porigin_site 5)
PhpStep: S_resumed ~> S_error
S_error = S_resumed[.TODO = ptask_tail*][.ORIGIN = (porigin_site)][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) 5]
S_done = $drive_steps(S_resumed, 2500)
''')
    else:
        checks += seek('S_entered', 4, 'S_discard') + prior.lines(r'''
S_discard.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*
S_discard.CURRENT = eps /\ S_discard.FRAMES = eps
S_discard.ERRORHANDLER.CALLBACK = eps
S_discard.OBJECTS[n_exception] = THROWABLE pthrowable
pthrowable.KIND = "Exception"
$throwable_field(S_discard, n_exception, "message") = PSTRING_CARRIER INTERNED_STRING ($ptascii("handler"))
$throwable_field(S_discard, n_exception, "line") = PINT 2
$error_read_discard(S_discard, perrorcall_entered.RESUME) = S_discard
S_after_discard_budget = $drive_steps(S_discard, 1)
S_after_discard_budget.COMPLETION = BUDGET
S_after_discard = S_after_discard_budget[.COMPLETION = NORMAL]
S_after_discard.TODO = (THROW_SEARCH n_exception) :: ptask_tail*
S_after_discard.ERRORHANDLER = S.ERRORHANDLER
S_after_discard.OBJECTS[n_exception] = S_discard.OBJECTS[n_exception]
S_done = $drive_steps(S_after_discard, 2500)
''')
    checks += prior.lines(r'''
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0 /\ S_done.TODO = eps
S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps
S_done.ERRORHANDLER = S.ERRORHANDLER
S_done.STORE[n_base] = S.STORE[n_base] /\ S_done.STORE[n_last] = S.STORE[n_last]
S_done.POOLS = S.POOLS /\ S_done.CODE = S.CODE
$nested_unset_outputs(S_done.EVENTS) = $ptascii("OUTPUT")
$nested_unset_diagnostics(S_done.EVENTS) = eps
$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done)
$drive_steps(S, 5000) = S_done
$drive_steps(S_dispatch, 5000) = S_done
'''.replace('OUTPUT', cases.OUTPUTS[tuple(cases.CASES)[INDEX]].decode()))
    return checks, 0


if __name__ == '__main__':
    own = Path(__file__).resolve()
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (0, 1)
    prior.NAME = tuple(cases.CASES)[INDEX]
    prior.OUTPUT = cases.OUTPUTS[prior.NAME]
    prior.cases, prior.conditions, prior.recorded, prior.PREFIX = cases, conditions, recorded, PREFIX
    passed = prior.main()
    assert hashlib.sha256(own.read_bytes()).hexdigest() == before
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['inputs'][str(own)] = before
    report['scope'] = 'Source-reached literal-NULL nested UNSET authenticates actual final7, carrier/source/NULL/line and no added input roots; Warning dispatch consumes exactly one producer head. Actual USER handler entry, four argument values, normal return/restored value-free resume versus same-Exception discard, exact raw Error, whole/split budgets, EOF/base/storage/CODE/POOLS and callback restoration hold. Fixture source0/native0; saved native observations reused without execution. No old base value is captured by the continuation and no owner/root/249/255 rule changes.'
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
