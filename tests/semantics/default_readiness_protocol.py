#!/usr/bin/env python3
"""Actual constant/default readiness cuts and public resume regression."""
from pathlib import Path
import base64, hashlib, json, os, subprocess, sys, tempfile
K = Path(__file__).resolve().parents[2]; R = K
sys.path.insert(0, str(K / 'tests/semantics'))
import function_call_state as cs
import function_scope as scope
import request_environment as q
import request_environment_state as rs
from recorded_worker import Worker
D = Path(tempfile.mkdtemp(prefix='default-readiness-protocol-', dir=R / '.tools'))
(D / 'producer.py').write_bytes(Path(__file__).read_bytes()); print(D, flush=True)
constant_cases = json.load(open(K / 'tests/semantics/user_constant_runtime_cases.json'))
cases = {'warning-empty-array-result': '<?php function f($x=(1+"2a")?[]:[1]){echo $x===[];}f();f();',
         'default-coalesce-present': '<?php const A="abc";function f($x=A??""){echo $x;}f();f();',
         'default-coalesce-null': '<?php const A=null;function f($x=A??"abc"){echo $x;}f();f();'}
cases.update({name:constant_cases[name] for name in ('selected-imported-string', 'coalesced-imported-string', 'null-coalesced-literal-string')})
rows = []
for name, source in cases.items():
    directory = D / name; directory.mkdir(); file = directory / 'source.php'; file.write_bytes(source.encode())
    entries = [b'LC_ALL=C', b'TZ=UTC', b'FIRST=one']
    payload = directory / 'request.input'; payload.write_bytes(q.packet(1700000000, 125000, entries))
    request = {'env': [[q.b64(k), q.b64(v)] for k,v in (entry.split(b'=',1) for entry in entries)],
               'argv':[q.b64(os.fsencode(file))], 'file':q.b64(os.fsencode(file)),
               'seconds':'1700000000','microseconds':125000,'variables':q.b64(b'EGPCS'),
               'jit':True,'cwd':q.b64(os.fsencode(directory))}
    rows.append({'id':name,'source_base64':q.b64(source.encode()),'context':str(file),'request':request,'native':scope.native(file,payload,directory)})
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
modules = [K / p for p in json.load(open(K / 'spec/semantics/modules.json'))]
runner = K / 'tests/semantics/_build/default/numeric_runner.exe'
before = q.t.syntax_validation.implementation_fingerprint()
direct = {str(p.relative_to(K)): sha(p) for p in [*modules, runner, K / 'tests/semantics/recorded_worker.py', Path(__file__), K / 'tests/semantics/user_constant_runtime_cases.json']}
(D / 'inputs.json').write_text(json.dumps({'fingerprint': before, 'direct': direct}, indent=2))
for p in direct:
    f = D / 'original-inputs' / p; f.parent.mkdir(parents=True, exist_ok=True); f.write_bytes((K / p).read_bytes())
