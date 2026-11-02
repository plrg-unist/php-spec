#!/usr/bin/env python3
"""Source-reached enum case-array user-method query guards."""
import hashlib
import json
from pathlib import Path
import subprocess

import enum_is_callable_protocol as base

ROOT, OUT, MODULES = base.ROOT, base.OUT, base.MODULES
WATCHED = [ROOT / 'spec/semantics/modules.json', ROOT / 'tests/semantics/enum_is_callable_cases.json',
           ROOT / 'tests/semantics/enum_is_callable_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_case_method_protocol.py',
           ROOT / 'tests/semantics/profile.json',
           ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *MODULES]

if __name__ == '__main__':
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in WATCHED}
    row = base.CASES['enum-is-callable-user-case-method']
    checks = [
        'S_initial = ' + base.checked_source(row),
        'S_initial.COMPLETION = BUDGET',
        'S_instance = $eic_seek(S_initial, 0, 2000)',
        '$eic_front(S_instance)',
        'S_instance.TODO = (CONFIG_INVOKE pconfigcall_instance) :: ptask_instance_tail*',
        'pconfigcall_instance.SENT = [NAMED_SENT (KNOWN (PARRAY n_instance))]',
        '$enum_is_callable_target(S_instance, PARRAY n_instance) = ((porigin_enum, ptbytes_instance, true))',
        'S_instance.ARRAYS[n_instance] = parray_instance',
        '$entry_lookup(parray_instance.ITEMS, KINT 0) = (pitem_case)',
        '$entry_value(S_instance, pitem_case) = POBJECT n_case',
        '(HOBJECT n_case) <- S_instance.ALLOCATIONS',
        'ptbytes_instance = $ptascii("ping")',
        '$typed_callable(S_instance, PARRAY n_instance) = eps',
        '$effective_method(S_instance, porigin_enum, ptbytes_instance, |S_instance.CLASSES|) = (pmethoddesc_instance)',
        'pmethoddesc_instance.OWNER = porigin_enum',
        'pmethoddesc_instance.VISIBILITY = PROPERTY_PUBLIC',
        '~pmethoddesc_instance.STATIC /\\ ~pmethoddesc_instance.ABSTRACT',
        '$enum_is_callable_case_user_method(S_instance, porigin_enum, ptbytes_instance)',
        '$enum_is_callable_result(S_instance, PARRAY n_instance, false) = (true)',
        '$config_invoke_valid(S_instance, pconfigcall_instance)',
        '$enum_is_callable_result(S_instance[.ALLOCATIONS = eps], PARRAY n_instance, false) = eps',
        'S_instance_after = $drive_steps(S_instance[.COMPLETION = NORMAL], 1)',
        'S_instance_after.RESULT = KNOWN (PBOOL true)',
        'S_instance_after.TODO = ptask_instance_tail*',
        'S_instance_after.EVENTS = S_instance.EVENTS',
        'S_instance_after.CLASSCONSTANTCACHE = S_instance.CLASSCONSTANTCACHE',
        'S_static = $eic_seek(S_instance_after, 2, 2000)',
        '$eic_front(S_static)',
        'S_static.TODO = (CONFIG_INVOKE pconfigcall_static) :: ptask_static_tail*',
        'pconfigcall_static.SENT = [NAMED_SENT (KNOWN (PARRAY n_static))]',
        '$enum_is_callable_target(S_static, PARRAY n_static) = ((porigin_enum_static, ptbytes_static, true))',
        'ptbytes_static = $ptascii("stat")',
        '$typed_callable(S_static, PARRAY n_static) = eps',
        '$effective_method(S_static, porigin_enum_static, ptbytes_static, |S_static.CLASSES|) = (pmethoddesc_static)',
        'pmethoddesc_static.OWNER = porigin_enum_static',
        'pmethoddesc_static.STATIC /\\ pmethoddesc_static.VISIBILITY = PROPERTY_PUBLIC',
        '$enum_is_callable_case_user_method(S_static, porigin_enum_static, ptbytes_static)',
        '$config_invoke_valid(S_static, pconfigcall_static)',
        '$enum_is_callable_result(S_static, PARRAY n_static, false) = (true)',
        'S_static_after = $drive_steps(S_static[.COMPLETION = NORMAL], 1)',
        'S_static_after.RESULT = KNOWN (PBOOL true)',
        'S_static_after.TODO = ptask_static_tail*',
        'S_static_after.EVENTS = S_static.EVENTS',
        'S_static_after.CLASSCONSTANTCACHE = S_static.CLASSCONSTANTCACHE',
        'S_zero = $drive_steps(S_static_after, 0)',
        'S_zero.COMPLETION = BUDGET',
        'S_done = $drive(S_zero[.COMPLETION = NORMAL], 5000)',
        'S_done.COMPLETION = NORMAL',
        '$eic_output(S_done.EVENTS) = $ptascii("' + row['expected_normal_stdout'] + '")',
    ]
    fixture = OUT / 'case-method.watsup'
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
