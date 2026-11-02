#!/usr/bin/env python3
"""Source-reached third-output replacement of initialized scalar CVs."""
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
           ROOT / 'tests/semantics/enum_is_callable_output_scalar_protocol.py',
           ROOT / 'tests/semantics/profile.json',
           ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *MODULES]

if __name__ == '__main__':
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in WATCHED}
    row = base.CASES['enum-is-callable-third-output-old-scalars']
    checks = ['S_initial = ' + base.checked_source(row),
              'S_initial.COMPLETION = BUDGET']
    previous = 'S_initial'
    for tag, old in [('int', 'PINT 42'), ('bool', 'PBOOL false'), ('null', 'PNULL')]:
        send, ref, invoke, after = (f'S_{tag}_{stage}' for stage in ('send', 'ref', 'invoke', 'after'))
        call_send, call_ref, call_invoke = (f'pconfigcall_{tag}_{stage}'
                                           for stage in ('send', 'ref', 'invoke'))
        task_send, task_invoke = (f'ptask_{tag}_{stage}_tail*'
                                  for stage in ('send', 'invoke'))
        checks.extend([
            f'{send} = $eio_seek({previous}, 2000)',
            f'$eio_front({send})',
            f'{send}.TODO = (CONFIG_SEND {call_send}) :: {task_send}',
            f'{call_send}.SENT = [NAMED_SENT (KNOWN pvalue_{tag}_input), NAMED_SENT (KNOWN (PBOOL false))]',
            f'$string_bytes(pvalue_{tag}_input) = ($ptascii("ScalarCheck::from"))',
            f'$enum_is_callable_ref_cell({send}, {call_send}, pvalue_{tag}_input) = (n_output)',
            f'{send}.STORE[n_output] = DEFINED ({old})' if old != 'PNULL' else
            f'{send}.STORE[n_output] = DEFINED PNULL',
            f'$value_nodes({old}) = eps',
            f'{ref} = $drive_steps({send}[.COMPLETION = NORMAL], 1)',
            f'{ref}.TODO = (CONFIG_ARGS {call_ref}) :: {task_send}',
            f'{call_ref}.SENT = [NAMED_SENT (KNOWN pvalue_{tag}_input), NAMED_SENT (KNOWN (PBOOL false)), NAMED_SENT (REFERENCE n_output)]',
            f'{ref}.STORE[n_output] = {send}.STORE[n_output]',
            f'{invoke} = $eic_seek({ref}, 0, 2000)',
            f'$eic_front({invoke})',
            f'{invoke}.TODO = (CONFIG_INVOKE {call_invoke}) :: {task_invoke}',
            f'{call_invoke}.SENT = {call_ref}.SENT',
            f'$enum_is_callable_ref_slots_valid({invoke}, {call_invoke})',
            f'$config_invoke_valid({invoke}, {call_invoke})',
            f'{after} = $drive_steps({invoke}[.COMPLETION = NORMAL], 1)',
            f'{after}.STORE[n_output] = DEFINED (PSTRING $ptascii("ScalarCheck::from"))',
            f'{after}.RESULT = KNOWN (PBOOL true)',
            f'{after}.TODO = {task_invoke}',
            f'{after}.EVENTS = {invoke}.EVENTS',
            f'{after}.CLASSCONSTANTCACHE = {invoke}.CLASSCONSTANTCACHE',
        ])
        previous = after
    checks.extend([
        'S_zero = $drive_steps(S_null_after, 0)',
        'S_zero.COMPLETION = BUDGET',
        'S_done = $drive(S_zero[.COMPLETION = NORMAL], 5000)',
        'S_done.COMPLETION = NORMAL',
        '$eic_output(S_done.EVENTS) = $ptascii("' + row['expected_normal_stdout'] + '")',
    ])
    fixture = OUT / 'output-old-scalars.watsup'
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
