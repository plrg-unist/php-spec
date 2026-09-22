#!/usr/bin/env python3
"""Linked empty-class identities and authenticated paused inheritance state."""
from pathlib import Path
import hashlib, json, subprocess, sys, tempfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(tempfile.mkdtemp(prefix='inheritance-protocol-', dir=ROOT/'.tools'))
sys.path.insert(0, str(Path(__file__).parent))
import request_environment as request
from recorded_worker import Worker

source = OUT/'chain.php'
source.write_text("<?php\nclass A {} class B extends A {} class C extends B {}\n$x=new C; $a=[$x]; unset($x); echo $a[0] instanceof A; unset($a);\n")
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
    'S = $seek(S_initial[.COMPLETION = NORMAL], 1000)[.COMPLETION = NORMAL]',
    '$class_state_valid(S)', '$heap_valid($heap_graph(S))',
    'S.CLASSES = [pclassdesc_a, pclassdesc_b, pclassdesc_c]',
    'pclassdesc_a.PARENT = eps',
    'pclassdesc_b.PARENT = (pclassdesc_a.NAME)',
    'pclassdesc_c.PARENT = (pclassdesc_b.NAME)',
    'S.LINKEDPARENTS = [CLASSLINK pclassdesc_b.ORIGIN (SOURCE_PARENT pclassdesc_a.ORIGIN), CLASSLINK pclassdesc_c.ORIGIN (SOURCE_PARENT pclassdesc_b.ORIGIN)]',
    '$class_origin_matches(S, pclassdesc_c.ORIGIN, pclassdesc_a.NAME, |S.CLASSES|)',
    '$typed_class_chain(S, [PTBRANCH ([(PTCLASS pclassdesc_a.NAME), (PTCLASS pclassdesc_b.NAME)])], pclassdesc_c.ORIGIN, |S.CLASSES|)',
    '~$class_origin_matches(S, pclassdesc_a.ORIGIN, pclassdesc_c.NAME, |S.CLASSES|)',
    '~$class_links_valid(S[.LINKEDPARENTS = eps])',
    '~$class_links_valid(S[.LINKEDPARENTS = [CLASSLINK pclassdesc_c.ORIGIN (SOURCE_PARENT pclassdesc_b.ORIGIN), CLASSLINK pclassdesc_b.ORIGIN (SOURCE_PARENT pclassdesc_a.ORIGIN)]])',
    '~$class_links_valid(S[.LINKEDPARENTS = S.LINKEDPARENTS ++ [CLASSLINK pclassdesc_b.ORIGIN (SOURCE_PARENT pclassdesc_a.ORIGIN)]])',
    '~$class_links_valid(S[.CLASSES = [pclassdesc_a, pclassdesc_b[.PARENT = (pclassdesc_c.NAME)], pclassdesc_c]][.LINKEDPARENTS = [CLASSLINK pclassdesc_b.ORIGIN (SOURCE_PARENT pclassdesc_c.ORIGIN), CLASSLINK pclassdesc_c.ORIGIN (SOURCE_PARENT pclassdesc_b.ORIGIN)]])',
    '~$class_links_valid(S[.LINKEDPARENTS = S.LINKEDPARENTS ++ [CLASSLINK (PORIGIN 999 eps) STDCLASS_PARENT]])',
    '~$class_links_valid(S[.CLASSES = [pclassdesc_a[.FINAL = true], pclassdesc_b, pclassdesc_c]])',
    '~$class_links_valid(S[.CLASSES = [pclassdesc_a, pclassdesc_b[.READONLY = true], pclassdesc_c]])',
    '~$class_state_valid(S[.LINKEDPARENTS = eps])',
    'S.TODO = (INSTANCEOF_RESULT z) :: ptask_tail*',
    'S_value = $resolve_at(S, S.RESULT, z)',
    'S_value.RESULT = KNOWN (POBJECT n_object)',
    'S.OBJECTS[n_object] = INSTANCE porigin_object',
    'porigin_object = pclassdesc_c.ORIGIN',
    '$( $heap_owners($heap_graph(S), HOBJECT n_object) > 0)',
    'S_done = $drive(S, 1000)', 'S_done.COMPLETION = NORMAL',
    '$outputs(S_done.EVENTS) = [49]',
    '$class_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    '$heap_owners($heap_graph(S_done), HOBJECT n_object) = 0',
]
fixture = OUT/'guard.watsup'
fixture.write_text(prefix+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+line+'\n' for line in checks))
modules = [str(ROOT/path) for path in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
result = subprocess.run([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'), *modules, str(fixture)], capture_output=True, timeout=300)
(OUT/'stdout').write_bytes(result.stdout); (OUT/'stderr').write_bytes(result.stderr)
assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr, result.stderr
assert before == request.t.syntax_validation.implementation_fingerprint()
(OUT/'report.json').write_text(json.dumps({'result':'pass','fingerprint':before,'assertions':len(checks),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()},indent=2)+'\n')
print('PASS inheritance protocol:',len(checks),'assertions',OUT)
