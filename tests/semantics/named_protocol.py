from pathlib import Path
import base64,json,os,subprocess,tempfile
import request_environment as q
import request_environment_state as rs
import function_scope as fs
from recorded_worker import Worker

R=Path(__file__).resolve().parents[2]
D=Path(tempfile.mkdtemp(prefix='named-protocol-',dir=R/'.tools'))
(D/'producer.py').write_bytes(Path(__file__).read_bytes())
before=q.t.syntax_validation.implementation_fingerprint()
(D/'inputs.json').write_text(json.dumps({'fingerprint':before},indent=2))
print(D,flush=True)
SOURCES = {'cache': 'PD9waHAKY29uc3QgQz0iMngiO2Z1bmN0aW9uIGYoaW50ICR4LCR5PUMrMSwkej0zKXt9CmYoejozLHg6W10pOw==', 'tail': 'PD9waHAgZnVuY3Rpb24gZihzdHJpbmcgJiRhLGludCAmLi4uJHhzKXtlY2hvICJCT0RZIjt9JHg9MTskYmFkPVtdO2VjaG8gIkJFRk9SRSI7ZihhOiR4LGZpcnN0OiR4LGJhZDokYmFkKTtlY2hvICJBRlRFUiI7', 'line': 'PD9waHAKZnVuY3Rpb24gZigkeCl7fQpmKAogejoKICR1Cik7'}
GROUPS = [('cache',
  'dec $review_stage(pstate) : bool\n'
  'def $review_stage(S) = true -- if S.TODO = [NAMED_PREFLIGHT porigin 1]\n'
  'def $review_stage(S) = false -- otherwise\n'
  'dec $review_find(pstate, nat) : pstate\n'
  'def $review_find(S, n) = S -- if $review_stage(S)\n'
  'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
  '  -- if ~$review_stage(S)\n'
  '  -- if $(n > 0)\n'
  '  -- if n_rest = $(n - 1)\n'
  '  -- if S_next = $drive_steps(S, 1)\n',
  ['S_initial = __INITIAL__',
   'S = $review_find(S_initial[.COMPLETION = NORMAL], 300)',
   'S.TODO = [NAMED_PREFLIGHT porigin 1]',
   'S.CURRENT = (pcallcontext)',
   'pcallcontext.FUNCTION = porigin',
   'pcallcontext.CALLSITE = (porigin_call)',
   'pcallcontext.ARGC = 3',
   'pcallcontext.NAMED = eps',
   'S.DEFAULTCACHE = eps',
   '$lookup(S.ENV, [120]) = (n_x)',
   'S.STORE[n_x] = DEFINED (PARRAY n_array)',
   '~$named_defined(S, [121])',
   '$call_descriptors_valid(S)'],
  [('preflight-control', 'S', True),
   ('preflight-wrong-function', 'S[.TODO = [NAMED_PREFLIGHT porigin_call 1]]', False),
   ('preflight-wrong-origin', 'S[.ORIGIN = (porigin_call)]', False),
   ('preflight-skip-hole', 'S[.TODO = [NAMED_PREFLIGHT porigin 3]]', False),
   ('preflight-outside-extent', 'S[.TODO = [NAMED_PREFLIGHT porigin 99]]', False),
   ('preflight-legacy-type-bypass', 'S[.TODO = [TYPE_RECEIVE porigin 0]]', False),
   ('preflight-extra-queue', 'S[.TODO = [NAMED_PREFLIGHT porigin 1, DISCARD]]', False),
   ('preflight-arbitrary-result', 'S[.RESULT = KNOWN (PINT 99)]', True),
   ('preflight-revisit-supplied', 'S[.TODO = [NAMED_PREFLIGHT porigin 0]]', True),
   ('preflight-arbitrary-provided-value', '$write_name(S, [120], PINT 99)', True)]),
 ('cache',
  'dec $review_stage(pstate) : bool\n'
  'def $review_stage(S) = true -- if S.TODO = [NAMED_DEFAULT_BIND porigin 1]\n'
  'def $review_stage(S) = false -- otherwise\n'
  'dec $review_find(pstate, nat) : pstate\n'
  'def $review_find(S, n) = S -- if $review_stage(S)\n'
  'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
  '  -- if ~$review_stage(S)\n'
  '  -- if $(n > 0)\n'
  '  -- if n_rest = $(n - 1)\n'
  '  -- if S_next = $drive_steps(S, 1)\n',
  ['S_initial = __INITIAL__',
   'S = $review_find(S_initial[.COMPLETION = NORMAL], 300)',
   'S.TODO = [NAMED_DEFAULT_BIND porigin 1]',
   'S.CURRENT = (pcallcontext)',
   'pcallcontext.FUNCTION = porigin',
   'pcallcontext.CALLSITE = (porigin_call)',
   'S.CONSTCONTEXT = (pconstantcontext)',
   'S.ORIGIN = (pconstantcontext.ORIGIN)',
   'S.RESULT = KNOWN (PINT 3)',
   'S.DEFAULTCACHE = eps',
   '~$named_defined(S, [121])',
   '$call_descriptors_valid(S)'],
  [('bind-control', 'S', True),
   ('bind-wrong-origin', 'S[.ORIGIN = (porigin_call)]', False),
   ('bind-extra-queue', 'S[.TODO = [NAMED_DEFAULT_BIND porigin 1, DISCARD]]', False),
   ('bind-wrong-function', 'S[.TODO = [NAMED_DEFAULT_BIND porigin_call 1]]', False),
   ('bind-wrong-index', 'S[.TODO = [NAMED_DEFAULT_BIND porigin 0]]', False),
   ('bind-missing-context', 'S[.CONSTCONTEXT = eps]', False),
   ('bind-wrong-source-line', 'S[.CONSTCONTEXT = (pconstantcontext[.LINE = 102])]', False),
   ('bind-arbitrary-result', 'S[.RESULT = KNOWN (PINT 99)]', True)]),
 ('cache',
  'dec $review_stage(pstate) : bool\n'
  'def $review_stage(S) = true -- if S.TODO = (NAMED_ARGS porigin phpType7* 1 pnamedargs porigin_call? z) :: '
  'ptask_tail*\n'
  'def $review_stage(S) = false -- otherwise\n'
  'dec $review_find(pstate, nat) : pstate\n'
  'def $review_find(S, n) = S -- if $review_stage(S)\n'
  'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
  '  -- if ~$review_stage(S)\n'
  '  -- if $(n > 0)\n'
  '  -- if n_rest = $(n - 1)\n'
  '  -- if S_next = $drive_steps(S, 1)\n',
  ['S_initial = __INITIAL__',
   'S = $review_find(S_initial[.COMPLETION = NORMAL], 300)',
   'S.TODO = (NAMED_ARGS porigin phpType7* 1 pnamedargs (porigin_call) z) :: ptask_tail*',
   'pnamedargs.SLOTS = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 3))]',
   'pnamedargs.NAMED = eps',
   'S.CURRENT = eps',
   'S.DEFAULTCACHE = eps',
   '$call_descriptors_valid(S)'],
  [('pending-control', 'S', True),
   ('pending-wrong-function',
    'S[.TODO = (NAMED_ARGS porigin_call phpType7* 1 pnamedargs (porigin_call) z) :: ptask_tail*]',
    False),
   ('pending-wrong-index',
    'S[.TODO = (NAMED_ARGS porigin phpType7* 0 pnamedargs (porigin_call) z) :: ptask_tail*]',
    False),
   ('pending-filled-original-hole',
    'S[.TODO = (NAMED_ARGS porigin phpType7* 1 pnamedargs[.SLOTS = [NAMED_SENT (KNOWN PNULL), NAMED_HOLE, '
    'NAMED_SENT (KNOWN (PINT 3))]] (porigin_call) z) :: ptask_tail*]',
    False),
   ('pending-wrong-destination',
    'S[.TODO = (NAMED_ARGS porigin phpType7* 1 pnamedargs[.SLOTS = [NAMED_HOLE, NAMED_SENT (KNOWN (PINT '
    '3))]] (porigin_call) z) :: ptask_tail*]',
    False),
   ('pending-forged-extra-name',
    'S[.TODO = (NAMED_ARGS porigin phpType7* 1 pnamedargs[.NAMED = [([103], KNOWN (PINT 1))]] (porigin_call) '
    'z) :: ptask_tail*]',
    False),
   ('pending-wrong-call-line',
    'S[.TODO = (NAMED_ARGS porigin phpType7* 1 pnamedargs (porigin_call) 103) :: ptask_tail*]',
    False),
   ('pending-arbitrary-sent-value',
    'S[.TODO = (NAMED_ARGS porigin phpType7* 1 pnamedargs[.SLOTS = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT '
    '(KNOWN (PINT 99))]] (porigin_call) z) :: ptask_tail*]',
    True)]),
 ('cache',
  'dec $review_stage(pstate) : bool\n'
  'def $review_stage(S) = true -- if S.TODO = (NAMED_SEND porigin phpType7* 1 pnamedargs porigin_call? z) :: '
  'ptask_tail*\n'
  'def $review_stage(S) = false -- otherwise\n'
  'dec $review_find(pstate, nat) : pstate\n'
  'def $review_find(S, n) = S -- if $review_stage(S)\n'
  'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
  '  -- if ~$review_stage(S)\n'
  '  -- if $(n > 0)\n'
  '  -- if n_rest = $(n - 1)\n'
  '  -- if S_next = $drive_steps(S, 1)\n',
  ['S_initial = __INITIAL__',
   'S = $review_find(S_initial[.COMPLETION = NORMAL], 300)',
   'S.TODO = (NAMED_SEND porigin phpType7* 1 pnamedargs (porigin_call) z) :: ptask_tail*',
   'pnamedargs.SLOTS = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 3))]',
   'pnamedargs.NAMED = eps',
   'S.CURRENT = eps',
   'S.DEFAULTCACHE = eps',
   '$call_descriptors_valid(S)'],
  [('send-control', 'S', True),
   ('send-wrong-index',
    'S[.TODO = (NAMED_SEND porigin phpType7* 0 pnamedargs (porigin_call) z) :: ptask_tail*]',
    False)]),
 ('tail',
  'dec $review_stage(pstate) : bool\n'
  'def $review_stage(S) = true -- if S.TODO = [NAMED_VARIADIC_RECEIVE porigin 1]\n'
  'def $review_stage(S) = false -- otherwise\n'
  'dec $review_find(pstate, nat) : pstate\n'
  'def $review_find(S, n) = S -- if $review_stage(S)\n'
  'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
  '  -- if ~$review_stage(S)\n'
  '  -- if $(n > 0)\n'
  '  -- if n_rest = $(n - 1)\n'
  '  -- if S_next = $drive_steps(S, 1)\n',
  ['S_initial = __INITIAL__',
   'S = $review_find(S_initial[.COMPLETION = NORMAL], 400)',
   'S.TODO = [NAMED_VARIADIC_RECEIVE porigin 1]',
   'S.CURRENT = (pcallcontext)',
   'pcallcontext.FUNCTION = porigin',
   'pcallcontext.CALLSITE = (porigin_call)',
   'pcallcontext.ARGC = 1',
   'pcallcontext.NAMED = [(n_first*, REFERENCE n_shared), (n_badname*, REFERENCE n_bad)]',
   'n_first* = [102, 105, 114, 115, 116]',
   'n_badname* = [98, 97, 100]',
   'n_wrong* = [111]',
   'n_x* = [120]',
   'S.STORE[n_shared] = DEFINED (PINT 1)',
   '$lookup(S.ENV, [120, 115]) = (n_tail)',
   'S.STORE[n_tail] = DEFINED (PARRAY n_array)',
   '$call_descriptors_valid(S)'],
  [('tail-control', 'S', True),
   ('tail-wrong-function', 'S[.TODO = [NAMED_VARIADIC_RECEIVE porigin_call 1]]', False),
   ('tail-wrong-origin', 'S[.ORIGIN = (porigin_call)]', False),
   ('tail-skip-error', 'S[.TODO = [NAMED_VARIADIC_RECEIVE porigin 2]]', False),
   ('tail-rewind-collected', 'S[.TODO = [NAMED_VARIADIC_RECEIVE porigin 0]]', False),
   ('tail-wrong-collected-key',
    'S[.ARRAYS = $array_replace(S.ARRAYS, n_array, $array_insert($array_empty(), KSTRING n_wrong*, ALIAS '
    'n_shared))]',
    False),
   ('tail-wrong-next',
    'S[.ARRAYS = $array_replace(S.ARRAYS, n_array, S.ARRAYS[n_array][.NEXT = 99])]',
    False),
   ('tail-arbitrary-collected-value',
    'S[.ARRAYS = $array_replace(S.ARRAYS, n_array, $array_insert(S.ARRAYS[n_array], KSTRING n_first*, DIRECT '
    '(PINT 99)))]',
    True),
   ('tail-shared-value-evolution', 'S[.STORE = $set_cell(S.STORE, n_shared, DEFINED (PINT 7))]', True),
   ('tail-unowned-variable-slot',
    'S[.CURRENT = (pcallcontext[.NAMED = [(n_first*, VARIABLE n_x* 1), (n_badname*, REFERENCE n_bad)]])]',
    False),
   ('tail-wrong-sent-reference-mode',
    'S[.CURRENT = (pcallcontext[.NAMED = [(n_first*, KNOWN (PINT 99)), (n_badname*, REFERENCE n_bad)]])]',
    False),
   ('tail-extra-queue', 'S[.TODO = [NAMED_VARIADIC_RECEIVE porigin 1, DISCARD]]', False)]),
 ('cache',
  'dec $review_stage(pstate) : bool\n'
  'def $review_stage(S) = true -- if S.TODO = (NAMED_ARGS porigin phpType7* 1 pnamedargs porigin_call? z) :: '
  'ptask_tail*\n'
  'def $review_stage(S) = false -- otherwise\n'
  'dec $review_find(pstate, nat) : pstate\n'
  'def $review_find(S, n) = S -- if $review_stage(S)\n'
  'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
  '  -- if ~$review_stage(S)\n'
  '  -- if $(n > 0)\n'
  '  -- if n_rest = $(n - 1)\n'
  '  -- if S_next = $drive_steps(S, 1)\n',
  ['S_initial = __INITIAL__',
   'S = $review_find(S_initial[.COMPLETION = NORMAL], 300)',
   'S.TODO = (NAMED_ARGS porigin phpType7* 1 pnamedargs (porigin_call) z) :: ptask_tail*',
   'pnamedargs.SLOTS = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 3))]',
   'pnamedargs.NAMED = eps',
   'S.CURRENT = eps',
   'S.DEFAULTCACHE = eps',
   '$call_descriptors_valid(S)',
   'poperand_sent* = [KNOWN (PINT 3)]'],
  [('legacy-args-substitution',
    'S[.TODO = (CALL_ARGS porigin phpType7* 1 poperand_sent* (porigin_call) z) :: ptask_tail*]',
    False)]),
 ('cache',
  'dec $review_stage(pstate) : bool\n'
  'def $review_stage(S) = true -- if S.TODO = (NAMED_SEND porigin phpType7* 1 pnamedargs porigin_call? z) :: '
  'ptask_tail*\n'
  'def $review_stage(S) = false -- otherwise\n'
  'dec $review_find(pstate, nat) : pstate\n'
  'def $review_find(S, n) = S -- if $review_stage(S)\n'
  'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
  '  -- if ~$review_stage(S)\n'
  '  -- if $(n > 0)\n'
  '  -- if n_rest = $(n - 1)\n'
  '  -- if S_next = $drive_steps(S, 1)\n',
  ['S_initial = __INITIAL__',
   'S = $review_find(S_initial[.COMPLETION = NORMAL], 300)',
   'S.TODO = (NAMED_SEND porigin phpType7* 1 pnamedargs (porigin_call) z) :: ptask_tail*',
   'pnamedargs.SLOTS = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PINT 3))]',
   'pnamedargs.NAMED = eps',
   'S.CURRENT = eps',
   'S.DEFAULTCACHE = eps',
   '$call_descriptors_valid(S)',
   'poperand_sent* = [KNOWN (PINT 3)]'],
  [('legacy-send-substitution',
    'S[.TODO = (CALL_SEND porigin phpType7* 1 poperand_sent* (porigin_call) z) :: ptask_tail*]',
    False)]),
 ('line',
  'dec $review_stage(pstate) : bool\n'
  'def $review_stage(S) = true -- if S.TODO = (NAMED_SEND porigin phpType7* 0 pnamedargs porigin_call? z) :: '
  'ptask_tail*\n'
  'def $review_stage(S) = false -- otherwise\n'
  'dec $review_find(pstate, nat) : pstate\n'
  'def $review_find(S, n) = S -- if $review_stage(S)\n'
  'def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)\n'
  '  -- if ~$review_stage(S)\n'
  '  -- if $(n > 0)\n'
  '  -- if n_rest = $(n - 1)\n'
  '  -- if S_next = $drive_steps(S, 1)\n'
  'dec $review_line(pcodeexpr*, pcpath) : pcodeexpr*\n'
  'def $review_line(eps, pcpath) = eps\n'
  'def $review_line((CODEEXPR pcpath z b) :: pcodeexpr*, pcpath) = (CODEEXPR pcpath $(z + 100) b) :: '
  'pcodeexpr*\n'
  'def $review_line((CODEEXPR pcpath_other z b) :: pcodeexpr*, pcpath) = (CODEEXPR pcpath_other z b) :: '
  '$review_line(pcodeexpr*, pcpath)\n'
  '  -- if pcpath_other =/= pcpath\n',
  ['S_initial = __INITIAL__',
   'S = $review_find(S_initial[.COMPLETION = NORMAL], 300)',
   'S.TODO = (NAMED_SEND porigin phpType7* 0 pnamedargs (porigin_call) z) :: ptask_tail*',
   'porigin_call = PORIGIN n_unit pcpath_call',
   'pcpath = pcpath_call ++ [PCFIELD 1, PCINDEX 0, PCFIELD 1]',
   'S.CODE = [pcode]',
   'pcode.UNIT = n_unit',
   'S.CURRENT = eps',
   'S.DEFAULTCACHE = eps',
   '$call_descriptors_valid(S)'],
  [('line-control', 'S', True),
   ('line-child-forgery',
    'S[.CODE = [pcode[.EXPRESSIONS = $review_line(pcode.EXPRESSIONS, pcpath)]]]',
    False)])]
