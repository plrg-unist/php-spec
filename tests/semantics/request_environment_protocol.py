#!/usr/bin/env python3
"""Primitive admissibility and autoglobal callback replacement controls."""
from pathlib import Path
import json
import subprocess
import tempfile

import static_types as t
import destructuring as d

ROOT = Path(__file__).resolve().parents[2]


def main():
    before = t.syntax_validation.implementation_fingerprint()
    out = Path(tempfile.mkdtemp(prefix='request-protocol-', dir=ROOT / '.tools'))
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    request = ('{ ENV ([([70,73,82,83,84], [111,110,101])]), ARGV ([[120]]), '
               'FILE ([120]), SECONDS 0, MICROSECONDS 0, '
               'VARIABLES ([69,71,80,67,83]), JIT true, CWD eps }')
    invalid = [
        '[.ENV = [([256], eps)]]', '[.ENV = [([65], [256])]]',
        '[.ENV = [([0], eps)]]', '[.ENV = [([65], [0])]]',
        '[.ENV = [([61], eps)]]', '[.ARGV = eps]', '[.ARGV = [[121]]]',
        '[.ARGV = [[120], [0]]]', '[.ARGV = [[120], [256]]]',
        '[.FILE = eps]', '[.FILE = [0]]', '[.FILE = [256]]',
        '[.SECONDS = -9223372036854775809]', '[.SECONDS = 9223372036854775808]',
        '[.MICROSECONDS = 1000000]', '[.VARIABLES = eps]',
        '[.VARIABLES = [0]]', '[.VARIABLES = [256]]',
        '[.CWD = (eps)]', '[.CWD = ([0])]', '[.CWD = ([256])]',
    ]
    valid = [
        '', '[.ENV = [(eps, eps), ([76,68,95,80,82,69,76,79,65,68], [61,255]), ([65], [9]), ([65], eps)]]',
        '[.ARGV = [[120], eps, [255]]]',
        '[.SECONDS = -9223372036854775808][.MICROSECONDS = 999999]',
        '[.SECONDS = 9223372036854775807]', '[.CWD = ([47,255])]',
    ]
    checks = ['Q = ' + request]
    checks += ['$request_valid(Q' + edit + ')' for edit in valid]
    checks += ['~$request_valid(Q' + edit + ')' for edit in invalid]
    checks += ['$php_request_run(PROGRAM eps, 1, "eA==", Q' + edit +
               ') = $initial_state(UNSUPPORTED "invalid request primitive facts")' for edit in invalid]
    for i, raw_name in enumerate((b'_ENV', b'_REQUEST')):
        name = d.byte_sequence(raw_name)
        checks += [
            f'S_before{i} = $bind_reference($acquire_name($write_name($request_bootstrap($initial_state(NORMAL), Q), {name}, PINT 7), {name}), [114])',
            f'$lookup(S_before{i}.ENV, [114]) = (n_old{i})',
            f'$lookup(S_before{i}.ENV, {name}) = (n_old{i})',
            f'S_after{i} = $request_activate(S_before{i}, {name})',
            f'S_after{i}.COMPLETION = NORMAL',
            f'$lookup(S_after{i}.ENV, [114]) = (n_old{i})',
            f'S_after{i}.STORE[n_old{i}] = DEFINED (PINT 7)',
            f'$lookup(S_after{i}.ENV, {name}) = (n_new{i})',
            f'n_old{i} =/= n_new{i}',
            f'S_after{i}.CELL = n_new{i}',
            f'S_after{i}.STORE[n_new{i}] = DEFINED (PARRAY n_array{i})',
            f'S_after{i}.SYMBOLS = S_before{i}.SYMBOLS',
            f'$request_activate(S_after{i}, {name}) = S_after{i}',
            f'$heap_valid($heap_graph(S_after{i}))',
            (f'S_after{i}.HTTPROOTS = S_before{i}.HTTPROOTS ++ [({name}, PARRAY n_array{i})]'
             if i == 0 else f'S_after{i}.HTTPROOTS = S_before{i}.HTTPROOTS'),
        ]
    fixture = out / 'checks.watsup'
    fixture.write_text('dec $main() : bool\ndef $main() = true\n' +
                       ''.join('  -- if ' + check + '\n' for check in checks))
    (out / 'originals.json').write_text(json.dumps({
        'fingerprint': before, 'checks': checks, 'fixture': str(fixture),
        'scope': 'Pure protocol and later-activation state checks; eval source execution remains separate.'
    }, indent=2) + '\n')
    run = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                          *[str(ROOT / module) for module in modules], str(fixture)],
                         capture_output=True, text=True, timeout=120)
    assert before == t.syntax_validation.implementation_fingerprint()
    report = {'fingerprint': before, 'assertions': len(checks), 'fixture': str(fixture),
              'status': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr,
              'result': 'pass' if run.returncode == 0 and run.stdout.strip() == 'true' else 'fail'}
    (out / 'results.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'], run.stderr)
    if report['result'] == 'pass':
        (ROOT / 'coverage/semantics/request-environment-protocol.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
