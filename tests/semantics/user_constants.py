"""Ordinary declaration/lookup profiles and exact non-owning class results."""
from pathlib import Path
import hashlib
import json
import function_scope
ROOT=Path(__file__).resolve().parents[2]
CASES={k:v.encode() for k,v in json.loads((ROOT/'tests/semantics/user_constant_runtime_cases.json').read_text()).items()}
def main():
 before=set((ROOT/'.tools').glob('user-constants-*'))
 if not function_scope.main(CASES,'user-constants',Path(__file__)):
  return False
 created=set((ROOT/'.tools').glob('user-constants-*'))-before
 assert len(created)==1
 out=created.pop();report=json.loads((out/'report.json').read_text())
 expected=json.loads((ROOT/'tests/semantics/user_constant_class_cases.json').read_text());classes=[]
 for row in report['records']:
  if row['id'] not in expected:continue
  path=out/row['id']/'state.json';state=json.loads(path.read_text())['state']
  constant=next(c for c in state['USERCONSTANTS'] if c['NAME']==['67'])
  passed=constant['CLASS']==expected[row['id']] and state['CONSTCONTEXT'] is None
  classes.append({'id':row['id'],'expected':expected[row['id']],'actual':constant['CLASS'],'state_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pass':passed})
  assert passed,classes[-1]
 report['class_assertions']=len(classes)*2;report['class_records']=classes
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 if not report['selection']:(ROOT/'coverage/semantics/user-constants.json').write_text(json.dumps(report,indent=2)+'\n')
 print('Constant class assertions:',report['class_assertions']);return True
if __name__=='__main__':raise SystemExit(0 if main() else 1)
