#!/usr/bin/env python3
"""Source-reached distinct variable input for enum callable-name output."""
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
           ROOT / 'tests/semantics/enum_is_callable_output_variable_protocol.py',
           ROOT / 'tests/semantics/profile.json',
           ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *MODULES]

if __name__ == '__main__':
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in WATCHED}
    row = base.CASES['enum-is-callable-third-output-variable-separate']
    checks = [
        'S_initial = ' + base.checked_source(row),
        'S_initial.COMPLETION = BUDGET',
        'S_send = $eio_seek(S_initial, 2000)',
        '$eio_front(S_send)',
        'S_send.TODO = (CONFIG_SEND pconfigcall_send) :: ptask_send_tail*',
        'pconfigcall_send.SENT = [NAMED_SENT (KNOWN pvalue_input), NAMED_SENT (KNOWN (PBOOL false))]',
        '$intrinsic_argument(S_send, pconfigcall_send.SITE, 0) = ((NExprVariable (BYTES text_target) metadata_target, false, eps, porigin_target, z_target))',
        '$intrinsic_argument(S_send, pconfigcall_send.SITE, 1) = ((NExprConstFetch (NName (BYTES text_false) metadata_false_name) metadata_false, false, eps, porigin_false, z_false))',
        '$base64(text_false) = $ptascii("false")',
        '$reference_cv(NExprVariable (BYTES text_target) metadata_target) = (n_target_name*)',
        '$lookup(S_send.ENV, n_target_name*) = (n_target)',
        '(HCELL n_target) <- S_send.ALLOCATIONS',
        'S_send.STORE[n_target] = DEFINED pvalue_target',
        '$string_bytes(pvalue_input) = ($ptascii("DynamicCheck::from"))',
        '$string_bytes(pvalue_target) = ($ptascii("DynamicCheck::from"))',
        '$enum_is_callable_target(S_send, pvalue_input) = ((porigin_enum, ptbytes_method, false))',
        '$enum_is_callable_ref_name(S_send, pconfigcall_send, pvalue_input) = ($ptascii("DynamicCheck::from"))',
        '$enum_is_callable_ref_cell(S_send, pconfigcall_send, pvalue_input) = (n_output)',
        'n_target =/= n_output',
        'S_send.STORE[n_output] = DEFINED pvalue_old',
        '$string_bytes(pvalue_old) = ($ptascii("old"))',
        'S_ref = $drive_steps(S_send[.COMPLETION = NORMAL], 1)',
        'S_ref.TODO = (CONFIG_ARGS pconfigcall_ref) :: ptask_send_tail*',
        'pconfigcall_ref.SENT = [NAMED_SENT (KNOWN pvalue_input), NAMED_SENT (KNOWN (PBOOL false)), NAMED_SENT (REFERENCE n_output)]',
        'S_ref.STORE[n_target] = S_send.STORE[n_target]',
        'S_ref.STORE[n_output] = S_send.STORE[n_output]',
        'S_invoke = $eic_seek(S_ref, 0, 2000)',
        '$eic_front(S_invoke)',
        'S_invoke.TODO = (CONFIG_INVOKE pconfigcall_invoke) :: ptask_invoke_tail*',
        'pconfigcall_invoke.SENT = pconfigcall_ref.SENT',
        '$enum_is_callable_ref_slots_valid(S_invoke, pconfigcall_invoke)',
        '$config_invoke_valid(S_invoke, pconfigcall_invoke)',
        'S_rebound = S_invoke[.STORE = $set_cell(S_invoke.STORE, n_target, DEFINED (PSTRING $ptascii("OtherCheck::from")))]',
        '$enum_is_callable_ref_name(S_rebound, pconfigcall_invoke, pvalue_input) = eps',
        'S_after = $drive_steps(S_invoke[.COMPLETION = NORMAL], 1)',
        'S_after.STORE[n_output] = DEFINED (PSTRING $ptascii("DynamicCheck::from"))',
        'S_after.STORE[n_target] = S_invoke.STORE[n_target]',
        'S_after.RESULT = KNOWN (PBOOL true)',
        'S_after.TODO = ptask_invoke_tail*',
        'S_after.EVENTS = S_invoke.EVENTS',
        'S_after.CLASSCONSTANTCACHE = S_invoke.CLASSCONSTANTCACHE',
        'S_zero = $drive_steps(S_after, 0)',
        'S_zero.COMPLETION = BUDGET',
        'S_done = $drive(S_zero[.COMPLETION = NORMAL], 5000)',
        'S_done.COMPLETION = NORMAL',
        '$eic_output(S_done.EVENTS) = $ptascii("' + row['expected_normal_stdout'] + '")',
    ]
    fixture = OUT / 'output-variable.watsup'
    fixture.write_text(base.PREFIX + output.SEND_PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
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
