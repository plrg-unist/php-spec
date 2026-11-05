#!/usr/bin/env python3
"""Independently check saved enum query inputs across callbacks and unwinding."""
import hashlib
import json
import subprocess

import enum_is_callable_output_protocol as output

base = output.base
ROOT, OUT, MODULES = base.ROOT, base.OUT, base.MODULES
WATCHED = [ROOT / 'spec/semantics/modules.json',
           ROOT / 'tests/semantics/enum_is_callable_cases.json',
           ROOT / 'tests/semantics/enum_is_callable_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_output_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_saved_input_protocol.py',
           ROOT / 'tests/semantics/profile.json',
           ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *MODULES]

PREFIX = r'''
dec $eis_first(pstate) : bool
def $eis_first(S) = true
  -- if S.TODO = (CONFIG_SEND pconfigcall) :: ptask_tail*
  -- if $enum_is_callable_capture(S, pconfigcall) = (penumqueryinput)
def $eis_first(S) = false -- otherwise
dec $eis_seek_first(pstate, nat) : pstate
def $eis_seek_first(S, 0) = S
def $eis_seek_first(S, n) = S -- if $(n > 0) /\ $eis_first(S)
def $eis_seek_first(S, n) = $eis_seek_first($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if $(n > 0) /\ ~$eis_first(S)
dec $eis_site(pstate, porigin, nat) : bool
def $eis_site(S, porigin, 2) = true
  -- if S.TODO = (CONFIG_SEND pconfigcall) :: ptask_tail*
  -- if pconfigcall.SITE = porigin /\ pconfigcall.INDEX = 2
def $eis_site(S, porigin, 3) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.SITE = porigin
def $eis_site(S, porigin, n) = false -- otherwise
dec $eis_seek(pstate, porigin, nat, nat) : pstate
def $eis_seek(S, porigin, n_stage, 0) = S
def $eis_seek(S, porigin, n_stage, n) = S
  -- if $(n > 0) /\ $eis_site(S, porigin, n_stage)
def $eis_seek(S, porigin, n_stage, n) = $eis_seek($drive_steps(S[.COMPLETION = NORMAL], 1), porigin, n_stage, $nabs($(n - 1)))
  -- if $(n > 0) /\ ~$eis_site(S, porigin, n_stage)
dec $eis_has(ptask*, penumqueryinput) : bool
def $eis_has(eps, penumqueryinput) = false
def $eis_has((ENUM_IS_CALLABLE_INPUT penumqueryinput) :: ptask_tail*, penumqueryinput) = true
def $eis_has(ptask :: ptask_tail*, penumqueryinput) = $eis_has(ptask_tail*, penumqueryinput) -- otherwise
'''


def checked(row, label):
    base.OUT = OUT / label
    base.OUT.mkdir()
    try:
        return base.checked_source(row)
    finally:
        base.OUT = OUT


def capture_checks(label, row):
    return [
        f'S_{label}_initial = ' + checked(row, label),
        f'S_{label}_initial.COMPLETION = BUDGET',
        f'S_{label}_first = $eis_seek_first(S_{label}_initial, 3000)',
        f'$eis_first(S_{label}_first)',
        f'S_{label}_first.TODO = (CONFIG_SEND c_{label}_first) :: tail_{label}*',
        f'c_{label}_first.INDEX = 0 /\\ c_{label}_first.SENT = eps',
        f'$enum_is_callable_capture(S_{label}_first, c_{label}_first) = (r_{label})',
        f'r_{label}.CALL = c_{label}_first',
        f'r_{label}.DEPTH = |S_{label}_first.FRAMES|',
        f'r_{label}.VALUE = $ptascii("FirstCheck::from")',
        f'$enum_is_callable_input_source(S_{label}_first, r_{label})',
        f'$task_nodes(ENUM_IS_CALLABLE_INPUT r_{label}) = eps',
        f'S_{label}_cap = $drive_steps(S_{label}_first[.COMPLETION = NORMAL], 1)',
        f'S_{label}_cap.TODO = (CONFIG_ARGS c_{label}_cap) :: (ENUM_IS_CALLABLE_INPUT r_{label}) :: tail_{label}*',
        f'c_{label}_cap.SENT = [NAMED_SENT (KNOWN v_{label})]',
        f'$string_bytes(v_{label}) = (r_{label}.VALUE)',
        f'$call_task_valid(S_{label}_cap, ENUM_IS_CALLABLE_INPUT r_{label})',
    ]


