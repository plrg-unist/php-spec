#!/usr/bin/env python3
"""Source-derived conditional provenance guards, with legitimate value changes."""
from pathlib import Path
import hashlib, json, os, subprocess, tempfile
import function_scope as fs
import request_environment_state as rs
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
PREFIX = r'''
dec $review_branch_stage(pstate) : bool
def $review_branch_stage(S) = true
  -- if S.TODO = (CONSTANT_OBSERVE porigin) :: ptask*
  -- if $origin_node(S.SOURCES, porigin) = (NExprTernary expression phpType5 expression_false metadata)
def $review_branch_stage(S) = false -- otherwise
dec $review_branch_find(pstate, nat) : pstate
def $review_branch_find(S, n) = S -- if $review_branch_stage(S)
def $review_branch_find(S, n) = $review_branch_find(S_next[.COMPLETION = NORMAL], n_rest)
  -- if ~$review_branch_stage(S)
  -- if $(n > 0)
  -- if n_rest = $(n - 1)
  -- if S_next = $drive_steps(S, 1)
'''

def main():
    q = fs.q
    source = json.loads((ROOT / 'tests/semantics/user_constant_runtime_cases.json').read_text())['selected-imported-string'].encode()
    before = q.t.syntax_validation.implementation_fingerprint()
    out = Path(tempfile.mkdtemp(prefix='user-constant-branch-protocol-', dir=ROOT / '.tools'))
    path = out / 'source.php'; path.write_bytes(source)
    entries = [b'LC_ALL=C', b'TZ=UTC', b'FIRST=one']
    payload = out / 'request.input'; payload.write_bytes(q.packet(1700000000, 125000, entries))
    request = {'env': [[q.b64(k), q.b64(v)] for k, v in (e.split(b'=', 1) for e in entries)],
               'argv': [q.b64(os.fsencode(path))], 'file': q.b64(os.fsencode(path)),
               'seconds': '1700000000', 'microseconds': 125000, 'variables': q.b64(b'EGPCS'),
               'jit': True, 'cwd': q.b64(os.fsencode(out))}
    native = fs.native(path, payload, out)
    (out / 'original.json').write_text(json.dumps({'source_base64': q.b64(source), 'context': str(path), 'request': request, 'native': native}, indent=2))
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = [*modules, runner, Path(__file__), ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/function_scope.py', ROOT / 'tests/semantics/user_constant_runtime_cases.json']
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    (out / 'inputs.json').write_text(json.dumps({'closure': before, 'direct': hashes}, indent=2))
    for p in paths:
        dest = out / 'original-inputs' / p.relative_to(ROOT); dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(p.read_bytes())
    frontend = adapter = None
    try:
        frontend = Worker([str(q.t.PHP), '-n', *q.t.FLAGS, '-d', 'extension='+str(ROOT/'.tools/php-file.so'), str(ROOT/'frontend/worker.php')], out/'frontend-wire')
        adapter = Worker([str(ROOT/'_build/default/adapter/main.exe'), str(ROOT)], out/'adapter-wire')
        parsed = frontend.request({'op': 'parse', 'source': q.b64(source)}); assert parsed['accepted']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
        result = adapter.request({'op':'execute', 'ast':parsed['ast'], 'steps':10000, 'filename':q.b64(os.fsencode(path)), 'request':request})
        (out/'checked.json').write_text(json.dumps(checked)); (out/'state.json').write_text(json.dumps(result))
        actual = q.cli.observe(result['state'], str(path))
        assert actual['status']=='normal' and all(actual[k]==native[k] for k in ['stdout','stderr','exit_status'])
    finally:
        try:
            if frontend: frontend.close()
        finally:
            if adapter: adapter.close()
    initial = '$php_request_run('+checked['fixture']+', 0, '+json.dumps(q.b64(os.fsencode(path)))+', '+rs.request_fixture(request)+')'
    common = ['S_initial = '+initial, 'S = $review_branch_find(S_initial[.COMPLETION = NORMAL], 200)', 'S.TODO = (CONSTANT_OBSERVE porigin) :: ptask*', 'S.CONSTCONTEXT = (pconstantcontext)', 'porigin_false = $constant_child(porigin, [PCFIELD 2])', 'porigin_true = $constant_child(porigin, [PCFIELD 1])', 'porigin_condition = $constant_child(porigin, [PCFIELD 0])', '$constant_fact_at(pconstantcontext.FACTS, porigin_true) = (pconstantfact_true)', '$constant_fact_at(pconstantcontext.FACTS, porigin_condition) = (pconstantfact_condition)', '$constant_fact_at(pconstantcontext.FACTS, porigin_false) = eps', 'porigin_literal = $constant_child(porigin, [PCFIELD 0,PCFIELD 1])', '$constant_fact_at(pconstantcontext.FACTS, porigin_literal) = (pconstantfact_literal)', '$pool_class(S.POOLS, porigin_literal) = (PVSTRING false)']
    variants = {
        'control': ('S', True),
        'both-arms-pooled-class': ('S[.CONSTCONTEXT = (pconstantcontext[.FACTS = pconstantcontext.FACTS ++ [{ORIGIN porigin_false,VALUE (PSTRING eps),CLASS PVSTRING true}]])]', False),
        'both-arms-wrong-class': ('S[.CONSTCONTEXT = (pconstantcontext[.FACTS = pconstantcontext.FACTS ++ [{ORIGIN porigin_false,VALUE (PSTRING eps),CLASS PVSTRING false}]])]', False),
        'wrong-pooled-observed-class': ('S[.CONSTCONTEXT = (pconstantcontext[.FACTS = $constant_fact_put(pconstantcontext.FACTS,pconstantfact_literal[.CLASS = PVSTRING true])])]', False),
        'arbitrary-truthy-value': ('S[.CONSTCONTEXT = (pconstantcontext[.FACTS = $constant_fact_put(pconstantcontext.FACTS,pconstantfact_condition[.VALUE = (PINT 99)])])]', True),
        'arbitrary-selected-value': ('S[.RESULT = KNOWN (PSTRING ([120,121,122]))][.CONSTCONTEXT = (pconstantcontext[.FACTS = $constant_fact_put(pconstantcontext.FACTS,pconstantfact_true[.VALUE = (PSTRING ([120,121,122]))])])]', True),
    }
    records = []
    for name, (term, valid) in variants.items():
        directory = out/name; directory.mkdir()
        checks = [*common, 'S_changed = '+term, '$call_descriptors_valid(S_changed) = '+str(valid).lower(), 'S_zero = $drive(S_changed, 0)', 'S_full = $drive(S_changed, 1000)']
        if valid:
            checks += ['S_zero.COMPLETION = BUDGET', 'S_full.COMPLETION = NORMAL', '$user_constant_at(S_full.USERCONSTANTS, [67]) = (puserconstant)', 'puserconstant.CLASS = PVSTRING true', 'puserconstant.VALUE = PSTRING ('+('[120,121,122]' if name=='arbitrary-selected-value' else '[97,98,99]')+')', 'S_full.CONSTCONTEXT = eps']
        else:
            checks += ['S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"', 'S_full.COMPLETION = S_zero.COMPLETION']
        fixture = directory/'case.watsup'; fixture.write_text(PREFIX+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+c+'\n' for c in checks))
        command = [str(runner), *map(str, modules), str(fixture)]; (directory/'command.json').write_text(json.dumps(command))
        try: result = subprocess.run(command, capture_output=True, timeout=60)
        except subprocess.TimeoutExpired as error:
            (directory/'stdout').write_bytes(error.stdout or b''); (directory/'stderr').write_bytes(error.stderr or b''); (directory/'status.json').write_text(json.dumps({'status':'timeout'})); raise
        (directory/'stdout').write_bytes(result.stdout); (directory/'stderr').write_bytes(result.stderr); (directory/'status.json').write_text(json.dumps({'status':'exit','exit_status':result.returncode}))
        passed = result.returncode==0 and result.stdout.strip()==b'true' and not result.stderr
        records.append({'id':name,'valid':valid,'pass':passed,'assertions':len(checks),'raw':str(directory)})
        (out/'results.json').write_text(json.dumps(records,indent=2)); print(name,passed,flush=True); assert passed
    assert before == q.t.syntax_validation.implementation_fingerprint()
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    report = {'result':'pass','fingerprint':before,'records':records,'assertions':sum(r['assertions'] for r in records),'raw':str(out),'scope':'One exact native source, three public metadata rejections and three valid controls; each checks public zero-budget and full resume. Legitimate changed runtime values are not reconstructed from source.'}
    (out/'report.json').write_text(json.dumps(report,indent=2)); print(out); return True

if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
