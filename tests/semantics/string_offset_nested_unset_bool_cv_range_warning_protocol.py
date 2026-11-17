#!/usr/bin/env python3
"""Source-reached copied range Warning, exact caller tail and normal completion."""
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

import string_offset_terminal_unset_protocol as runner
import string_offset_nested_unset_null_warning_protocol as sl
import string_offset_nested_unset_bool_cv_warning_review_state as shared
import string_offset_nested_unset_bool_cv_range_warning_cases as cases

PREFIX = shared.PREFIX + r'''
dec $range_unset_at(pstate, text) : bool
def $range_unset_at(S, "entered") = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = STRING_UNSET_CV_RANGE_WARNING_RESULT porigin z n_cell n_bits
def $range_unset_at(S, "returned") = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = STRING_UNSET_CV_RANGE_WARNING_RESULT porigin z n_cell n_bits
def $range_unset_at(S, "resume") = true
  -- if S.TODO = (STRING_UNSET_CV_RANGE_WARNING_RESULT porigin z n_cell n_bits) :: ptask_tail*
def $range_unset_at(S, text) = false -- otherwise
dec $range_unset_seek(pstate, text, nat) : pstate
def $range_unset_seek(S, text, 0) = S
def $range_unset_seek(S, text, n) = S
  -- if $(n > 0)
  -- if $range_unset_at(S, text) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $range_unset_seek(S, text, n) = $range_unset_seek($drive_steps($review_cv_running(S), 1), text, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$range_unset_at(S, text)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def seek(start, stage, target):
    return [target + '_found = $range_unset_seek(' + start + ', "' + stage + '", 1000)',
        '$range_unset_at(' + target + '_found, "' + stage + '")',
        target + ' = $review_cv_running(' + target + '_found)']


def conditions(program, path):
    checks = [
        'S_I = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(path)).decode()) + ')',
        'S_I.COMPLETION = BUDGET',
        'S_E_found = $review_cv_seek(S_I, "entry", 1000)',
        '$review_cv_at(S_E_found, "entry")',
        'S_E = $review_cv_running(S_E_found)',
        '$string_unset_bool_cv_plan(S_E) = ((porigin_site, z, n_key))',
        'S_E.STORE[n_key] = DEFINED (PBOOL true)',
        'S_R_found = $review_cv_seek(S_E, "resume", 1000)',
        '$review_cv_at(S_R_found, "resume")',
        'S_R = $review_cv_running(S_R_found)',
        'S_R.COMPLETION = NORMAL',
        'S_R.TODO = (STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key) :: ptask_after*',
        'ptask_after* = ptask_caller :: ptask_caller_tail*',
        '$string_unset_bool_cv_source(S_R, porigin_site, z) = ((n_base_name*, z_outer, n_key_name*, z_key))',
        '$lookup(S_R.ENV, n_key_name*) = (n_key)',
        '$lookup(S_R.ENV, n_base_name*) = (n_base)',
        '$lookup(S_R.ENV, $ptascii("last")) = (n_last)',
        'S_R.STORE[n_base] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("ab")))',
        'S_R.STORE[n_last] = DEFINED (PINT 7)',
        'n_bits = ' + str(cases.BITS),
        'S_R.STORE[n_key] = DEFINED (PFLOAT n_bits)',
        '$(n_bits < 18446744073709551616)',
        '$float_decode(n_bits) = FINITE n_sign n_num n_den',
        '~$fparts_fits($float_decode(n_bits))',
        '$string_unset_bool_cv_post_cell(S_R, n_key_name*, z_key, n_key)',
        '~$string_unset_bool_cv_post_normal_cell(S_R, n_key_name*, z_key, n_key)',
        '$resolve_at(S_R, VARIABLE n_key_name* z_key, z_key) = S_R[.RESULT = KNOWN (PFLOAT n_bits)]',
        '$error_handler_eligible(S_R, 2)',
        '$arithmetic_add_named(S_R)',
        'S_R.ERRORHANDLER = S_E.ERRORHANDLER',
        'S_R.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        r'S_R.REQUEST = eps /\ S_R.CURRENT = eps /\ S_R.FRAMES = eps /\ S_R.HELD = eps',
        r'S_R.SOURCEPENDING = eps /\ S_R.CONSTCONTEXT = eps',
        '~$eval_compile_recorded_error(S_R, 2)',
        '~$recorded_runtime_pending(S_R, 2)',
        '$integer_float_notices([RANGEWARNING], n_bits) = [(2, n_message*)]',
        'n_message* = $ptascii("The float 1.0E+20 is not representable as an int, cast occurred")',
        '$review_cv_outputs(S_R.EVENTS) = $ptascii("H:2:String offset cast occurred;")',
        *shared.public('S_R'),
        '$string_unset_cv_range_plan(S_R) = ((porigin_site, z, n_key, n_bits))',
        'ptask_range = STRING_UNSET_CV_RANGE_WARNING_RESULT porigin_site z n_key n_bits',
        '$task_nodes(ptask_range) = eps',
        '$value_nodes(pvalue_callback) = eps',
        'PhpStep: S_R ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_range) :: ptask_after*',
        'S_dispatch = S_R[.TODO = (ERROR_HANDLER_INVOKE perrorcall_range) :: ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.ERRORFATALTRACE = eps]',
        'perrorcall_range.SITE = porigin_site',
        r'perrorcall_range.LEVEL = 2 /\ perrorcall_range.LINE = z',
        'perrorcall_range.MESSAGE = n_message*',
        'perrorcall_range.EVENT = DIAGNOSTIC "Warning" n_message* z',
        'perrorcall_range.CALLBACK = pvalue_callback',
        'perrorcall_range.TARGET = eps',
        'perrorcall_range.RESUME = ptask_range',
        '$error_call_valid(S_dispatch, perrorcall_range)',
        '$call_task_valid(S_dispatch, ERROR_HANDLER_INVOKE perrorcall_range)',
        '$call_task_valid(S_dispatch, ptask_range)',
        '$heap_graph(S_dispatch) = $heap_graph(S_R)',
        '$drive_steps(S_R, 0) = S_R[.COMPLETION = BUDGET]',
        '$drive_steps(S_R, 1) = S_dispatch[.COMPLETION = BUDGET]',
        *shared.public('S_dispatch'),
    ]
    reached = len(checks)
    for field, value in (('LINE', '$(z + 1)'), ('LEVEL', '8'),
                         ('MESSAGE', '$ptascii("forged")'),
                         ('EVENT', 'DIAGNOSTIC "Warning" ($ptascii("forged")) z')):
        checks.append('~$error_call_valid(S_dispatch, perrorcall_range[.' + field + ' = ' + value + '])')
    checks += [
        'n_oob = |S_dispatch.STORE|',
        '~$call_task_valid(S_dispatch, STRING_UNSET_CV_RANGE_WARNING_RESULT porigin_site z n_oob n_bits)',
        '~$call_task_valid(S_dispatch, STRING_UNSET_CV_RANGE_WARNING_RESULT porigin_site $(z + 1) n_key n_bits)',
        '~$call_task_valid(S_dispatch[.ORIGIN = eps], ptask_range)',
        '~$call_task_valid(S_dispatch[.SOURCES = eps], ptask_range)',
        '~$call_task_valid(S_dispatch[.CODE = eps], ptask_range)',
        '~$error_call_valid(S_dispatch, perrorcall_range[.RESUME = STRING_UNSET_CV_RANGE_WARNING_RESULT porigin_site z n_base n_bits])',
        '~$error_call_valid(S_dispatch, perrorcall_range[.RESUME = STRING_UNSET_CV_RANGE_WARNING_RESULT porigin_site z n_key 4890909195324358656])',
        '~$error_call_valid(S_dispatch[.STORE[n_key] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("done")))], perrorcall_range)',
    ]
    for bits in (0, 4890909195324358655, 14114281232179134464,
                 9218868437227405312, 18442240474082181120,
                 9218868437227405313, 18446744073709551616):
        checks.append('~$string_unset_cv_range_bits(' + str(bits) + ')')
    for tag, changed in (
        ('mask', 'S_R[.ERRORHANDLER.LEVELS = 0]'),
        ('other_mask', 'S_R[.ERRORHANDLER.LEVELS = 512]'),
        ('no_callback', 'S_R[.ERRORHANDLER.CALLBACK = eps]'),
        ('nonnamed', 'S_R[.ERRORHANDLER.CALLBACK = (PARRAY 0)]'),
        ('budget', 'S_R[.COMPLETION = BUDGET]'),
        ('result', 'S_R[.RESULT = KNOWN (PINT 0)]'),
        ('held', 'S_R[.HELD = [HCELL n_key]]'),
        ('no_origin', 'S_R[.ORIGIN = eps]'),
        ('no_source', 'S_R[.SOURCES = eps]'),
        ('no_code', 'S_R[.CODE = eps]'),
        ('absent', 'S_R[.ENV = $unbind(S_R.ENV, n_key_name*)]'),
        ('reference', 'S_R[.REFCELLS = S_R.REFCELLS ++ [n_key]]'),
        ('undefined', 'S_R[.STORE[n_key] = UNDEFINED]'),
        ('nonfinite', 'S_R[.STORE[n_key] = DEFINED (PFLOAT 9218868437227405312)]'),
    ):
        state = 'S_range_bad_' + tag
        checks += [state + ' = ' + changed, '$string_unset_cv_range_plan(' + state + ') = eps']
    checks += [
        'PhpStep: S_range_bad_mask ~> S_range_mask_next',
        'S_range_mask_next = S_range_bad_mask[.TODO = ptask_after*][.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]',
        'PhpStep: S_range_bad_nonfinite ~> S_range_nonfinite_next',
        'S_range_nonfinite_next = S_range_bad_nonfinite[.TODO = ptask_after*][.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]',
    ]
    derived = len(checks) - reached
    checks += seek('S_dispatch', 'entered', 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_after*',
        'perrorcall_entered.RESUME = ptask_range',
        'perrorcall_entered.TARGET = (pcalltarget)',
        'S_entered.CURRENT = (pcallcontext)',
        '$error_context_anchor(S_entered, pcallcontext, (pcallcontext), S_entered.FRAMES)',
        'S_entered.ERRORHANDLER.CALLBACK = eps',
        *shared.public('S_entered'),
    ] + seek('S_entered', 'returned', 'S_returned') + [
        'S_returned.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_after*',
        'S_returned.RESULT = KNOWN (PBOOL true)',
        r'S_returned.CURRENT = eps /\ S_returned.FRAMES = eps',
        '$error_entered_call_valid(S_returned, perrorcall_entered)',
    ] + seek('S_returned', 'resume', 'S_resumed') + [
        'S_resumed.TODO = ptask_range :: ptask_after*',
        'S_resumed.STORE[n_key] = DEFINED (PFLOAT n_bits)',
        'S_resumed.ERRORHANDLER = S_E.ERRORHANDLER',
        'S_resumed.HELD = eps',
        '$call_task_valid(S_resumed, ptask_range)',
        'PhpStep: S_resumed ~> S_error',
        'S_error = S_resumed[.TODO = ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z]',
        '$review_cv_outputs(S_error.EVENTS) = $ptascii("H:2:String offset cast occurred;H:2:The float 1.0E+20 is not representable as an int, cast occurred;")',
        '$heap_graph(S_error) = $heap_graph(S_resumed)',
        *shared.public('S_resumed'),
        'S_DONE = $drive_steps(S_resumed, 2000)',
        r'S_DONE.COMPLETION = NORMAL /\ S_DONE.TODO = eps /\ S_DONE.EXITSTATUS = 0',
        r'S_DONE.CURRENT = eps /\ S_DONE.FRAMES = eps /\ S_DONE.HELD = eps',
        'S_DONE.ERRORHANDLER = S_E.ERRORHANDLER',
        'S_DONE.STORE[n_key] = S_resumed.STORE[n_key]',
        'S_DONE.STORE[n_base] = S_R.STORE[n_base]',
        'S_DONE.STORE[n_last] = S_R.STORE[n_last]',
        r'S_DONE.CODE = S_R.CODE /\ S_DONE.POOLS = S_R.POOLS',
        '$review_cv_outputs(S_DONE.EVENTS) = $base64(' + json.dumps(base64.b64encode(cases.OUTPUTS[cases.RETURN]).decode()) + ')',
        *shared.public('S_DONE'),
        '$drive_steps(S_R, 2000) = S_DONE',
        '$drive_steps(S_dispatch, 2000) = S_DONE',
        '$drive_steps(S_E, 3000) = S_DONE',
    ]
    return checks, derived


if __name__ == '__main__':
    own = Path(__file__).resolve()
    watched = [own, Path(shared.__file__), Path(sl.__file__), Path(cases.prior.__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.NAME, runner.OUTPUT = cases.RETURN, cases.OUTPUTS[cases.RETURN]
    runner.cases, runner.conditions, runner.PREFIX, runner.recorded = cases, conditions, PREFIX, sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    p = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(p.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 2
    report['scope'] = ('Actual NORMAL first-handler resume snapshots the finite OOB value before the second '
        'Warning. Dispatch preserves the complete original caller tail, exact pure message and nonowning '
        'source/cell/bits task; pretarget snapshot, selected callback, source and bit forgeries remain checked. '
        'Second return restores the callback and raises the fixed nested Error without a converter replay; '
        'normal/masked/nonfinite bounds, heap, final storage and whole/split budgets retain source0/native0.')
    p.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
