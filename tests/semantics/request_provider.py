from pathlib import Path
import base64,hashlib,json,os,struct,subprocess,sys,tempfile
R=Path(__file__).resolve().parents[2];D=R
sys.path.insert(0,str(R/'tests/semantics'));import coalesce_assignment as cases
profile=json.loads((R/'tests/semantics/profile.json').read_text());flags=[arg for key,value in profile.items() for arg in ['-d',key+'='+value]]
environment=[b'LC_ALL=C',b'LD_PRELOAD=logical-loader',b'FIRST=one',b'PHP_SPEC_REQUEST_CLOCK=logical-clock',b'TZ=UTC',b'SECOND=two']
before=cases.t.syntax_validation.implementation_fingerprint()
out=Path(tempfile.mkdtemp(prefix='request-provider-',dir=R/'.tools'));records=[]
def packet(seconds,useconds,entries):
 return b'PHPRQ001'+struct.pack('<qII',seconds,useconds,len(entries))+b''.join(struct.pack('<I',len(e))+e for e in entries)
def invoke(path,data):
 q=out/(path.stem+'.input');q.write_bytes(data)
 with q.open('rb') as payload:
  os.dup2(payload.fileno(),198)
  try:r=subprocess.run([str(R/'.tools/php/bin/php'),'-n',*flags,'-d','variables_order=EGPCS',str(path),'alpha','beta'],env={'LD_PRELOAD':str(R/'.tools/request-clock.so')},pass_fds=(198,),cwd=out,capture_output=True,timeout=10)
  finally:os.close(198)
 return {'stdout':base64.b64encode(r.stdout).decode(),'stderr':base64.b64encode(r.stderr).decode(),'status':r.returncode}
source=b'<?php echo $_SERVER["REQUEST_TIME_FLOAT"],":",$_SERVER["REQUEST_TIME"],":",$argc,":",$argv[1],":",$argv[2];foreach($_ENV as $k=>$v){echo ":",$k,"=",$v;}echo ":",$_SERVER["LD_PRELOAD"],":",$_SERVER["PHP_SPEC_REQUEST_CLOCK"];'
for index,(s,u,expected) in enumerate([(1700000000,0,b'1700000000:1700000000'),(1700000000,125000,b'1700000000.125:1700000000'),(1700000001,999999,b'1700000002:1700000001'),(-1,500000,b'-0.5:0')]):
 p=out/f'clock-{index}.php';p.write_bytes(source);actual=invoke(p,packet(s,u,environment));expected+=b':3:alpha:beta:'+b':'.join(environment)+b':logical-loader:logical-clock';records.append({'id':p.stem,'source_base64':base64.b64encode(source).decode(),'context':str(p),'clock':[s,u],'environment_base64':[base64.b64encode(e).decode() for e in environment],'actual':actual,'expected_stdout':base64.b64encode(expected).decode()});assert actual=={'stdout':base64.b64encode(expected).decode(),'stderr':'','status':0},actual
plain_env={'LC_ALL':'C','TZ':'UTC','FIRST':'one','SECOND':'two'};entries=[(k+'='+v).encode() for k,v in plain_env.items()]
for index,(name,source) in enumerate(cases.CASES.items()):
 p=out/f'plain-{index}.php';p.write_bytes(source);q=subprocess.run([str(R/'.tools/php/bin/php'),'-n',*flags,'-d','variables_order=EGPCS',str(p),'alpha','beta'],env=plain_env,cwd=out,capture_output=True,timeout=10);plain={'stdout':base64.b64encode(q.stdout).decode(),'stderr':base64.b64encode(q.stderr).decode(),'status':q.returncode};actual=invoke(p,packet(1700000000,125000,entries));records.append({'id':name,'source_base64':base64.b64encode(source).decode(),'context':str(p),'plain':plain,'actual':actual});assert actual==plain,(name,actual,plain)
valid=packet(0,0,[])
for index,data in enumerate([b'',b'bad',valid[:-1],valid+b'x',packet(0,1000000,[]),packet(0,0,[b'bad']),packet(0,0,[b'A=x\x00y'])]):
 p=out/f'bad-{index}.php';p.write_bytes(b'<?php echo "unexpected";');actual=invoke(p,data);records.append({'id':p.stem,'context':str(p),'packet_base64':base64.b64encode(data).decode(),'actual':actual});assert actual['status']==125 and actual['stdout']=='',actual
assert before==cases.t.syntax_validation.implementation_fingerprint(), 'request provider inputs changed'
report={'fingerprint':before,'invocation':'pinned CLI with explicit LD_PRELOAD fixture provider and inherited FD198 payload; paired plain runs have no provider','scope':'Native-only FD clock/environment transport; no semantic request admission','files':{n:hashlib.sha256((D/n).read_bytes()).hexdigest() for n in ['native/request_clock.c','.tools/request-clock.so','scripts/build-request-provider.sh','tests/semantics/request_provider.py']},'oracle_sha256':hashlib.sha256((R/'.tools/php/bin/php').read_bytes()).hexdigest(),'records':records,'result':'pass'};(out/'results.json').write_text(json.dumps(report,indent=2)+'\n');(R/'coverage/semantics/request-provider.json').write_text(json.dumps(report,indent=2)+'\n');print(out,len(records),'pass')
