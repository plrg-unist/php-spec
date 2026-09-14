#!/usr/bin/env python3
"""Closure instance static cells, recursive initialization, capture cycles and pending call owners."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile
import destructuring as d
import foreach as f
import closures
import function_scope as scope
import request_environment as q
import request_environment_state as rs
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SELECTION = ['closure-instance-static-counters', 'closure-instance-static-reentry']

PREFIX = d.PREFIX + f.PREFIX + r'''

dec $closure_dense_stage(pstate, nat) : bool
def $closure_dense_stage(S, 0) = true
  -- if S.TODO = (CLOSURE_CAPTURE n_object 0) :: ptask*
def $closure_dense_stage(S, 1) = true
  -- if S.TODO = (CALL_ARGS (CLOSURE_TARGET n_object) phpType7* n poperand* porigin? z) :: ptask*
def $closure_dense_stage(S, 2) = true
  -- if S.TODO = (STATIC_INIT porigin) :: ptask*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.INSTANCE = (n_object)
  -- if S.OBJECTS[n_object] = REALCLOSURE porigin_template pitem* eps
def $closure_dense_stage(S, 3) = true
  -- if S.TODO = (STATIC_BIND porigin) :: ptask*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.INSTANCE = (n_object)
  -- if S.OBJECTS[n_object] = REALCLOSURE porigin_template pitem* eps
def $closure_dense_stage(S, 4) = true
  -- if S.TODO = (STATIC_BIND porigin) :: ptask*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.INSTANCE = (n_object)
  -- if S.OBJECTS[n_object] = REALCLOSURE porigin_template pitem* pstaticcell*
  -- if pstaticcell* =/= eps
def $closure_dense_stage(S, n) = false -- otherwise
dec $closure_dense_cut(pstate, nat, nat, nat) : nat
def $closure_dense_cut(S, n_kind, n, n_left) = n -- if $closure_dense_stage(S, n_kind)
def $closure_dense_cut(S, n_kind, n, n_left) = $closure_dense_cut($drive_steps(S[.COMPLETION = NORMAL], 1), n_kind, $(n + 1), n_rest)
  -- if ~$closure_dense_stage(S, n_kind)
  -- if $(n_left > 0)
  -- if n_rest = $(n_left - 1)
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
    out = Path(tempfile.mkdtemp(prefix='closures-state-', dir=ROOT / '.tools'))
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
            source = closures.CASES[name]
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
            if actual['status'] == 'php_error':
                diagnostic = actual['diagnostic']
                completion = 'THROWN ' + json.dumps(diagnostic['class']) + ' ' + d.byte_sequence(base64.b64decode(diagnostic['message'])) + ' ' + str(diagnostic['line'])
            checks = ['S_initial = ' + initial, 'S_initial.COMPLETION = BUDGET', 'S = S_initial[.COMPLETION = NORMAL]',
                      'S_out = $drive(S, 10000)', 'S_out.COMPLETION = ' + completion,
                      '$outputs(S_out.EVENTS) = ' + d.byte_sequence(base64.b64decode(native['stdout'])),
                      'S_out.FRAMES = eps', 'S_out.CURRENT = eps', 'S_out.GLOBALTABLE = eps',
                      'S_out.ITERATORS = eps', 'S_out.HELD = eps', 'S_out.TODO = eps',
                      '$heap_valid($heap_graph(S_out))', '$call_valid(S_out)', 'S_out.CONSTCONTEXT = eps', '$call_descriptors_valid(S_out)']
            checks += ['S_out.DEFAULTCACHE = eps', 'S_out.STATICS = eps', 'S_out.REPORTING = 30719', 'S_out.SILENCES = eps']
            recursive = name == 'closure-instance-static-reentry'
            stages = [('capture', 0), ('selected', 1)] + ([('inner', 3), ('outer', 4)] if recursive else [('init', 2)])
            for stage, kind in stages:
                checks += [f'n_{stage} = $closure_dense_cut(S, {kind}, 0, 512)',
                           f'S_{stage} = $drive(S, n_{stage})', f'$closure_dense_stage(S_{stage}, {kind})',
                           f'$call_descriptors_valid(S_{stage})']
            checks += ['S_capture.TODO = (CLOSURE_CAPTURE n_created 0) :: ptask_capture*',
                       '$heap_owners($heap_graph(S_capture), HOBJECT n_created) = 1',
                       'S_capture.RESULT = KNOWN PNULL',
                       'S_selected.TODO = (CALL_ARGS (CLOSURE_TARGET n_chosen) phpType7_selected* n_arg poperand_selected* porigin_selected? z_selected) :: ptask_selected*',
                       '(HOBJECT n_chosen) <- $task_nodes((CALL_ARGS (CLOSURE_TARGET n_chosen) phpType7_selected* n_arg poperand_selected* porigin_selected? z_selected))']
            if not recursive:
                checks += ['$lookup(S_out.ENV, [97]) = (n_a)', '$lookup(S_out.ENV, [98]) = (n_b)',
                           '$lookup(S_out.ENV, [99]) = (n_c)',
                           'S_out.STORE[n_a] = DEFINED (POBJECT n_first)',
                           'S_out.STORE[n_b] = DEFINED (POBJECT n_second)',
                           'S_out.STORE[n_c] = DEFINED (POBJECT n_first)', 'n_first =/= n_second',
                           'S_out.OBJECTS[n_first] = REALCLOSURE porigin_template eps ([pstaticcell_first])',
                           'S_out.OBJECTS[n_second] = REALCLOSURE porigin_template eps ([pstaticcell_second])',
                           'n_static_first = pstaticcell_first.CELL', 'n_static_second = pstaticcell_second.CELL',
                           'n_static_first =/= n_static_second',
                           'S_out.STORE[n_static_first] = DEFINED (PINT 3)',
                           'S_out.STORE[n_static_second] = DEFINED (PINT 1)',
                           '$heap_owners($heap_graph(S_out), HOBJECT n_first) = 2',
                           '$heap_owners($heap_graph(S_out), HOBJECT n_second) = 1',
                           '$heap_owners($heap_graph(S_out), HCELL n_static_first) = 1',
                           '$heap_owners($heap_graph(S_out), HCELL n_static_second) = 1']
            else:
                checks += ['$lookup(S_out.ENV, [102]) = (n_self)', '$lookup(S_out.ENV, [110]) = (n_counter)',
                           'S_out.STORE[n_self] = DEFINED (POBJECT n_object)',
                           'S_out.STORE[n_counter] = DEFINED (PINT 2)',
                           'S_out.OBJECTS[n_object] = REALCLOSURE porigin_template ([(ALIAS n_self), (ALIAS n_counter)]) ([pstaticcell_final])',
                           'n_static = pstaticcell_final.CELL', 'S_out.STORE[n_static] = DEFINED (PINT 10)',
                           '$heap_owners($heap_graph(S_out), HOBJECT n_object) = 1',
                           '$heap_owners($heap_graph(S_out), HCELL n_self) = 2',
                           '$heap_owners($heap_graph(S_out), HCELL n_counter) = 2',
                           '$heap_owners($heap_graph(S_out), HCELL n_static) = 1',
                           'S_inner_bound = $drive(S, $(n_inner + 1))',
                           'S_inner_bound.OBJECTS[n_object] = REALCLOSURE porigin_template ([(ALIAS n_self), (ALIAS n_counter)]) ([pstaticcell_final])',
                           'S_inner_bound.STORE[n_static] = DEFINED (PINT 7)',
                           'S_outer.OBJECTS[n_object] = S_inner_bound.OBJECTS[n_object]',
                           'S_outer.STORE[n_static] = DEFINED (PINT 8)',
                           'S_outer_bound = $drive(S, $(n_outer + 1))',
                           'S_outer_bound.OBJECTS[n_object] = S_outer.OBJECTS[n_object]',
                           'S_outer_bound.STORE[n_static] = DEFINED (PINT 8)',
                           'H_cycle = $heap_prune($heap_graph(S_out)[.ROOTS = eps])',
                           '(HOBJECT n_object) <- H_cycle.NODES', '(HCELL n_self) <- H_cycle.NODES', '$heap_valid(H_cycle)']
            budgets = ['0', '1', '3', '7'] + [f'$(n_{stage} {sign} {offset})' for stage, _ in stages for sign, offset in [('-', 1), ('+', 0), ('+', 1), ('+', 2)]]
            for index, budget in enumerate(budgets):
                checks += [f'n_b{index} = {budget}', f'S_b{index} = $drive(S, n_b{index})',
                           f'$resume_destructuring(S_b{index}, 1) = $drive(S, $(n_b{index} + 1))',
                           f'$heap_valid($heap_graph(S_b{index}))', f'$call_valid(S_b{index})',
                           f'$call_descriptors_valid(S_b{index})', f'S_b{index}.REQUEST = S.REQUEST',
                           f'S_b{index}.HTTPROOTS = S.HTTPROOTS']
            full_indices = list(range(len(budgets)))
            checks += [f'$resume_destructuring(S_b{index}, 10000) = S_out' for index in full_indices]
            fixture = directory / 'state.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
            row.update({'assertions': len(checks), 'fixture': str(fixture), 'one_step_budgets': budgets, 'full_resume_indices': full_indices})
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
            result = subprocess.run(command, capture_output=True, timeout=900)
        except subprocess.TimeoutExpired as error:
            (directory / 'runner.stdout').write_bytes(error.stdout or b'')
            (directory / 'runner.stderr').write_bytes(error.stderr or b'')
            (directory / 'runner.status.json').write_text(json.dumps({'status': 'timeout', 'seconds': 900}))
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
              'records': records, 'assertions': sum(row['assertions'] for row in records)}
    (out / 'report.json').write_text(json.dumps(report, indent=2))
    (ROOT / 'coverage/semantics/closures-state.json').write_text(json.dumps(report, indent=2))
    return True


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
