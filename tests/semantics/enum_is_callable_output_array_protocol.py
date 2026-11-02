#!/usr/bin/env python3
"""Source-reached class and enum-case array callable-name output."""
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
           ROOT / 'tests/semantics/enum_is_callable_output_array_protocol.py',
           ROOT / 'tests/semantics/profile.json',
           ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *MODULES]

if __name__ == '__main__':
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in WATCHED}
    row = base.CASES['enum-is-callable-third-output-array']
    checks = [
        'S_initial = ' + base.checked_source(row),
        'S_initial.COMPLETION = BUDGET',
        'S_class_send = $eio_seek(S_initial, 2000)',
        '$eio_front(S_class_send)',
        'S_class_send.TODO = (CONFIG_SEND pconfigcall_class_send) :: ptask_class_send_tail*',
        'pconfigcall_class_send.SENT = [NAMED_SENT (KNOWN (PARRAY n_class_array)), NAMED_SENT (KNOWN (PBOOL false))]',
        '(HARRAY n_class_array) <- S_class_send.ALLOCATIONS',
        'S_class_send.ARRAYS[n_class_array].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_class), ENTRY (KINT 1) (DIRECT pvalue_class_method)]',
        '$string_bytes(pvalue_class) = ($ptascii("ArrayCheck"))',
        '$string_bytes(pvalue_class_method) = ($ptascii("from"))',
        '$enum_is_callable_target(S_class_send, PARRAY n_class_array) = ((porigin_enum, ptbytes_from, false))',
        '$enum_is_callable_ref_name(S_class_send, pconfigcall_class_send, PARRAY n_class_array) = ($ptascii("ArrayCheck::from"))',
        '$enum_is_callable_ref_cell(S_class_send, pconfigcall_class_send, PARRAY n_class_array) = (n_output)',
        'S_class_ref = $drive_steps(S_class_send[.COMPLETION = NORMAL], 1)',
        'S_class_ref.TODO = (CONFIG_ARGS pconfigcall_class_ref) :: ptask_class_send_tail*',
        'pconfigcall_class_ref.SENT = [NAMED_SENT (KNOWN (PARRAY n_class_array)), NAMED_SENT (KNOWN (PBOOL false)), NAMED_SENT (REFERENCE n_output)]',
        'n_output <- S_class_ref.REFCELLS',
        'S_class_invoke = $eic_seek(S_class_ref, 0, 2000)',
        '$eic_front(S_class_invoke)',
        'S_class_invoke.TODO = (CONFIG_INVOKE pconfigcall_class_invoke) :: ptask_class_invoke_tail*',
        '(HARRAY n_class_array) <- S_class_invoke.ALLOCATIONS',
        'pconfigcall_class_invoke.SENT = pconfigcall_class_ref.SENT',
        '$enum_is_callable_ref_slots_valid(S_class_invoke, pconfigcall_class_invoke)',
        '$config_invoke_valid(S_class_invoke, pconfigcall_class_invoke)',
        'S_class_after = $drive_steps(S_class_invoke[.COMPLETION = NORMAL], 1)',
        'S_class_after.STORE[n_output] = DEFINED (PSTRING $ptascii("ArrayCheck::from"))',
        'S_class_after.RESULT = KNOWN (PBOOL true)',
        'S_class_after.TODO = ptask_class_invoke_tail*',
        'S_class_after.EVENTS = S_class_invoke.EVENTS',
        'S_class_after.CLASSCONSTANTCACHE = S_class_invoke.CLASSCONSTANTCACHE',
        'S_case_send = $eio_seek(S_class_after, 2000)',
        '$eio_front(S_case_send)',
        'S_case_send.TODO = (CONFIG_SEND pconfigcall_case_send) :: ptask_case_send_tail*',
        'pconfigcall_case_send.SENT = [NAMED_SENT (KNOWN (PARRAY n_case_array)), NAMED_SENT (KNOWN (PBOOL false))]',
        '(HARRAY n_case_array) <- S_case_send.ALLOCATIONS',
        'S_case_send.ARRAYS[n_case_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_case)), ENTRY (KINT 1) (DIRECT pvalue_case_method)]',
        '(HOBJECT n_case) <- S_case_send.ALLOCATIONS',
        '$enum_case_object(S_case_send, n_case) = (pclassconstantdesc)',
        'pclassconstantdesc.OWNER = porigin_enum',
        'pclassconstantdesc.NAME = $ptascii("A")',
        '$string_bytes(pvalue_case_method) = ($ptascii("tryFrom"))',
        '$enum_is_callable_target(S_case_send, PARRAY n_case_array) = ((porigin_enum, ptbytes_try, true))',
        '$enum_is_callable_ref_name(S_case_send, pconfigcall_case_send, PARRAY n_case_array) = ($ptascii("ArrayCheck::tryFrom"))',
        '$enum_is_callable_ref_cell(S_case_send, pconfigcall_case_send, PARRAY n_case_array) = (n_output)',
        'S_case_ref = $drive_steps(S_case_send[.COMPLETION = NORMAL], 1)',
        'S_case_ref.TODO = (CONFIG_ARGS pconfigcall_case_ref) :: ptask_case_send_tail*',
        'pconfigcall_case_ref.SENT = [NAMED_SENT (KNOWN (PARRAY n_case_array)), NAMED_SENT (KNOWN (PBOOL false)), NAMED_SENT (REFERENCE n_output)]',
        'S_case_invoke = $eic_seek(S_case_ref, 0, 2000)',
        '$eic_front(S_case_invoke)',
        'S_case_invoke.TODO = (CONFIG_INVOKE pconfigcall_case_invoke) :: ptask_case_invoke_tail*',
        '(HARRAY n_case_array) <- S_case_invoke.ALLOCATIONS',
        '(HOBJECT n_case) <- S_case_invoke.ALLOCATIONS',
        'pconfigcall_case_invoke.SENT = pconfigcall_case_ref.SENT',
        '$enum_is_callable_ref_slots_valid(S_case_invoke, pconfigcall_case_invoke)',
        '$config_invoke_valid(S_case_invoke, pconfigcall_case_invoke)',
        'S_case_after = $drive_steps(S_case_invoke[.COMPLETION = NORMAL], 1)',
        'S_case_after.STORE[n_output] = DEFINED (PSTRING $ptascii("ArrayCheck::tryFrom"))',
        'S_case_after.RESULT = KNOWN (PBOOL true)',
        'S_case_after.TODO = ptask_case_invoke_tail*',
        'S_case_after.EVENTS = S_case_invoke.EVENTS',
        'S_case_after.CLASSCONSTANTCACHE = S_case_invoke.CLASSCONSTANTCACHE',
        'S_zero = $drive_steps(S_case_after, 0)',
        'S_zero.COMPLETION = BUDGET',
        'S_done = $drive(S_zero[.COMPLETION = NORMAL], 5000)',
        'S_done.COMPLETION = NORMAL',
        '$eic_output(S_done.EVENTS) = $ptascii("' + row['expected_normal_stdout'] + '")',
    ]
    fixture = OUT / 'output-array.watsup'
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
