from pathlib import Path
import hashlib,json,subprocess,sys,tempfile
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tests/semantics'))
import function_scope as scope
from recorded_worker import Worker
q=scope.q
out=Path(tempfile.mkdtemp(prefix='user-constant-protocol-',dir=R/'.tools'));source=b'<?php const C=1;echo C;';path=out/'source.php';path.write_bytes(source)
mods=[R/p for p in json.loads((R/'spec/semantics/modules.json').read_text())];runner=R/'tests/semantics/_build/default/numeric_runner.exe';inputs={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [*mods,runner,Path(__file__)]}
for p in inputs:
 t=out/'original-inputs'/p;t.parent.mkdir(parents=True,exist_ok=True);t.write_bytes((R/p).read_bytes())
(out/'inputs.json').write_text(json.dumps({'fingerprint':q.t.syntax_validation.implementation_fingerprint(),'files':inputs},indent=2))
f=Worker([str(q.t.PHP),'-n',*q.t.FLAGS,'-d','extension='+str(R/'.tools/php-file.so'),str(R/'frontend/worker.php')],out/'frontend-wire');a=Worker([str(R/'_build/default/adapter/main.exe'),str(R)],out/'adapter-wire')
try:
 parsed=f.request({'op':'parse','source':q.b64(source)});checked=a.request({'op':'check','ast':parsed['ast'],'fixture':True});(out/'checked.json').write_text(json.dumps(checked))
finally:f.close();a.close()
initial='$php_run('+checked['fixture']+', 10000, '+json.dumps(q.b64(bytes(path)))+')'
variants={
'control':'S',
'wrong-name':'S[.USERCONSTANTS = [puserconstant[.NAME = [90]]]]',
'wrong-origin':'S[.USERCONSTANTS = [puserconstant[.ORIGIN = PORIGIN 0 eps]]]',
'wrong-tag':'S[.USERCONSTANTS = [puserconstant[.CLASS = PVSTRING true]]]',
'empty-static-string':'S[.USERCONSTANTS = [puserconstant[.VALUE = PSTRING eps][.CLASS = PVSTRING true]]]',
'empty-allocated-string':'S[.USERCONSTANTS = [puserconstant[.VALUE = PSTRING eps][.CLASS = PVSTRING false]]]',
'arbitrary-static-string':'S[.USERCONSTANTS = [puserconstant[.VALUE = PSTRING ([0,255,65])][.CLASS = PVSTRING true]]]',
'arbitrary-allocated-string':'S[.USERCONSTANTS = [puserconstant[.VALUE = PSTRING ([0,255,65])][.CLASS = PVSTRING false]]]',
'empty-static-array':'S_empty[.USERCONSTANTS = [puserconstant[.VALUE = PARRAY n_empty][.CLASS = PVARRAY true eps]]]',
'empty-allocated-array':'S_empty[.USERCONSTANTS = [puserconstant[.VALUE = PARRAY n_empty][.CLASS = PVARRAY false eps]]]',
'allocated-array':'S_array[.USERCONSTANTS = [puserconstant[.VALUE = PARRAY n_array][.CLASS = PVARRAY false ([(KINT 0, PVSCALAR)])]]]',
'static-nonempty-array':'S_array[.USERCONSTANTS = [puserconstant[.VALUE = PARRAY n_array][.CLASS = PVARRAY true ([(KINT 0, PVSCALAR)])]]]',
'wrong-array-key':'S_array[.USERCONSTANTS = [puserconstant[.VALUE = PARRAY n_array][.CLASS = PVARRAY false ([(KINT 1, PVSCALAR)])]]]',
'wrong-array-child':'S_array[.USERCONSTANTS = [puserconstant[.VALUE = PARRAY n_array][.CLASS = PVARRAY false ([(KINT 0, PVSTRING true)])]]]',
}

records=[]
for name,term in variants.items():
 d=out/name;d.mkdir();fixture=d/'case.watsup';fixture.write_text('dec $main() : pstate\ndef $main() = $drive('+term+', 0)\n  -- if S = '+initial+'\n  -- if S.USERCONSTANTS = [puserconstant]\n  -- if S_empty = $allocate_array(S, $array_empty())\n  -- if S_empty.RESULT = KNOWN (PARRAY n_empty)\n  -- if S_array = $allocate_array(S, $array_insert($array_empty(), KINT 0, DIRECT (PINT 7)))\n  -- if S_array.RESULT = KNOWN (PARRAY n_array)\n')
 cmd=[str(runner),*map(str,mods),str(fixture)];(d/'command.json').write_text(json.dumps(cmd));p=subprocess.run(cmd,capture_output=True,timeout=60);(d/'stdout').write_bytes(p.stdout);(d/'stderr').write_bytes(p.stderr);(d/'status.json').write_text(json.dumps({'exit_status':p.returncode}));records.append({'id':name,'exit_status':p.returncode,'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(p.stderr).hexdigest()});print(name,p.returncode,p.stdout[:70],p.stderr[:100],flush=True)
(out/'report.json').write_text(json.dumps({'scope':'Actual-source public drive0 table/class source and metadata invariants; arbitrary values and allocated/shared empty classes remain positive controls.','raw':str(out),'records':records},indent=2));print(out)

invalid={'wrong-name','wrong-origin','wrong-tag','static-nonempty-array','wrong-array-key','wrong-array-child'}
for row in records:
 d=out/row['id'];expected='UNSUPPORTED' if row['id'] in invalid else 'NORMAL'
 assert row['exit_status']==0 and not (d/'stderr').read_bytes() and 'COMPLETION '+expected in (d/'stdout').read_text(),row['id']
report=json.loads((out/'report.json').read_text());report.update(result='pass',assertions=len(records),fingerprint=q.t.syntax_validation.implementation_fingerprint());(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(R/'coverage/semantics/user-constant-protocol.json').write_text(json.dumps(report,indent=2)+'\n')
