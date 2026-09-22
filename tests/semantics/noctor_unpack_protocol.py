#!/usr/bin/env python3
"""Owned no-constructor dummy sends and authenticated paused tasks."""
from pathlib import Path
import hashlib, json, subprocess, sys, tempfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(tempfile.mkdtemp(prefix='noctor-unpack-protocol-', dir=ROOT/'.tools'))
sys.path.insert(0, str(ROOT/'tests/semantics'))
import request_environment as request
from recorded_worker import Worker

source = OUT/'owned.php'
source.write_text("<?php\nnew stdClass(...[new stdClass,'foo'=>new stdClass]);\n")
def semantic_hashes():
 return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())}
sem_before=semantic_hashes()
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
def $stage(S) = true
  -- if S.TODO = (NOCTOR_UNPACK_NEXT pnoctorcall poperand 1) :: ptask*
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
 'S = $seek(S_initial[.COMPLETION = NORMAL], 1000)[.COMPLETION = NORMAL]',
 '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
 'S.TODO = (NOCTOR_UNPACK_NEXT pnoctorcall (KNOWN (PARRAY n_array)) 1) :: ptask_tail*',
 'pnoctorcall.SENT = [KNOWN (POBJECT n_sent)]',
 'S.OBJECTS[pnoctorcall.OBJECT] = STDINSTANCE',
 '$call_task_valid(S, NOCTOR_UNPACK_NEXT pnoctorcall (KNOWN (PARRAY n_array)) 1)',
 '~$call_task_valid(S, NOCTOR_UNPACK_NEXT pnoctorcall (KNOWN (PARRAY n_array)) 2)',
 '~$call_task_valid(S, NOCTOR_UNPACK_NEXT pnoctorcall (KNOWN (PARRAY n_array)) 99)',
 '~$call_task_valid(S, NOCTOR_UNPACK_NEXT pnoctorcall (KNOWN PNULL) 1)',
 '~$call_task_valid(S, NOCTOR_UNPACK_NEXT pnoctorcall[.SENT = eps] (KNOWN (PARRAY n_array)) 1)',
 '~$call_task_valid(S, NOCTOR_UNPACK_NEXT pnoctorcall[.INDEX = 99] (KNOWN (PARRAY n_array)) 1)',
 '~$call_task_valid(S, NOCTOR_UNPACK_NEXT pnoctorcall[.LINE = 99] (KNOWN (PARRAY n_array)) 1)',
 '$( $heap_owners($heap_graph(S), HOBJECT pnoctorcall.OBJECT) > 0)',
 '$( $heap_owners($heap_graph(S), HARRAY n_array) > 0)',
 '$( $heap_owners($heap_graph(S), HOBJECT n_sent) > 0)',
 'S_done = $drive(S,1000)',
 'S_done.COMPLETION = THROWN "Error" n_message* 2',
 '$heap_valid($heap_graph(S_done))',
 '$heap_owners($heap_graph(S_done), HOBJECT pnoctorcall.OBJECT) = 0',
 '$heap_owners($heap_graph(S_done), HARRAY n_array) = 0',
 '$heap_owners($heap_graph(S_done), HOBJECT n_sent) = 0',
]

fixture = OUT/'guard.watsup'
fixture.write_text(prefix+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+line+'\n' for line in checks))
modules = [str(ROOT/path) for path in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
result = subprocess.run([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'), *modules, str(fixture)], capture_output=True, timeout=300)
(OUT/'stdout').write_bytes(result.stdout); (OUT/'stderr').write_bytes(result.stderr)
assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr, result.stderr
assert sem_before == semantic_hashes()
(OUT/'report.json').write_text(json.dumps({'result':'pass','fingerprint':before,'semantic_hashes':sem_before,'scope':'exact semantic modules stable','assertions':len(checks),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()},indent=2)+'\n')
print('PASS noctor protocol:',len(checks),'assertions',OUT)
