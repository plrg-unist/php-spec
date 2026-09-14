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
import call_unpack
import function_scope as scope
import request_environment as q
import request_environment_state as rs
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SELECTION = ['unpack-partial-reference-collection-then-key-error', 'unpack-held-owner-after-later-call']

PREFIX = d.PREFIX + f.PREFIX + r'''
dec $unpack_state_stage(pstate, nat) : bool
def $unpack_state_stage(S, 0) = true -- if S.TODO = (UNPACK_PREP punpackcall) :: ptask*
def $unpack_state_stage(S, 1) = true -- if S.TODO = (UNPACK_NEXT punpackcall poperand 0 b) :: ptask*
def $unpack_state_stage(S, 2) = true -- if S.TODO = (UNPACK_NEXT punpackcall poperand 2 b) :: ptask*
def $unpack_state_stage(S, 3) = true -- if S.TODO = (NAMED_VARIADIC_RECEIVE porigin 0) :: ptask*
def $unpack_state_stage(S, 4) = true
  -- if S.TODO = (UNPACK_SEND punpackcall) :: ptask*
  -- if punpackcall.INDEX = 1
def $unpack_state_stage(S, n) = false -- otherwise
dec $unpack_state_cut(pstate, nat, nat, nat) : nat
def $unpack_state_cut(S, n_kind, n, n_left) = n -- if $unpack_state_stage(S, n_kind)
def $unpack_state_cut(S, n_kind, n, n_left) = $unpack_state_cut($drive_steps(S[.COMPLETION = NORMAL], 1), n_kind, $(n + 1), n_rest)
  -- if ~$unpack_state_stage(S, n_kind)
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
    out = Path(tempfile.mkdtemp(prefix='call-unpack-state-', dir=ROOT / '.tools'))
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
            source = call_unpack.CASES[name]
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
            checks += ['S_out.DEFAULTCACHE = eps']
            checks += ['S_out.REPORTING = 30719', 'S_out.SILENCES = eps']
            partial = name == 'unpack-partial-reference-collection-then-key-error'
            stages = [('prepare', 0), ('separated', 1), ('sent', 2 if partial else 4)]
            if not partial:
                stages.append(('tail', 3))
            for stage, kind in stages:
                checks += [f'n_{stage} = $unpack_state_cut(S, {kind}, 0, 512)',
                           f'S_{stage} = $drive(S, n_{stage})', f'$unpack_state_stage(S_{stage}, {kind})']
            checks += ['S_separated.TODO = (UNPACK_NEXT punpackcall poperand 0 false) :: ptask*',
                       'n_container = $unpack_array(S_separated, poperand)',
                       'punpackcall.SENT.SLOTS = eps', 'punpackcall.SENT.NAMED = eps']
            if partial:
                checks += ['$lookup(S_separated.ENV, [97]) = (n_a)', '$lookup(S_separated.ENV, [98]) = (n_b)',
                           'S_separated.STORE[n_a] = DEFINED (PARRAY n_container)',
                           'S_separated.STORE[n_b] = DEFINED (PARRAY n_before)', 'n_before =/= n_container',
                           'S_separated.ARRAYS[n_container].ITEMS = S_separated.ARRAYS[n_before].ITEMS',
                           'S_sent.TODO = (UNPACK_NEXT punpackcall_sent poperand_sent 2 true) :: ptask_sent*',
                           'punpackcall_sent.SENT.SLOTS = [NAMED_SENT (REFERENCE n_first)]',
                           'n_z* = [122]', 'punpackcall_sent.SENT.NAMED = [(n_z*, REFERENCE n_second)]',
                           'S_sent.ARRAYS[n_container].ITEMS = [ENTRY (KINT 0) (ALIAS n_first), ENTRY (KSTRING n_z*) (ALIAS n_second), ENTRY (KINT 2) (DIRECT (PINT 3))]',
                           'S_sent.STORE[n_first] = DEFINED (PINT 1)', 'S_sent.STORE[n_second] = DEFINED (PINT 2)',
                           '$($heap_owners($heap_graph(S_sent), HCELL n_first) >= 2)',
                           '$($heap_owners($heap_graph(S_sent), HCELL n_second) >= 2)',
                           'S_out.ARRAYS[n_container].ITEMS = S_sent.ARRAYS[n_container].ITEMS',
                           'S_out.ARRAYS[n_before].ITEMS = S_separated.ARRAYS[n_before].ITEMS',
                           '$heap_owners($heap_graph(S_out), HCELL n_first) = 1',
                           '$heap_owners($heap_graph(S_out), HCELL n_second) = 1']
            else:
                checks += ['S_sent.TODO = (UNPACK_SEND punpackcall_sent) :: ptask_sent*',
                           '$lookup(S_sent.ENV, [97]) = eps',
                           'punpackcall_sent.SENT.SLOTS = [NAMED_SENT (REFERENCE n_first)]',
                           'S_sent.STORE[n_first] = DEFINED (PARRAY n_original)',
                           'S_tail.CURRENT = (pcallcontext)', 'pcallcontext.ARGC = 1',
                           'pcallcontext.EXTRA = [REFERENCE n_first]',
                           'n_gone* = [103,111,110,101]', 'pcallcontext.NAMED = [(n_gone*, REFERENCE n_second)]',
                           '$lookup(S_tail.ENV, [120,115]) = (n_tail_cell)',
                           'S_tail.STORE[n_tail_cell] = DEFINED (PARRAY n_tail_array)',
                           'S_tail.ARRAYS[n_tail_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_first)]',
                           '$lookup(S_out.ENV, [97]) = eps', '$lookup(S_out.ENV, [114]) = (n_r)', '$lookup(S_out.ENV, [118]) = (n_v)',
                           'S_out.STORE[n_r] = DEFINED (PARRAY n_r_array)', 'S_out.STORE[n_v] = DEFINED (PARRAY n_v_array)',
                           'n_r_array =/= n_v_array',
                           '$entry_lookup(S_out.ARRAYS[n_r_array].ITEMS, KINT 0) = (ALIAS n_first)',
                           '$entry_lookup(S_out.ARRAYS[n_v_array].ITEMS, KINT 0) = (DIRECT (PARRAY n_copy))',
                           'S_out.STORE[n_first] = DEFINED (PARRAY n_original)', 'n_original =/= n_copy',
                           'S_out.ARRAYS[n_original].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
                           'S_out.ARRAYS[n_copy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 3))]',
                           '$heap_owners($heap_graph(S_out), HCELL n_first) = 1']
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
              'records': records, 'assertions': sum(row['assertions'] for row in records),
              'one_step_budgets': budgets, 'full_resume_indices': full_indices}
    (out / 'report.json').write_text(json.dumps(report, indent=2))
    (ROOT / 'coverage/semantics/call-unpack-state.json').write_text(json.dumps(report, indent=2))
    return True


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
