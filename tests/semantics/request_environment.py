#!/usr/bin/env python3
"""Explicit primitive CLI facts → native provider and checked SpecTec source runs."""
from pathlib import Path
import argparse,base64,hashlib,importlib.machinery,importlib.util,json,os,struct,subprocess,tempfile
import static_types as t
from request_environment_cases import CASES
ROOT=Path(__file__).resolve().parents[2]
loader=importlib.machinery.SourceFileLoader('request_cli',str(ROOT/'bin/php-semantics'));spec=importlib.util.spec_from_loader(loader.name,loader);cli=importlib.util.module_from_spec(spec);loader.exec_module(cli)

def b64(value):return base64.b64encode(value).decode('ascii')
def packet(seconds,microseconds,entries):
 return b'PHPRQ001'+struct.pack('<qII',seconds,microseconds,len(entries))+b''.join(struct.pack('<I',len(e))+e for e in entries)
def invoke(path,payload_path,extra_ini,argv,cwd):
 with payload_path.open('rb') as payload:
  os.dup2(payload.fileno(),198)
  try:
   command=[str(t.PHP),'-n',*t.FLAGS,'-d','variables_order=EGPCS',*[arg for x in extra_ini for arg in ['-d',x]],str(path),*argv]
   result=subprocess.run(command,env={'LD_PRELOAD':str(ROOT/'.tools/request-clock.so')},pass_fds=(198,),cwd=cwd,capture_output=True,timeout=10)
  finally:os.close(198)
 return {'stdout':b64(result.stdout),'stderr':b64(result.stderr),'exit_status':result.returncode,'command':[os.fsdecode(x) for x in command]}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--match',default='');args=parser.parse_args()
 before=t.syntax_validation.implementation_fingerprint();out=Path(tempfile.mkdtemp(prefix='request-source-',dir=ROOT/'.tools'));records=[]
 selected=[row for row in CASES if args.match in row['id']]
 assert selected, 'no request source cases matched'
 assert len({row['id'] for row in CASES}) == len(CASES), 'duplicate request source IDs'
 for i,row in enumerate(selected):
  path=out/f'case{i}.php';path.write_bytes(row['source']);entries=row.get('environment',[b'LC_ALL=C',b'TZ=UTC',b'FIRST=one']);seconds,micros=row.get('clock',[1700000000,125000]);argv=row.get('argv',[b'alpha',b'beta']);extra_ini=row.get('extra_ini',[]);config=dict(x.split('=',1) for x in extra_ini)
  spelling=path
  if row.get('invocation')=='relative':spelling=Path(path.name)
  if row.get('invocation')=='symlink':
   link=out/f'link{i}.php';link.symlink_to(path.name);spelling=Path(link.name)
  request={'env':[[b64(k),b64(v)] for k,v in (entry.split(b'=',1) for entry in entries)],'argv':[b64(os.fsencode(spelling)),*[b64(v) for v in argv]],'file':b64(os.fsencode(spelling)),'seconds':str(seconds),'microseconds':micros,'variables':b64(config.get('variables_order','EGPCS').encode()),'jit':config.get('auto_globals_jit','1')!='0','cwd':b64(os.fsencode(out))}
  payload=out/f'case{i}.input';payload.write_bytes(packet(seconds,micros,entries));oracle=invoke(spelling,payload,extra_ini,argv,out);context=out/f'case{i}.json';context.write_text(json.dumps(request))
  records.append({'id':row['id'],'source_base64':b64(row['source']),'context':str(path),'native_cwd':str(out),'invocation_spelling':os.fsdecode(spelling),'request':request,'payload_sha256':hashlib.sha256(payload.read_bytes()).hexdigest(),'oracle':oracle})
 (out/'originals.json').write_text(json.dumps({'fingerprint':before,'records':records},indent=2)+'\n')
 f=t.Worker([str(t.PHP),'-n',*t.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')]);a=t.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
 try:
  for i,row in enumerate(records):
   parsed=f.request({'op':'parse','source':row['source_base64']});assert parsed.get('accepted'),parsed
   result=a.request({'op':'execute','ast':parsed['ast'],'steps':10000,'filename':b64(os.fsencode(row['context'])),'request':row['request']})
   state=result['state'];actual=cli.observe(state,row['context']);row['actual']=actual;row['state_sha256']=hashlib.sha256(json.dumps(state,sort_keys=True).encode()).hexdigest();row['pass']=actual['status'] in ('normal','php_error','static_rejection') and all(actual[k]==row['oracle'][k] for k in ('stdout','stderr','exit_status'))
   if not row['pass']:(out/f'case{i}-state.json').write_text(json.dumps(state,indent=2)+'\n')
   (out/'results.json').write_text(json.dumps({'fingerprint':before,'records':records},indent=2)+'\n');print(row['id'],row['pass'],flush=True)
 finally:f.close();a.close()
 assert before==t.syntax_validation.implementation_fingerprint(),'request source inputs changed'
 report={'selection':args.match,'catalogue_cases':len(CASES),'selected_cases':len(selected),'result':'pass' if all(r['pass'] for r in records) else 'fail','scope':'Exact file-mode CLI request source comparisons with identical explicit environment/argv/config/clock facts; provider supplies primitives only. Ordinary absent-request execution remains separately scoped.','invocation':'pinned PHP CLI with explicit LD_PRELOAD provider and FD198; checked SpecTec php_request_run receives identical primitive facts','fingerprint':before,'records':records}
 (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');print(out,len(records),report['result'])
 if report['result']=='pass':(ROOT/'coverage/semantics/request-environment-source.json').write_text(json.dumps(report,indent=2)+'\n')
 return report['result']=='pass'
if __name__=='__main__':raise SystemExit(0 if main() else 1)
