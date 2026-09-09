#!/usr/bin/env python3
"""Checked request JSON transport, primitive admissibility and bootstrap observations."""
from pathlib import Path
import base64,copy,hashlib,json,signal,subprocess,tempfile
import static_types as t
ROOT=Path(__file__).resolve().parents[2]
R=ROOT
RUNTIME_ROOT=ROOT
ADAPTER=ROOT/'_build/default/adapter/main.exe'
REPORT=ROOT/'coverage/semantics/request-adapter.json'

ABSENT_REQUEST = {'ok': True,
 'state': {'REQUEST': None,
           'SYMBOLS': [],
           'CVS': [],
           'HTTPROOTS': [],
           'ACTIVATED': [],
           'TODO': [],
           'EVENTS': [],
           'COMPLETION': {'tag': 'NORMAL', 'args': []},
           'ENV': [],
           'STORE': [],
           'REFCELLS': [],
           'RESULT': {'tag': 'KNOWN', 'args': [{'tag': 'PNULL', 'args': []}]},
           'CELL': '0',
           'ARRAYS': [],
           'KEY': {'tag': 'KINT', 'args': ['0']},
           'BASE': {'tag': 'BASE_VALUE', 'args': [{'tag': 'KNOWN', 'args': [{'tag': 'PNULL', 'args': []}]}]},
           'LOCATION': {'tag': 'ROOT', 'args': ['0']},
           'ALLOCATIONS': [],
           'HELD': [],
           'SOURCES': [{'ID': '0', 'AST': {'tag': 'PROGRAM', 'args': [[]]}, 'OCCURRENCES': []}],
           'ORIGIN': None,
           'POOLS': [{'UNIT': '0', 'CONSTANTS': []}],
           'FILES': [{'tag': 'SOURCEFILE',
                      'args': ['0',
                               ['47',
                                '114',
                                '101',
                                '113',
                                '117',
                                '101',
                                '115',
                                '116',
                                '46',
                                '112',
                                '104',
                                '112']]}],
           'CODE': [{'UNIT': '0', 'EXPRESSIONS': [], 'NAMES': [], 'REDIRECTS': []}],
           'ITERATORS': [],
           'NEXTITER': '0'}}

