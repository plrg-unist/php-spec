#!/usr/bin/env python3
"""Source-reached callable-name write on false and syntax-only true."""
import hashlib
import json
import subprocess

import enum_is_callable_protocol as base

ROOT, OUT, MODULES = base.ROOT, base.OUT, base.MODULES
WATCHED = [ROOT / 'spec/semantics/modules.json',
           ROOT / 'tests/semantics/enum_is_callable_cases.json',
           ROOT / 'tests/semantics/enum_is_callable_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_output_false_protocol.py',
           ROOT / 'tests/semantics/profile.json',
           ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *MODULES]

if __name__ == '__main__':
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in WATCHED}
    row = base.CASES['enum-is-callable-third-output-false']
    checks = [
        'S_initial = ' + base.checked_source(row),
        'S_initial.COMPLETION = BUDGET',
        'S_false = $eic_seek(S_initial, 0, 2000)',
        '$eic_front(S_false)',
        'S_false.TODO = (CONFIG_INVOKE pconfigcall_false) :: ptask_false_tail*',
        'pconfigcall_false.SENT = [NAMED_SENT (KNOWN pvalue_missing), NAMED_SENT (KNOWN (PBOOL false)), NAMED_SENT (REFERENCE n_name)]',
        '(HCELL n_name) <- S_false.ALLOCATIONS',
        'n_name <- S_false.REFCELLS',
        '$enum_is_callable_ref_slots_valid(S_false, pconfigcall_false)',
        '$enum_is_callable_result(S_false, pvalue_missing, false) = (false)',
        '$config_invoke_valid(S_false, pconfigcall_false)',
        'S_false.STORE[n_name] = DEFINED pvalue_old',
        '$string_bytes(pvalue_old) = ($ptascii("old"))',
        'S_false_after = $drive_steps(S_false[.COMPLETION = NORMAL], 1)',
        'S_false_after.STORE[n_name] = DEFINED (PSTRING $ptascii("MissingCheck::missing"))',
        'S_false_after.RESULT = KNOWN (PBOOL false)',
        'S_false_after.TODO = ptask_false_tail*',
        'S_false_after.EVENTS = S_false.EVENTS',
        'S_false_after.CLASSCONSTANTCACHE = S_false.CLASSCONSTANTCACHE',
        'S_true = $eic_seek(S_false_after, 0, 2000)',
        '$eic_front(S_true)',
        'S_true.TODO = (CONFIG_INVOKE pconfigcall_true) :: ptask_true_tail*',
        'pconfigcall_true.SENT = [NAMED_SENT (KNOWN pvalue_missing), NAMED_SENT (KNOWN (PBOOL true)), NAMED_SENT (REFERENCE n_name)]',
        '$enum_is_callable_ref_slots_valid(S_true, pconfigcall_true)',
        '$enum_is_callable_result(S_true, pvalue_missing, true) = (true)',
        '$config_invoke_valid(S_true, pconfigcall_true)',
        'S_true.STORE[n_name] = DEFINED pvalue_reset',
        '$string_bytes(pvalue_reset) = ($ptascii("old"))',
        'S_true_after = $drive_steps(S_true[.COMPLETION = NORMAL], 1)',
        'S_true_after.STORE[n_name] = DEFINED (PSTRING $ptascii("MissingCheck::missing"))',
        'S_true_after.RESULT = KNOWN (PBOOL true)',
        'S_true_after.TODO = ptask_true_tail*',
        'S_true_after.EVENTS = S_true.EVENTS',
        'S_true_after.CLASSCONSTANTCACHE = S_true.CLASSCONSTANTCACHE',
        'S_zero = $drive_steps(S_true_after, 0)',
        'S_zero.COMPLETION = BUDGET',
        'S_done = $drive(S_zero[.COMPLETION = NORMAL], 5000)',
        'S_done.COMPLETION = NORMAL',
        '$eic_output(S_done.EVENTS) = $ptascii("' + row['expected_normal_stdout'] + '")',
    ]
    fixture = OUT / 'output-false.watsup'
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
              'stdout': result.stdout.decode(errors='replace'),
              'stderr': result.stderr.decode(errors='replace'),
              'stable': before == {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                   for path in WATCHED}, 'direct_inputs': before}
    (OUT / 'report.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k: record[k] for k in ['revision', 'checks', 'exit', 'stdout', 'stderr', 'stable']}), OUT, flush=True)
    assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr and record['stable'], OUT