initials={}
for kind,encoded in SOURCES.items():
 directory=D/kind;directory.mkdir();path=directory/'source.php';path.write_bytes(base64.b64decode(encoded))
 entries=[b'LC_ALL=C',b'TZ=UTC',b'FIRST=one'];payload=directory/'request.input';payload.write_bytes(q.packet(1700000000,125000,entries))
 request={'env':[[q.b64(k),q.b64(v)]for k,v in(e.split(b'=',1)for e in entries)],'argv':[q.b64(os.fsencode(path))],'file':q.b64(os.fsencode(path)),'seconds':'1700000000','microseconds':125000,'variables':q.b64(b'EGPCS'),'jit':True,'cwd':q.b64(os.fsencode(directory))}
 native=fs.native(path,payload,directory);row={'source_base64':encoded,'context':str(path),'request':request,'native':native};(directory/'original.json').write_text(json.dumps(row,indent=2))
 frontend=adapter=None
 try:
  frontend=Worker([str(q.t.PHP),'-n',*q.t.FLAGS,'-d','extension='+str(R/'.tools/php-file.so'),str(R/'frontend/worker.php')],directory/'frontend-wire')
  adapter=Worker([str(R/'_build/default/adapter/main.exe'),str(R)],directory/'adapter-wire')
  parsed=frontend.request({'op':'parse','source':encoded});assert parsed['accepted']
  checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True});(directory/'checked.json').write_text(json.dumps(checked))
  execute={'op':'execute','ast':parsed['ast'],'steps':10000,'filename':q.b64(os.fsencode(path)),'request':request};(directory/'execute.json').write_text(json.dumps(execute))
  result=adapter.request(execute);(directory/'state.json').write_text(json.dumps(result));actual=q.cli.observe(result['state'],str(path));assert actual['status']=='php_error' and all(actual[k]==native[k]for k in ['stdout','stderr','exit_status'])
 finally:
  try:
   if frontend:frontend.close()
  finally:
   if adapter:adapter.close()
 initials[kind]='$php_request_run('+checked['fixture']+', 0, '+json.dumps(q.b64(os.fsencode(path)))+', '+rs.request_fixture(request)+')'
