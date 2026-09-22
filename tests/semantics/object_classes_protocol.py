#!/usr/bin/env python3
"""Paused class activation, object ownership, and instanceof task guards."""
from pathlib import Path
import base64, hashlib, json, subprocess, sys, tempfile
D=Path(__file__).resolve().parent; R=D.parents[1]; O=Path(tempfile.mkdtemp(prefix='object-classes-protocol-',dir=R/'.tools'))
sys.path.insert(0,str(D))
import request_environment as q
from recorded_worker import Worker
source=O/'owner.php'; source.write_text("<?php\nclass A {}\n$x=new A; $a=[$x]; unset($x);\necho $a[0] instanceof A;\nunset($a);\n")
before=q.t.syntax_validation.implementation_fingerprint()
f=a=None
try:
 f=Worker([str(q.t.PHP),'-n',*q.t.FLAGS,'-d','extension='+str(R/'.tools/php-file.so'),str(R/'frontend/worker.php')],O/'frontend-wire')
 a=Worker([str(R/'_build/default/adapter/main.exe'),str(R)],O/'adapter-wire')
 parsed=f.request({'op':'parse','source':q.b64(source.read_bytes())});assert parsed['ok'] and parsed['accepted']
 checked=a.request({'op':'check','ast':parsed['ast'],'fixture':True});assert checked['ok']
finally:
 try:
  if f:f.close()
 finally:
  if a:a.close()
initial='$php_run('+checked['fixture']+', 0, '+json.dumps(q.b64(str(source).encode()))+')'
prefix='''
dec $review_stage(pstate) : bool
def $review_stage(S) = true -- if S.TODO = (INSTANCEOF_RESULT z) :: ptask*
def $review_stage(S) = false -- otherwise
dec $review_seek(pstate, nat) : pstate
def $review_seek(S, n) = S -- if $review_stage(S)
def $review_seek(S, n) = $review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$review_stage(S)
  -- if $(n > 0)
dec $outputs(pevent*) : nat*
def $outputs(eps) = eps
def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)
def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)
def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)
'''
checks=[
'S_initial = '+initial,'S_pause = $review_seek(S_initial[.COMPLETION = NORMAL], 512)',
'S = S_pause[.COMPLETION = NORMAL]','$call_descriptors_valid(S)','$heap_valid($heap_graph(S))',
'$drive(S, 1) = $drive_steps(S, 1)','S_done = $drive(S, 1000)','S_done.COMPLETION = NORMAL',
'$outputs(S_done.EVENTS) = [49]',
'S.TODO = (INSTANCEOF_RESULT z) :: ptask_tail*',
'~$call_tasks_valid(S, (INSTANCEOF_RESULT $(z + 1)) :: ptask_tail*)',
'~$call_tasks_valid(S[.ORIGIN = eps], S.TODO)',
'~$call_task_valid($initial_state(NORMAL), INSTANCEOF_RESULT 99)',
'S.CLASSES = [pclassdesc]','$class_state_valid(S)',
'$origin_node(S.SOURCES, pclassdesc.ORIGIN) = (NStmtClass phpType14 (INTEGER 0) phpType3 phpType44 phpType42 phpType23 metadata_class)',
'S_class = S[.ORIGIN = (pclassdesc.ORIGIN)]',
'$call_task_valid(S_class, STMT (NStmtClass phpType14 (INTEGER 0) phpType3 phpType44 phpType42 phpType23 metadata_class))',
'~$call_task_valid(S_class, STMT (NStmtClass phpType14 (INTEGER 1) phpType3 phpType44 phpType42 phpType23 metadata_class))',
'~$call_task_valid(S_class[.ORIGIN = eps], STMT (NStmtClass phpType14 (INTEGER 0) phpType3 phpType44 phpType42 phpType23 metadata_class))',
'S.ORIGIN = (porigin_instanceof)',
'$origin_node(S.SOURCES, porigin_instanceof) = (NExprInstanceof expression name metadata_instanceof)',
'metadata_instanceof =/= eps',
'$call_task_valid(S, EVAL (NExprInstanceof expression name metadata_instanceof))',
'~$call_task_valid(S, EVAL (NExprInstanceof expression name eps))',
'~$class_state_valid(S[.CLASSES = eps])',
'~$class_state_valid(S[.CLASSES = [pclassdesc[.EARLY = (~pclassdesc.EARLY)]]])',
'~$class_state_valid(S[.CLASSES = [pclassdesc[.NAME = $ptascii("B")]]])',
'~$class_state_valid(S[.CLASSNAMES = eps])',
'~$class_registry_valid([pclassdesc[.NAME = $ptascii("Closure")]], [($ptascii("closure"), pclassdesc.ORIGIN)])',
'S_value = $resolve_at(S, S.RESULT, z)','S_value.RESULT = KNOWN (POBJECT n_object)',
'S.OBJECTS[n_object] = INSTANCE porigin_class','$closure_live_object_valid(S, n_object)',
'~$closure_live_object_valid(S[.OBJECTS = $object_set(S.OBJECTS, n_object, INSTANCE (PORIGIN 0 eps))], n_object)',
'n_owners = $heap_owners($heap_graph(S), HOBJECT n_object)','$(n_owners > 0)',
'$heap_valid($heap_graph(S_done))','$heap_owners($heap_graph(S_done), HOBJECT n_object) = 0',
]
fixture=O/'guard.watsup';fixture.write_text(prefix+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+x+'\n' for x in checks))
modules=[str(R/p) for p in json.loads((R/'spec/semantics/modules.json').read_text())]
result=subprocess.run([str(R/'tests/semantics/_build/default/numeric_runner.exe'),*modules,str(fixture)],capture_output=True,timeout=300)
(O/'stdout').write_bytes(result.stdout);(O/'stderr').write_bytes(result.stderr)
assert result.returncode==0 and result.stdout==b'true\n' and not result.stderr,result.stderr
assert before==q.t.syntax_validation.implementation_fingerprint()
(O/'report.json').write_text(json.dumps({'result':'pass','fingerprint':before,'assertions':len(checks),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()},indent=2)+'\n')
print('PASS object class protocol:',len(checks),'assertions',O)
