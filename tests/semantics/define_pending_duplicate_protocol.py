#!/usr/bin/env python3
"""Literal pending duplicate skips an eligible handler without replacing state."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import define_pending_duplicate_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_pending_duplicate_front(pstate) : bool
def $test_pending_duplicate_front(S) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall
def $test_pending_duplicate_front(S) = false -- otherwise
dec $test_pending_duplicate_seek(pstate, nat) : pstate
def $test_pending_duplicate_seek(S, 0) = S
def $test_pending_duplicate_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_pending_duplicate_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_pending_duplicate_seek(S, n) = $test_pending_duplicate_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_pending_duplicate_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def checks(program, path, name):
    assert name == 'literal-true-pending-duplicate-eligible-handler'
    return [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $test_pending_duplicate_seek(S_initial,1500)',
        'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$test_pending_duplicate_front(S)',
        'S.TODO = (THROW_SEARCH n_throw) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall',
        'perrorcall.LEVEL = 2', 'perrorcall.MESSAGE = $dynamic_constant_case_message()',
        'perrorcall.SITE = pconfigcall.SITE', 'perrorcall.LINE = pconfigcall.LINE',
        'S.ORIGIN = (pconfigcall.SITE)', '$throwable_live(S,n_throw)',
        'S.OBJECTS[n_throw] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
        '$string_bytes($throwable_field(S,n_throw,"message")) = (' + text('first') + ')',
        'pconfigcall.KIND = INTRINSIC_DEFINE', 'pconfigcall.OWNER = eps', 'pconfigcall.PACKS = eps',
        'pconfigcall.SELECTION = eps',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_captured_name),NAMED_SENT (KNOWN (PINT 169)),NAMED_SENT (KNOWN (PBOOL true))]',
        '$string_bytes(pvalue_captured_name) = (' + text('LiteralPendingDup34') + ')',
        '$config_invoke_valid(S,pconfigcall)', '~$config_strict(S,pconfigcall)',
        '$dynamic_define_known(S,pconfigcall.SITE,0) = (pvalue_literal_name)',
        '$string_bytes(pvalue_literal_name) = (' + text('LiteralPendingDup34') + ')',
        '$dynamic_define_known(S,pconfigcall.SITE,1) = (PINT 169)',
        '$dynamic_constant_case_valid(S,pconfigcall)',
        '$user_constant_at(S.USERCONSTANTS,' + text('LiteralPendingDup34') + ') = (puserconstant)',
        'S.USERCONSTANTS = [puserconstant]', 'puserconstant.VALUE = PINT 269',
        'puserconstant.CLASS = PVSCALAR', 'puserconstant.ORIGIN =/= pconfigcall.SITE', *common.public('S'),
        '$lookup(S.ENV,' + text('effect') + ') = (n_effect)', 'S.STORE[n_effect] = DEFINED pvalue_effect',
        '$string_bytes(pvalue_effect) = (' + text('after') + ')',
        '$lookup(S.ENV,' + text('warnings') + ') = (n_warnings)', 'S.STORE[n_warnings] = DEFINED (PINT 1)',
        '$lookup(S.ENV,' + text('pending') + ') = (n_pending)', 'S.STORE[n_pending] = DEFINED (POBJECT n_throw)',
        '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
        'S_discard = S[.TODO = (THROW_SEARCH n_throw) :: ptask_tail*]',
        'S_before = $error_handler_restore($identity_read_discard(S_discard,perrorcall.RESUME),perrorcall.CALLBACK)',
        '$dynamic_constant_case_valid(S_before,pconfigcall)', '$throwable_live(S_before,n_throw)',
        '$source_constant_lookup(S_before,' + text('LiteralPendingDup34') + ') = (VALUE (PINT 269))',
        '$error_handler_eligible(S_before,2)', 'S_before.ERRORFATALTRACE = eps',
        'S_expected = S_before[.ERRORFATALTRACE = eps]',
        '$dynamic_constant_case_pending(S_before,pconfigcall) = S_expected',
        '$error_read_discard(S_before,perrorcall.RESUME) = S_expected',
        *common.step('S_after', 'S'), 'S_after = S_expected',
        'S_after.TODO = (THROW_SEARCH n_throw) :: ptask_tail*',
        'S_after.OBJECTS[n_throw] = THROWABLE pthrowable', '$throwable_live(S_after,n_throw)',
        'S_after.STORE[n_result] = DEFINED (PINT 99)',
        'S_after.USERCONSTANTS = [puserconstant]', 'S_after.EVENTS = S_before.EVENTS', *common.public('S_after'),
        'pconfigcall_bad_value = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,1,KNOWN (PINT 170))]',
        '~$dynamic_constant_case_valid(S_before,pconfigcall_bad_value)',
        'S_bad_value = $dynamic_constant_case_pending(S_before,pconfigcall_bad_value)',
        'S_bad_value.COMPLETION = UNSUPPORTED "boolean define flag pending-exception registration"',
        'S_bad_value.USERCONSTANTS = S_before.USERCONSTANTS',
        'pconfigcall_bad_name = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,0,KNOWN (PSTRING ' + text('OtherPendingDup34') + '))]',
        '~$dynamic_constant_case_valid(S_before,pconfigcall_bad_name)',
        'S_bad_name = $dynamic_constant_case_pending(S_before,pconfigcall_bad_name)',
        'S_bad_name.COMPLETION = UNSUPPORTED "boolean define flag pending-exception registration"',
        'S_bad_name.USERCONSTANTS = S_before.USERCONSTANTS',
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S,1)', 'S_one = $drive_steps(S_pause[.COMPLETION = NORMAL],1)',
    ]


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    sources.family.CASES = {name: value for name, value in sources.family.CASES.items()
        if name == 'literal-true-pending-duplicate-eligible-handler'}
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
