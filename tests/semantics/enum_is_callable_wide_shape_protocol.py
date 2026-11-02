#!/usr/bin/env python3
"""Source-reached array shape precheck for is_callable."""
import hashlib
import json
from pathlib import Path
import subprocess

import enum_is_callable_protocol as base

ROOT, OUT, MODULES = base.ROOT, base.OUT, base.MODULES
WATCHED = [ROOT / 'spec/semantics/modules.json', ROOT / 'tests/semantics/enum_is_callable_cases.json',
           ROOT / 'tests/semantics/enum_is_callable_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_wide_shape_protocol.py',
           ROOT / 'tests/semantics/profile.json',
           ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *MODULES]

if __name__ == '__main__':
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in WATCHED}
    row = base.CASES['enum-is-callable-wide-shape']
    checks = [
        'S_initial = ' + base.checked_source(row),
        'S_initial.COMPLETION = BUDGET',
        'S_missing = $eic_seek(S_initial, 0, 2000)',
        '$eic_front(S_missing)',
        'S_missing.TODO = (CONFIG_INVOKE pconfigcall_missing) :: ptask_missing_tail*',
        'pconfigcall_missing.SENT = [NAMED_SENT (KNOWN (PARRAY n_missing)), NAMED_SENT (KNOWN (PBOOL true))]',
        '(HARRAY n_missing) <- S_missing.ALLOCATIONS',
        '$array_shape_error(S_missing, n_missing) = ($ptascii("Array callback has to contain indices 0 and 1"))',
        '$enum_is_callable_target(S_missing, PARRAY n_missing) = eps',
        '$enum_is_callable_result(S_missing, PARRAY n_missing, true) = (false)',
        '$enum_is_callable_result(S_missing, PARRAY n_missing, false) = (false)',
        '$config_invoke_valid(S_missing, pconfigcall_missing)',
        'S_missing_after = $drive_steps(S_missing[.COMPLETION = NORMAL], 1)',
        'S_missing_after.RESULT = KNOWN (PBOOL false)',
        'S_missing_after.TODO = ptask_missing_tail*',
        'S_missing_after.EVENTS = S_missing.EVENTS',
        'S_missing_after.CLASSCONSTANTCACHE = S_missing.CLASSCONSTANTCACHE',
        'S_nonclass = $eic_seek(S_missing_after, 1, 2000)',
        '$eic_front(S_nonclass)',
        'S_nonclass.TODO = (CONFIG_INVOKE pconfigcall_nonclass) :: ptask_nonclass_tail*',
        'pconfigcall_nonclass.SENT = [NAMED_SENT (KNOWN (PARRAY n_nonclass)), NAMED_SENT (KNOWN (PBOOL true))]',
        '(HARRAY n_nonclass) <- S_nonclass.ALLOCATIONS',
        '$array_shape_error(S_nonclass, n_nonclass) = ($ptascii("First array member is not a valid class name or object"))',
        '$enum_is_callable_target(S_nonclass, PARRAY n_nonclass) = eps',
        '$enum_is_callable_result(S_nonclass, PARRAY n_nonclass, true) = (false)',
        '$enum_is_callable_result(S_nonclass, PARRAY n_nonclass, false) = (false)',
        '$config_invoke_valid(S_nonclass, pconfigcall_nonclass)',
        'S_nonclass_after = $drive_steps(S_nonclass[.COMPLETION = NORMAL], 1)',
        'S_nonclass_after.RESULT = KNOWN (PBOOL false)',
        'S_nonclass_after.TODO = ptask_nonclass_tail*',
        'S_nonclass_after.EVENTS = S_nonclass.EVENTS',
        'S_nonclass_after.CLASSCONSTANTCACHE = S_nonclass.CLASSCONSTANTCACHE',
        'S_reordered = $eic_seek(S_nonclass_after, 1, 2000)',
        '$eic_front(S_reordered)',
        'S_reordered.TODO = (CONFIG_INVOKE pconfigcall_reordered) :: ptask_reordered_tail*',
        'pconfigcall_reordered.SENT = [NAMED_SENT (KNOWN (PARRAY n_reordered)), NAMED_SENT (KNOWN (PBOOL true))]',
        '$array_shape_error(S_reordered, n_reordered) = eps',
        '$enum_is_callable_target(S_reordered, PARRAY n_reordered) = ((porigin_enum, ptbytes_method, false))',
        'ptbytes_method = $ptascii("cases")',
        '$enum_is_callable_result(S_reordered, PARRAY n_reordered, true) = (true)',
        '$config_invoke_valid(S_reordered, pconfigcall_reordered)',
        'S_zero = $drive_steps(S_reordered, 0)',
        'S_zero.COMPLETION = BUDGET',
        'S_done = $drive(S_zero[.COMPLETION = NORMAL], 5000)',
        'S_done.COMPLETION = NORMAL',
        '$eic_output(S_done.EVENTS) = $ptascii("' + row['expected_normal_stdout'] + '")',
    ]
    fixture = OUT / 'wide-shape.watsup'
    fixture.write_text(base.PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                       + ''.join('  -- if ' + check + '\n' for check in checks))
    command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
               *map(str, MODULES), str(fixture)]
    result = subprocess.run(command, capture_output=True, timeout=120)
    (OUT / 'command.json').write_text(json.dumps(command) + '\n')
    (OUT / 'stdout').write_bytes(result.stdout)
    (OUT / 'stderr').write_bytes(result.stderr)
    record = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'checks': len(checks), 'exit': result.returncode,
              'stdout': result.stdout.decode(errors='replace'), 'stderr': result.stderr.decode(errors='replace'),
              'stable': before == {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                   for path in WATCHED}, 'direct_inputs': before}
    (OUT / 'report.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k: record[k] for k in ['revision', 'checks', 'exit', 'stdout', 'stderr', 'stable']}), OUT, flush=True)
    assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr and record['stable'], OUT
