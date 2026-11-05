#!/usr/bin/env python3
"""Independent last-owner enum callable-output continuations and refusal guards."""
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
           ROOT / 'tests/semantics/enum_is_callable_output_unique_protocol.py',
           ROOT / 'tests/semantics/profile.json',
           ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *MODULES]
PREFIX = r'''
dec $eiu_entry(pstate, penumqueryoutput) : bool
def $eiu_entry(S, penumqueryoutput) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OBJECT = penumqueryoutput.OLD
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = ENUM_IS_CALLABLE_CLEAR penumqueryoutput
def $eiu_entry(S, penumqueryoutput) = false -- otherwise
dec $eiu_exit(pstate, penumqueryoutput) : bool
def $eiu_exit(S, penumqueryoutput) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (ENUM_IS_CALLABLE_OUTPUT penumqueryoutput) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = ENUM_IS_CALLABLE_CLEAR penumqueryoutput
def $eiu_exit(S, penumqueryoutput) = false -- otherwise
dec $eiu_at(pstate, penumqueryoutput, bool) : bool
def $eiu_at(S, penumqueryoutput, true) = $eiu_entry(S, penumqueryoutput)
def $eiu_at(S, penumqueryoutput, false) = $eiu_exit(S, penumqueryoutput)
dec $eiu_seek(pstate, penumqueryoutput, bool, nat) : pstate
def $eiu_seek(S, penumqueryoutput, b_entry, 0) = S
def $eiu_seek(S, penumqueryoutput, b_entry, n) = S
  -- if $(n > 0) /\ $eiu_at(S, penumqueryoutput, b_entry)
def $eiu_seek(S, penumqueryoutput, b_entry, n) = $eiu_seek($drive_steps(S[.COMPLETION = NORMAL], 1), penumqueryoutput, b_entry, $nabs($(n - 1)))
  -- if $(n > 0) /\ ~$eiu_at(S, penumqueryoutput, b_entry)
'''


def checked(row, label):
    base.OUT = OUT / label
    base.OUT.mkdir()
    try:
        return base.checked_source(row)
    finally:
        base.OUT = OUT


