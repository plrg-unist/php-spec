#!/usr/bin/env python3
"""Source-free stdClass identity in the owned object graph."""
from pathlib import Path
import hashlib, json, subprocess, sys, tempfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(tempfile.mkdtemp(prefix='stdclass-protocol-', dir=ROOT/'.tools'))
sys.path.insert(0, str(Path(__file__).parent))
import request_environment as request
from recorded_worker import Worker

source = OUT/'owned.php'
source.write_text("<?php\n$s=new stdClass; $a=[$s]; unset($s);\necho $a[0] instanceof stdClass; unset($a);\n$b=(object)[]; $c=(object)null; echo $b==$c?'E':'X'; unset($b,$c);\n")
before = request.t.syntax_validation.implementation_fingerprint()
frontend = adapter = None
try:
    frontend = Worker([str(request.t.PHP), '-n', *request.t.FLAGS, '-d',
                       'extension='+str(ROOT/'.tools/php-file.so'),
                       str(ROOT/'frontend/worker.php')], OUT/'frontend-wire')
    adapter = Worker([str(ROOT/'_build/default/adapter/main.exe'), str(ROOT)], OUT/'adapter-wire')
    parsed = frontend.request({'op':'parse','source':request.b64(source.read_bytes())})
    assert parsed['ok'] and parsed['accepted']
    checked = adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
    assert checked['ok']
finally:
    try:
        if frontend: frontend.close()
    finally:
        if adapter: adapter.close()
initial = '$php_run('+checked['fixture']+', 0, '+json.dumps(request.b64(str(source).encode()))+')'
prefix = '''
dec $stage(pstate) : bool
def $stage(S) = true -- if S.TODO = (INSTANCEOF_RESULT z) :: ptask*
def $stage(S) = false -- otherwise
dec $seek(pstate, nat) : pstate
def $seek(S, n) = S -- if $stage(S)
def $seek(S, n) = $seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$stage(S)
  -- if $(n > 0)
dec $outputs(pevent*) : nat*
def $outputs(eps) = eps
def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)
def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)
def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)
'''
checks = [
    'S_initial = '+initial,
    'S = $seek(S_initial[.COMPLETION = NORMAL], 512)[.COMPLETION = NORMAL]',
    'S.CLASSES = eps', 'S.CLASSNAMES = eps',
    '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    'S.TODO = (INSTANCEOF_RESULT z) :: ptask_tail*',
    'S_value = $resolve_at(S, S.RESULT, z)',
    'S_value.RESULT = KNOWN (POBJECT n)', 'S.OBJECTS[n] = STDINSTANCE',
    '$object_name(S, n) = $ptascii("stdClass")',
    '$class_plain_instance(S, n)',
    '$class_instanceof(S_value, POBJECT n, $ptascii("stdClass"))',
    '~$class_instanceof(S_value, POBJECT n, $ptascii("Other"))',
    '$closure_live_object_valid(S, n)',
    '~$closure_live_object_valid(S[.ALLOCATIONS = eps], n)',
    '$($heap_owners($heap_graph(S), HOBJECT n) > 0)',
    'S_done = $drive(S, 1000)', 'S_done.COMPLETION = NORMAL',
    '$outputs(S_done.EVENTS) = [49,69]',
    '$heap_valid($heap_graph(S_done))',
    'S_done.OBJECTS[1] = STDINSTANCE',
    'S_done.OBJECTS[2] = STDINSTANCE',
    '$heap_owners($heap_graph(S_done), HOBJECT n) = 0',
    '$heap_owners($heap_graph(S_done), HOBJECT 1) = 0',
    '$heap_owners($heap_graph(S_done), HOBJECT 2) = 0',
]
fixture = OUT/'guard.watsup'
fixture.write_text(prefix+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+line+'\n' for line in checks))
modules = [str(ROOT/path) for path in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
result = subprocess.run([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'), *modules, str(fixture)], capture_output=True, timeout=300)
(OUT/'stdout').write_bytes(result.stdout); (OUT/'stderr').write_bytes(result.stderr)
assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr, result.stderr
assert before == request.t.syntax_validation.implementation_fingerprint()
(OUT/'report.json').write_text(json.dumps({'result':'pass','fingerprint':before,'assertions':len(checks),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()},indent=2)+'\n')
print('PASS stdClass protocol:', len(checks), 'assertions', OUT)