SOURCE_RECORDS = [{'id': 'proxy-duplicate',
  'environment_base64': ['TENfQUxMPUM=',
                         'VFo9VVRD',
                         'SFRUUF9QUk9YWT1maXJzdA==',
                         'SFRUUF9QUk9YWT1sYXN0',
                         'RFVQPWZpcnN0',
                         'RFVQPWxhc3Q='],
  'context': '/home/user/workspace/php-spec/.tools/review7-request-bootstrap-originals/proxy-duplicate.php',
  'clock': [-1, 500000],
  'extra_ini': [],
  'source_base64': 'PD9waHAgZWNobyAkX0VOVlsiSFRUUF9QUk9YWSJdLCI6IiwkX1NFUlZFUlsiSFRUUF9QUk9YWSJdLCI6IiwkX0VOVlsiRFVQIl0sIjoiLCRfU0VSVkVSWyJEVVAiXTs=',
  'oracle': {'stdout': 'Zmlyc3Q6Zmlyc3Q6bGFzdDpsYXN0', 'stderr': '', 'exit_status': 0}},
 {'id': 'proxy-empty-first',
  'environment_base64': ['TENfQUxMPUM=', 'VFo9VVRD', 'SFRUUF9QUk9YWT0=', 'SFRUUF9QUk9YWT1sYXN0'],
  'context': '/home/user/workspace/php-spec/.tools/review7-request-bootstrap-originals/proxy-empty-first.php',
  'clock': [-1, 500000],
  'extra_ini': [],
  'source_base64': 'PD9waHAgZWNobyAiWyIsJF9FTlZbIkhUVFBfUFJPWFkiXSwiXVsiLCRfU0VSVkVSWyJIVFRQX1BST1hZIl0sIl0iOw==',
  'oracle': {'stdout': 'W11bXQ==', 'stderr': '', 'exit_status': 0}},
 {'id': 'proxy-case-sensitive',
  'environment_base64': ['TENfQUxMPUM=',
                         'VFo9VVRD',
                         'aHR0cF9wcm94eT1sb3dlcg==',
                         'SFRUUF9QUk9YWT11cHBlcg==',
                         'aHR0cF9wcm94eT1sYXN0'],
  'context': '/home/user/workspace/php-spec/.tools/review7-request-bootstrap-originals/proxy-case-sensitive.php',
  'clock': [-1, 500000],
  'extra_ini': [],
  'source_base64': 'PD9waHAgZWNobyAkX0VOVlsiSFRUUF9QUk9YWSJdLCI6IiwkX0VOVlsiaHR0cF9wcm94eSJdOw==',
  'oracle': {'stdout': 'dXBwZXI6bGFzdA==', 'stderr': '', 'exit_status': 0}},
 {'id': 'server-overwrite-order',
  'environment_base64': ['TENfQUxMPUM=',
                         'VFo9VVRD',
                         'UkVRVUVTVF9USU1FPW9sZA==',
                         'YXJndj1vbGQ=',
                         'UEhQX1NFTEY9b2xk',
                         'UkVRVUVTVF9USU1FX0ZMT0FUPW9sZA==',
                         'YXJnYz1vbGQ=',
                         'U0NSSVBUX0ZJTEVOQU1FPW9sZA==',
                         'Wj1sYXN0'],
  'context': '/home/user/workspace/php-spec/.tools/review7-request-bootstrap-originals/server-overwrite-order.php',
  'clock': [-1, 500000],
  'extra_ini': [],
  'source_base64': 'PD9waHAgZm9yZWFjaCgkX1NFUlZFUiBhcyAkaz0+JHYpe2VjaG8gIlsiLCRrLCJdIjt9IGVjaG8gIjoiLCRfU0VSVkVSWyJSRVFVRVNUX1RJTUUiXSwiOiIsJF9TRVJWRVJbIlJFUVVFU1RfVElNRV9GTE9BVCJdLCI6IiwkX1NFUlZFUlsiYXJnYyJdLCI6IiwkX1NFUlZFUlsiYXJndiJdWzFdOw==',
  'oracle': {'stdout': 'W0xDX0FMTF1bVFpdW1JFUVVFU1RfVElNRV1bYXJndl1bUEhQX1NFTEZdW1JFUVVFU1RfVElNRV9GTE9BVF1bYXJnY11bU0NSSVBUX0ZJTEVOQU1FXVtaXVtTQ1JJUFRfTkFNRV1bUEFUSF9UUkFOU0xBVEVEXVtET0NVTUVOVF9ST09UXTowOi0wLjU6MzphbHBoYQ==',
             'stderr': '',
             'exit_status': 0}},
 {'id': 'argc-disabled',
  'environment_base64': ['TENfQUxMPUM=', 'VFo9VVRD'],
  'context': '/home/user/workspace/php-spec/.tools/review7-request-bootstrap-originals/argc-disabled.php',
  'clock': [-1, 500000],
  'extra_ini': ['register_argc_argv=0'],
  'source_base64': 'PD9waHAgZWNobyAkYXJnYywiOiIsJGFyZ3ZbMV0sIjoiLCRfU0VSVkVSWyJhcmdjIl0sIjoiLCRfU0VSVkVSWyJhcmd2Il1bMV07',
  'oracle': {'stdout': 'MzphbHBoYTozOmFscGhh', 'stderr': '', 'exit_status': 0}},
 {'id': 'server-disabled',
  'environment_base64': ['TENfQUxMPUM=', 'VFo9VVRD'],
  'context': '/home/user/workspace/php-spec/.tools/review7-request-bootstrap-originals/server-disabled.php',
  'clock': [-1, 500000],
  'extra_ini': ['variables_order=EGPC'],
  'source_base64': 'PD9waHAgZWNobyAkYXJnYywiOiIsJGFyZ3ZbMV0sIjoiO2ZvcmVhY2goJF9TRVJWRVIgYXMgJGs9PiR2KXtlY2hvICRrO30=',
  'oracle': {'stdout': 'MzphbHBoYTo=', 'stderr': '', 'exit_status': 0}},
 {'id': 'env-disabled',
  'environment_base64': ['TENfQUxMPUM=', 'VFo9VVRD', 'QT1vbmU='],
  'context': '/home/user/workspace/php-spec/.tools/review7-request-bootstrap-originals/env-disabled.php',
  'clock': [-1, 500000],
  'extra_ini': ['variables_order=GPCS'],
  'source_base64': 'PD9waHAgZWNobyBlbXB0eSgkX0VOViksIjoiLCRfU0VSVkVSWyJBIl07',
  'oracle': {'stdout': 'MTpvbmU=', 'stderr': '', 'exit_status': 0}},
 {'id': 'jit-disabled',
  'environment_base64': ['TENfQUxMPUM=', 'VFo9VVRD', 'QT1vbmU='],
  'context': '/home/user/workspace/php-spec/.tools/review7-request-bootstrap-originals/jit-disabled.php',
  'clock': [-1, 500000],
  'extra_ini': ['auto_globals_jit=0'],
  'source_base64': 'PD9waHAgZm9yZWFjaCgkR0xPQkFMUyBhcyAkaz0+JHYpe2VjaG8gIlsiLCRrLCJdIjt9',
  'oracle': {'stdout': 'W2FyZ3ZdW2FyZ2NdW19HRVRdW19QT1NUXVtfQ09PS0lFXVtfU0VSVkVSXVtfRU5WXVtfUkVRVUVTVF1bX0ZJTEVTXQ==',
             'stderr': '',
             'exit_status': 0}}]

