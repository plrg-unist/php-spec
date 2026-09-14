#!/usr/bin/env python3
"""Arrow captured-array COW and fresh reference-return local owners."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile
import destructuring as d
import foreach as f
import arrows
import function_scope as scope
import request_environment as q
import request_environment_state as rs
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SELECTION = ['arrow-factory-array-reference-cow', 'arrow-reference-return-local-lifetime']

PREFIX = d.PREFIX + f.PREFIX + r'''

dec $arrow_dense_stage(pstate, nat) : bool
def $arrow_dense_stage(S, 0) = true
  -- if S.TODO = (CLOSURE_CAPTURE n_object 0) :: ptask*
def $arrow_dense_stage(S, 1) = true
  -- if S.TODO = (CLOSURE_RECEIVE porigin 0) :: ptask*
def $arrow_dense_stage(S, 2) = true
  -- if S.TODO = (RETURN_REF_FETCH z) :: ptask*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.INSTANCE = (n_object)
def $arrow_dense_stage(S, 3) = true
  -- if S.TODO = (RETURN_UNWIND (REFERENCE n_cell)) :: ptask*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.INSTANCE = (n_object)
def $arrow_dense_stage(S, 4) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.INSTANCE = (n_object)
def $arrow_dense_stage(S, n) = false -- otherwise
dec $arrow_dense_cut(pstate, nat, nat, nat) : nat
def $arrow_dense_cut(S, n_kind, n, n_left) = n -- if $arrow_dense_stage(S, n_kind)
def $arrow_dense_cut(S, n_kind, n, n_left) = $arrow_dense_cut($drive_steps(S[.COMPLETION = NORMAL], 1), n_kind, $(n + 1), n_rest)
  -- if ~$arrow_dense_stage(S, n_kind)
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
    out = Path(tempfile.mkdtemp(prefix='arrows-state-', dir=ROOT / '.tools'))
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
            source = arrows.CASES[name]
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
            reference = name == 'arrow-reference-return-local-lifetime'
            stages = [('capture', 0), ('receive', 1)] + ([('fetch', 2), ('unwind', 3)] if reference else [('return', 4)])
            for stage, kind in stages:
                checks += [f'n_{stage} = $arrow_dense_cut(S, {kind}, 0, 512)',
                           f'S_{stage} = $drive(S, n_{stage})', f'$arrow_dense_stage(S_{stage}, {kind})',
                           f'$call_descriptors_valid(S_{stage})']
            checks += ['S_capture.TODO = (CLOSURE_CAPTURE n_object 0) :: ptask_capture*',
                       '$heap_owners($heap_graph(S_capture), HOBJECT n_object) = 1',
                       'S_capture.RESULT = KNOWN PNULL',
                       'S_receive.CURRENT = (pcallcontext_receive)', 'pcallcontext_receive.INSTANCE = (n_object)',
                       'S_receive_bound = $drive(S, $(n_receive + 1))',
                       '$call_descriptors_valid(S_receive_bound)',
                       '$lookup(S_out.ENV, [102]) = (n_f)', 'S_out.STORE[n_f] = DEFINED (POBJECT n_object)']
            if reference:
                checks += ['S_out.OBJECTS[n_object] = REALCLOSURE porigin_template ([(DIRECT (PINT 2))]) eps',
                           '$lookup(S_out.ENV, [120]) = (n_outer)', '$lookup(S_out.ENV, [97]) = (n_a)',
                           '$lookup(S_out.ENV, [98]) = (n_b)', 'n_a =/= n_b', 'n_a =/= n_outer', 'n_b =/= n_outer',
                           'S_out.STORE[n_outer] = DEFINED (PINT 2)', 'S_out.STORE[n_a] = DEFINED (PINT 7)',
                           'S_out.STORE[n_b] = DEFINED (PINT 9)', 'n_a <- S_out.REFCELLS', 'n_b <- S_out.REFCELLS',
                           '$heap_owners($heap_graph(S_out), HCELL n_a) = 1', '$heap_owners($heap_graph(S_out), HCELL n_b) = 1',
                           '$heap_owners($heap_graph(S_out), HOBJECT n_object) = 1',
                           '$lookup(S_receive_bound.ENV, [120]) = (n_local)', 'n_local =/= n_outer',
                           'S_receive_bound.STORE[n_local] = DEFINED (PINT 2)',
                           'S_unwind.TODO = (RETURN_UNWIND (REFERENCE n_local)) :: ptask_unwind*',
                           'n_local = n_a', 'n_local <- S_unwind.REFCELLS',
                           '$heap_owners($heap_graph(S_unwind), HCELL n_local) = 2',
                           'S_unwind.OBJECTS[n_object] = S_out.OBJECTS[n_object]']
            else:
                checks += ['S_out.OBJECTS[n_object] = REALCLOSURE porigin_template ([(DIRECT (PARRAY n_captured))]) eps',
                           '$lookup(S_out.ENV, [112]) = (n_p)', 'S_out.STORE[n_p] = DEFINED (PARRAY n_pair)',
                           '$lookup(S_out.ENV, [98]) = (n_b)', 'S_out.STORE[n_b] = DEFINED (PARRAY n_changed)',
                           '$lookup(S_out.ENV, [99]) = (n_c)', 'S_out.STORE[n_c] = DEFINED (PARRAY n_captured)',
                           'n_changed =/= n_captured',
                           'S_out.ARRAYS[n_pair].ITEMS = [(ENTRY (KINT 0) (DIRECT (POBJECT n_object))), (ENTRY (KINT 1) (ALIAS n_shared))]',
                           'S_out.ARRAYS[n_captured].ITEMS = [(ENTRY (KINT 0) (DIRECT (PARRAY n_inner))), (ENTRY (KINT 1) (ALIAS n_shared))]',
                           'S_out.ARRAYS[n_changed].ITEMS = [(ENTRY (KINT 0) (DIRECT (PARRAY n_inner_changed))), (ENTRY (KINT 1) (ALIAS n_shared))]',
                           'n_inner =/= n_inner_changed', 'S_out.ARRAYS[n_inner].ITEMS = [(ENTRY (KSTRING ([120])) (DIRECT (PINT 1)))]',
                           'S_out.ARRAYS[n_inner_changed].ITEMS = [(ENTRY (KSTRING ([120])) (DIRECT (PINT 9)))]',
                           'S_out.STORE[n_shared] = DEFINED (PINT 8)', 'n_shared <- S_out.REFCELLS',
                           '$heap_owners($heap_graph(S_out), HCELL n_shared) = 3',
                           '$heap_owners($heap_graph(S_out), HARRAY n_captured) = 2',
                           '$heap_owners($heap_graph(S_out), HARRAY n_changed) = 1',
                           '$heap_owners($heap_graph(S_out), HOBJECT n_object) = 2',
                           '$lookup(S_receive_bound.ENV, [97]) = (n_local)', 'S_receive_bound.STORE[n_local] = DEFINED (PARRAY n_captured)',
                           '$heap_owners($heap_graph(S_receive), HARRAY n_captured) = 1',
                           '$heap_owners($heap_graph(S_receive_bound), HARRAY n_captured) = 2']
            common_count = len(checks)
            budgets = ['0', '1', '3', '7'] + [f'$(n_{stage} {sign} {offset})' for stage, _ in stages for sign, offset in [('-', 1), ('+', 0), ('+', 1), ('+', 2)]]
            for index, budget in enumerate(budgets):
                checks += [f'n_b{index} = {budget}', f'S_b{index} = $drive(S, n_b{index})',
                           f'$resume_destructuring(S_b{index}, 0) = S_b{index}',
                           f'$resume_destructuring(S_b{index}, 1) = $drive(S, $(n_b{index} + 1))',
                           f'$heap_valid($heap_graph(S_b{index}))', f'$call_valid(S_b{index})',
                           f'$call_descriptors_valid(S_b{index})', f'S_b{index}.REQUEST = S.REQUEST',
                           f'S_b{index}.HTTPROOTS = S.HTTPROOTS']
            full_indices = list(range(len(budgets)))
            checks += [f'$resume_destructuring(S_b{index}, 10000) = S_out' for index in full_indices]
            assert len(checks) == common_count + 10 * len(budgets)
            full_fixture = directory / 'state-all.watsup'
            full_fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
            fixtures = []
            for start in range(0, len(budgets), 4):
                indices = list(range(start, min(start + 4, len(budgets))))
                positions = list(range(common_count))
                for index in indices:
                    positions += list(range(common_count + 9 * index, common_count + 9 * (index + 1)))
                positions += [common_count + 9 * len(budgets) + index for index in indices]
                fixture = directory / ('state-' + str(start // 4) + '.watsup')
                fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + checks[index] + '\n' for index in positions))
                fixtures.append({'fixture': str(fixture), 'budget_indices': indices,
                                 'check_positions': positions, 'assertions': len(positions)})
            assert sorted(index for part in fixtures for index in part['check_positions'] if index >= common_count) == list(range(common_count, len(checks)))
            row.update({'assertions': len(checks), 'executed_assertions': sum(part['assertions'] for part in fixtures),
                        'common_assertions_per_fixture': common_count, 'full_fixture': str(full_fixture),
                        'fixtures': fixtures, 'one_step_budgets': budgets, 'full_resume_indices': full_indices})
    finally:
        try:
            frontend.close()
        finally:
            adapter.close()
    print(out, flush=True)
    for row in records:
        directory = out / row['id']
        for part in row['fixtures']:
            prefix = Path(part['fixture']).stem
            command = [str(runner), *map(str, modules), part['fixture']]
            (directory / (prefix + '.command.json')).write_text(json.dumps(command))
            try:
                result = subprocess.run(command, capture_output=True, timeout=900)
            except subprocess.TimeoutExpired as error:
                (directory / (prefix + '.stdout')).write_bytes(error.stdout or b'')
                (directory / (prefix + '.stderr')).write_bytes(error.stderr or b'')
                (directory / (prefix + '.status.json')).write_text(json.dumps({'status': 'timeout', 'seconds': 900}))
                raise
            (directory / (prefix + '.stdout')).write_bytes(result.stdout)
            (directory / (prefix + '.stderr')).write_bytes(result.stderr)
            (directory / (prefix + '.status.json')).write_text(json.dumps({'status': 'exit', 'exit_status': result.returncode}))
            part['pass'] = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            row['pass'] = all(item.get('pass', False) for item in row['fixtures'])
            (out / 'results.json').write_text(json.dumps(records, indent=2))
            print(row['id'], prefix, part['pass'], flush=True)
            assert part['pass'], result
    assert before == q.t.syntax_validation.implementation_fingerprint()
    report = {'result': 'pass', 'fingerprint': before, 'inputs': inputs, 'raw': str(out),
              'records': records, 'assertions': sum(row['assertions'] for row in records),
              'executed_assertions': sum(row['executed_assertions'] for row in records),
              'fixture_limit_seconds': 900, 'budget_group_size': 4}
    (out / 'report.json').write_text(json.dumps(report, indent=2))
    (ROOT / 'coverage/semantics/arrows-state.json').write_text(json.dumps(report, indent=2))
    return True


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
