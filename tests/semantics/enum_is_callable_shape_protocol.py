#!/usr/bin/env python3
"""Source-reached malformed enum array query guards."""
import hashlib
import json
from pathlib import Path
import subprocess

import enum_is_callable_protocol as base

ROOT, OUT, MODULES = base.ROOT, base.OUT, base.MODULES
WATCHED = [ROOT / 'spec/semantics/modules.json', ROOT / 'tests/semantics/enum_is_callable_cases.json',
           ROOT / 'tests/semantics/enum_is_callable_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_shape_protocol.py',
           ROOT / 'tests/semantics/profile.json',
           ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *MODULES]

if __name__ == '__main__':
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in WATCHED}
    row = base.CASES['enum-is-callable-published-malformed-arrays']
    checks = [
        'S_initial = ' + base.checked_source(row),
        'S_initial.COMPLETION = BUDGET',
        'S_short = $eic_seek(S_initial, 2, 2000)',
        '$eic_front(S_short)',
        'S_short.TODO = (CONFIG_INVOKE pconfigcall_short) :: ptask_tail*',
        'pconfigcall_short.SENT = [NAMED_SENT (KNOWN (PARRAY n_array)), NAMED_SENT (KNOWN (PBOOL true))]',
        '$config_invoke_valid(S_short, pconfigcall_short)',
        '$(n_array < |S_short.ARRAYS|) /\\ (HARRAY n_array) <- S_short.ALLOCATIONS',
        'S_short.ARRAYS[n_array] = parray',
        '$entry_lookup(parray.ITEMS, KINT 0) = (pitem_receiver)',
        '$enum_is_callable_receiver(S_short, $entry_value(S_short, pitem_receiver)) = ((porigin_enum, false))',
        '~$typed_callback_array(S_short, n_array)',
        '$enum_is_callable_result(S_short, PARRAY n_array, true) = (false)',
        '$enum_is_callable_result(S_short, PARRAY n_array, false) = (false)',
        '$enum_is_callable_result(S_short[.ALLOCATIONS = eps], PARRAY n_array, true) = eps',
        'S_after = $drive_steps(S_short[.COMPLETION = NORMAL], 1)',
        'S_after.RESULT = KNOWN (PBOOL false)',
        'S_after.CLASSCONSTANTCACHE = S_short.CLASSCONSTANTCACHE',
        'S_zero = $drive_steps(S_after, 0)',
        'S_zero.COMPLETION = BUDGET',
        'S_done = $drive(S_zero[.COMPLETION = NORMAL], 5000)',
        'S_done.COMPLETION = NORMAL',
        '$eic_output(S_done.EVENTS) = $ptascii("' + row['expected_normal_stdout'] + '")',
    ]
    fixture = OUT / 'shape.watsup'
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