def finish_checks(label, row):
    return [
        f'S_{label}_send = $eis_seek(S_{label}_cap, c_{label}_first.SITE, 2, 5000)',
        f'$eis_site(S_{label}_send, c_{label}_first.SITE, 2)',
        f'S_{label}_send.TODO = (CONFIG_SEND c_{label}_send) :: (ENUM_IS_CALLABLE_INPUT r_{label}) :: tail_{label}*',
        f'c_{label}_send.SENT = [NAMED_SENT (KNOWN v_{label}), NAMED_SENT (KNOWN (PBOOL false))]',
        f'$enum_is_callable_saved(S_{label}_send, c_{label}_send, v_{label}) = (r_{label})',
        f'$enum_is_callable_ref_name(S_{label}_send, c_{label}_send, v_{label}) = (r_{label}.VALUE)',
        f'$enum_is_callable_ref_cell(S_{label}_send, c_{label}_send, v_{label}) = (cell_{label})',
        f'S_{label}_ref = $drive_steps(S_{label}_send[.COMPLETION = NORMAL], 1)',
        f'S_{label}_ref.TODO = (CONFIG_ARGS c_{label}_ref) :: (ENUM_IS_CALLABLE_INPUT r_{label}) :: tail_{label}*',
        f'c_{label}_ref.SENT = [NAMED_SENT (KNOWN v_{label}), NAMED_SENT (KNOWN (PBOOL false)), NAMED_SENT (REFERENCE cell_{label})]',
        f'S_{label}_invoke = $eis_seek(S_{label}_ref, c_{label}_first.SITE, 3, 2000)',
        f'$eis_site(S_{label}_invoke, c_{label}_first.SITE, 3)',
        f'S_{label}_invoke.TODO = (CONFIG_INVOKE c_{label}_invoke) :: (ENUM_IS_CALLABLE_INPUT r_{label}) :: tail_{label}*',
        f'$enum_is_callable_ref_slots_valid(S_{label}_invoke, c_{label}_invoke)',
        f'$config_invoke_valid(S_{label}_invoke, c_{label}_invoke)',
        f'S_{label}_after = $drive_steps(S_{label}_invoke[.COMPLETION = NORMAL], 1)',
        f'S_{label}_after.TODO = tail_{label}*',
        f'S_{label}_after.STORE[cell_{label}] = DEFINED (PSTRING r_{label}.VALUE)',
        f'S_{label}_after.RESULT = KNOWN (PBOOL true)',
        f'~$eis_has(S_{label}_after.TODO, r_{label})',
        f'S_{label}_zero = $drive_steps(S_{label}_invoke[.COMPLETION = NORMAL], 0)',
        f'S_{label}_zero.COMPLETION = BUDGET',
        f'$drive_steps(S_{label}_zero[.COMPLETION = NORMAL], 1) = S_{label}_after',
        f'S_{label}_done = $drive(S_{label}_after[.COMPLETION = NORMAL], 5000)',
        f'S_{label}_done.COMPLETION = NORMAL',
        f'$eic_output(S_{label}_done.EVENTS) = $ptascii(' + json.dumps(row['expected_normal_stdout']) + ')',
    ]


