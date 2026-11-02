#!/usr/bin/env python3
"""Source-reached enum is_callable magic-handler selection guards."""
import hashlib
import json
from pathlib import Path
import subprocess

import enum_is_callable_protocol as base

ROOT, OUT, MODULES = base.ROOT, base.OUT, base.MODULES
WATCHED = [ROOT / 'spec/semantics/modules.json', ROOT / 'tests/semantics/enum_is_callable_cases.json',
           ROOT / 'tests/semantics/enum_is_callable_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_magic_protocol.py',
           ROOT / 'tests/semantics/profile.json',
           ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *MODULES]

if __name__ == '__main__':
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in WATCHED}
    row = base.CASES['enum-is-callable-magic-prefix']
    checks = [
        'S_initial = ' + base.checked_source(row),
        'S_initial.COMPLETION = BUDGET',
        'S_static = $eic_seek(S_initial, 0, 2000)',
        '$eic_front(S_static)',
        'S_static.TODO = (CONFIG_INVOKE pconfigcall_static) :: ptask_static_tail*',
        'pconfigcall_static.SENT = [NAMED_SENT (KNOWN pvalue_static)]',
        '$string_bytes(pvalue_static) = ($ptascii("QueryStaticMagic::from"))',
        '$enum_is_callable_target(S_static, pvalue_static) = ((porigin_static, ptbytes_static, false))',
        '$typed_callable(S_static, pvalue_static) = eps',
        '$effective_method(S_static, porigin_static, ptbytes_static, |S_static.CLASSES|) = eps',
        '$enum_generated_kind(S_static, porigin_static, ptbytes_static) = eps',
        '$effective_method(S_static, porigin_static, $ptascii("__callStatic"), |S_static.CLASSES|) = (pmethoddesc_static)',
        '$enum_magic_source(S_static, pmethoddesc_static, true)',
        '$enum_is_callable_magic(S_static, porigin_static, false) = (true)',
        '$config_invoke_valid(S_static, pconfigcall_static)',
        '$enum_is_callable_result(S_static, pvalue_static, false) = (true)',
        'S_static_after = $drive_steps(S_static[.COMPLETION = NORMAL], 1)',
        'S_static_after.RESULT = KNOWN (PBOOL true)',
        'S_static_after.TODO = ptask_static_tail*',
        'S_static_after.CLASSCONSTANTCACHE = S_static.CLASSCONSTANTCACHE',
        'S_case_no = $eic_seek(S_static_after, 1, 2000)',
        '$eic_front(S_case_no)',
        'S_case_no.TODO = (CONFIG_INVOKE pconfigcall_case_no) :: ptask_case_no_tail*',
        'pconfigcall_case_no.SENT = [NAMED_SENT (KNOWN (PARRAY n_case_no))]',
        '$enum_is_callable_target(S_case_no, PARRAY n_case_no) = ((porigin_case_no, ptbytes_case_no, true))',
        '$typed_callable(S_case_no, PARRAY n_case_no) = eps',
        '$effective_method(S_case_no, porigin_case_no, ptbytes_case_no, |S_case_no.CLASSES|) = eps',
        '$enum_generated_kind(S_case_no, porigin_case_no, ptbytes_case_no) = eps',
        '$array_magic(S_case_no, porigin_case_no)',
        '$enum_is_callable_magic(S_case_no, porigin_case_no, true) = (false)',
        '$config_invoke_valid(S_case_no, pconfigcall_case_no)',
        '$enum_is_callable_result(S_case_no, PARRAY n_case_no, false) = (false)',
        'S_case_no_after = $drive_steps(S_case_no[.COMPLETION = NORMAL], 1)',
        'S_case_no_after.RESULT = KNOWN (PBOOL false)',
        'S_instance = $eic_seek(S_case_no_after, 2, 2000)',
        '$eic_front(S_instance)',
        'S_instance.TODO = (CONFIG_INVOKE pconfigcall_instance) :: ptask_instance_tail*',
        'pconfigcall_instance.SENT = [NAMED_SENT (KNOWN (PARRAY n_instance))]',
        '$enum_is_callable_target(S_instance, PARRAY n_instance) = ((porigin_instance, ptbytes_instance, true))',
        '$typed_callable(S_instance, PARRAY n_instance) = eps',
        '$effective_method(S_instance, porigin_instance, ptbytes_instance, |S_instance.CLASSES|) = eps',
        '$enum_generated_kind(S_instance, porigin_instance, ptbytes_instance) = eps',
        '$effective_method(S_instance, porigin_instance, $ptascii("__call"), |S_instance.CLASSES|) = (pmethoddesc_instance)',
        '$enum_magic_source(S_instance, pmethoddesc_instance, false)',
        '$enum_is_callable_magic(S_instance, porigin_instance, true) = (true)',
        '$config_invoke_valid(S_instance, pconfigcall_instance)',
        '$enum_is_callable_result(S_instance, PARRAY n_instance, false) = (true)',
        'S_instance_after = $drive_steps(S_instance[.COMPLETION = NORMAL], 1)',
        'S_instance_after.RESULT = KNOWN (PBOOL true)',
        'S_instance_after.TODO = ptask_instance_tail*',
        'S_instance_after.CLASSCONSTANTCACHE = S_instance.CLASSCONSTANTCACHE',
        'S_zero = $drive_steps(S_instance_after, 0)',
        'S_zero.COMPLETION = BUDGET',
        'S_done = $drive(S_zero[.COMPLETION = NORMAL], 5000)',
        'S_done.COMPLETION = NORMAL',
        '$eic_output(S_done.EVENTS) = $ptascii("' + row['expected_normal_stdout'] + '")',
    ]
    fixture = OUT / 'magic.watsup'
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
