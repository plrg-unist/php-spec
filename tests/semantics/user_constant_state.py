#!/usr/bin/env python3
"""Suspended source calls preserve owning values, frames and error cleanup."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile
import destructuring as d
import foreach as f
import user_constants
import function_scope as scope
import request_environment as q
import request_environment_state as rs
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SELECTION = ['ordered-declarations','line-name-before-division','deferred-key-nested-array']

PREFIX = d.PREFIX + f.PREFIX + r'''
dec $call_saved_tasks(pframe*) : ptask*
def $call_saved_tasks(eps) = eps
def $call_saved_tasks(pframe :: pframe_tail*) = pframe.TODO ++ $call_saved_tasks(pframe_tail*)
dec $call_saved_valid(pstate, pframe*) : bool
def $call_saved_valid(S, eps) = true
def $call_saved_valid(S, [pframe]) = (pframe.LOCALS = eps /\ pframe.CONTEXT = eps /\ $foreach_origin_valid(S, pframe.ORIGIN))
def $call_saved_valid(S, pframe :: pframe_tail*) = (pframe.LOCALS =/= eps /\ pframe.CONTEXT =/= eps /\ $foreach_origin_valid(S, pframe.ORIGIN) /\ $call_saved_valid(S, pframe_tail*))
  -- if pframe_tail* =/= eps
dec $call_valid(pstate) : bool
def $call_valid(S) = ($foreach_valid(S[.TODO = S.TODO ++ $call_saved_tasks(S.FRAMES)]) /\ $call_saved_valid(S, S.FRAMES) /\ ((S.FRAMES = eps) = (S.GLOBALTABLE = eps)) /\ ((S.FRAMES = eps) = (S.CURRENT = eps)))
'''


def main():
    before = q.t.syntax_validation.implementation_fingerprint()
    out = Path(tempfile.mkdtemp(prefix='user-constant-state-', dir=ROOT / '.tools'))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    inputs = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in [*modules, runner, Path(__file__), ROOT / 'tests/semantics/recorded_worker.py']}
    (out / 'inputs.json').write_text(json.dumps({'closure': before, 'direct': inputs}, indent=2))
    for name in inputs:
        target = out / 'original-inputs' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / name).read_bytes())
    frontend = Worker([str(q.t.PHP), '-n', *q.t.FLAGS, '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend-wire')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter-wire')
    records = []
    try:
        for name in SELECTION:
            directory = out / name
            directory.mkdir()
            source = user_constants.CASES[name]
            path = directory / 'source.php'
            path.write_bytes(source)
            payload = directory / 'request.input'
            payload.write_bytes(q.packet(1700000000, 125000, [b'LC_ALL=C', b'TZ=UTC', b'FIRST=one']))
            request = {'env': [[q.b64(k), q.b64(v)] for k, v in [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one')]],
                       'argv': [q.b64(bytes(path))], 'file': q.b64(bytes(path)), 'seconds': '1700000000',
                       'microseconds': 125000, 'variables': q.b64(b'EGPCS'), 'jit': True, 'cwd': q.b64(bytes(directory))}
            native = scope.native(path, payload, directory)
            parsed = frontend.request({'op': 'parse', 'source': q.b64(source)})
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            result = adapter.request({'op': 'execute', 'ast': parsed['ast'], 'steps': 10000,
                                      'filename': q.b64(bytes(path)), 'request': request})
            actual = q.cli.observe(result['state'], str(path))
            row = {'id': name, 'source_base64': q.b64(source), 'request': request, 'native': native, 'actual': actual}
            records.append(row)
            (directory / 'checked.json').write_text(json.dumps(checked))
            (directory / 'state.json').write_text(json.dumps(result))
            (out / 'originals.json').write_text(json.dumps(records, indent=2))
            assert actual['status'] in ('normal', 'php_error') and all(actual[k] == native[k] for k in ('stdout', 'stderr', 'exit_status')), row
            initial = '$php_request_run(' + checked['fixture'] + ', 0, ' + json.dumps(q.b64(bytes(path))) + ', ' + rs.request_fixture(request) + ')'
            completion = 'NORMAL'
            if name == 'line-name-before-division':
                completion = 'THROWN "DivisionByZeroError" ([68,105,118,105,115,105,111,110,32,98,121,32,122,101,114,111]) 3'
            checks = ['S_initial = ' + initial, 'S_initial.COMPLETION = BUDGET', 'S = S_initial[.COMPLETION = NORMAL]',
                      'S_out = $drive(S, 10000)', 'S_out.COMPLETION = ' + completion,
                      '$outputs(S_out.EVENTS) = ' + d.byte_sequence(base64.b64decode(native['stdout'])),
                      'S_out.FRAMES = eps', 'S_out.CURRENT = eps', 'S_out.GLOBALTABLE = eps',
                      'S_out.ITERATORS = eps', 'S_out.HELD = eps', 'S_out.TODO = eps',
                      '$heap_valid($heap_graph(S_out))', '$call_valid(S_out)', 'S_out.CONSTCONTEXT = eps', '$call_descriptors_valid(S_out)']
            if name == 'ordered-declarations':
                checks += ['$user_constant_at(S_out.USERCONSTANTS, [65]) = (puserconstant_a)', 'puserconstant_a.VALUE = PINT 1', '$user_constant_at(S_out.USERCONSTANTS, [66]) = (puserconstant_b)', 'puserconstant_b.VALUE = PINT 2', '|S_out.USERCONSTANTS| = 2']
            if name == 'line-name-before-division':
                checks += ['$user_constant_at(S_out.USERCONSTANTS, [65]) = (puserconstant_a)', 'puserconstant_a.VALUE = PINT 1', '|S_out.USERCONSTANTS| = 1', 'S_out.ALLOCATIONS = S.ALLOCATIONS']
            if name == 'deferred-key-nested-array':
                checks += ['$user_constant_at(S_out.USERCONSTANTS, [67]) = (puserconstant_c)', 'puserconstant_c.VALUE = PARRAY n_c', '$entry_lookup(S_out.ARRAYS[n_c].ITEMS, KSTRING ([120])) = (DIRECT (PARRAY n_x))', '$entry_lookup(S_out.ARRAYS[n_x].ITEMS, KINT 0) = (DIRECT (PINT 1))', '$entry_lookup(S_out.ARRAYS[n_c].ITEMS, KSTRING ([121])) = (DIRECT (PARRAY n_y))', '$entry_lookup(S_out.ARRAYS[n_y].ITEMS, KINT 0) = (DIRECT (PINT 2))', '|S_out.USERCONSTANTS| = 2', 'puserconstant_c.CLASS = PVARRAY false ([(KSTRING ([120]), PVARRAY false ([(KINT 0, PVSCALAR)])), (KSTRING ([121]), PVARRAY false ([(KINT 0, PVSCALAR)]))])']
            for budget in [*range(33), 64, 128]:
                checks += [f'S_b{budget} = $drive(S, {budget})',
                           f'$resume_destructuring(S_b{budget}, 1) = $drive(S, {budget + 1})',
                           f'$heap_valid($heap_graph(S_b{budget}))', f'$call_valid(S_b{budget})',
                           f'$call_descriptors_valid(S_b{budget})', f'S_b{budget}.REQUEST = S.REQUEST', f'S_b{budget}.HTTPROOTS = S.HTTPROOTS']
            checks += [f'$resume_destructuring(S_b{budget}, 10000) = S_out' for budget in (0, 1, 7, 16, 32, 64, 128)]
            fixture = directory / 'state.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
            row.update({'assertions': len(checks), 'fixture': str(fixture)})
    finally:
        try:
            frontend.close()
        finally:
            adapter.close()
    print(out, flush=True)
    for row in records:
        directory = out / row['id']
        command = [str(runner), *map(str, modules), row['fixture']]
        (directory / 'runner.command.json').write_text(json.dumps(command))
        try:
            result = subprocess.run(command, capture_output=True, timeout=300)
        except subprocess.TimeoutExpired as error:
            (directory / 'runner.stdout').write_bytes(error.stdout or b'')
            (directory / 'runner.stderr').write_bytes(error.stderr or b'')
            (directory / 'runner.status.json').write_text(json.dumps({'status': 'timeout', 'seconds': 300}))
            raise
        (directory / 'runner.stdout').write_bytes(result.stdout)
        (directory / 'runner.stderr').write_bytes(result.stderr)
        (directory / 'runner.status.json').write_text(json.dumps({'status': 'exit', 'exit_status': result.returncode}))
        row['pass'] = result.returncode == 0 and result.stdout.strip() == b'true' and not result.stderr
        (out / 'results.json').write_text(json.dumps(records, indent=2))
        print(row['id'], row['pass'], flush=True)
        assert row['pass'], result
    assert before == q.t.syntax_validation.implementation_fingerprint()
    report = {'result': 'pass', 'fingerprint': before, 'inputs': inputs, 'raw': str(out),
              'records': records, 'assertions': sum(row['assertions'] for row in records),
              'one_step_budgets': [*range(33), 64, 128], 'full_resume_budgets': [0, 1, 7, 16, 32, 64, 128]}
    (out / 'report.json').write_text(json.dumps(report, indent=2))
    (ROOT / 'coverage/semantics/user-constant-state.json').write_text(json.dumps(report, indent=2))
    return True


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