def reached(label, case_id, thrown=False):
    row = base.CASES['enum-is-callable-third-output-' + case_id]
    checks = [
        f'S_{label}_initial = ' + checked(row, label),
        f'S_{label}_initial.COMPLETION = BUDGET',
        f'S_{label}_invoke = $eic_seek(S_{label}_initial, 0, 3000)',
        f'$eic_front(S_{label}_invoke)',
        f'S_{label}_invoke.TODO = (CONFIG_INVOKE pconfigcall_{label}) :: ptask_{label}_tail*',
        f'$config_invoke_valid(S_{label}_invoke, pconfigcall_{label})',
        f'$enum_is_callable_output_capture(S_{label}_invoke, pconfigcall_{label}) = (penumqueryoutput_{label})',
        f'penumqueryoutput_{label}.CALL = pconfigcall_{label}',
        f'penumqueryoutput_{label}.NAME = $ptascii("FirstCheck::from")',
        f'penumqueryoutput_{label}.RESULT',
        f'$enum_is_callable_output_valid(S_{label}_invoke, penumqueryoutput_{label})',
        f'$enum_is_callable_ref_last(S_{label}_invoke, penumqueryoutput_{label}.CELL, pconfigcall_{label}.LINE)',
        f'$task_nodes(ENUM_IS_CALLABLE_OUTPUT penumqueryoutput_{label}) = $config_nodes(pconfigcall_{label})',
        f'$task_nodes(ENUM_IS_CALLABLE_OUTPUT penumqueryoutput_{label}) = [HCELL penumqueryoutput_{label}.CELL]',
        f'~((HOBJECT penumqueryoutput_{label}.OLD) <- $task_nodes(ENUM_IS_CALLABLE_OUTPUT penumqueryoutput_{label}))',
        f'~$call_task_valid(S_{label}_invoke, ENUM_IS_CALLABLE_CLEAR penumqueryoutput_{label})',
        f'S_{label}_clear = $drive_steps(S_{label}_invoke[.COMPLETION = NORMAL], 1)',
        f'S_{label}_clear.STORE[penumqueryoutput_{label}.CELL] = DEFINED PNULL',
        f'S_{label}_clear.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_{label}) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_{label}_initial) :: (ENUM_IS_CALLABLE_OUTPUT penumqueryoutput_{label}) :: ptask_{label}_tail*',
        f'pdestructionoperation_{label}_initial.SOURCE = ENUM_IS_CALLABLE_CLEAR penumqueryoutput_{label}',
        f'pdestructionoperation_{label}_initial.CELL = penumqueryoutput_{label}.CELL',
        f'pdestructionoperation_{label}_initial.VALUE = KNOWN (PBOOL true)',
        f'$eager_operation_source_guard(S_{label}_clear, pdestructionoperation_{label}_initial)',
        f'S_{label}_entry = $eiu_seek(S_{label}_clear, penumqueryoutput_{label}, true, 2000)',
        f'$eiu_entry(S_{label}_entry, penumqueryoutput_{label})',
        f'S_{label}_entry.TODO = (DESTRUCTOR_ENTER pdestructorcall_{label}) :: ptask_{label}_entry_tail*',
        f'pdestructorcall_{label}.OBJECT = penumqueryoutput_{label}.OLD',
        f'pdestructorcall_{label}.SITE = eps',
        f'penumqueryoutput_{label}.OLD <- S_{label}_entry.DESTRUCTION.CALLED',
        f'S_{label}_entry.STORE[penumqueryoutput_{label}.CELL] = DEFINED PNULL',
        f'S_{label}_exit = $eiu_seek(S_{label}_entry, penumqueryoutput_{label}, false, 5000)',
        f'$eiu_exit(S_{label}_exit, penumqueryoutput_{label})',
        f'S_{label}_exit.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_{label}) :: (ENUM_IS_CALLABLE_OUTPUT penumqueryoutput_{label}) :: ptask_{label}_tail*',
        f'$enum_is_callable_output_ready(S_{label}_exit, penumqueryoutput_{label})',
        f'$eager_operation_source_guard(S_{label}_exit, pdestructionoperation_{label})',
    ]
    if thrown:
        checks += [
            f'pdestructionoperation_{label}.PENDING = (n_{label}_exception)',
            f'$throwable_live(S_{label}_exit, n_{label}_exception)',
        ]
    else:
        checks += [f'pdestructionoperation_{label}.PENDING = eps']
    checks += [
        f'S_{label}_after = $drive_steps(S_{label}_exit[.COMPLETION = NORMAL], 1)',
        f'S_{label}_after.STORE[penumqueryoutput_{label}.CELL] = DEFINED (PSTRING penumqueryoutput_{label}.NAME)',
    ]
    if thrown:
        checks += [
            f'S_{label}_after.TODO = (THROW_SEARCH n_{label}_exception) :: ptask_{label}_tail*',
            f'S_{label}_after.RESULT = KNOWN PNULL',
            f'$throwable_live(S_{label}_after, n_{label}_exception)',
        ]
    else:
        checks += [
            f'S_{label}_after.TODO = ptask_{label}_tail*',
            f'S_{label}_after.RESULT = KNOWN (PBOOL true)',
        ]
    checks += [
        f'S_{label}_zero = $drive_steps(S_{label}_exit[.COMPLETION = NORMAL], 0)',
        f'S_{label}_zero.COMPLETION = BUDGET',
        f'$drive_steps(S_{label}_zero[.COMPLETION = NORMAL], 1) = S_{label}_after',
        f'S_{label}_done = $drive(S_{label}_after[.COMPLETION = NORMAL], 5000)',
        f'S_{label}_done.COMPLETION = NORMAL',
        f'$eic_output(S_{label}_done.EVENTS) = $ptascii(' + json.dumps(row['expected_normal_stdout']) + ')',
    ]
    return checks


