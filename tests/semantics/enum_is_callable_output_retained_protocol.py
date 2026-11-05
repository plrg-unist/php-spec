#!/usr/bin/env python3
"""Check a retained old output object at real is_callable CONFIG states."""
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
           ROOT / 'tests/semantics/enum_is_callable_output_retained_protocol.py',
           ROOT / 'tests/semantics/profile.json',
           ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *MODULES]

SEEK = r'''
dec $eiro_front(pstate) : bool
def $eiro_front(S) = true
  -- if S.TODO = (CONFIG_SEND pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_IS_CALLABLE /\ pconfigcall.INDEX = 2
def $eiro_front(S) = false -- otherwise
dec $eiro_seek(pstate, nat) : pstate
def $eiro_seek(S, 0) = S
def $eiro_seek(S, n) = S
  -- if $(n > 0) /\ $eiro_front(S)
def $eiro_seek(S, n) = $eiro_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if $(n > 0) /\ ~$eiro_front(S)
'''

if __name__ == '__main__':
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in WATCHED}
    retained = base.CASES['enum-is-callable-third-output-old-object-retained']
    unique = base.CASES['enum-is-callable-third-output-old-object-unsupported']
    base.OUT = OUT / 'retained-source'
    base.OUT.mkdir()
    retained_source = base.checked_source(retained)
    base.OUT = OUT / 'unique-source'
    base.OUT.mkdir()
    unique_source = base.checked_source(unique)
    base.OUT = OUT
    checks = [
        'S_ret_initial = ' + retained_source,
        'S_ret_initial.COMPLETION = BUDGET',
        'S_ret_send = $eiro_seek(S_ret_initial, 2000)',
        '$eiro_front(S_ret_send)',
        'S_ret_send.TODO = (CONFIG_SEND pconfigcall_ret_send) :: ptask_ret_tail*',
        'pconfigcall_ret_send.SENT = [NAMED_SENT (KNOWN pvalue_ret_input), NAMED_SENT (KNOWN (PBOOL false))]',
        '$enum_is_callable_ref_name(S_ret_send, pconfigcall_ret_send, pvalue_ret_input) = ($ptascii("HoldCheck::from"))',
        '$intrinsic_argument(S_ret_send, pconfigcall_ret_send.SITE, 2) = ((NExprVariable (BYTES text_ret_output) metadata_ret_output, false, eps, porigin_ret_output, z_ret_output))',
        '$reference_cv(NExprVariable (BYTES text_ret_output) metadata_ret_output) = (n_ret_name*)',
        '$lookup(S_ret_send.ENV, n_ret_name*) = (n_ret_cell)',
        '$lookup(S_ret_send.ENV, $ptascii("hold")) = (n_hold_cell)',
        'n_ret_cell =/= n_hold_cell',
        'S_ret_send.STORE[n_ret_cell] = DEFINED (POBJECT n_old)',
        'S_ret_send.STORE[n_hold_cell] = DEFINED (POBJECT n_old)',
        '(HOBJECT n_old) <- S_ret_send.ALLOCATIONS',
        'S_ret_send.OBJECTS[n_old] = INSTANCE porigin_old',
        '$node_children(S_ret_send, HOBJECT n_old) = eps',
        '$propref_at(S_ret_send.PROPREFS, n_ret_cell) = eps',
        '$reference_coercion_at(S_ret_send.REFCOERCIONS, n_ret_cell) = eps',
        '~$foreach_released_cell(S_ret_send, n_ret_cell)',
        '$enum_is_callable_ref_old(S_ret_send, n_ret_cell, POBJECT n_old, $ptascii("HoldCheck::from"), pconfigcall_ret_send.LINE)',
        '$enum_is_callable_ref_cell(S_ret_send, pconfigcall_ret_send, pvalue_ret_input) = (n_ret_cell)',
        'S_ret_preview = $write_cell_checked(S_ret_send, n_ret_cell, PSTRING $ptascii("HoldCheck::from"), pconfigcall_ret_send.LINE)',
        '$($heap_owners($heap_graph(S_ret_preview), HOBJECT n_old) > 0)',
        'S_nohold = S_ret_send[.STORE = $set_cell(S_ret_send.STORE, n_hold_cell, DEFINED PNULL)]',
        '~$enum_is_callable_ref_old(S_nohold, n_ret_cell, POBJECT n_old, $ptascii("HoldCheck::from"), pconfigcall_ret_send.LINE)',
        'S_dead = S_ret_send[.ALLOCATIONS = $destruction_node_delete(S_ret_send.ALLOCATIONS, HOBJECT n_old)]',
        '~$enum_is_callable_ref_old(S_dead, n_ret_cell, POBJECT n_old, $ptascii("HoldCheck::from"), pconfigcall_ret_send.LINE)',
        'S_ret_ref = $drive_steps(S_ret_send[.COMPLETION = NORMAL], 1)',
        'S_ret_ref.TODO = (CONFIG_ARGS pconfigcall_ret_ref) :: ptask_ret_tail*',
        'pconfigcall_ret_ref.SENT = [NAMED_SENT (KNOWN pvalue_ret_input), NAMED_SENT (KNOWN (PBOOL false)), NAMED_SENT (REFERENCE n_ret_cell)]',
        'n_ret_cell <- S_ret_ref.REFCELLS',
        'S_ret_ref.STORE[n_ret_cell] = S_ret_send.STORE[n_ret_cell]',
        'S_ret_invoke = $eic_seek(S_ret_ref, 0, 2000)',
        '$eic_front(S_ret_invoke)',
        'S_ret_invoke.TODO = (CONFIG_INVOKE pconfigcall_ret_invoke) :: ptask_ret_invoke_tail*',
        'pconfigcall_ret_invoke.SENT = pconfigcall_ret_ref.SENT',
        '$enum_is_callable_ref_slots_valid(S_ret_invoke, pconfigcall_ret_invoke)',
        '$config_invoke_valid(S_ret_invoke, pconfigcall_ret_invoke)',
        'S_ret_invoke.STORE[n_hold_cell] = DEFINED (POBJECT n_old)',
        'S_ret_after = $drive_steps(S_ret_invoke[.COMPLETION = NORMAL], 1)',
        'S_ret_after.STORE[n_ret_cell] = DEFINED (PSTRING $ptascii("HoldCheck::from"))',
        'S_ret_after.STORE[n_hold_cell] = DEFINED (POBJECT n_old)',
        '(HOBJECT n_old) <- S_ret_after.ALLOCATIONS',
        'S_ret_after.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_ret) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_ret) :: ptask_ret_invoke_tail*',
        'pdestructionrelease_ret.JOBS = [DESTRUCTION_VALUE (HOBJECT n_old), DESTRUCTION_VALUE (HCELL n_ret_cell)]',
        'pdestructionoperation_ret.SOURCE = CONFIG_INVOKE pconfigcall_ret_invoke',
        'pdestructionoperation_ret.VALUE = KNOWN (PBOOL true)',
        'S_ret_after.RESULT = KNOWN PNULL',
        'S_ret_after.EVENTS = S_ret_invoke.EVENTS',
        'S_ret_after.CLASSCONSTANTCACHE = S_ret_invoke.CLASSCONSTANTCACHE',
        'S_ret_restored = $drive_steps(S_ret_after[.COMPLETION = NORMAL], 4)',
        'S_ret_restored.TODO = ptask_ret_invoke_tail*',
        'S_ret_restored.RESULT = KNOWN (PBOOL true)',
        'S_ret_restored.EVENTS = S_ret_invoke.EVENTS',
        'S_ret_restored.STORE[n_hold_cell] = DEFINED (POBJECT n_old)',
        'S_ret_zero = $drive_steps(S_ret_after[.COMPLETION = NORMAL], 0)',
        'S_ret_zero.COMPLETION = BUDGET',
        '$drive_steps(S_ret_zero[.COMPLETION = NORMAL], 4) = S_ret_restored',
        'S_ret_done = $drive(S_ret_restored[.COMPLETION = NORMAL], 5000)',
        'S_ret_done.COMPLETION = NORMAL',
        '$eic_output(S_ret_done.EVENTS) = $ptascii("' + retained['expected_normal_stdout'] + '")',
        'S_unique_initial = ' + unique_source,
        'S_unique_initial.COMPLETION = BUDGET',
        'S_unique_send = $eiro_seek(S_unique_initial, 2000)',
        '$eiro_front(S_unique_send)',
        'S_unique_send.TODO = (CONFIG_SEND pconfigcall_unique) :: ptask_unique_tail*',
        'pconfigcall_unique.SENT = [NAMED_SENT (KNOWN pvalue_unique_input), NAMED_SENT (KNOWN (PBOOL false))]',
        '$intrinsic_argument(S_unique_send, pconfigcall_unique.SITE, 2) = ((NExprVariable (BYTES text_unique_output) metadata_unique_output, false, eps, porigin_unique_output, z_unique_output))',
        '$reference_cv(NExprVariable (BYTES text_unique_output) metadata_unique_output) = (n_unique_name*)',
        '$lookup(S_unique_send.ENV, n_unique_name*) = (n_unique_cell)',
        'S_unique_send.STORE[n_unique_cell] = DEFINED (POBJECT n_unique_old)',
        '(HOBJECT n_unique_old) <- S_unique_send.ALLOCATIONS',
        'S_unique_send.OBJECTS[n_unique_old] = INSTANCE porigin_unique_old',
        '$node_children(S_unique_send, HOBJECT n_unique_old) = eps',
        '$enum_is_callable_ref_old(S_unique_send, n_unique_cell, POBJECT n_unique_old, $ptascii("OldCheck::from"), pconfigcall_unique.LINE) = false',
        '$enum_is_callable_ref_cell(S_unique_send, pconfigcall_unique, pvalue_unique_input) = eps',
    ]
    fixture = OUT / 'output-retained.watsup'
    fixture.write_text(base.PREFIX + SEEK + '\ndec $main() : bool\ndef $main() = true\n'
                       + ''.join('  -- if ' + check + '\n' for check in checks))
    command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
               *map(str, MODULES), str(fixture)]
    result = subprocess.run(command, capture_output=True, timeout=120)
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