prefix = cs.PREFIX + r'''
dec $review_ready_child(pstate, porigin) : bool
def $review_ready_child(S, porigin) = $constant_has_fact(S, $constant_child(porigin, [PCFIELD 1]))
  -- if $origin_node(S.SOURCES, porigin) = (NExprTernary expression phpType5 expression_false metadata)
def $review_ready_child(S, porigin) = $constant_has_fact(S, $constant_child(porigin, [PCFIELD 0]))
  -- if $origin_node(S.SOURCES, porigin) = (NExprBinaryOpCoalesce expression expression_right metadata)
def $review_ready_child(S, porigin) = false -- otherwise
dec $review_ready_cut(pstate) : bool
def $review_ready_cut(S) = true
  -- if S.CONSTCONTEXT = (pconstantcontext)
  -- if $constant_expression_root(S, pconstantcontext.ORIGIN) = (porigin)
  -- if ~$constant_result_required(S, porigin)
  -- if $review_ready_child(S, porigin)
def $review_ready_cut(S) = false -- otherwise
dec $review_ready_find(pstate, nat) : pstate
def $review_ready_find(S, n) = S -- if $review_ready_cut(S)
def $review_ready_find(S, n) = $review_ready_find($drive_steps(S, 1)[.COMPLETION = NORMAL], $nabs($(n - 1)))
  -- if ~$review_ready_cut(S)
  -- if $(n > 0)
dec $review_ready_steps(pstate, nat) : bool
def $review_ready_steps(S, 0) = true
  -- if $call_descriptors_valid(S)
  -- if $heap_valid($heap_graph(S))
def $review_ready_steps(S, n) = true
  -- if $(n > 0)
  -- if $call_descriptors_valid(S)
  -- if $heap_valid($heap_graph(S))
  -- if S_zero = $drive(S, 0)
  -- if S_zero.COMPLETION = BUDGET \/ S_zero.COMPLETION = NORMAL
  -- if S_next = $drive(S, 1)
  -- if $review_ready_steps(S_next[.COMPLETION = NORMAL], $nabs($(n - 1)))
'''
front = adapter = None; records = []
try:
    front = Worker([str(q.t.PHP), '-n', *q.t.FLAGS, '-d', 'extension=' + str(K / '.tools/php-file.so'), str(K / 'frontend/worker.php')], D / 'frontend-wire')
    adapter = Worker([str(K / '_build/default/adapter/main.exe'), str(K)], D / 'adapter-wire')
    for row in rows:
        d = D / row['id']; (d / 'original.json').write_text(json.dumps(row, indent=2))
        assert Path(row['context']).read_bytes() == base64.b64decode(row['source_base64'])
        parsed = front.request({'op': 'parse', 'source': row['source_base64']}); assert parsed['accepted']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
        state = adapter.request({'op': 'execute', 'ast': parsed['ast'], 'steps': 10000, 'filename': q.b64(row['context'].encode()), 'request': row['request']})
        (d / 'checked.json').write_text(json.dumps(checked)); (d / 'state.json').write_text(json.dumps(state))
        actual = q.cli.observe(state['state'], row['context'])
        assert actual['status'] == 'normal' and all(actual[k] == row['native'][k] for k in ('stdout', 'stderr', 'exit_status'))
        initial = '$php_request_run(' + checked['fixture'] + ', 0, ' + json.dumps(q.b64(row['context'].encode())) + ', ' + rs.request_fixture(row['request']) + ')'
        checks = ['S_initial = ' + initial, 'S = S_initial[.COMPLETION = NORMAL]', 'S_cut = $review_ready_find(S, 200)', '$review_ready_cut(S_cut)', 'S_zero = $drive(S_cut, 0)', 'S_zero.COMPLETION = BUDGET', '$drive(S_cut, 1000) = $drive_steps(S, 1000)', '$review_ready_steps(S, 100)']
        fixture = d / 'case.watsup'; fixture.write_text(prefix + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + x + '\n' for x in checks))
        records.append({'id': row['id'], 'fixture': str(fixture), 'assertions': len(checks), 'native_agreement': True})
finally:
    try:
        if front: front.close()
    finally:
        if adapter: adapter.close()
for row in records:
    d = Path(row['fixture']).parent; command = [str(runner), *map(str, modules), row['fixture']]
    (d / 'command.json').write_text(json.dumps(command))
    try: p = subprocess.run(command, capture_output=True, timeout=180)
    except subprocess.TimeoutExpired as e:
        (d / 'stdout').write_bytes(e.stdout or b''); (d / 'stderr').write_bytes(e.stderr or b''); (d / 'status.json').write_text(json.dumps({'status': 'timeout'})); raise
    (d / 'stdout').write_bytes(p.stdout); (d / 'stderr').write_bytes(p.stderr); (d / 'status.json').write_text(json.dumps({'status': 'exit', 'exit_status': p.returncode}))
    row['pass'] = p.returncode == 0 and p.stdout == b'true\n' and not p.stderr
    (D / 'results.json').write_text(json.dumps(records, indent=2)); print(row['id'], row['pass'], flush=True)
assert before == q.t.syntax_validation.implementation_fingerprint()
assert all(sha(K / p) == h for p, h in direct.items())
report = {'result': 'pass' if all(r['pass'] for r in records) else 'fail', 'fingerprint': before, 'records': records, 'scope': 'Six retained native/source profiles cover ternary and both coalesce arms in constant/default contexts; each checks exact pre-observer public zero/full resume and first100 adjacent guard/heap states.'}
(D / 'report.json').write_text(json.dumps(report, indent=2)); (K / 'coverage/semantics/default-readiness-protocol.json').write_text(json.dumps(report, indent=2)); print(D, report['result']); raise SystemExit(0 if report['result']=='pass' else 1)
