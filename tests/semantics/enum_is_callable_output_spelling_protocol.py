#!/usr/bin/env python3
"""Source-reached literal class-array callable-name spelling."""
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
           ROOT / 'tests/semantics/enum_is_callable_output_spelling_protocol.py',
           ROOT / 'tests/semantics/profile.json',
           ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *MODULES]

if __name__ == '__main__':
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in WATCHED}
    row = base.CASES['enum-is-callable-third-output-array-spelling']
    prefix, suffix = row['expected_normal_stdout'].split('\\', 1)
    expected = '$ptascii("' + prefix + '") ++ [92] ++ $ptascii("' + suffix + '")'
    checks = [
        'S_initial = ' + base.checked_source(row),
        'S_initial.COMPLETION = BUDGET',
        'S_lower_send = $eio_seek(S_initial, 2000)',
        '$eio_front(S_lower_send)',
        'S_lower_send.TODO = (CONFIG_SEND pconfigcall_lower_send) :: ptask_lower_send_tail*',
        'pconfigcall_lower_send.SENT = [NAMED_SENT (KNOWN (PARRAY n_lower_array)), NAMED_SENT (KNOWN (PBOOL false))]',
        '(HARRAY n_lower_array) <- S_lower_send.ALLOCATIONS',
        'S_lower_send.ARRAYS[n_lower_array].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_lower), ENTRY (KINT 1) (DIRECT pvalue_method)]',
        '$string_bytes(pvalue_lower) = ($ptascii("casespell"))',
        '$string_bytes(pvalue_method) = ($ptascii("FROM"))',
        '$enum_is_callable_target(S_lower_send, PARRAY n_lower_array) = ((porigin_enum, ptbytes_method, false))',
        '$enum_is_callable_ref_name(S_lower_send, pconfigcall_lower_send, PARRAY n_lower_array) = ($ptascii("casespell::FROM"))',
        '$enum_is_callable_ref_cell(S_lower_send, pconfigcall_lower_send, PARRAY n_lower_array) = (n_output)',
        'S_lower_ref = $drive_steps(S_lower_send[.COMPLETION = NORMAL], 1)',
        'S_lower_ref.TODO = (CONFIG_ARGS pconfigcall_lower_ref) :: ptask_lower_send_tail*',
        'pconfigcall_lower_ref.SENT = [NAMED_SENT (KNOWN (PARRAY n_lower_array)), NAMED_SENT (KNOWN (PBOOL false)), NAMED_SENT (REFERENCE n_output)]',
        'S_lower_ref.STORE[n_output] = S_lower_send.STORE[n_output]',
        'S_lower_invoke = $eic_seek(S_lower_ref, 0, 2000)',
        '$eic_front(S_lower_invoke)',
        'S_lower_invoke.TODO = (CONFIG_INVOKE pconfigcall_lower_invoke) :: ptask_lower_invoke_tail*',
        '(HARRAY n_lower_array) <- S_lower_invoke.ALLOCATIONS',
        'pconfigcall_lower_invoke.SENT = pconfigcall_lower_ref.SENT',
        '$enum_is_callable_ref_slots_valid(S_lower_invoke, pconfigcall_lower_invoke)',
        '$config_invoke_valid(S_lower_invoke, pconfigcall_lower_invoke)',
        'S_lower_after = $drive_steps(S_lower_invoke[.COMPLETION = NORMAL], 1)',
        'S_lower_after.STORE[n_output] = DEFINED (PSTRING $ptascii("casespell::FROM"))',
        'S_lower_after.RESULT = KNOWN (PBOOL true)',
        'S_lower_after.TODO = ptask_lower_invoke_tail*',
        'S_lower_after.EVENTS = S_lower_invoke.EVENTS',
        'S_lower_after.CLASSCONSTANTCACHE = S_lower_invoke.CLASSCONSTANTCACHE',
        'S_slash_send = $eio_seek(S_lower_after, 2000)',
        '$eio_front(S_slash_send)',
        'S_slash_send.TODO = (CONFIG_SEND pconfigcall_slash_send) :: ptask_slash_send_tail*',
        'pconfigcall_slash_send.SENT = [NAMED_SENT (KNOWN (PARRAY n_slash_array)), NAMED_SENT (KNOWN (PBOOL false))]',
        '(HARRAY n_slash_array) <- S_slash_send.ALLOCATIONS',
        'S_slash_send.ARRAYS[n_slash_array].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_slash), ENTRY (KINT 1) (DIRECT pvalue_slash_method)]',
        '$string_bytes(pvalue_slash) = ([92] ++ $ptascii("CaseSpell"))',
        '$string_bytes(pvalue_slash_method) = ($ptascii("FROM"))',
        '$enum_is_callable_target(S_slash_send, PARRAY n_slash_array) = ((porigin_enum, ptbytes_method, false))',
        '$enum_is_callable_ref_name(S_slash_send, pconfigcall_slash_send, PARRAY n_slash_array) = ([92] ++ $ptascii("CaseSpell::FROM"))',
        '$enum_is_callable_ref_cell(S_slash_send, pconfigcall_slash_send, PARRAY n_slash_array) = (n_output)',
        'S_slash_ref = $drive_steps(S_slash_send[.COMPLETION = NORMAL], 1)',
        'S_slash_ref.TODO = (CONFIG_ARGS pconfigcall_slash_ref) :: ptask_slash_send_tail*',
        'pconfigcall_slash_ref.SENT = [NAMED_SENT (KNOWN (PARRAY n_slash_array)), NAMED_SENT (KNOWN (PBOOL false)), NAMED_SENT (REFERENCE n_output)]',
        'S_slash_ref.STORE[n_output] = S_slash_send.STORE[n_output]',
        'S_slash_invoke = $eic_seek(S_slash_ref, 0, 2000)',
        '$eic_front(S_slash_invoke)',
        'S_slash_invoke.TODO = (CONFIG_INVOKE pconfigcall_slash_invoke) :: ptask_slash_invoke_tail*',
        '(HARRAY n_slash_array) <- S_slash_invoke.ALLOCATIONS',
        'pconfigcall_slash_invoke.SENT = pconfigcall_slash_ref.SENT',
        '$enum_is_callable_ref_slots_valid(S_slash_invoke, pconfigcall_slash_invoke)',
        '$config_invoke_valid(S_slash_invoke, pconfigcall_slash_invoke)',
        'S_slash_after = $drive_steps(S_slash_invoke[.COMPLETION = NORMAL], 1)',
        'S_slash_after.STORE[n_output] = DEFINED pvalue_output',
        '$string_bytes(pvalue_output) = ([92] ++ $ptascii("CaseSpell::FROM"))',
        'S_slash_after.RESULT = KNOWN (PBOOL true)',
        'S_slash_after.TODO = ptask_slash_invoke_tail*',
        'S_slash_after.EVENTS = S_slash_invoke.EVENTS',
        'S_slash_after.CLASSCONSTANTCACHE = S_slash_invoke.CLASSCONSTANTCACHE',
        'S_zero = $drive_steps(S_slash_after, 0)',
        'S_zero.COMPLETION = BUDGET',
        'S_done = $drive(S_zero[.COMPLETION = NORMAL], 5000)',
        'S_done.COMPLETION = NORMAL',
        '$eic_output(S_done.EVENTS) = (' + expected + ')',
    ]
    fixture = OUT / 'output-spelling.watsup'
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
