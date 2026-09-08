"""Copy current project inputs and existing executables for isolated validation."""
import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
R=Path.cwd(); sys.path.insert(0,str(R/'tests'));import validate
before=validate.implementation_fingerprint()
S=Path(tempfile.mkdtemp(prefix='php-spec-validation-',dir='/var/tmp'))
exclude={R:{'.git','.tools','_build'},R/'tests/semantics':{'_build'}}
def ignore(path,names):return list(exclude.get(Path(path),set()).intersection(names)|{'__pycache__'}.intersection(names))
shutil.copytree(R,S,dirs_exist_ok=True,symlinks=True,ignore=ignore)
binaries=['.tools/php/bin/php','.tools/php-file.so','_build/default/adapter/main.exe','tests/semantics/_build/default/numeric_runner.exe','.tools/php-coverage-build/sapi/cli/php','.tools/trace-enable.so']
for name in binaries:
 dst=S/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/name,dst)
for path in S.rglob('*'):
 if path.is_symlink():
  assert path.resolve().is_relative_to(S),(path,os.readlink(path))
loader={}
for name in binaries:
 run=subprocess.run(['ldd',str(S/name)],capture_output=True,text=True,check=True);assert 'not found' not in run.stdout
 for line in run.stdout.splitlines():
  if '=>' in line:
   target=line.split('=>',1)[1].strip().split(' ',1)[0]
   assert target.startswith(('/lib/','/usr/lib/')),(name,line)
 loader[name]=run.stdout
identity=subprocess.run([sys.executable,'-c','import sys,json;sys.path.insert(0,"tests");import validate;print(json.dumps(validate.implementation_fingerprint()))'],cwd=S,capture_output=True,text=True,check=True)
copyfp=json.loads(identity.stdout);after=validate.implementation_fingerprint();assert before==after==copyfp,(before,after,copyfp)
# Corpus membership includes source and non-source extraction records with exact source/profile bytes.
cmd=[sys.executable,'-c','import sys,json,hashlib;sys.path.insert(0,"tests");from corpus import inputs; rows=list(inputs()); print(json.dumps({"records":len(rows),"sha256":hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()}))']
original=subprocess.run(cmd,cwd=R,capture_output=True,text=True,check=True);copied=subprocess.run(cmd,cwd=S,capture_output=True,text=True,check=True)
assert original.stdout==copied.stdout,(original.stdout,copied.stdout)
syntax_roots=['frontend','adapter','spec','native','tests','scripts','bin','vendor/php-parser']
# Preserve exact scoped source bytes; future live semantic-only drift is distinguished during final acceptance.
manifest={}
for root in syntax_roots:
 for path in (S/root).rglob('*'):
  if path.is_file() and not {'__pycache__','_build'}.intersection(path.relative_to(S).parts) and path.suffix!='.pyc':manifest[str(path.relative_to(S))]=hashlib.sha256(path.read_bytes()).hexdigest()
for name in binaries+['Makefile','dune-project','coverage/encoding-spellings.json']:manifest[name]=hashlib.sha256((S/name).read_bytes()).hexdigest()
report={'snapshot':str(S),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'fingerprint':before,'corpus':json.loads(original.stdout),'files':manifest,'loader_dependencies':loader,'audit_script':{'path':'coverage/frontend-snapshot-audit.py','sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},'scope':'immutable copied-input validation using existing binaries; no rebuild or portability claim'}
(S/'coverage/validation-snapshot.json').write_text(json.dumps(report,indent=2)+'\n');(R/'.tools/review3-snapshot.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'snapshot':str(S),'fingerprint':before,'corpus':report['corpus']}),flush=True)