if __name__ == '__main__':
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in WATCHED}
    checks = reached('normal', 'unique-null-then-assignment')
    checks += [
        'S_normal_exit.STORE[penumqueryoutput_normal.CELL] = DEFINED pvalue_rebound',
        '$string_bytes(pvalue_rebound) = ($ptascii("REBOUND"))',
        '$intrinsic_argument(S_normal_exit, pconfigcall_normal.SITE, 2) = ((expression_output, false, eps, porigin_output, z_output))',
        'S_origin = S_normal_exit[.ORIGIN = (porigin_output)]',
        '~$enum_is_callable_output_valid(S_origin, penumqueryoutput_normal)',
        '$enum_is_callable_output_scope(S_origin, pdestructionoperation_normal) = eps',
        '~$eager_operation_source_guard(S_origin, pdestructionoperation_normal)',
        'penumqueryoutput_depth = penumqueryoutput_normal[.DEPTH = $(penumqueryoutput_normal.DEPTH + 1)]',
        '~$enum_is_callable_output_valid(S_normal_exit, penumqueryoutput_depth)',
        'penumqueryoutput_name = penumqueryoutput_normal[.NAME = $ptascii("OtherCheck::from")]',
        '~$enum_is_callable_output_valid(S_normal_exit, penumqueryoutput_name)',
        'penumqueryoutput_result = penumqueryoutput_normal[.RESULT = false]',
        '~$enum_is_callable_output_valid(S_normal_exit, penumqueryoutput_result)',
        'penumqueryoutput_old = penumqueryoutput_normal[.OLD = |S_normal_exit.OBJECTS|]',
        '~$enum_is_callable_output_valid(S_normal_exit, penumqueryoutput_old)',
        'S_detached = S_normal_exit[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_normal) :: ptask_normal_tail*]',
        '$enum_is_callable_output_scope(S_detached, pdestructionoperation_normal) = eps',
        '~$eager_operation_source_guard(S_detached, pdestructionoperation_normal)',
        'pdestructionoperation_origin = pdestructionoperation_normal[.ORIGIN = (porigin_output)]',
        'S_operation_origin = S_normal_exit[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_origin) :: (ENUM_IS_CALLABLE_OUTPUT penumqueryoutput_normal) :: ptask_normal_tail*]',
        '~$eager_operation_source_guard(S_operation_origin, pdestructionoperation_origin)',
        'S_body = $drive_steps(S_normal_entry[.COMPLETION = NORMAL], 1)',
        'S_body.CURRENT = (pcallcontext_body)',
        'S_body.FRAMES = pframe_body :: eps',
        '$enum_is_callable_output_at(pframe_body.TODO, pdestructionoperation_normal_initial) = (penumqueryoutput_normal)',
        'S_frame_origin = S_body[.FRAMES = (pframe_body[.ORIGIN = (porigin_output)]) :: eps]',
        '$enum_is_callable_output_scope(S_frame_origin, pdestructionoperation_normal_initial) = eps',
        '~$eager_operation_source_guard(S_frame_origin, pdestructionoperation_normal_initial)',
        'pdestructionoperation_caller = pdestructionoperation_normal[.CALLER = (pcallcontext_body)]',
        'S_operation_caller = S_normal_exit[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_caller) :: (ENUM_IS_CALLABLE_OUTPUT penumqueryoutput_normal) :: ptask_normal_tail*]',
        '~$eager_operation_source_guard(S_operation_caller, pdestructionoperation_caller)',
        'S_caller = S_normal_exit[.CURRENT = (pcallcontext_body)]',
        '~$enum_is_callable_output_valid(S_caller, penumqueryoutput_normal)',
    ]
    checks += reached('thrown', 'unique-throw-after-assignment', thrown=True)
    checks += reached('rebind', 'unique-global-ref-rebind')
    checks += [
        '$lookup(S_rebind_exit.ENV, $ptascii("name")) = (n_new_cell)',
        '$lookup(S_rebind_exit.ENV, $ptascii("alias")) = (penumqueryoutput_rebind.CELL)',
        'n_new_cell =/= penumqueryoutput_rebind.CELL',
        'S_rebind_after.STORE[n_new_cell] = DEFINED pvalue_new',
        '$string_bytes(pvalue_new) = ($ptascii("OTHER"))',
    ]
    checks += reached('unset', 'unique-unset-output')
    checks += [
        '$lookup(S_unset_exit.ENV, $ptascii("name")) = eps',
        '(HCELL penumqueryoutput_unset.CELL) <- S_unset_exit.ALLOCATIONS',
        'penumqueryoutput_unset.CELL <- S_unset_exit.REFCELLS',
    ]
    checks += reached('resurrect', 'unique-resurrect-old')
    checks += [
        '$lookup(S_resurrect_exit.ENV, $ptascii("hold")) = (n_hold_cell)',
        'S_resurrect_exit.STORE[n_hold_cell] = DEFINED (POBJECT penumqueryoutput_resurrect.OLD)',
        '(HOBJECT penumqueryoutput_resurrect.OLD) <- S_resurrect_after.ALLOCATIONS',
        '~((HOBJECT penumqueryoutput_resurrect.OLD) <- S_resurrect_done.ALLOCATIONS)',
        'S_heap = S_resurrect_exit[.TODO = (ENUM_IS_CALLABLE_OUTPUT penumqueryoutput_resurrect) :: ptask_resurrect_tail*][.STORE = $set_cell(S_resurrect_exit.STORE, penumqueryoutput_resurrect.CELL, DEFINED (POBJECT penumqueryoutput_resurrect.OLD))]',
        '~$enum_is_callable_output_ready(S_heap, penumqueryoutput_resurrect)',
        'S_heap_after = $enum_is_callable_output_commit(S_heap, penumqueryoutput_resurrect)',
        'S_heap_after.COMPLETION = UNSUPPORTED "is_callable output rebound to owning value or new type source"',
        'S_heap_after.STORE = S_heap.STORE',
    ]
    fixture = OUT / 'output-unique.watsup'
    fixture.write_text(base.PREFIX + PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                       + ''.join('  -- if ' + check + '\n' for check in checks))
    command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
               *map(str, MODULES), str(fixture)]
    result = subprocess.run(command, capture_output=True, timeout=240)
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