modules=[R/p for p in json.loads((R/'spec/semantics/modules.json').read_text())];runner=R/'tests/semantics/_build/default/numeric_runner.exe';records=[]
for kind,prefix,common,variants in GROUPS:
 for name,change,valid in variants:
  checks=[c.replace('__INITIAL__',initials[kind])for c in common]+['S_changed = '+change,'$heap_valid($heap_graph(S_changed))','$call_descriptors_valid(S_changed) = '+str(valid).lower(),'S_zero = $drive(S_changed, 0)','S_zero.COMPLETION = '+('BUDGET'if valid else 'UNSUPPORTED "invalid compiled function descriptor"')]
  completion='THROWN "Error" n_message* 4'if kind=='line'else 'NORMAL'if name=='preflight-arbitrary-provided-value'else 'THROWN "TypeError" n_message* '+('1'if kind=='tail'else '2')
  checks+=['S_full = $drive(S_changed, 10000)','S_full.COMPLETION = '+(completion if valid else 'UNSUPPORTED "invalid compiled function descriptor"')]
  if valid:
   cache='eps'if kind in ['tail','line']else '[{ORIGIN porigin_default, VALUE PINT '+('99'if name=='bind-arbitrary-result'else '3')+', CLASS PVSCALAR}]'
   checks+=['S_full.DEFAULTCACHE = '+cache,'S_full.REPORTING = 30719','S_full.FRAMES = eps','S_full.CURRENT = eps','S_full.HELD = eps','S_full.SILENCES = eps','$heap_valid($heap_graph(S_full))']
  fixture=D/(name+'.watsup');fixture.write_text(prefix+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+c+'\n'for c in checks))
  command=[str(runner),*map(str,modules),str(fixture)];(D/(name+'.command.json')).write_text(json.dumps(command))
  try:result=subprocess.run(command,capture_output=True,timeout=90)
  except subprocess.TimeoutExpired as error:
   (D/(name+'.stdout')).write_bytes(error.stdout or b'');(D/(name+'.stderr')).write_bytes(error.stderr or b'');(D/(name+'.status.json')).write_text(json.dumps({'status':'timeout','seconds':90}));raise
  (D/(name+'.stdout')).write_bytes(result.stdout);(D/(name+'.stderr')).write_bytes(result.stderr);(D/(name+'.status.json')).write_text(json.dumps({'status':'exit','exit_status':result.returncode}))
  item={'id':name,'valid':valid,'assertions':len(checks),'pass':result.returncode==0 and result.stdout.strip()==b'true' and not result.stderr};records.append(item);(D/'results.json').write_text(json.dumps(records,indent=2));print(item,flush=True)
assert before==q.t.syntax_validation.implementation_fingerprint()
report={'result':'pass'if all(r['pass']for r in records)else 'fail','fingerprint':before,'raw':str(D),'controls':len(records),'assertions':sum(r['assertions']for r in records),'fresh_native_contexts':len(SOURCES),'records':records}
(D/'report.json').write_text(json.dumps(report,indent=2));assert report['result']=='pass';(R/'coverage/semantics/named-protocol.json').write_text(json.dumps(report,indent=2));print(D,report['controls'],report['assertions'])