def main():
    OUT=Path(tempfile.mkdtemp(prefix='request-adapter-',dir=ROOT/'.tools')); records=[]
    paths=json.loads((RUNTIME_ROOT/'spec/semantics/modules.json').read_text())
    bound={str(RUNTIME_ROOT/n):hashlib.sha256((RUNTIME_ROOT/n).read_bytes()).hexdigest() for n in paths}
    tools={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ADAPTER,t.PHP,ROOT/'.tools/php-file.so',Path(__file__)]}
    before=t.syntax_validation.implementation_fingerprint()
    def verify():
     for n,h in {**bound,**tools}.items():assert hashlib.sha256(Path(n).read_bytes()).hexdigest()==h,n
    verify()
    def enc(b):return base64.b64encode(b).decode()
    def bytes_json(b):return [str(n) for n in b]
    base={'op':'execute','ast':{'version':1,'program':[]},'steps':10000,'filename':enc(b'/request.php')}
    q={'env':[[enc(b'DUP'),enc(b'first')],[enc(b'DUP'),enc(b'last')],[enc(b'\xff'),enc(b'\xfe')]],'argv':[enc(b'/request.php'),enc(b''),enc(b'\xffarg')],'file':enc(b'/request.php'),'seconds':'-1','microseconds':500000,'variables':enc(b'EGPCS'),'jit':True}
    p=subprocess.Popen([str(ADAPTER),str(RUNTIME_ROOT)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    def ask(value):
     signal.setitimer(signal.ITIMER_REAL,45)
     try:
      p.stdin.write((value if isinstance(value,str) else json.dumps(value))+'\n');p.stdin.flush();return json.loads(p.stdout.readline())
     finally:signal.setitimer(signal.ITIMER_REAL,0)
    def record(name,request,predicate):
     response=ask(request);row={'id':name,'request':request,'response':response,'pass':predicate(response)};records.append(row)
     (OUT/'results.json').write_text(json.dumps({'records':records},indent=2)+'\n')
     assert row['pass'],row
    def completion(x,tag):return x.get('ok') is True and x['state']['COMPLETION']['tag']==tag
    def invalid(x):return completion(x,'UNSUPPORTED') and x['state']['COMPLETION']['args']==['invalid request primitive facts']
    def reject(x):return x.get('ok') is False and x.get('category')=='runner_failure'
    try:
     old=ABSENT_REQUEST
     record('absent-request-preserves-php-run',base,lambda x:x==old)
     expected={'ENV':[[bytes_json(base64.b64decode(a)),bytes_json(base64.b64decode(b))] for a,b in q['env']],'ARGV':[bytes_json(base64.b64decode(a)) for a in q['argv']],'FILE':bytes_json(b'/request.php'),'SECONDS':'-1','MICROSECONDS':'500000','VARIABLES':bytes_json(b'EGPCS'),'JIT':True,'CWD':None}
     record('ordered-byte-record-roundtrip',dict(base,request=q),lambda x:completion(x,'NORMAL') and x['state']['REQUEST']==expected)
     for seconds in ['-9223372036854775808','9223372036854775807','0']:
      value=dict(q,seconds=seconds)
      record('seconds-'+seconds,dict(base,request=value),lambda x,s=seconds:completion(x,'NORMAL') and x['state']['REQUEST']['SECONDS']==s)
     # Shape/base64 errors stay transport failures; none reaches request_valid.
     malformed=[('null',None),('list',[])]
     for key in q:
      value=copy.deepcopy(q);del value[key];malformed.append(('missing-'+key,value))
     malformed.extend([('extra',dict(q,extra=1)),('env-object',dict(q,env={})),('env-scalar',dict(q,env=['eA=='])),('env-short',dict(q,env=[['eA==']])),('env-long',dict(q,env=[['eA==','eQ==','eg==']])),('env-nonstring',dict(q,env=[[3,'eQ==']])),('argv-object',dict(q,argv={})),('argv-tag',dict(q,argv=[{'bytes':'eA=='}])),('file-tag',dict(q,file={'bytes':'eA=='})),('seconds-number',dict(q,seconds=1)),('seconds-zero-padding',dict(q,seconds='01')),('seconds-plus',dict(q,seconds='+1')),('seconds-negative-zero',dict(q,seconds='-0')),('seconds-large',dict(q,seconds='9223372036854775808')),('microseconds-negative',dict(q,microseconds=-1)),('microseconds-string',dict(q,microseconds='1')),('microseconds-float',dict(q,microseconds=1.5)),('jit-number',dict(q,jit=1)),('jit-string',dict(q,jit='true'))])
     for value in ['Y','YR==','YQ=','YQ===','Y?==','====']:
      malformed.append(('bad-base64-'+value,dict(q,file=value)))
     for name,value in malformed:record(name,dict(base,request=value),reject)
     text=json.dumps(dict(base,request=q))
     record('duplicate-inner-field',text.replace('"jit": true','"jit": true, "jit": false'),reject)
     record('duplicate-request-field',text[:-1]+', "request": '+json.dumps(q)+'}',reject)
     # Well-typed primitive inputs rejected explicitly by pure semantic admissibility.
     invalids=[('empty-env-name',dict(q,env=[['',enc(b'value')]]),False),('empty-argv',dict(q,argv=[]),True),('argv-file-mismatch',dict(q,argv=[enc(b'/other.php')]),True),('empty-file',dict(q,file='',argv=['']),True),('nul-file',dict(q,file=enc(b'/x\0'),argv=[enc(b'/x\0')]),True),('nul-argv',dict(q,argv=[q['file'],enc(b'a\0')]),True),('nul-env-name',dict(q,env=[[enc(b'A\0'),enc(b'x')]]),True),('equals-env-name',dict(q,env=[[enc(b'A=B'),enc(b'x')]]),True),('nul-env-value',dict(q,env=[[enc(b'A'),enc(b'x\0')]]),True),('usec-range',dict(q,microseconds=1000000),True),('empty-effective-config',dict(q,variables=''),True),('nul-effective-config',dict(q,variables=enc(b'E\0')),True)]
     for name,value,bad in invalids:record(name,dict(base,request=value),invalid if bad else lambda x:completion(x,'NORMAL'))
     # Optional CWD has independent transport and semantic validity checks.
     for name,cwd in [('absolute',b'/cwd'),('root',b'/'),('binary',b'/cwd\xff')]:
      value=dict(q,cwd=enc(cwd));record('cwd-'+name,dict(base,request=value),lambda x,c=cwd:completion(x,'NORMAL') and x['state']['REQUEST']['CWD']==bytes_json(c))
     for name,cwd in [('null',None),('integer',1),('bad-base64','YR=='),('object',{'bytes':'L2N3ZA=='})]:
      record('cwd-transport-'+name,dict(base,request=dict(q,cwd=cwd)),reject)
     for name,cwd in [('empty',b''),('nul',b'/x\0')]:record('cwd-semantic-'+name,dict(base,request=dict(q,cwd=enc(cwd))),invalid)
     text=json.dumps(dict(base,request=dict(q,cwd='L2N3ZA==')))
     record('cwd-duplicate',text.replace('"cwd": "L2N3ZA=="','"cwd": "L2N3ZA==", "cwd": "L290aGVy"'),reject)
     # An actual source pipeline through the new adapter, using unchanged retained inputs.
     frontend=t.Worker([str(t.PHP),'-n',*t.FLAGS,'-d','extension='+str(R/'.tools/php-file.so'),str(R/'frontend/worker.php')])
     try:
      for row in SOURCE_RECORDS:
       entries=[base64.b64decode(e).split(b'=',1) for e in row['environment_base64']]
       values={'env':[[enc(a),enc(b)] for a,b in entries],'argv':[enc(row['context'].encode()),enc(b'alpha'),enc(b'beta')],'file':enc(row['context'].encode()),'seconds':str(row['clock'][0]),'microseconds':row['clock'][1],'variables':enc(next((i.split('=',1)[1] for i in row['extra_ini'] if i.startswith('variables_order=')),'EGPCS').encode()),'jit':'auto_globals_jit=0' not in row['extra_ini']}
       parsed=frontend.request({'op':'parse','source':row['source_base64']})
       def matches(x,row=row):
        if not completion(x,'NORMAL'):return False
        events=x['state']['EVENTS'];stdout=b''.join(bytes(int(n) for n in e['args'][0]) for e in events if e['tag']=='OUTPUT')
        return stdout==base64.b64decode(row['oracle']['stdout']) and all(e['tag']=='OUTPUT' for e in events) and row['oracle']['exit_status']==0 and row['oracle']['stderr']==''
       record('source-'+row['id'],dict(base,ast=parsed['ast'],filename=values['file'],request=values),matches)
     finally:frontend.close()
    finally:
     p.stdin.close();p.wait(timeout=10)
     verify()
    assert before==t.syntax_validation.implementation_fingerprint()
    report={'result':'pass','scope':'Checked primitive request transport and eight literal bootstrap observations; optional CWD controls are distinct from compiled identity.','records':records,'runtime_inputs':bound,'tool_inputs':tools,'fingerprint':before}
    (OUT/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text(json.dumps(report,indent=2)+'\n')
    print(OUT,len(records),'request transport controls passed')

if __name__=="__main__":main()