if __name__ == '__main__':
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in WATCHED}
    rebind = base.CASES['enum-is-callable-third-output-variable-rebind']
    alias = base.CASES['enum-is-callable-third-output-variable-alias-after-rebind']
    nested = base.CASES['enum-is-callable-third-output-variable-nested-saved-query']
    thrown = base.CASES['enum-is-callable-third-output-variable-second-argument-throw']
    checks = capture_checks('rebind', rebind) + finish_checks('rebind', rebind)
    checks += [
        '$lookup(S_rebind_send.ENV, $ptascii("target")) = (cell_target)',
        'S_rebind_send.STORE[cell_target] = DEFINED value_target',
        '$string_bytes(value_target) = ($ptascii("OtherCheck::from"))',
        'S_missing = S_rebind_send[.TODO = (CONFIG_SEND c_rebind_send) :: tail_rebind*]',
        '$enum_is_callable_saved(S_missing, c_rebind_send, v_rebind) = eps',
        '$enum_is_callable_ref_name(S_missing, c_rebind_send, v_rebind) = eps',
        'S_moved = S_rebind_send[.TODO = (CONFIG_SEND c_rebind_send) :: DISCARD :: (ENUM_IS_CALLABLE_INPUT r_rebind) :: tail_rebind*]',
        '$enum_is_callable_saved(S_moved, c_rebind_send, v_rebind) = eps',
        'r_line = r_rebind[.LINE = $(r_rebind.LINE + 1)]',
        '~$enum_is_callable_input_source(S_rebind_send, r_line)',
        'S_line = S_rebind_send[.TODO = (CONFIG_SEND c_rebind_send) :: (ENUM_IS_CALLABLE_INPUT r_line) :: tail_rebind*]',
        '$enum_is_callable_saved(S_line, c_rebind_send, v_rebind) = eps',
        'r_argument = r_rebind[.ARGUMENT = c_rebind_send.SITE]',
        '~$enum_is_callable_input_source(S_rebind_send, r_argument)',
        'r_depth = r_rebind[.DEPTH = $(r_rebind.DEPTH + 1)]',
        '~$call_task_valid(S_rebind_send, ENUM_IS_CALLABLE_INPUT r_depth)',
        'S_depth = S_rebind_send[.TODO = (CONFIG_SEND c_rebind_send) :: (ENUM_IS_CALLABLE_INPUT r_depth) :: tail_rebind*]',
        '$enum_is_callable_saved(S_depth, c_rebind_send, v_rebind) = eps',
        'r_call = r_rebind[.CALL = r_rebind.CALL[.SITE = r_rebind.ARGUMENT]]',
        '~$enum_is_callable_input_source(S_rebind_send, r_call)',
        'r_value = r_rebind[.VALUE = $ptascii("OtherCheck::from")]',
        'S_value = S_rebind_send[.TODO = (CONFIG_SEND c_rebind_send) :: (ENUM_IS_CALLABLE_INPUT r_value) :: tail_rebind*]',
        '$enum_is_callable_saved(S_value, c_rebind_send, v_rebind) = eps',
        'c_bytes = c_rebind_invoke[.SENT = [NAMED_SENT (KNOWN (PSTRING $ptascii("OtherCheck::from"))), NAMED_SENT (KNOWN (PBOOL false)), NAMED_SENT (REFERENCE cell_rebind)]]',
        'S_bytes = S_rebind_invoke[.TODO = (CONFIG_INVOKE c_bytes) :: (ENUM_IS_CALLABLE_INPUT r_rebind) :: tail_rebind*]',
        '~$enum_is_callable_ref_slots_valid(S_bytes, c_bytes)',
        'S_orphan = S_rebind_cap[.TODO = (ENUM_IS_CALLABLE_INPUT r_rebind) :: tail_rebind*]',
        'S_orphan_after = $drive_steps(S_orphan[.COMPLETION = NORMAL], 1)',
        'S_orphan_after.COMPLETION = UNSUPPORTED "orphan enum is_callable input receipt"',
    ]
    checks += capture_checks('alias', alias) + finish_checks('alias', alias)
    checks += [
        '$lookup(S_alias_send.ENV, $ptascii("target")) = (cell_alias)',
        'S_alias_send.STORE[cell_alias] = DEFINED value_alias_old',
        '$string_bytes(value_alias_old) = ($ptascii("OtherCheck::from"))',
        'S_alias_after.STORE[cell_alias] = DEFINED (PSTRING $ptascii("FirstCheck::from"))',
    ]
    checks += capture_checks('nested', nested)
    checks += [
        'S_inner_first = $eis_seek_first(S_nested_cap, 5000)',
        '$eis_first(S_inner_first)',
        'S_inner_first.TODO = (CONFIG_SEND c_inner_first) :: tail_inner*',
        '$enum_is_callable_capture(S_inner_first, c_inner_first) = (r_inner)',
        'r_inner.DEPTH = 1 /\\ r_nested.DEPTH = 0',
        'r_inner.CALL.SITE =/= r_nested.CALL.SITE',
        'r_inner.VALUE = $ptascii("OtherCheck::missing")',
        'S_inner_first.FRAMES = frame_inner :: eps',
        '$eis_has(frame_inner.TODO, r_nested)',
        'S_inner_cap = $drive_steps(S_inner_first[.COMPLETION = NORMAL], 1)',
        'S_inner_cap.TODO = (CONFIG_ARGS c_inner_cap) :: (ENUM_IS_CALLABLE_INPUT r_inner) :: tail_inner*',
        '$call_task_valid(S_inner_cap, ENUM_IS_CALLABLE_INPUT r_inner)',
    ]
    checks += finish_checks('nested', nested)
    checks += [
        '~$eis_has(S_nested_send.TODO, r_inner)',
        'S_nested_send.FRAMES = eps',
    ]
    checks += capture_checks('thrown', thrown)
    checks += [
        'S_thrown_done = $drive(S_thrown_cap[.COMPLETION = NORMAL], 7000)',
        'S_thrown_done.COMPLETION = NORMAL',
        '$eic_output(S_thrown_done.EVENTS) = $ptascii(' + json.dumps(thrown['expected_normal_stdout']) + ')',
        'S_thrown_done.TODO = eps /\\ S_thrown_done.FRAMES = eps',
        'S_thrown_zero = $drive_steps(S_thrown_cap[.COMPLETION = NORMAL], 0)',
        'S_thrown_zero.COMPLETION = BUDGET',
        '$drive(S_thrown_zero[.COMPLETION = NORMAL], 7000) = S_thrown_done',
    ]
    fixture = OUT / 'saved-input.watsup'
    fixture.write_text(base.PREFIX + PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                       + ''.join('  -- if ' + check + '\n' for check in checks))
    command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
               *map(str, MODULES), str(fixture)]
    result = subprocess.run(command, capture_output=True, timeout=180)
    (OUT / 'command.json').write_text(json.dumps(command) + '\n')
    (OUT / 'stdout').write_bytes(result.stdout)
    (OUT / 'stderr').write_bytes(result.stderr)
    record = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'checks': len(checks), 'exit': result.returncode,
              'stdout': result.stdout.decode(errors='replace'),
              'stderr': result.stderr.decode(errors='replace'),
              'stable': before == {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                  for path in WATCHED}, 'direct_inputs': before}
    (OUT / 'report.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k: record[k] for k in ['revision', 'checks', 'exit', 'stdout', 'stderr', 'stable']}), OUT, flush=True)
    assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr and record['stable'], OUT
